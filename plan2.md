# Plan: Migrate gameRocket to a Web Game

## Context

gameRocket is a Python arcade game (using the Arcade library) where a player controls a rocket navigating a 30x3 maze grid, avoiding obstacles, and answering quiz questions. The current codebase has a **clean separation** between game logic (models, managers, challenges) and presentation (views), making it well-suited for a web migration. The goal is to create a playable web version accessible from any browser.

## Architecture Decision

**Python backend (FastAPI) + Vanilla JS frontend (HTML5 Canvas), all inside `web/` folder**

Rationale:
- **Self-contained web version** -- everything needed to run the web game lives in one `web/` directory
- **Flat package structure** -- simplified imports, no nested packages
- **Existing Python code copied into `web/`** -- models, managers, challenges are ported with flat imports
- **Server runs from `web/`** -- `uvicorn server:app` from inside `web/` starts everything
- **FastAPI** provides REST API + WebSocket + static file serving in one process
- **Vanilla JS + Canvas** avoids build toolchain complexity
- **Original code untouched** -- desktop game continues to work

## Required Libraries

### Python Backend (installed inside `web/`)
| Library | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.115+ | REST API framework |
| uvicorn[standard] | 0.32+ | ASGI server |
| websockets | 14+ | WebSocket support |
| pydantic | 2.10+ | Request/response validation |
| requests | 2.32+ | API testing |

### Existing (unchanged, kept in root)
| Library | Version | Purpose |
|---------|---------|---------|
| arcade | 3.3.3 | Desktop game UI (kept for original app) |
| pytest | latest | Testing |

### Frontend
No external libraries needed -- vanilla JS + HTML5 Canvas only.

---

## Directory Structure (Final)

```
gameRocket/                          # Original project (unchanged)
  gameRocket/                        # Original package
    main.py, models/, managers/, challenges/, views/, tests/
  questions.json
  plan2.md

web/                                 # Self-contained web game
  pyproject.toml                     # Python package config for web server
  requirements.txt                   # Backend dependencies
  questions.json                     # Copy from root
  server.py                          # FastAPI app (single file server)
  game/                              # Flattened game logic (copied + adapted)
    __init__.py
    constants.py                     # Pure constants (flattened from game_engine)
    engine.py                        # GameEngine class (flattened)
    maze_generator.py                # Copied from models/
    game_grid.py                     # Copied from models/
    rocket.py                        # Copied from models/
    fog_of_war.py                    # Copied from models/
    lives_manager.py                 # Copied from managers/
    score_manager.py                 # Copied from managers/
    challenge_manager.py             # Copied from managers/
    challenge.py                     # Copied from challenges/
    challenge_loader.py              # Copied from challenges/
  static/                            # Frontend files
    index.html
    css/
      styles.css
    js/
      main.js
      game.js
      canvas.js
      challenge.js
      api.js
      utils.js
    assets/
      title_rocket.png
      rocket_small.png
      ingame_background.jpg
      rock_1.png ... rock_5.png
```

## Game State Model (shared between backend and frontend)

The server becomes the source of truth. Frontend sends actions, server validates and broadcasts state updates.

```
GameState = {
  grid: Cell[][]           // 30x3 grid with obstacle positions
  rocket: { col: number, row: number }
  lives: number
  score: number
  challenges: Challenge[]  // remaining unanswered questions
  wrongAnswers: { question, userAnswer }[]
  fogDiscovered: boolean[][]  // 30x3 visibility matrix
  level: number
  challengeActive: boolean
  currentChallenge: Challenge | null
  gameOver: boolean
  victory: boolean
}
```

---

## Phase 1: Set Up `web/` Directory and Copy Reusable Code

### Step 1.1: Create `web/` directory structure

```bash
mkdir -p web/game web/static/css web/static/js web/static/assets
```

**Tests to verify:**
```bash
test -d web/game && echo "game dir: PASS" || echo "game dir: FAIL"
test -d web/static && echo "static dir: PASS" || echo "static dir: FAIL"
test -d web/static/css && echo "css dir: PASS" || echo "css dir: FAIL"
test -d web/static/js && echo "js dir: PASS" || echo "js dir: FAIL"
test -d web/static/assets && echo "assets dir: PASS" || echo "assets dir: FAIL"
```

### Step 1.2: Copy reusable Python code into `web/game/` (flattened)

Copy all pure-logic Python files from the original project into `web/game/` with flat structure. Adapt imports to use flat paths.

**Files to copy and adapt:**

| From (original) | To (web/) | Import changes |
|----------------|-----------|----------------|
| `game_constants.py` | `web/game/constants.py` | Remove Arcade window deps, keep gameplay constants |
| `models/maze_generator.py` | `web/game/maze_generator.py` | Change `from game_constants import ...` to `from constants import ...` |
| `models/game_grid.py` | `web/game/game_grid.py` | Change `from game_constants import ...` to `from constants import ...` |
| `models/rocket.py` | `web/game/rocket.py` | Change `from game_constants import ...` to `from constants import ...` |
| `models/fog_of_war.py` | `web/game/fog_of_war.py` | Change `from game_constants import ...` to `from constants import ...` |
| `managers/lives_manager.py` | `web/game/lives_manager.py` | No internal imports, no changes |
| `managers/score_manager.py` | `web/game/score_manager.py` | No internal imports, no changes |
| `managers/challenge_manager.py` | `web/game/challenge_manager.py` | Change `from challenges.challenge_loader import ...` to `from challenge_loader import ...` |
| `challenges/challenge.py` | `web/game/challenge.py` | No imports, no changes |
| `challenges/challenge_loader.py` | `web/game/challenge_loader.py` | Change `from challenges.challenge import ...` to `from challenge import ...` |

**Also copy:**
- `questions.json` -> `web/questions.json`
- `assets/*` -> `web/static/assets/`

**Tests to verify:**
```bash
# Verify all files exist
for f in constants.py maze_generator.py game_grid.py rocket.py fog_of_war.py lives_manager.py score_manager.py challenge_manager.py challenge.py challenge_loader.py; do
  test -f "web/game/$f" && echo "$f: PASS" || echo "$f: FAIL"
done

# Verify questions.json copied
test -f web/questions.json && echo "questions.json: PASS" || echo "questions.json: FAIL"

# Verify assets copied
for i in 1 2 3 4 5; do test -f "web/static/assets/rock_$i.png" && echo "rock_$i.png: PASS" || echo "rock_$i.png: FAIL"; done
test -f web/static/assets/rocket_small.png && echo "rocket_small.png: PASS" || echo "rocket_small.png: FAIL"
test -f web/static/assets/ingame_background.jpg && echo "ingame_background.jpg: PASS" || echo "ingame_background.jpg: FAIL"
test -f web/static/assets/title_rocket.png && echo "title_rocket.png: PASS" || echo "title_rocket.png: FAIL"
```

### Step 1.3: Create `web/game/__init__.py`

```python
"""Flattened game logic package for web version."""
```

### Step 1.4: Create `web/game/constants.py`

Pure gameplay constants (no Arcade window dimension dependencies).

**Content:**
- `GRID_COLS = 30`, `GRID_ROWS = 5`
- `ROCKET_MIN_ROW = 0`, `ROCKET_MAX_ROW = 4`, `ROCKET_ANIMATION_DURATION = 0.2`
- `OBSTACLE_ROTATION_START_SPEED = 180.0`, `OBSTACLE_ROTATION_DECAY = 45.0`
- `STARTING_LIVES = 3`, `POINTS_PER_CORRECT_ANSWER = 10`, `CHALLENGE_CHANCE = 0.2`
- `FEEDBACK_DURATION_MS = 750`, `VICTORY_MAX_MISSED = 5`
- Aliases: `COLS`, `ROWS`, `MIN_ROW`, `MAX_ROW`

**Tests to verify:**
```bash
cd web && python -c "from game.constants import GameConstants; assert GameConstants.GRID_COLS == 30; assert GameConstants.STARTING_LIVES == 3; print('Constants PASS')" && cd ..
```

### Step 1.5: Verify copied game logic works

Test that all flat imports resolve correctly from within `web/`.

```bash
cd web && python -c "
from game.constants import GameConstants
from game.maze_generator import MazeGenerator
from game.game_grid import GameGrid
from game.rocket import Rocket
from game.fog_of_war import FogOfWar
from game.lives_manager import LivesManager
from game.score_manager import ScoreManager
from game.challenge_manager import ChallengeManager
from game.challenge import MultipleChoiceChallenge, TextChallenge
from game.challenge_loader import ChallengeLoader
print('All flat imports PASS')
" && cd ..
```

**Phase 1 verification: All file existence tests + constants test + flat imports test must pass.**

---

## Phase 2: Build Game Engine Inside `web/game/`

### Step 2.1: Create `web/game/engine.py`

Create the core `GameEngine` class that composes all game logic classes into a pure-Python engine.

**Public API:**
- `__init__(questions_file="questions.json")` -- create new game with random start row
- `reset() -> dict` -- reset to new random game, return serializable state
- `move_forward() -> dict` -- move rocket forward, may trigger challenge/collision/level advance
- `move_up() -> dict` -- move rocket up
- `move_down() -> dict` -- move rocket down
- `get_next_challenge() -> dict` -- get next random challenge
- `answer_challenge(answer: str) -> dict` -- submit answer
- `update_obstacle_rotation(dt: float) -> dict` -- update rotation physics
- `get_state() -> dict` -- get full serializable game state

**State serialization includes:**
- `grid`: 30x3 list of strings (cell values)
- `rocket`: `{col, row}`
- `lives`, `score`, `level`
- `challenges_remaining`: count of unanswered questions
- `challenges`: list of `{id, question, correct_answer, type, options}`
- `wrong_answers`: list of `{question, user_answer, correct_answer}`
- `fog_discovered`: 30x3 boolean matrix
- `obstacle_rotation`: dict of `{col,row}: {angle, speed, active, dir, texture}`
- `challenge_active`, `current_challenge`, `game_over`, `victory`

**Bug fix included:** `wrong_answers` is now populated on wrong answers (was never populated before).

**Tests to verify:**
```bash
cd web && python -c "
from game.engine import GameEngine

# Test 1: Engine creation
engine = GameEngine('questions.json')
state = engine.get_state()
assert state['lives'] == 3
assert state['score'] == 0
assert state['level'] == 1
assert state['challenges_remaining'] == 10
assert state['rocket'] == {'col': 0, 'row': 4}
assert state['game_over'] == False
assert state['victory'] == False
print('Test 1 PASS: Engine creation and initial state')

# Test 2: Move forward
state = engine.move_forward()
assert engine.get_state()['rocket']['col'] == 1
print('Test 2 PASS: Move forward')

# Test 3: Move up/down
state = engine.move_up()
state = engine.move_down()
assert engine.get_state()['rocket']['row'] == 4
print('Test 3 PASS: Move up/down')

# Test 4: Reset
state2 = engine.reset()
assert state2['lives'] == 3
assert state2['score'] == 0
assert state2['game_over'] == False
print('Test 4 PASS: Reset')

# Test 5: Terminal state blocks moves
engine.game_over = True
state = engine.move_forward()
assert state['game_over'] == True
print('Test 5 PASS: Terminal state blocks moves')
" && cd ..
```

### Step 2.2: Verify maze generation from flat imports

```bash
cd web && python -c "
from game.maze_generator import MazeGenerator
gen = MazeGenerator()
grid = gen.generate(2)
assert len(grid) == 30
assert all(len(row) == 5 for row in grid)
assert grid[0][2] == 'start'
print('Maze generation PASS')
" && cd ..
```

**Phase 2 verification: All 5 engine tests + 1 maze test must pass.**

---

## Phase 3: Build FastAPI Server Inside `web/`

### Step 3.1: Create `web/server.py`

Single-file FastAPI application with all endpoints and WebSocket support.

**Endpoints:**

| Method | Path | Request Body | Response | Description |
|--------|------|-------------|----------|-------------|
| POST | `/api/game/start` | `{}` | `{ "state": {...} }` | Start new game |
| POST | `/api/game/move` | `{ "direction": "forward"|"up"|"down" }` | `{ "state": {...}, "challenge": {...\|null} }` | Move rocket |
| POST | `/api/game/answer` | `{ "answer": "string" }` | `{ "state": {...}, "result": "correct"\|"wrong" }` | Submit answer |
| POST | `/api/game/reset` | `{}` | `{ "state": {...} }` | Reset game |
| GET | `/api/game/state` | `{}` | `{ "state": {...} }` | Get current state |

**WebSocket:**
- `ws://host/ws` -- real-time state sync
- Client messages: `{ "type": "move", "direction": "..." }`, `{ "type": "answer", "answer": "..." }`, `{ "type": "reset" }`
- Server broadcasts: `{ "type": "state", "state": {...} }`, `{ "type": "challenge", "challenge": {...} }`, `{ "type": "game_over" }`, `{ "type": "victory" }`

**Static files:**
- `GET /` -> serves `static/index.html`
- `GET /css/styles.css` -> serves CSS
- `GET /js/*.js` -> serves JS files
- `GET /assets/*` -> serves game assets

**Tests to verify:**
```bash
cd web && python -c "
# Verify server.py exists and has required components
import ast, sys

with open('server.py', 'r') as f:
    tree = ast.parse(f.read())

code = open('server.py').read()
assert 'FastAPI' in code, 'Missing FastAPI import'
assert 'api/game/start' in code or '/start' in code, 'Missing start endpoint'
assert 'api/game/move' in code or '/move' in code, 'Missing move endpoint'
assert 'api/game/answer' in code or '/answer' in code, 'Missing answer endpoint'
assert 'api/game/reset' in code or '/reset' in code, 'Missing reset endpoint'
assert 'WebSocket' in code or 'websocket' in code, 'Missing WebSocket'
assert 'StaticFiles' in code or 'static' in code, 'Missing static files'
assert 'GameEngine' in code, 'Missing GameEngine import'
print('All server.py structure checks PASS')
" && cd ..
```

### Step 3.2: Create `web/requirements.txt`

```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
websockets>=14.0
pydantic>=2.10.0
requests>=2.32.0
```

### Step 3.3: Create `web/pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "gameRocket-web"
version = "1.0.0"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "websockets>=14.0",
    "pydantic>=2.10.0",
]
```

### Step 3.4: Test server from within `web/`

Start server and test all endpoints via HTTP.

```bash
cd web
pip install -r requirements.txt

uvicorn server:app --reload --port 8765 &
SERVER_PID=$!
sleep 2

# Test start endpoint
curl -s -X POST http://localhost:8765/api/game/start | python -c "
import sys, json
data = json.load(sys.stdin)
state = data['state']
assert state['lives'] == 3
assert state['score'] == 0
assert state['challenges_remaining'] == 10
print('Test: POST /api/game/start PASS')
"

# Test move forward endpoint
curl -s -X POST http://localhost:8765/api/game/move -H 'Content-Type: application/json' -d '{"direction": "forward"}' | python -c "
import sys, json
data = json.load(sys.stdin)
state = data['state']
assert state['rocket']['col'] == 1
print('Test: POST /api/game/move (forward) PASS')
"

# Test move up endpoint
curl -s -X POST http://localhost:8765/api/game/move -H 'Content-Type: application/json' -d '{"direction": "up"}' | python -c "
import sys, json
data = json.load(sys.stdin)
state = data['state']
assert state['rocket']['row'] == 4
print('Test: POST /api/game/move (up) PASS')
"

# Test answer endpoint
curl -s -X POST http://localhost:8765/api/game/answer -H 'Content-Type: application/json' -d '{"answer": "4"}' | python -c "
import sys, json
data = json.load(sys.stdin)
state = data['state']
assert state['score'] == 10
print('Test: POST /api/game/answer PASS')
"

# Test reset endpoint
curl -s -X POST http://localhost:8765/api/game/reset | python -c "
import sys, json
data = json.load(sys.stdin)
state = data['state']
assert state['lives'] == 3
assert state['score'] == 0
print('Test: POST /api/game/reset PASS')
"

kill $SERVER_PID 2>/dev/null
echo "All REST endpoint tests PASS"
cd ..
```

### Step 3.5: Test WebSocket from within `web/`

```bash
cd web
uvicorn server:app --reload --port 8766 &
SERVER_PID=$!
sleep 2

python -c "
import asyncio, websockets, json

async def test_ws():
    async with websockets.connect('ws://localhost:8766/ws') as ws:
        # Test 1: Connect and get initial state
        msg = await asyncio.wait_for(ws.recv(), timeout=2)
        data = json.loads(msg)
        assert data['type'] == 'state'
        assert data['state']['lives'] == 3
        print('Test 1: WebSocket connect + initial state PASS')

        # Test 2: Send move forward
        await ws.send(json.dumps({'type': 'move', 'direction': 'forward'}))
        msg = await asyncio.wait_for(ws.recv(), timeout=2)
        data = json.loads(msg)
        assert data['type'] == 'state'
        assert data['state']['rocket']['col'] == 1
        print('Test 2: WebSocket move PASS')

        # Test 3: Reset
        await ws.send(json.dumps({'type': 'reset'}))
        msg = await asyncio.wait_for(ws.recv(), timeout=2)
        data = json.loads(msg)
        assert data['type'] == 'state'
        assert data['state']['lives'] == 3
        print('Test 3: WebSocket reset PASS')

asyncio.run(test_ws())
"

kill $SERVER_PID 2>/dev/null
echo "All WebSocket tests PASS"
cd ..
```

### Step 3.6: Test static file serving from within `web/`

```bash
cd web
uvicorn server:app --reload --port 8767 &
SERVER_PID=$!
sleep 2

curl -s http://localhost:8767/ | grep -q '<canvas' && echo "Static index.html: PASS" || echo "Static index.html: FAIL"
curl -s http://localhost:8767/css/styles.css | grep -q 'canvas' && echo "Static CSS: PASS" || echo "Static CSS: FAIL"
curl -s http://localhost:8767/js/main.js | grep -q 'GameAPI' && echo "Static JS: PASS" || echo "Static JS: FAIL"
curl -s http://localhost:8767/assets/rocket_small.png -o /dev/null -w '%{http_code}' | grep -q '200' && echo "Static assets: PASS" || echo "Static assets: FAIL"

kill $SERVER_PID 2>/dev/null
echo "All static file tests PASS"
cd ..
```

**Phase 3 verification: Server structure check + 5 REST tests + 3 WebSocket tests + 4 static file tests must pass.**

---

## Phase 4: Build Web Frontend Inside `web/static/`

### Step 4.1: Create `web/static/index.html`

HTML structure with:
- Canvas element for game rendering
- Container divs for each screen (start, game, challenge, victory, game-over)
- Link to CSS and JS files

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>gameRocket</title>
  <link rel="stylesheet" href="css/styles.css">
</head>
<body>
  <canvas id="game-canvas"></canvas>

  <!-- Start Screen -->
  <div id="start-screen">
    <h1>GAME ROCKET</h1>
    <p>Educational Rocket Game</p>
    <div id="instructions">
      <p>Use ARROW KEYS to control the rocket:</p>
      <p>  UP/DOWN - Change row</p>
      <p>  RIGHT - Move forward</p>
      <p>Avoid RED obstacles (lose life on collision)</p>
      <p>Answer questions (20% chance on forward move)</p>
      <p>  Correct: +10 points</p>
      <p>  Wrong: -1 life</p>
      <p>Answer ALL questions correctly to WIN!</p>
    </div>
    <button id="start-btn">START GAME</button>
  </div>

  <!-- Game Screen (canvas is always visible behind screens) -->

  <!-- Challenge Modal -->
  <div id="challenge-modal" class="hidden">
    <div id="challenge-content">
      <h2 id="challenge-question"></h2>
      <div id="challenge-options"></div>
      <input type="text" id="challenge-input" class="hidden" placeholder="Type your answer...">
    </div>
  </div>

  <!-- Victory Screen -->
  <div id="victory-screen" class="hidden">
    <h1>VICTORY!</h1>
    <p id="victory-score"></p>
    <div id="victory-missed"></div>
    <button id="victory-restart-btn">NEW GAME</button>
  </div>

  <!-- Game Over Screen -->
  <div id="gameover-screen" class="hidden">
    <h1>GAME OVER</h1>
    <p id="gameover-score"></p>
    <button id="gameover-restart-btn">RESTART</button>
  </div>

  <script src="js/utils.js"></script>
  <script src="js/api.js"></script>
  <script src="js/canvas.js"></script>
  <script src="js/challenge.js"></script>
  <script src="js/game.js"></script>
  <script src="js/main.js"></script>
</body>
</html>
```

**Tests to verify:**
```bash
grep -q '<canvas' web/static/index.html && echo "Canvas element: PASS" || echo "Canvas element: FAIL"
grep -q 'id="start-screen"' web/static/index.html && echo "Start screen: PASS" || echo "Start screen: FAIL"
grep -q 'id="game-canvas"' web/static/index.html && echo "Game canvas: PASS" || echo "Game canvas: FAIL"
grep -q 'id="challenge-modal"' web/static/index.html && echo "Challenge modal: PASS" || echo "Challenge modal: FAIL"
grep -q 'id="victory-screen"' web/static/index.html && echo "Victory screen: PASS" || echo "Victory screen: FAIL"
grep -q 'id="gameover-screen"' web/static/index.html && echo "Game over screen: PASS" || echo "Game over screen: FAIL"
grep -q 'id="start-btn"' web/static/index.html && echo "Start button: PASS" || echo "Start button: FAIL"
grep -q 'js/utils.js' web/static/index.html && echo "utils.js included: PASS" || echo "utils.js included: FAIL"
grep -q 'js/api.js' web/static/index.html && echo "api.js included: PASS" || echo "api.js included: FAIL"
grep -q 'js/canvas.js' web/static/index.html && echo "canvas.js included: PASS" || echo "canvas.js included: FAIL"
grep -q 'js/challenge.js' web/static/index.html && echo "challenge.js included: PASS" || echo "challenge.js included: FAIL"
grep -q 'js/game.js' web/static/index.html && echo "game.js included: PASS" || echo "game.js included: FAIL"
grep -q 'js/main.js' web/static/index.html && echo "main.js included: PASS" || echo "main.js included: FAIL"
```

### Step 4.2: Create `web/static/css/styles.css`

CSS for all screens:
- Full-screen canvas, no scrollbars
- Start screen: centered content, title, instructions, button
- Challenge modal: overlay with question, options, input
- Victory/game-over screens: centered content, score display, restart button
- Button hover effects
- Responsive layout

**Tests to verify:**
```bash
grep -q 'canvas' web/static/css/styles.css && echo "Canvas styles: PASS" || echo "Canvas styles: FAIL"
grep -q '#challenge-modal' web/static/css/styles.css && echo "Modal styles: PASS" || echo "Modal styles: FAIL"
grep -q '#start-btn' web/static/css/styles.css && echo "Button styles: PASS" || echo "Button styles: FAIL"
grep -q '.hidden' web/static/css/styles.css && echo "Hidden class: PASS" || echo "Hidden class: FAIL"
grep -q '#victory-screen' web/static/css/styles.css && echo "Victory styles: PASS" || echo "Victory styles: FAIL"
grep -q '#gameover-screen' web/static/css/styles.css && echo "GameOver styles: PASS" || echo "GameOver styles: FAIL"
```

### Step 4.3: Create `web/static/js/utils.js`

Helper functions:
```javascript
function lerp(a, b, t) { return a + (b - a) * t; }
function colToPixel(col, cellSize, offset) { return offset + col * cellSize; }
function rowToPixel(row, cellSize, offset) { return offset + row * cellSize; }
function pixelToCol(x, cellSize, offset) { return Math.floor((x - offset) / cellSize); }
function pixelToRow(y, cellSize, offset) { return Math.floor((y - offset) / cellSize); }
function clamp(val, min, max) { return Math.max(min, Math.min(max, val)); }
```

**Tests to verify:**
```bash
grep -q 'function lerp' web/static/js/utils.js && echo 'lerp: PASS' || echo 'lerp: FAIL'
grep -q 'function colToPixel' web/static/js/utils.js && echo 'colToPixel: PASS' || echo 'colToPixel: FAIL'
grep -q 'function rowToPixel' web/static/js/utils.js && echo 'rowToPixel: PASS' || echo 'rowToPixel: FAIL'
grep -q 'function pixelToCol' web/static/js/utils.js && echo 'pixelToCol: PASS' || echo 'pixelToCol: FAIL'
grep -q 'function clamp' web/static/js/utils.js && echo 'clamp: PASS' || echo 'clamp: FAIL'
```

### Step 4.4: Create `web/static/js/api.js`

HTTP + WebSocket client:
```javascript
class GameAPI {
  constructor(baseURL = '/api') { ... }

  // HTTP methods
  async startGame() { ... }
  async move(direction) { ... }
  async answer(answer) { ... }
  async resetGame() { ... }
  async getState() { ... }

  // WebSocket methods
  connect(onStateUpdate, onChallenge, onGameOver, onVictory) { ... }
  sendMove(direction) { ... }
  sendAnswer(answer) { ... }
  sendReset() { ... }
  disconnect() { ... }
}
```

**Tests to verify:**
```bash
grep -q 'class GameAPI' web/static/js/api.js && echo 'API class: PASS' || echo 'API class: FAIL'
grep -q 'async startGame' web/static/js/api.js && echo 'startGame method: PASS' || echo 'startGame method: FAIL'
grep -q 'async move' web/static/js/api.js && echo 'move method: PASS' || echo 'move method: FAIL'
grep -q 'async answer' web/static/js/api.js && echo 'answer method: PASS' || echo 'answer method: FAIL'
grep -q 'WebSocket' web/static/js/api.js && echo 'WebSocket: PASS' || echo 'WebSocket: FAIL'
grep -q 'sendMove' web/static/js/api.js && echo 'sendMove: PASS' || echo 'sendMove: FAIL'
grep -q 'sendAnswer' web/static/js/api.js && echo 'sendAnswer: PASS' || echo 'sendAnswer: FAIL'
grep -q 'sendReset' web/static/js/api.js && echo 'sendReset: PASS' || echo 'sendReset: FAIL'
```

### Step 4.5: Create `web/static/js/canvas.js`

Canvas2D rendering engine:
```javascript
class CanvasRenderer {
  constructor(canvas, cellSize) { ... }

  // Drawing methods
  drawBackground(ctx, backgroundImage) { ... }
  drawGrid(ctx, grid, fogDiscovered) { ... }
  drawObstacles(ctx, grid, obstacleRotation, cellSize, offset) { ... }
  drawRocket(ctx, rocket, cellSize, offset) { ... }
  drawUI(ctx, score, lives) { ... }

  // Animation
  update(dt) { ... }
  render() { ... }
}
```

**Rendering details:**
- Background image stretched to full canvas
- Grid cells drawn as rectangles with fog-of-war overlay (black for undiscovered)
- Obstacles drawn as rotated rock images using `ctx.rotate()`
- Rocket drawn as sprite with smooth animation (lerp between cells)
- Score and lives drawn as text overlay in top-left corner

**Tests to verify:**
```bash
grep -q 'class CanvasRenderer' web/static/js/canvas.js && echo 'Renderer class: PASS' || echo 'Renderer class: FAIL'
grep -q 'drawBackground' web/static/js/canvas.js && echo 'drawBackground: PASS' || echo 'drawBackground: FAIL'
grep -q 'drawGrid' web/static/js/canvas.js && echo 'drawGrid: PASS' || echo 'drawGrid: FAIL'
grep -q 'drawObstacles' web/static/js/canvas.js && echo 'drawObstacles: PASS' || echo 'drawObstacles: FAIL'
grep -q 'drawRocket' web/static/js/canvas.js && echo 'drawRocket: PASS' || echo 'drawRocket: FAIL'
grep -q 'drawUI' web/static/js/canvas.js && echo 'drawUI: PASS' || echo 'drawUI: FAIL'
grep -q 'ctx.rotate' web/static/js/canvas.js && echo 'Obstacle rotation: PASS' || echo 'Obstacle rotation: FAIL'
grep -q 'lerp' web/static/js/canvas.js && echo 'Animation lerp: PASS' || echo 'Animation lerp: FAIL'
```

### Step 4.6: Create `web/static/js/challenge.js`

Challenge modal UI:
```javascript
class ChallengeModal {
  constructor(container, onSubmit) { ... }

  show(challenge) { ... }
  hide() { ... }
  _renderMultipleChoice(challenge) { ... }
  _renderTextChallenge(challenge) { ... }
}
```

**Features:**
- Multiple choice: clickable option buttons, keyboard 1/2/3
- Text challenge: text input field, Enter to submit
- Green/red flash feedback for 750ms
- Closes automatically after feedback

**Tests to verify:**
```bash
grep -q 'class ChallengeModal' web/static/js/challenge.js && echo 'Modal class: PASS' || echo 'Modal class: FAIL'
grep -q 'MultipleChoice' web/static/js/challenge.js && echo 'Multiple choice: PASS' || echo 'Multiple choice: FAIL'
grep -q 'TextChallenge' web/static/js/challenge.js && echo 'Text challenge: PASS' || echo 'Text challenge: FAIL'
grep -q '750' web/static/js/challenge.js && echo 'Feedback duration: PASS' || echo 'Feedback duration: FAIL'
```

### Step 4.7: Create `web/static/js/game.js`

Main game logic and rendering loop:
```javascript
class Game {
  constructor(api, renderer, challengeModal) { ... }

  start() { ... }
  reset() { ... }
  handleMove(direction) { ... }
  handleAnswer(answer) { ... }
  onStateUpdate(state) { ... }
  onChallenge(challenge) { ... }
  onGameOver(score) { ... }
  onVictory(score, wrongAnswers) { ... }
  gameLoop() { ... }
}
```

**Game flow:**
1. User clicks "Start Game" -> `api.startGame()` -> renders game screen
2. User presses arrow keys -> `api.move(direction)` -> renders updated state
3. 20% chance on forward move -> challenge triggers -> shows challenge modal
4. User answers -> `api.answer()` -> updates score/lives
5. All questions answered correctly + reach goal -> victory screen
6. Lives reach 0 -> game over screen

**Tests to verify:**
```bash
grep -q 'class Game' web/static/js/game.js && echo 'Game class: PASS' || echo 'Game class: FAIL'
grep -q 'handleMove' web/static/js/game.js && echo 'handleMove: PASS' || echo 'handleMove: FAIL'
grep -q 'handleAnswer' web/static/js/game.js && echo 'handleAnswer: PASS' || echo 'handleAnswer: FAIL'
grep -q 'gameLoop' web/static/js/game.js && echo 'gameLoop: PASS' || echo 'gameLoop: FAIL'
grep -q 'onStateUpdate' web/static/js/game.js && echo 'onStateUpdate: PASS' || echo 'onStateUpdate: FAIL'
grep -q 'onChallenge' web/static/js/game.js && echo 'onChallenge: PASS' || echo 'onChallenge: FAIL'
grep -q 'onGameOver' web/static/js/game.js && echo 'onGameOver: PASS' || echo 'onGameOver: FAIL'
grep -q 'onVictory' web/static/js/game.js && echo 'onVictory: PASS' || echo 'onVictory: FAIL'
```

### Step 4.8: Create `web/static/js/main.js`

Application entry point:
```javascript
document.addEventListener('DOMContentLoaded', () => {
  const api = new GameAPI('/api');
  const canvas = document.getElementById('game-canvas');
  const renderer = new CanvasRenderer(canvas);
  const challengeModal = new ChallengeModal(
    document.getElementById('challenge-modal'),
    (answer) => api.sendAnswer(answer)
  );
  const game = new Game(api, renderer, challengeModal);

  // Wire up UI events
  document.getElementById('start-btn').addEventListener('click', () => game.start());
  document.getElementById('victory-restart-btn').addEventListener('click', () => game.reset());
  document.getElementById('gameover-restart-btn').addEventListener('click', () => game.reset());
  document.addEventListener('keydown', (e) => game.handleKey(e));
});
```

**Tests to verify:**
```bash
grep -q 'new GameAPI' web/static/js/main.js && echo 'GameAPI init: PASS' || echo 'GameAPI init: FAIL'
grep -q 'new CanvasRenderer' web/static/js/main.js && echo 'CanvasRenderer init: PASS' || echo 'CanvasRenderer init: FAIL'
grep -q 'new ChallengeModal' web/static/js/main.js && echo 'ChallengeModal init: PASS' || echo 'ChallengeModal init: FAIL'
grep -q 'new Game' web/static/js/main.js && echo 'Game init: PASS' || echo 'Game init: FAIL'
grep -q 'start-btn' web/static/js/main.js && echo 'Start button: PASS' || echo 'Start button: FAIL'
grep -q 'keydown' web/static/js/main.js && echo 'Keyboard handler: PASS' || echo 'Keyboard handler: FAIL'
```

**Phase 4 verification: All HTML structure tests (13) + CSS tests (6) + JS tests (25+) must pass.**

---

## Phase 5: End-to-End Testing

### Step 5.1: Integration test - full game flow

Start the server from within `web/` and test the complete game flow via HTTP API:

```bash
cd web
uvicorn server:app --reload --port 8768 &
SERVER_PID=$!
sleep 2

python -c "
import requests, json

BASE = 'http://localhost:8768/api/game'

# 1. Start game
r = requests.post(f'{BASE}/start')
assert r.status_code == 200
state = r.json()['state']
assert state['lives'] == 3
assert state['score'] == 0
assert state['challenges_remaining'] == 10
print('1. Start game: PASS')

# 2. Move forward multiple times
for i in range(5):
    r = requests.post(f'{BASE}/move', json={'direction': 'forward'})
    assert r.status_code == 200
print('2. Move forward x5: PASS')

# 3. Move up
r = requests.post(f'{BASE}/move', json={'direction': 'up'})
assert r.status_code == 200
print('3. Move up: PASS')

# 4. Move down
r = requests.post(f'{BASE}/move', json={'direction': 'down'})
assert r.status_code == 200
print('4. Move down: PASS')

# 5. Reset
r = requests.post(f'{BASE}/reset')
assert r.status_code == 200
state = r.json()['state']
assert state['lives'] == 3
assert state['score'] == 0
print('5. Reset: PASS')

# 6. Answer a question (first question in questions.json is '2+2=4')
r = requests.post(f'{BASE}/answer', json={'answer': '4'})
assert r.status_code == 200
state = r.json()['state']
assert state['score'] == 10  # correct answer
print('6. Answer correct: PASS')

# 7. Answer wrong
r = requests.post(f'{BASE}/answer', json={'answer': 'wrong'})
assert r.status_code == 200
state = r.json()['state']
assert state['score'] == 0  # -10 points
print('7. Answer wrong: PASS')

print()
print('All integration tests PASS')
"

kill $SERVER_PID 2>/dev/null
cd ..
```

### Step 5.2: Browser test

Start server from `web/` and open `http://localhost:8768/` in a browser:

```bash
cd web
uvicorn server:app --reload --port 8769 &
# Then manually open http://localhost:8769/ in browser
```

Verify:
1. Start screen displays with title, instructions, and "Start Game" button
2. Clicking "Start Game" shows the game canvas with grid, rocket, and UI
3. Arrow keys move the rocket smoothly
4. Fog of war reveals cells as rocket moves
5. Obstacles are displayed with rotation animation
6. Score and lives are displayed in top-left corner
7. When a challenge triggers, the modal appears with question and options
8. Selecting an answer shows green/red feedback and returns to game
9. Reaching goal advances to next level with new maze
10. Game over screen shows when lives reach 0
11. Victory screen shows when all questions answered correctly
12. Restart button returns to start screen

```bash
kill $SERVER_PID 2>/dev/null
cd ..
```

**Phase 5 verification: Integration test must pass all 7 sub-tests. Browser test must pass all 12 manual checks.**

---

## File Summary

| Action | File/Directory | Purpose |
|--------|---------------|---------|
| **Inside `web/`** | | |
| Create | `web/game/__init__.py` | Package init |
| Create | `web/game/constants.py` | Pure gameplay constants |
| Create | `web/game/engine.py` | Core game engine class |
| Create | `web/game/maze_generator.py` | Copied from models/, flat imports |
| Create | `web/game/game_grid.py` | Copied from models/, flat imports |
| Create | `web/game/rocket.py` | Copied from models/, flat imports |
| Create | `web/game/fog_of_war.py` | Copied from models/, flat imports |
| Create | `web/game/lives_manager.py` | Copied from managers/ |
| Create | `web/game/score_manager.py` | Copied from managers/ |
| Create | `web/game/challenge_manager.py` | Copied from managers/, flat imports |
| Create | `web/game/challenge.py` | Copied from challenges/ |
| Create | `web/game/challenge_loader.py` | Copied from challenges/, flat imports |
| Create | `web/server.py` | FastAPI app (single file) |
| Create | `web/requirements.txt` | Backend dependencies |
| Create | `web/pyproject.toml` | Python package config |
| Create | `web/questions.json` | Copy from root |
| Create | `web/static/index.html` | Frontend entry |
| Create | `web/static/css/styles.css` | Styles |
| Create | `web/static/js/utils.js` | Helper functions |
| Create | `web/static/js/api.js` | HTTP + WebSocket client |
| Create | `web/static/js/canvas.js` | Canvas2D rendering |
| Create | `web/static/js/challenge.js` | Challenge modal UI |
| Create | `web/static/js/game.js` | Game logic + rendering loop |
| Create | `web/static/js/main.js` | App entry point |
| Create | `web/static/assets/*` | Game assets (copy) |
| **Root (unchanged)** | | |
| Keep | `gameRocket/models/` | Original code untouched |
| Keep | `gameRocket/managers/` | Original code untouched |
| Keep | `gameRocket/challenges/` | Original code untouched |
| Keep | `gameRocket/tests/` | Original tests untouched |
| Keep | `gameRocket/requirements.txt` | Original deps unchanged |

### Running the web version

```bash
cd web
pip install -r requirements.txt
uvicorn server:app
# Open http://localhost:8000 in browser
```

---

## Verification Checklist

- [ ] Phase 1: All files copied to `web/game/` with flat structure (12 files)
- [ ] Phase 1: Constants import correctly from flat path (1 test)
- [ ] Phase 1: All flat imports resolve (1 test)
- [ ] Phase 2: Game engine creates, moves, resets, handles terminal states (5 tests)
- [ ] Phase 2: Maze generation works from flat imports (1 test)
- [ ] Phase 3: Server.py has all required components (8 structure checks)
- [ ] Phase 3: REST endpoints (start, move, answer, reset) all return correct data (5 tests)
- [ ] Phase 3: WebSocket connects, sends/receives messages, handles reset (3 tests)
- [ ] Phase 3: Static files served correctly (4 tests)
- [ ] Phase 4: HTML has all screen containers, canvas, and script includes (13 tests)
- [ ] Phase 4: CSS has all required styles (6 tests)
- [ ] Phase 4: JS has all required classes and methods (25+ tests)
- [ ] Phase 5: Full integration test (7 sub-tests)
- [ ] Phase 5: Browser manual test (12 checks)
- [ ] Server starts with `uvicorn server:app` from inside `web/`
