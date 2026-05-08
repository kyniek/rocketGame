# Implementation Plan for gameRocket POC

This document outlines the sequential tasks for implementing the gameRocket POC using Test-Driven Development (TDD).

---

## Task 1: MazeGenerator - Grid Generation with Obstacles

**Goal:** Implement a maze generator that creates a 30×3 grid with obstacles, start position, and goal position.

**Deliverable:**
- File: `models/maze_generator.py`
- Class: `MazeGenerator` with method `generate(start_row: int, goal_row: int) -> list[list[str]]`

**Requirements:**
- Column 0 (start): `'start'` in `start_row`, `'empty'` elsewhere
- Column 29 (goal): `'goal'` in `goal_row`, `'empty'` elsewhere
- Columns 1-28: Each may have at most one obstacle
- 50% of non-path columns (1-28): place obstacle in a row different from path
- Path exists where each column has at least one empty cell

**Tests:**
- `test_maze_generator_creates_correct_dimensions()`: Grid is 30×3
- `test_maze_generator_start_position()`: Column 0 has `'start'` at correct row
- `test_maze_generator_goal_position()`: Column 29 has `'goal'` at correct row
- `test_maze_generator_max_one_obstacle_per_column()`: No column has >1 obstacle
- `test_maze_generator_path_exists()`: Each column has at least one empty cell

**Test Command:** `pytest tests/models/test_maze_generator.py`

---

## Task 2: GameGrid - Cell Management and Collision Detection

**Goal:** Implement a wrapper class for the maze grid that provides cell access and collision checking.

**Deliverable:**
- File: `models/game_grid.py`
- Class: `GameGrid` with methods:
  - `get_cell(col, row) -> str`
  - `set_cell(col, row, value)`
  - `is_walkable(col, row) -> bool`

**Requirements:**
- Store grid from MazeGenerator
- Handle boundary checking (columns 0-29, rows 0-2)
- Return `True` for walkable cells (empty or start/goal), `False` for obstacles

**Tests:**
- `test_game_grid_get_cell()`: Returns correct cell value
- `test_game_grid_set_cell()`: Updates cell value correctly
- `test_game_grid_is_walkable_empty()`: `'empty'` returns True
- `test_game_grid_is_walkable_obstacle()`: `'obstacle'` returns False
- `test_game_grid_is_walkable_start_goal()`: `'start'` and `'goal'` return True
- `test_game_grid_boundary_checks()`: Handles out-of-bounds gracefully

**Test Command:** `pytest tests/models/test_game_grid.py`

---

## Task 3: Rocket - Movement Logic

**Goal:** Implement the Rocket class with movement methods and boundary checking.

**Deliverable:**
- File: `models/rocket.py`
- Class: `Rocket` with methods:
  - `move_up()`: Increases row (max 2)
  - `move_down()`: Decreases row (min 0)
  - `move_forward() -> int`: Returns col+1 without modifying state
  - `reset(col, row)`

**Requirements:**
- Position tracked as `col` and `row` attributes
- Row constrained to 0-2 (3 rows)
- `move_forward()` is pure (returns new position without changing state)

**Tests:**
- `test_rocket_initial_position()`: Starts at correct position
- `test_rocket_move_up()`: Row increases, capped at 2
- `test_rocket_move_down()`: Row decreases, capped at 0
- `test_rocket_move_forward_pure()`: Returns col+1 without modifying state
- `test_rocket_reset()`: Position updates correctly

**Test Command:** `pytest tests/models/test_rocket.py`

---

## Task 4: FogOfWar - Visibility Tracking

**Goal:** Implement fog of war that tracks visible grid cells.

**Deliverable:**
- File: `models/fog_of_war.py`
- Class: `FogOfWar` with methods:
  - `update(current_col, current_row)`: Mark cells as discovered
  - `reset()`: Reset to initial state (cols 0 and 1 visible)
  - `is_discovered(col, row) -> bool`

**Requirements:**
- Grid size: 30×3 boolean matrix
- When updating at (col, row): mark all cells with `col <= current_col` as discovered
- Additionally mark column `current_col + 1` as discovered (one step ahead)
- After reset: only columns 0 and 1 are visible

**Tests:**
- `test_fog_of_war_initial_state()`: Only cols 0,1 discovered
- `test_fog_of_war_update()`: Marks cells correctly when moving forward
- `test_fog_of_war_see_current_column()`: Current column fully visible
- `test_fog_of_war_see_next_column()`: Next column visible (one ahead)
- `test_fog_of_war_reset()`: Resets to initial state
- `test_fog_of_war_is_discovered()`: Returns correct visibility status

**Test Command:** `pytest tests/models/test_fog_of_war.py`

---

## Task 5: LivesManager and ScoreManager - Game State

**Goal:** Implement managers for lives and score with observer pattern support.

**Deliverables:**
- File: `managers/lives_manager.py` - Class `LivesManager`
  - `lose_life()` -> int (remaining lives)
  - `reset()`: Reset to 3 lives
  - `is_alive() -> bool`
  - `on_life_lost(callback)`: Subscribe to life lost events
  
- File: `managers/score_manager.py` - Class `ScoreManager`
  - `add_points(amount) -> int (new score)`
  - `reset()`: Reset to 0
  - `on_score_changed(callback)`: Subscribe to score change events

**Requirements:**
- Start with 3 lives, 0 points
- Lives never go below 0
- Support event callbacks for UI updates

**Tests:**
- `test_lives_manager_initial()`: Starts with 3 lives
- `test_lives_manager_lose_life()`: Decrements correctly
- `test_lives_manager_no_negative()`: Lives don't go below 0
- `test_lives_manager_reset()`: Resets to 3 lives
- `test_lives_manager_callback()`: Calls callback with remaining lives
- `test_score_manager_initial()`: Starts with 0 points
- `test_score_manager_add_points()`: Adds correctly
- `test_score_manager_reset()`: Resets to 0

**Test Command:** `pytest tests/managers/test_lives_manager.py tests/managers/test_score_manager.py`

---

## Task 6: Challenge Classes - Base, Multiple Choice, Text

**Goal:** Implement challenge class hierarchy for quiz logic.

**Deliverables:**
- File: `challenges/challenge.py`
  - Abstract base class `Challenge` with:
    - Fields: `question`, `correct_answer`
    - Method: `check_answer(user_input) -> bool` (abstract)
  
  - Class: `MultipleChoiceChallenge(Challenge)`
    - Field: `options: list[str]` (3 options)
  
  - Class: `TextChallenge(Challenge)`
    - Normalize user input for comparison

**Requirements:**
- Check answers (case-insensitive, trim whitespace)
- First option is always correct

**Tests:**
- `test_multiple_choice_check_correct()`: Correct answer passes
- `test_multiple_choice_check_incorrect()`: Wrong answer fails
- `test_text_challenge_case_insensitive()`: "Answer" matches "answer"
- `test_text_challenge_whitespace_trim()`: " answer " matches "answer"
- `test_challenge_base_abstract()`: Cannot instantiate base class

**Test Command:** `pytest tests/challenges/test_challenges.py`

---

## Task 7: ChallengeLoader - JSON Parsing

**Goal:** Implement loader that reads questions from JSON file.

**Deliverable:**
- File: `challenges/challenge_loader.py`
- Class: `ChallengeLoader` with method:
  - `load_from_json(filepath) -> list[Challenge]`

**Requirements:**
- Parse JSON array of questions
- If `answerB` and `answerC` are empty strings -> create `TextChallenge`
- Otherwise -> create `MultipleChoiceChallenge`

**Test JSON file:**
```json
[
  {"question": "2+2?", "answerA": "3", "answerB": "4", "answerC": "5"},
  {"question": "Sky color?", "answerA": "blue", "answerB": "", "answerC": ""}
]
```

**Tests:**
- `test_loader_loads_questions()`: Returns list of challenges
- `test_loader_creates_multiple_choice()`: Populates options for MC questions
- `test_loader_creates_text_challenge()`: Creates text challenge when B, C empty
- `test_loader_empty_file()`: Returns empty list for empty JSON array

**Test Command:** `pytest tests/challenges/test_challenge_loader.py`

---

## Task 8: ChallengeManager - Challenge Presentation and Scoring

**Goal:** Implement manager that presents challenges, tracks wrong answers, and updates score/lives.

**Deliverable:**
- File: `managers/challenge_manager.py`
- Class: `ChallengeManager` with:
  - Fields: `challenges`, `wrong_answers`
  - Method: `present_challenge(game_view)` -> callback to handle answer
  - Callback registration for score/lives updates

**Requirements:**
- Select random challenge from loaded list
- Callbacks for correct/incorrect responses:
  - Correct: `score_manager.add_points(1)`
  - Incorrect: `lives_manager.lose_life()`, record wrong answer
- No time limit

**Tests:**
- `test_manager_loads_challenges()`: Loads from JSON
- `test_manager_record_wrong_answer()`: Adds to wrong_answers list
- `test_manager_score_callback()`: Calls score manager on correct
- `test_manager_life_callback()`: Decrements lives on incorrect

**Test Command:** `pytest tests/managers/test_challenge_manager.py`

---

## Task 9: Views - UI Layer

**Goal:** Implement Arcade View classes for game states.

**Deliverables:**

### 9a. StartView
- File: `views/start_view.py`
- Display title, instructions, "Start Game" button
- Button creates `GameView` with random start/goal rows

### 9b. GameView
- File: `views/game_view.py`
- Main game loop with:
  - Draw grid, obstacles (red), start (green), goal (yellow)
  - Draw rocket (blue) at current position
  - Fog of war: only discovered cells drawn, others black
  - Handle keyboard input (arrows)
  - 20% chance on forward move to trigger challenge
  - Life loss on collision, respawn
  - Victory on reaching goal

### 9c. ChallengeView
- File: `views/challenge_view.py`
- Display question
- For multiple choice: buttons/options 1,2,3
- For text challenge: input field + OK button
- Handle key presses (1-3, Enter) or clicks
- After answer: call callback with result

### 9d. VictoryView
- File: `views/victory_view.py`
- Show score, wrong answers list, "New Game" button

### 9e. GameOverView
- File: `views/game_over_view.py`
- "Game Over" message, score, restart button

**Tests:**
- `test_views_instantiate()`: All views instantiate without error
- `test_game_view_draw()`: Draw method completes (mock Arcade)
- `test_challenge_view_multiple_choice()`: Renders options correctly
- `test_victory_view_shows_score()`: Displays correct score

**Test Command:** `pytest tests/views/test_views.py`

---

## Task 10: Integration - Main Entry Point and End-to-End Test

**Goal:** Wire everything together and add integration test.

**Deliverables:**

### main.py
- Create Arcade window (1200×600)
- Show `StartView` initially
- Handle window close

### questions.json
- Sample data with 5+ multiple choice + text questions

**Integration Test:**
- Simulate gameplay flow: Start -> Move forward (hit obstacle) -> Lose life -> Respawn -> Complete game
- Verify state transitions are correct
- Mock arcade Window and test GameView logic

**Tests:**
- `test_integration_full_flow()`: Simulate complete game session
- `test_integration_obstacle_collision()`: Verify life loss and respawn
- `test_integration_victory_conditions()`: Reach goal triggers victory

**Test Command:** `pytest tests/test_integration.py`

---

## Implementation Order Summary

| Task | Files | Duration Estimate |
|------|-------|-------------------|
| 1 | `models/maze_generator.py` | ~30 min |
| 2 | `models/game_grid.py` | ~20 min |
| 3 | `models/rocket.py` | ~15 min |
| 4 | `models/fog_of_war.py` | ~25 min |
| 5 | `managers/lives_manager.py`, `score_manager.py` | ~30 min |
| 6 | `challenges/challenge.py` | ~25 min |
| 7 | `challenges/challenge_loader.py`, `questions.json` | ~25 min |
| 8 | `managers/challenge_manager.py` | ~30 min |
| 9 | `views/*.py` (5 files) | ~60 min |
| 10 | `main.py`, `test_integration.py` | ~30 min |

**Total:** ~5 hours

---

## Running Tests

```bash
# Install dependencies
pip install arcade pytest pytest-cov

# Run all unit tests
pytest tests/ -v

# Run integration test only
pytest tests/test_integration.py -v

# Coverage report
pytest tests/ --cov=. --cov-report=html
```
