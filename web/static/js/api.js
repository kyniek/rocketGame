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
    return this._request('POST', '/api/game/start');
  }

  async move(direction) {
    return this._request('POST', '/api/game/move', { direction });
  }

  async answer(answer) {
    return this._request('POST', '/api/game/answer', { answer });
  }

  async resetGame() {
    return this._request('POST', '/api/game/reset');
  }

  async getState() {
    return this._request('GET', '/api/game/state');
  }

  connect(onStateUpdate, onChallenge, onGameOver, onVictory) {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
    this.ws = new WebSocket(`${protocol}//${location.host}/ws`);

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      switch (data.type) {
        case 'state':
          onStateUpdate(data.state);
          break;
        case 'challenge':
          onChallenge(data.challenge);
          break;
        case 'game_over':
          onGameOver(data.state, data.score);
          break;
        case 'victory':
          onVictory(data.state, data.score, data.wrong_answers);
          break;
      }
    };

    this.ws.onclose = () => {
      this.wsReconnectTimer = setTimeout(() => this.connect(onStateUpdate, onChallenge, onGameOver, onVictory), 2000);
    };
  }

  sendMove(direction) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'move', direction }));
    }
  }

  sendAnswer(answer) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'answer', answer }));
    }
  }

  sendReset() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'reset' }));
    }
  }

  disconnect() {
    if (this.wsReconnectTimer) {
      clearTimeout(this.wsReconnectTimer);
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
