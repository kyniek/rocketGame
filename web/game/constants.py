"""Pure game constants for web version (no Arcade/window dependencies)."""


class GameConstants:
    # ── Grid / Maze ─────────────────────────────────────────────
    GRID_COLS = 30
    GRID_ROWS = 5

    # ── Rocket ──────────────────────────────────────────────────
    ROCKET_MIN_ROW = 0
    ROCKET_MAX_ROW = 4
    ROCKET_ANIMATION_DURATION = 0.2  # seconds per cell movement

    # ── Obstacle Rotation ───────────────────────────────────────
    OBSTACLE_ROTATION_START_SPEED = 180.0  # degrees per second
    OBSTACLE_ROTATION_DECAY = 45.0  # degrees per second per second (deceleration)

    # ── Gameplay ────────────────────────────────────────────────
    STARTING_LIVES = 3
    POINTS_PER_CORRECT_ANSWER = 10
    CHALLENGE_CHANCE = 0.2

    # ── UI Constants ────────────────────────────────────────────
    FEEDBACK_DURATION_MS = 750
    VICTORY_MAX_MISSED = 5

    # Aliases for backward compatibility
    COLS = GRID_COLS
    ROWS = GRID_ROWS
    MIN_ROW = ROCKET_MIN_ROW
    MAX_ROW = ROCKET_MAX_ROW
