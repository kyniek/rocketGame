document.addEventListener('DOMContentLoaded', () => {
  const api = new GameAPI('/api');
  const canvas = document.getElementById('game-canvas');
  const renderer = new CanvasRenderer(canvas);
  const challengeModal = new ChallengeModal(
    document.getElementById('challenge-modal'),
    (answer) => api.sendAnswer(answer)
  );
  const game = new Game(api, renderer, challengeModal);

  document.getElementById('start-btn').addEventListener('click', () => game.start());
  document.getElementById('victory-restart-btn').addEventListener('click', () => game.reset());
  document.getElementById('gameover-restart-btn').addEventListener('click', () => game.reset());
  document.addEventListener('keydown', (e) => game.handleKey(e));
});
