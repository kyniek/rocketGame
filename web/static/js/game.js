class Game {
  constructor(api, renderer, challengeModal) {
    this.api = api;
    this.renderer = renderer;
    this.challengeModal = challengeModal;
    this.state = null;
    this.running = false;
    this.lastTime = 0;
    this.feedbackTimer = null;
  }

  start() {
    document.getElementById('start-screen').classList.add('hidden');
    document.getElementById('victory-screen').classList.add('hidden');
    document.getElementById('gameover-screen').classList.add('hidden');
    this.challengeModal.hide();

    this.api.startGame().then((data) => {
      this.onStateUpdate(data.state);
      this.running = true;
      this.lastTime = performance.now();
      this.gameLoop();
    });
  }

  reset() {
    this.running = false;
    this.api.disconnect();
    document.getElementById('start-screen').classList.remove('hidden');
    document.getElementById('victory-screen').classList.add('hidden');
    document.getElementById('gameover-screen').classList.add('hidden');
    this.challengeModal.hide();
  }

  handleMove(direction) {
    if (!this.running || !this.state) return;
    if (this.state.challenge_active) return;
    if (this.state.game_over || this.state.victory) return;

    this.api.sendMove(direction);
  }

  handleAnswer(answer) {
    if (!this.running) return;
    this.challengeModal.hide();
    this.api.sendAnswer(answer);
  }

  onStateUpdate(state) {
    this.state = state;
    this.renderer.render(state);

    if (state.challenge_active && state.current_challenge) {
      this.challengeModal.show(state.current_challenge);
    }

    if (state.game_over) {
      this.running = false;
      document.getElementById('gameover-score').textContent = `Score: ${state.score}`;
      document.getElementById('gameover-screen').classList.remove('hidden');
    }
  }

  onChallenge(challenge) {
    if (this.state) {
      this.challengeModal.show(challenge);
    }
  }

  onGameOver(state, score) {
    this.running = false;
    this.state = state;
    this.renderer.render(state);
    document.getElementById('gameover-score').textContent = `Score: ${score}`;
    document.getElementById('gameover-screen').classList.remove('hidden');
  }

  onVictory(state, score, wrongAnswers) {
    this.running = false;
    this.state = state;
    this.renderer.render(state);

    document.getElementById('victory-score').textContent = `Score: ${score}`;

    const missedEl = document.getElementById('victory-missed');
    missedEl.innerHTML = '';
    if (wrongAnswers && wrongAnswers.length > 0) {
      const label = document.createElement('p');
      label.textContent = 'Questions you missed:';
      label.style.fontWeight = 'bold';
      label.style.marginBottom = '8px';
      missedEl.appendChild(label);

      const maxMissed = Math.min(wrongAnswers.length, 5);
      for (let i = 0; i < maxMissed; i++) {
        const item = document.createElement('p');
        item.textContent = `${wrongAnswers[i].question} (Your answer: ${wrongAnswers[i].user_answer}, Correct: ${wrongAnswers[i].correct_answer})`;
        missedEl.appendChild(item);
      }
    }

    document.getElementById('victory-screen').classList.remove('hidden');
  }

  gameLoop() {
    if (!this.running) return;

    const now = performance.now();
    const dt = (now - this.lastTime) / 1000;
    this.lastTime = now;

    this.renderer.render(this.state);

    requestAnimationFrame(() => this.gameLoop());
  }

  handleKey(e) {
    if (!this.running) return;

    switch (e.key) {
      case 'ArrowRight':
        e.preventDefault();
        this.handleMove('forward');
        break;
      case 'ArrowUp':
        e.preventDefault();
        this.handleMove('up');
        break;
      case 'ArrowDown':
        e.preventDefault();
        this.handleMove('down');
        break;
    }
  }
}
