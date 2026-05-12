class GameAPI {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
    this.ws = null;
    this.wsReconnectTimer = null;
  }

  async _request(method, path, body) {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    if (body !== undefined) {
      opts.body = JSON.stringify(body);
    }
    const res = await fetch(`${this.baseURL}${path}`, opts);
    return res.json();
  }

  async startGame() {
    return this._request('POST', '/game/start');
  }

  async move(direction) {
    return this._request('POST', '/game/move', { direction });
  }

  async answer(answer) {
    return this._request('POST', '/game/answer', { answer });
  }

  async resetGame() {
    return this._request('POST', '/game/reset');
  }

  async getState() {
    return this._request('GET', '/game/state');
  }

  async updateRotation(dt) {
    return this._request('POST', '/game/update_rotation', { dt });
  }

  async sendMove(direction) {
    return this._request('POST', '/game/move', { direction });
  }

  async sendAnswer(answer) {
    return this._request('POST', '/game/answer', { answer });
  }

  async sendReset() {
    return this._request('POST', '/game/reset');
  }

  disconnect() {
    // No-op for REST-only mode
  }
}
