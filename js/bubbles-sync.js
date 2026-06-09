/**
 * 双屏同步 — BroadcastChannel + localStorage 兜底（跨窗口/跨标签页）
 */
(function (global) {
  const CHANNEL_NAME = 'bubbles-dual-screen-v1';

  class BubblesSync {
    constructor(role) {
      this.role = role;
      this.listeners = new Set();
      this._connected = false;
      this._lastPeerTs = 0;

      this.channel = typeof BroadcastChannel !== 'undefined'
        ? new BroadcastChannel(CHANNEL_NAME)
        : null;

      if (this.channel) {
        this.channel.onmessage = (e) => this._dispatch(e.data);
      }

      this._onStorage = (e) => {
        if (e.key !== CHANNEL_NAME || !e.newValue) return;
        try {
          this._dispatch(JSON.parse(e.newValue));
        } catch (_) { /* ignore */ }
      };
      window.addEventListener('storage', this._onStorage);

      this._heartbeat = setInterval(() => {
        this.send({ type: 'ping' });
      }, 2500);
    }

    _dispatch(data) {
      if (!data || data.source === this.role) return;
      this._lastPeerTs = Date.now();
      this._connected = true;
      for (const fn of this.listeners) fn(data);
    }

    on(fn) {
      this.listeners.add(fn);
      return () => this.listeners.delete(fn);
    }

    send(payload) {
      const msg = { ...payload, source: this.role, ts: Date.now() };
      if (this.channel) this.channel.postMessage(msg);
      try {
        localStorage.setItem(CHANNEL_NAME, JSON.stringify(msg));
      } catch (_) { /* ignore quota */ }
    }

    isPeerConnected(maxAgeMs = 8000) {
      return this._connected && Date.now() - this._lastPeerTs < maxAgeMs;
    }

    destroy() {
      clearInterval(this._heartbeat);
      window.removeEventListener('storage', this._onStorage);
      if (this.channel) this.channel.close();
      this.listeners.clear();
    }
  }

  global.BubblesSync = BubblesSync;
})(window);
