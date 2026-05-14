class CanvasRenderer {
  constructor(canvas, cellSize = 40) {
    // Uses lerp() from utils.js for smooth animation
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.cellSize = cellSize;
    this.offsetX = 0;
    this.offsetY = 0;

    // Preload images
    this.images = {};
    this.imageLoadPromises = [];

    const assetPath = 'assets/';
    const imageFiles = {
      background: `${assetPath}ingame_background.jpg`,
      rocket: `${assetPath}rocket_small.png`,
      titleRocket: `${assetPath}title_rocket.png`,
    };
    for (let i = 1; i <= 5; i++) {
      imageFiles[`rock_${i}`] = `${assetPath}rock_${i}.png`;
    }

    for (const [key, url] of Object.entries(imageFiles)) {
      this.images[key] = new Image();
      this.images[key].src = url;
    }

    this.resize();
    window.addEventListener('resize', () => this.resize());
  }

  resize() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
    this._computeLayout();
  }

  _computeLayout() {
    const cols = 30;
    const rows = 5;
    const maxCellW = this.canvas.width / cols;
    const maxCellH = this.canvas.height / rows;
    this.cellSize = Math.min(maxCellW, maxCellH, 50);
    this.offsetX = (this.canvas.width - cols * this.cellSize) / 2;
    this.offsetY = (this.canvas.height - rows * this.cellSize) / 2;
  }

  drawBackground(ctx) {
    const img = this.images.background;
    if (img && img.complete && img.naturalWidth > 0) {
      ctx.drawImage(img, 0, 0, this.canvas.width, this.canvas.height);
    } else {
      ctx.fillStyle = '#0a0a1a';
      ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }
  }

  drawGrid(ctx, grid, fogDiscovered, obstacleRotation) {
    const cols = grid.length;
    const rows = cols > 0 ? grid[0].length : 0;

    for (let col = 0; col < cols; col++) {
      for (let row = 0; row < rows; row++) {
        const x = this.offsetX + col * this.cellSize;
        const y = this.offsetY + row * this.cellSize;
        const cell = grid[col]?.[row] || '';

        if (!fogDiscovered[col]?.[row]) {
          ctx.fillStyle = '#000';
          ctx.fillRect(x, y, this.cellSize, this.cellSize);
          continue;
        }

        if (cell === 'obstacle') {
          ctx.fillStyle = '#4a2020';
        } else if (cell === 'start') {
          ctx.fillStyle = '#204a20';
        } else {
          ctx.fillStyle = '#1a1a2e';
        }
        ctx.fillRect(x, y, this.cellSize, this.cellSize);

        ctx.strokeStyle = 'rgba(255,255,255,0.1)';
        ctx.strokeRect(x, y, this.cellSize, this.cellSize);
      }
    }
  }

  drawObstacles(ctx, grid, obstacleRotation) {
    const cols = grid.length;
    const rows = cols > 0 ? grid[0].length : 0;

    for (let col = 0; col < cols; col++) {
      for (let row = 0; row < rows; row++) {
        if (grid[col]?.[row] !== 'obstacle') continue;
        if (!obstacleRotation[`${col},${row}`]?.active) continue;

        const x = this.offsetX + col * this.cellSize + this.cellSize / 2;
        const y = this.offsetY + row * this.cellSize + this.cellSize / 2;
        const rot = obstacleRotation[`${col},${row}`];
        const angle = (rot.angle || 0) * Math.PI / 180;
        const texture = rot.texture || 0;

        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(angle);

        const img = this.images[`rock_${texture + 1}`];
        if (img && img.complete && img.naturalWidth > 0) {
          const size = this.cellSize * 0.8;
          ctx.drawImage(img, -size / 2, -size / 2, size, size);
        } else {
          ctx.fillStyle = '#8B4513';
          ctx.beginPath();
          ctx.arc(0, 0, this.cellSize * 0.4, 0, Math.PI * 2);
          ctx.fill();
        }

        ctx.restore();
      }
    }
  }

  drawRocket(ctx, rocket) {
    const x = this.offsetX + rocket.col * this.cellSize + this.cellSize / 2;
    const y = this.offsetY + rocket.row * this.cellSize + this.cellSize / 2;
    const img = this.images.rocket;

    ctx.save();
    ctx.translate(x, y);

    // Point rocket to the right (facing forward)
    ctx.rotate(Math.PI / 2);

    if (img && img.complete && img.naturalWidth > 0) {
      const size = this.cellSize * 0.7;
      ctx.drawImage(img, -size / 2, -size / 2, size, size);
    } else {
      ctx.fillStyle = '#ffcc00';
      ctx.beginPath();
      ctx.moveTo(0, -this.cellSize * 0.35);
      ctx.lineTo(-this.cellSize * 0.2, this.cellSize * 0.35);
      ctx.lineTo(this.cellSize * 0.2, this.cellSize * 0.35);
      ctx.closePath();
      ctx.fill();
    }

    ctx.restore();
  }

  drawUI(ctx, score, lives) {
    ctx.fillStyle = '#fff';
    ctx.font = `bold ${this.cellSize * 0.6}px 'Segoe UI', sans-serif`;
    ctx.textAlign = 'left';
    ctx.fillText(`Score: ${score}`, this.offsetX, this.offsetY - 10);

    // Draw lives as small rocket icons
    for (let i = 0; i < lives; i++) {
      const lx = this.offsetX + (i + 1) * this.cellSize * 0.8;
      ctx.fillStyle = '#ffcc00';
      ctx.beginPath();
      ctx.arc(lx, this.offsetY - 10, this.cellSize * 0.2, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  render(state) {
    const ctx = this.ctx;
    const s = state;

    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    this.drawBackground(ctx);
    this.drawGrid(ctx, s.grid, s.fog_discovered);
    this.drawObstacles(ctx, s.grid, s.obstacle_rotation || {});
    this.drawRocket(ctx, s.rocket);
    this.drawUI(ctx, s.score, s.lives);
  }
}
