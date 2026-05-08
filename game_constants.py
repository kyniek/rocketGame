"""Centralized constants for gameRocket."""


class GameConstants:
    # ── Window / Display ────────────────────────────────────────
    FEEDBACK_DURATION_MS = 750
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 600
    WINDOW_TITLE = "GameRocket - Educational Rocket Game"

    # ── Grid / Maze ─────────────────────────────────────────────
    GRID_COLS = 30
    GRID_ROWS = 5

    # ── Rocket ──────────────────────────────────────────────────
    ROCKET_MIN_ROW = 0
    ROCKET_MAX_ROW = 4
    ROCKET_ANIMATION_DURATION = 0.2  # seconds per cell movement

    # ── Obstacle Rotation ─────────────────────────────────────────
    OBSTACLE_ROTATION_START_SPEED = 180.0  # degrees per second (initial speed)
    OBSTACLE_ROTATION_DECAY = 45.0  # degrees per second per second (deceleration rate)

    # ── Display / Grid Sizing ───────────────────────────────────
    CELL_SIZE = WINDOW_WIDTH / GRID_COLS # was 40

    # Computed grid dimensions based on window and cell size
    GRID_WIDTH = GRID_COLS * CELL_SIZE
    GRID_HEIGHT = (ROCKET_MAX_ROW + 1) * CELL_SIZE

    # ── Gameplay ────────────────────────────────────────────────
    STARTING_LIVES = 3
    POINTS_PER_CORRECT_ANSWER = 10
    CHALLENGE_CHANCE = 0.2

    # ── UI Constants - Computed from window dimensions (using only * and /) ─────────
    # Victory View - positions as fractions of window height/width
    VICTORY_TITLE_Y_OFFSET = WINDOW_HEIGHT / 4           # was 150
    VICTORY_SCORE_Y_OFFSET = WINDOW_HEIGHT / 2.4         # was 250
    VICTORY_MISSED_Y_OFFSET = WINDOW_HEIGHT / 1.714      # was 350
    VICTORY_MISSED_START_Y_OFFSET = WINDOW_HEIGHT / 1.5  # was 400
    VICTORY_TITLE_SIZE = WINDOW_WIDTH / 15               # was 64
    VICTORY_SCORE_SIZE = WINDOW_WIDTH / 30               # was 36
    VICTORY_MISSED_LABEL_SIZE = WINDOW_WIDTH / 50        # was 24
    VICTORY_MISSED_ITEM_SIZE = WINDOW_WIDTH / 75         # was 16
    VICTORY_MISSED_SPACING = CELL_SIZE                   # was 40
    VICTORY_MAX_MISSED = 5
    VICTORY_BUTTON_Y = WINDOW_HEIGHT / 4                 # was 150
    VICTORY_BUTTON_WIDTH = WINDOW_WIDTH / 6              # was 200
    VICTORY_BUTTON_HEIGHT = CELL_SIZE                    # was 60

    # Game Over View
    GAME_OVER_TITLE_Y_OFFSET = VICTORY_TITLE_Y_OFFSET
    GAME_OVER_SCORE_Y_OFFSET = VICTORY_SCORE_Y_OFFSET
    GAME_OVER_TITLE_SIZE = VICTORY_TITLE_SIZE
    GAME_OVER_SCORE_SIZE = VICTORY_SCORE_SIZE
    GAME_OVER_BUTTON_Y = VICTORY_BUTTON_Y
    GAME_OVER_BUTTON_WIDTH = VICTORY_BUTTON_WIDTH
    GAME_OVER_BUTTON_HEIGHT = VICTORY_BUTTON_HEIGHT

    # Challenge View
    CHALLENGE_QUESTION_Y_OFFSET = WINDOW_HEIGHT / 4      # was 150
    CHALLENGE_OPTIONS_Y_OFFSET = WINDOW_HEIGHT / 6       # was 100
    CHALLENGE_OPTION_SPACING = CELL_SIZE * 1.5           # was 60
    CHALLENGE_QUESTION_SIZE = WINDOW_WIDTH / 60          # was 20
    CHALLENGE_OPTION_SIZE = WINDOW_WIDTH / 75            # was 16
    CHALLENGE_INSTRUCTIONS_Y = WINDOW_HEIGHT / 12        # was 50
    CHALLENGE_INSTRUCTIONS_SIZE = WINDOW_WIDTH / 85      # was 14
    CHALLENGE_ERROR_Y = WINDOW_HEIGHT / 6                # was 100
    CHALLENGE_ERROR_SIZE = WINDOW_WIDTH / 75             # was 16
    CHALLENGE_INPUT_WIDTH = WINDOW_WIDTH / 3             # was 400
    CHALLENGE_INPUT_HEIGHT = CELL_SIZE                   # was 40
    CHALLENGE_OPTION_WIDTH = WINDOW_WIDTH / 3            # was 400
    CHALLENGE_OPTION_HEIGHT = CELL_SIZE                  # was 40
    CHALLENGE_OPTION_OFFSET_X = WINDOW_WIDTH / 6.5       # was 180
    CHALLENGE_CLICK_Y_MARGIN = CELL_SIZE / 2             # was 20

    # Start View
    START_TITLE_Y_OFFSET = WINDOW_HEIGHT / 6             # was 100
    START_SUBTITLE_Y_OFFSET = WINDOW_HEIGHT / 4          # was 150
    START_TITLE_SIZE = WINDOW_WIDTH / 21.4               # was 56
    START_SUBTITLE_SIZE = WINDOW_WIDTH / 50              # was 24
    START_INSTRUCTION_Y_OFFSET = CELL_SIZE * 1.5         # was 60
    START_INSTRUCTION_SIZE = WINDOW_WIDTH / 67           # was 18
    START_INSTRUCTION_SPACING = CELL_SIZE - 14           # was 26
    START_BUTTON_WIDTH = WINDOW_WIDTH / 5.45             # was 220
    START_BUTTON_HEIGHT = CELL_SIZE * 1.5                # was 60
    START_BUTTON_Y = WINDOW_HEIGHT / 7.5                 # was 80

    # Game View UI
    GAME_UI_X_OFFSET = 10                                # was 10
    GAME_UI_Y_OFFSET = 30                                # was 30
    GAME_UI_LIVES_Y_SPACING = 25                         # was 25
    GAME_UI_SCORE_SIZE = WINDOW_WIDTH / 60               # was 20
    GAME_UI_LIVES_SIZE = WINDOW_WIDTH / 60               # was 20

    # Aliases for backward compatibility
    COLS = GRID_COLS
    ROWS = GRID_ROWS
    MIN_ROW = ROCKET_MIN_ROW
    MAX_ROW = ROCKET_MAX_ROW
