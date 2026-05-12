function lerp(a, b, t) {
  return a + (b - a) * t;
}

function colToPixel(col, cellSize, offset) {
  return offset + col * cellSize;
}

function rowToPixel(row, cellSize, offset) {
  return offset + row * cellSize;
}

function pixelToCol(x, cellSize, offset) {
  return Math.floor((x - offset) / cellSize);
}

function pixelToRow(y, cellSize, offset) {
  return Math.floor((y - offset) / cellSize);
}

function clamp(val, min, max) {
  return Math.max(min, Math.min(max, val));
}
