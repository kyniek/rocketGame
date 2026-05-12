# gameRocket Web - Code Documentation

## Overview

gameRocket is an educational maze navigation game where players guide a rocket through a grid-based maze while answering trivia questions. 
The web version is a client-server architecture using FastAPI with a pure Python game engine and HTML5 Canvas for rendering.

---

## Game Rules & Mechanics

### Objective
Navigate the rocket from the left side of the maze to the right side (column 29), while answering ALL trivia questions correctly to achieve victory.

### Controls
- **Arrow Right**: Move rocket forward (one column)
- **Arrow Up**: Move rocket up one row
- **Arrow Down**: Move rocket down one row

### Grid Structure
- **Dimensions**: 30 columns x 5 rows
- **Cell Types**: `empty`, `obstacle`, `start`
- **Starting Position**: Column 0, randomly selected row (0-4)

### Fog of War
- Only the current column and the next column are visible
- Previously visited columns remain visible
- Obstacles in hidden areas are invisible

### Obstacles (Rocks)
- Randomly placed throughout the maze
- When the rocket enters a column, obstacles within 1 row of the rocket start spinning
- Obstacles rotate with decreasing speed and stop after a few seconds

### Lives System
- Player starts with 3 lives
- Hitting an obstacle costs 1 life
- When lives reach 0, game over
- After collision, player respawns at column 0 with visible columns reset

### Challenge Questions
- 20% chance to trigger a challenge after moving forward
- 10 questions total, loaded from `questions.json`
- Questions can be multiple choice or text-based
- **Correct answer**: +10 points, question removed from pool
- **Wrong answer**: -1 life, question recorded as wrong

### Victory Condition
- Answer ALL questions correctly
- Can happen during challenges OR when in the last column after moving up/down
- Shows list of questions answered wrong (up to 5)

### Level Progression
- Reaching the last column (col 29) generates a new maze with new random start row
- Level counter increases
- Challenge questions remain from the same pool

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        BROWSER (Client)                             │
├─────────────────────────────────────────────────────────────────────┤
│  index.html          - Main HTML structure, canvas, overlays         │
│  css/styles.css      - All styling for screens and UI                │
├─────────────────────────────────────────────────────────────────────┤
│  js/main.js          - Bootstrap: initializes all components         │
│  js/game.js          - Game class: state machine, game loop, input   │
│  js/canvas.js        - CanvasRenderer: all drawing logic              │
│  js/challenge.js    - ChallengeModal: question display & input       │
│  js/api.js          - GameAPI: REST API communication                │
│  js/utils.js        - Helper functions (lerp, clamp, etc.)            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP REST API
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     FASTAPI SERVER (server.py)                       │
├─────────────────────────────────────────────────────────────────────┤
│  API Endpoints:                                                       │
│    POST /api/game/start        - Start new game                       │
│    POST /api/game/move         - Move rocket (forward/up/down)        │
│    POST /api/game/answer       - Submit challenge answer             │
│    POST /api/game/reset        - Reset game state                    │
│    POST /api/game/update_rotation - Update obstacle rotation (unused) │
│    GET  /api/game/state        - Get current game state               │
├─────────────────────────────────────────────────────────────────────┤
│  WebSocket: /ws (defined but not actively used in current UI)          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ Game Logic
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    GAME ENGINE (game/engine.py)                      │
├─────────────────────────────────────────────────────────────────────┤
│  GameEngine class - Central orchestrator for all game logic            │
└─────────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  game/rocket.py  │ │ game/maze_gen.py│ │ game/game_grid.py
│  Rocket position │ │ Maze generation │ │ Cell access     │
│  Movement logic │ │ & obstacle      │ │ Collision check │
│  Animation state │ │ placement        │ │ Rotation state  │
└─────────────────┘ └─────────────────┘ └─────────────────┘
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│game/fog_of_war  │ │game/lives_mgr   │ │game/score_mgr   │
│ Visibility      │ │ Lives counter   │ │ Score tracking  │
│ tracking        │ │ 3 starting     │ │ +10 per correct │
└─────────────────┘ └─────────────────┘ └─────────────────┘
          │
          ▼
┌─────────────────────────────────────────────┐
│          game/challenge_manager.py           │
│  Challenge loading, random selection,        │
│  victory condition checking                  │
└─────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────┐
│          game/challenge_loader.py            │
│          game/challenge.py                   │
│  Loads JSON, creates Challenge objects       │
└─────────────────────────────────────────────┘
```

---

## File-by-File Documentation

### Frontend Files

#### `static/index.html`
**Purpose**: Main HTML structure

| Element ID | Description |
|-----------|-------------|
| `#game-canvas` | Canvas element for rendering the game |
| `#start-screen` | Initial screen with title and START GAME button |
| `#challenge-modal` | Modal overlay for trivia questions |
| `#victory-screen` | Screen shown on winning |
| `#gameover-screen` | Screen shown when lives reach 0 |

**Flow**: Canvas is always rendered behind screens. Screens use CSS `display: none` (via `.hidden` class) to show/hide.

---

#### `static/css/styles.css`
**Purpose**: All styling for the game UI

| Class/ID | Description |
|---------|-------------|
| `#start-screen` | Centered flex container with semi-transparent background |
| `#challenge-modal` | Full-screen overlay (z-index 20) for questions |
| `.hidden` | `display: none !important` - hides any element |
| `#challenge-content` | Question modal styling with yellow border |

---

#### `static/js/main.js`
**Purpose**: Bootstrap - initializes all components and sets up event listeners

```javascript
// Creates: GameAPI, CanvasRenderer, ChallengeModal, Game
// Sets up: start-btn, victory-restart-btn, gameover-restart-btn clicks
// Sets up: keyboard listener (Arrow keys)
```

Key initialization flow:
1. Create `GameAPI('/api')` instance
2. Create `CanvasRenderer(canvas)` with automatic resizing
3. Create `ChallengeModal` linked to challenge DOM elements
4. Create `Game(api, renderer, challengeModal)`
5. Attach event listeners to buttons

---

#### `static/js/game.js` - **Game Class**
**Purpose**: Main game state machine, handles input, runs game loop

| Method | Responsibility |
|--------|----------------|
| `start()` | Hides start screen, calls API, starts game loop |
| `reset()` | Calls API to reset, shows start screen |
| `handleMove(direction)` | Calls API `/api/game/move`, updates state |
| `handleAnswer(answer)` | Calls API `/api/game/answer`, shows feedback, closes modal |
| `onStateUpdate(state)` | Updates local state, renders game, handles game over |
| `gameLoop()` | Updates obstacle rotation visuals, renders state |
| `handleKey(e)` | Maps Arrow keys to move directions |

**Key State Variables**:
```javascript
this.state      // Current game state from server
this.running    // Is game loop active
this.lastTime   // For delta time calculation
```

**Keyboard Mapping**:
- `ArrowRight` → `forward`
- `ArrowUp` → `up`
- `ArrowDown` → `down`

**Challenge Answer Flow**:
1. `setInputEnabled(false)` - disable buttons
2. Call `api.sendAnswer(answer)`
3. On response, `showFeedback(is_correct)`
4. After 800ms, close modal and update state

---

#### `static/js/canvas.js` - **CanvasRenderer Class**
**Purpose**: All drawing/rendering logic using HTML5 Canvas

| Method | Description |
|--------|-------------|
| `resize()` | Handles window resize, recalculates cellSize, offsets |
| `drawBackground(ctx)` | Draws ingame_background.jpg or dark fallback |
| `drawGrid(ctx, grid, fogDiscovered)` | Draws cells, respects fog of war |
| `drawObstacles(ctx, grid, rotation)` | Draws rotating rock images |
| `drawRocket(ctx, rocket)` | Draws rocket at current position |
| `drawUI(ctx, score, lives)` | Draws score and lives indicators |
| `render(state)` | Main render method - calls all draw methods |

**Layout Calculation** (`_computeLayout`):
```javascript
cols = 30, rows = 5
maxCellW = canvas.width / cols
maxCellH = canvas.height / rows
cellSize = min(maxCellW, maxCellH, 50)
offsetX = (canvas.width - cols * cellSize) / 2
offsetY = (canvas.height - rows * cellSize) / 2
```

**Cell Colors**:
- `empty`: `#1a1a2e` (dark blue)
- `obstacle`: `#4a2020` (dark red)
- `start`: `#204a20` (dark green)
- Hidden (fog): `#000` (black)

**Obstacle Textures**: 5 rock images (`rock_1.png` to `rock_5.png`)

**Fog of War Logic**: Cells not in `fogDiscovered[col][row]` are drawn as black rectangles.

---

#### `static/js/challenge.js` - **ChallengeModal Class**
**Purpose**: Handles trivia question display and answer input

| Method | Description |
|--------|-------------|
| `show(challenge)` | Displays question, creates buttons or input |
| `hide()` | Hides modal, cleans up event listeners |
| `setInputEnabled(bool)` | Disables buttons during submission |
| `showFeedback(isCorrect)` | Shows CORRECT!/WRONG! feedback |
| `_renderMultipleChoice()` | Creates clickable option buttons |
| `_renderTextChallenge()` | Shows text input field |

**Question Types**:
- `multiple_choice`: Shows options as buttons, keyboard shortcuts 1/2/3
- `text`: Shows input field, submit on Enter

---

#### `static/js/api.js` - **GameAPI Class**
**Purpose**: HTTP communication with the FastAPI server

| Method | Description |
|--------|-------------|
| `startGame()` | POST `/api/game/start` |
| `move(direction)` | POST `/api/game/move` |
| `sendMove(direction)` | POST `/api/game/move` (REST fallback) |
| `sendAnswer(answer)` | POST `/api/game/answer` |
| `sendReset()` | POST `/api/game/reset` |
| `updateRotation(dt)` | POST `/api/game/update_rotation` |
| `_request(method, path, body)` | Generic fetch wrapper |

Note: `sendMove`, `sendAnswer`, `sendReset` are async and return Promises for the Game class to await.

---

#### `static/js/utils.js`
**Purpose**: Helper functions for calculations

| Function | Description |
|----------|-------------|
| `lerp(a, b, t)` | Linear interpolation |
| `colToPixel(col, size, offset)` | Convert column to X pixel |
| `rowToPixel(row, size, offset)` | Convert row to Y pixel |
| `clamp(val, min, max)` | Clamp value between min/max |

---

### Backend Files (Python)

#### `server.py`
**Purpose**: FastAPI application - HTTP endpoints, static file serving

**Endpoints**:

| Endpoint | Method | Handler | Description |
|----------|--------|---------|-------------|
| `/` | GET | `serve_index()` | Serves `static/index.html` |
| `/api/game/start` | POST | `start_game()` | Creates new GameEngine |
| `/api/game/move` | POST | `move_game()` | Calls engine.move_forward/up/down |
| `/api/game/answer` | POST | `answer_game()` | Calls engine.answer_challenge |
| `/api/game/reset` | POST | `reset_game()` | Resets engine |
| `/api/game/state` | GET | `get_game_state()` | Returns current state |
| `/ws` | WS | `websocket_endpoint()` | WebSocket (defined but unused) |

**Static File Mounts**:
```python
app.mount("/css", StaticFiles(directory="static/css"))
app.mount("/js", StaticFiles(directory="static/js"))
app.mount("/assets", StaticFiles(directory="static/assets"))
```

**State Management**:
```python
_engine_state = {"engine": GameEngine("questions.json")}
```
Single game instance shared across requests.

---

#### `game/engine.py` - **GameEngine Class**
**Purpose**: Central game logic orchestrator

| Method | Description |
|--------|-------------|
| `__init__()` | Initializes all components, generates maze |
| `move_forward()` | Move right, check collision, maybe trigger challenge |
| `move_up()` | Move up one row, update fog, check collision |
| `move_down()` | Move down one row, update fog, check collision |
| `answer_challenge(answer)` | Check answer, update score/lives, check victory |
| `update_obstacle_rotation(dt)` | Update rotation angles, decay speeds |
| `get_state()` | Serialize all state for client |
| `reset()` | Generate new maze with random start |

**Key State Variables**:
```python
self.grid            # GameGrid - maze data
self.rocket         # Rocket - position
self.fog            # FogOfWar - visibility
self.lives_manager   # LivesManager - lives remaining
self.score_manager   # ScoreManager - points
self.challenge_manager  # ChallengeManager - questions
self.challenge_active   # bool - is challenge modal shown
self.current_challenge  # Challenge - current question
self.game_over       # bool - game ended, player lost
self.victory         # bool - all questions answered
```

**Internal Methods**:
- `_check_collision(col, row)`: Returns True if obstacle, loses life
- `_respawn()`: Reset rocket to start after collision
- `_start_challenge()`: Activate challenge, get random question
- `_check_victory()`: Check if all questions answered
- `_next_level()`: Generate new maze, increment level

---

#### `game/rocket.py` - **Rocket Class**
**Purpose**: Track rocket position and movement

| Method | Description |
|--------|-------------|
| `move_up()` | Decrease row by 1 (minimum row 0) |
| `move_down()` | Increase row by 1 (maximum row 4) |
| `move_forward()` | Return next column (col + 1) |
| `reset(col, row)` | Reset to given position |
| `start_animation()` | Start smooth animation (unused in web) |
| `update_animation()` | Update animation progress (unused in web) |

---

#### `game/maze_generator.py` - **MazeGenerator Class**
**Purpose**: Generate random maze grid

| Method | Description |
|--------|-------------|
| `generate(start_row)` | Returns 30x5 grid with start position |

**Algorithm**:
- Column 0: Set `start_row` as 'start'
- Columns 1-28: Random walk, leaving path empty
- Column 29: All empty (goal area)
- All other cells: 'obstacle'

---

#### `game/game_grid.py` - **GameGrid Class**
**Purpose**: Wrapper for maze data with rotation state

| Method | Description |
|--------|-------------|
| `get_cell(col, row)` | Returns cell value ('empty', 'obstacle', 'start') |
| `is_walkable(col, row)` | Returns False if obstacle |
| `get_obstacle_texture(col, row)` | Returns rock texture index (0-4) |
| `get_obstacle_rotation_angle(col, row)` | Returns current angle |
| `set_obstacle_rotation_angle(col, row, angle)` | Set rotation angle |
| `get_obstacle_rotation_speed(col, row)` | Returns current speed |
| `set_obstacle_rotation_speed(col, row, speed)` | Set rotation speed |
| `get_obstacle_rotation_active(col, row)` | Returns if rotating |
| `set_obstacle_rotation_active(col, row, bool)` | Activate/deactivate rotation |
| `get_obstacle_rotation_dir(col, row)` | Returns rotation direction (1 or -1) |
| `update_rotation_dirs_for_rocket(row)` | Set rotation direction based on rocket position |

---

#### `game/fog_of_war.py` - **FogOfWar Class**
**Purpose**: Track which cells player has discovered

| Method | Description |
|--------|-------------|
| `is_discovered(col, row)` | Returns True if cell is visible |
| `update(col, row)` | Reveal current + next column |
| `reset()` | Reset to initial state (cols 0-1 visible) |

**Initial State**: Columns 0 and 1 are always visible.

---

#### `game/lives_manager.py` - **LivesManager Class**
**Purpose**: Manage player lives

| Method | Description |
|--------|-------------|
| `lose_life()` | Decrement lives, return remaining |
| `is_alive()` | Returns True if lives > 0 |
| `reset()` | Reset to 3 lives |

**Starting Lives**: 3 (defined in `constants.py`)

---

#### `game/score_manager.py` - **ScoreManager Class**
**Purpose**: Track player score

| Method | Description |
|--------|-------------|
| `add_points(amount)` | Increase score, return new total |
| `subtract_points(amount)` | Decrease score, return new total |
| `reset()` | Reset score to 0 |

**Points per Correct Answer**: 10 (defined in `constants.py`)

---

#### `game/challenge_manager.py` - **ChallengeManager Class**
**Purpose**: Manage trivia questions

| Method | Description |
|--------|-------------|
| `get_random_challenge()` | Return random challenge from list |
| `all_questions_answered_correctly()` | Returns True if challenge list empty |

---

#### `game/challenge.py` - **Challenge Classes**
**Purpose**: Question and answer validation

| Class | Description |
|-------|-------------|
| `Challenge` (ABC) | Base abstract class |
| `MultipleChoiceChallenge` | Has options array, check_answer() |
| `TextChallenge` | Text input, check_answer() |

**Answer Checking**: Case-insensitive, trimmed whitespace comparison.

---

#### `game/challenge_loader.py` - **ChallengeLoader Class**
**Purpose**: Load questions from JSON file

**JSON Format**:
```json
{
  "question": "What is 2 + 2?",
  "answerA": "4",
  "answerB": "3",
  "answerC": "5"
}
```
- If `answerB` and `answerC` are empty: `TextChallenge`
- Otherwise: `MultipleChoiceChallenge`

---

#### `game/constants.py` - **GameConstants**
**Purpose**: Central configuration values

| Constant | Value | Description |
|----------|-------|-------------|
| `GRID_COLS` | 30 | Number of columns |
| `GRID_ROWS` | 5 | Number of rows |
| `MIN_ROW` | 0 | Minimum row index |
| `MAX_ROW` | 4 | Maximum row index |
| `STARTING_LIVES` | 3 | Initial lives |
| `POINTS_PER_CORRECT_ANSWER` | 10 | Score per correct answer |
| `CHALLENGE_CHANCE` | 0.2 | 20% chance for challenge |
| `OBSTACLE_ROTATION_START_SPEED` | 180.0 | Degrees per second |
| `OBSTACLE_ROTATION_DECAY` | 45.0 | Deceleration rate |

---

#### `questions.json`
**Purpose**: Trivia questions data file

Contains 10 questions about math, science, geography, and art. Format described above under ChallengeLoader.

---

## How to Find Code for Specific Features

### "How the rocket moves"
| Layer | File | Method/Line |
|-------|------|-------------|
| Frontend Input | `js/game.js` | `handleMove()` line 37 |
| Frontend Keyboard | `js/game.js` | `handleKey()` line 152 |
| API Request | `js/api.js` | `sendMove()` line 44 |
| Server Endpoint | `server.py` | `move_game()` line 107 |
| Movement Logic | `game/engine.py` | `move_forward/up/down()` lines 63-126 |
| Rocket Class | `game/rocket.py` | `move_up/down/forward()` lines 64-76 |

### "How obstacles are drawn"
| Layer | File | Method |
|-------|------|--------|
| Frontend | `js/canvas.js` | `drawObstacles()` line 90 |
| Backend Data | `game/engine.py` | `get_state()` - includes `obstacle_rotation` |
| Backend Rotation | `game/engine.py` | `update_obstacle_rotation()` line 165 |
| Grid Data | `game/game_grid.py` | `get_obstacle_*` methods |

### "How questions work"
| Layer | File | Method/Line |
|-------|------|-------------|
| Question Display | `js/challenge.js` | `show()` line 12 |
| Frontend Answer | `js/game.js` | `handleAnswer()` line 50 |
| API Request | `js/api.js` | `sendAnswer()` line 49 |
| Server Endpoint | `server.py` | `answer_game()` line 126 |
| Engine Logic | `game/engine.py` | `answer_challenge()` line 136 |
| Challenge Classes | `game/challenge.py` | `check_answer()` methods |

### "How game over is detected"
| Layer | File | Condition |
|-------|------|-----------|
| Engine | `game/engine.py` | `lives_manager.lives <= 0` triggers `_game_over()` line 321 |
| State | `game/engine.py` | `game_over = True` in `get_state()` |
| Frontend | `js/game.js` | `if (state.game_over)` in `onStateUpdate()` line 80 |
| UI | `static/index.html` | `#gameover-screen` div |

### "How victory is detected"
| Layer | File | Condition |
|-------|------|-----------|
| Engine | `game/engine.py` | `_check_victory()` called after correct answer or in last column |
| Manager | `game/challenge_manager.py` | `all_questions_answered_correctly()` checks if challenge list empty |
| State | `game/engine.py` | `victory = True` in `get_state()` |
| Frontend | `js/game.js` | `if (state.victory)` handled in `onVictory()` (not currently wired) |

### "How fog of war works"
| Layer | File | Method/Line |
|-------|------|-------------|
| Backend | `game/fog_of_war.py` | `is_discovered()` checks `_discovered[col][row]` |
| Backend | `game/fog_of_war.py` | `update()` reveals current + next column |
| Backend | `game/engine.py` | `move_forward/up/down()` all call `fog.update()` |
| Serialization | `game/engine.py` | `_serialize_fog()` returns 2D boolean array |
| Frontend | `js/canvas.js` | `drawGrid()` checks `fogDiscovered[col][row]` line 69 |

### "How level progression works"
| Layer | File | Description |
|-------|------|-------------|
| Trigger | `game/engine.py` | `move_forward()` line 76 - checks if `col == COLS - 1` |
| Action | `game/engine.py` | `_next_level()` generates new maze |
| Reset | `game/engine.py` | Rocket, fog, grid all regenerated |

---

## Running the Game

```bash
cd /Users/krzysztofnielepkowicz/DEV/gameRocket/web
source .venv/bin/activate
uvicorn server:app --reload --port 8080
```

Then open http://localhost:8080 in a browser.

---

## Dependencies

From `requirements.txt`:
- `fastapi>=0.115.0` - Web framework
- `uvicorn[standard]>=0.32.0` - ASGI server
- `websockets>=14.0` - WebSocket support
- `pydantic>=2.10.0` - Request validation