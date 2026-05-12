"""Pure-Python game engine composed from existing game classes."""

import random

from game_engine.constants import GameConstants
from models.maze_generator import MazeGenerator
from models.game_grid import GameGrid
from models.rocket import Rocket
from models.fog_of_war import FogOfWar
from managers.lives_manager import LivesManager
from managers.score_manager import ScoreManager
from managers.challenge_manager import ChallengeManager


class GameEngine:
    """Pure-Python game engine that composes all existing game classes."""

    def __init__(self, questions_file: str = "questions.json"):
        """Initialize a new game.

        Args:
            questions_file: Path to questions JSON file.
        """
        self._init_state = None
        self._start_row = random.randint(0, GameConstants.ROWS - 1)
        self._reset(self._start_row, questions_file)

    def _reset(self, start_row: int, questions_file: str):
        """Reset game to initial state.

        Args:
            start_row: Starting row for the rocket.
            questions_file: Path to questions JSON file.
        """
        self.start_row = start_row
        self.level = 1

        # Generate maze
        grid_data = MazeGenerator().generate(start_row)
        self.grid = GameGrid(grid_data)
        self.grid.update_rotation_dirs_for_rocket(start_row)

        # Rocket
        self.rocket = Rocket(col=0, row=start_row)

        # Fog of war
        self.fog = FogOfWar()
        self.fog.update(0, start_row)

        # Managers
        self.lives_manager = LivesManager()
        self.score_manager = ScoreManager()

        # Challenge tracking
        self.previous_col = 0
        self._activated_columns: set = set()

        # Load challenges
        self.challenge_manager = ChallengeManager(questions_file)

        # Challenge state
        self.challenge_active = False
        self.current_challenge = None

        # Game state
        self.game_over = False
        self.victory = False

        # Save initial state for reset
        self._init_state = {
            "start_row": start_row,
            "questions_file": questions_file,
        }

    def reset(self) -> dict:
        """Reset game to a new random start state.

        Returns:
            Serializable game state.
        """
        new_start_row = random.randint(0, GameConstants.ROWS - 1)
        self._reset(new_start_row, self._init_state["questions_file"])
        return self.get_state()

    def move_forward(self) -> dict:
        """Move rocket forward.

        Returns:
            Serializable game state. May trigger challenge, collision, or level advance.
        """
        if self._is_terminal():
            return self.get_state()

        next_col = self.rocket.move_forward()

        if next_col >= GameConstants.GRID_COLS:
            return self.get_state()

        # Reached last column - advance to next level
        if next_col == GameConstants.GRID_COLS - 1:
            self._next_level()
            return self.get_state()

        # Check collision
        if self._check_collision(next_col, self.rocket.row):
            return self.get_state()

        # Move successful
        self.rocket.col = next_col
        self.fog.update(self.rocket.col, self.rocket.row)

        # Check for challenge
        if random.random() < GameConstants.CHALLENGE_CHANCE:
            self._start_challenge()
            # Challenge interrupts movement - return state with challenge active
            return self.get_state()

        return self.get_state()

    def move_up(self) -> dict:
        """Move rocket up.

        Returns:
            Serializable game state.
        """
        if self._is_terminal() or self.challenge_active:
            return self.get_state()

        if self.rocket.col == GameConstants.GRID_COLS - 1:
            self._check_victory()
            return self.get_state()

        self.rocket.move_up()
        self.fog.update(self.rocket.col, self.rocket.row)
        self.grid.update_rotation_dirs_for_rocket(self.rocket.row)

        if self._check_collision(self.rocket.col, self.rocket.row):
            return self.get_state()

        return self.get_state()

    def move_down(self) -> dict:
        """Move rocket down.

        Returns:
            Serializable game state.
        """
        if self._is_terminal() or self.challenge_active:
            return self.get_state()

        if self.rocket.col == GameConstants.GRID_COLS - 1:
            self._check_victory()
            return self.get_state()

        self.rocket.move_down()
        self.fog.update(self.rocket.col, self.rocket.row)
        self.grid.update_rotation_dirs_for_rocket(self.rocket.row)

        if self._check_collision(self.rocket.col, self.rocket.row):
            return self.get_state()

        return self.get_state()

    def get_next_challenge(self) -> dict:
        """Get the next random challenge.

        Returns:
            Serializable game state with current_challenge populated.
        """
        if self._is_terminal() or self.challenge_active:
            return self.get_state()

        self._start_challenge()
        return self.get_state()

    def answer_challenge(self, answer: str) -> dict:
        """Submit an answer to the current challenge.

        Args:
            answer: The user's answer string.

        Returns:
            Serializable game state.
        """
        if not self.challenge_active or self.current_challenge is None:
            return self.get_state()

        is_correct = self.current_challenge.check_answer(answer)

        if is_correct:
            self.score_manager.add_points(GameConstants.POINTS_PER_CORRECT_ANSWER)
            if self.current_challenge in self.challenge_manager.challenges:
                self.challenge_manager.challenges.remove(self.current_challenge)
            self._check_victory()
        else:
            self.score_manager.subtract_points(GameConstants.POINTS_PER_CORRECT_ANSWER)
            # Track wrong answer (bug fix - was never populated before)
            self.challenge_manager.wrong_answers.append({
                "question": self.current_challenge.question,
                "user_answer": answer,
                "correct_answer": self.current_challenge.correct_answer,
            })
            self.lives_manager.lose_life()

        self.challenge_active = False
        self.current_challenge = None

        if not self.lives_manager.is_alive():
            self._game_over()

        return self.get_state()

    def update_obstacle_rotation(self, dt: float) -> dict:
        """Update obstacle rotation physics.

        Args:
            dt: Delta time in seconds.

        Returns:
            Serializable game state.
        """
        if self._is_terminal():
            return self.get_state()

        start_speed = GameConstants.OBSTACLE_ROTATION_START_SPEED
        decay_rate = GameConstants.OBSTACLE_ROTATION_DECAY

        # Activate column obstacles when rocket moves
        if self.rocket.col != self.previous_col:
            if self.rocket.col not in self._activated_columns:
                self._activated_columns.add(self.rocket.col)
                for row in range(GameConstants.ROWS):
                    if self.grid.get_cell(self.rocket.col, row) == "obstacle":
                        if abs(self.rocket.row - row) > 1:
                            continue
                        self.grid.set_obstacle_rotation_speed(
                            self.rocket.col, row, start_speed
                        )
                        self.grid.set_obstacle_rotation_active(
                            self.rocket.col, row, True
                        )
            self.previous_col = self.rocket.col

        # Update rotation for all activated columns
        for col in self._activated_columns:
            for row in range(GameConstants.ROWS):
                if self.grid.get_cell(col, row) == "obstacle":
                    angle = self.grid.get_obstacle_rotation_angle(col, row)
                    direction = self.grid.get_obstacle_rotation_dir(col, row)
                    speed = self.grid.get_obstacle_rotation_speed(col, row)
                    active = self.grid.get_obstacle_rotation_active(col, row)

                    if angle is not None and direction is not None and active is not None:
                        if active and speed > 0:
                            new_angle = angle + speed * direction * dt
                            new_speed = max(0, speed - decay_rate * dt)
                            new_angle = new_angle % 360

                            self.grid.set_obstacle_rotation_angle(col, row, new_angle)
                            self.grid.set_obstacle_rotation_speed(col, row, new_speed)

                            if new_speed <= 0:
                                self.grid.set_obstacle_rotation_active(col, row, False)

        return self.get_state()

    def get_state(self) -> dict:
        """Get serializable game state.

        Returns:
            Dictionary representing full game state.
        """
        return {
            "grid": self._serialize_grid(),
            "rocket": {"col": self.rocket.col, "row": self.rocket.row},
            "lives": self.lives_manager.lives,
            "score": self.score_manager.score,
            "level": self.level,
            "challenges_remaining": len(self.challenge_manager.challenges),
            "challenges": [
                {
                    "id": i,
                    "question": c.question,
                    "correct_answer": c.correct_answer,
                    "type": "multiple_choice" if hasattr(c, "options") else "text",
                    "options": getattr(c, "options", None),
                }
                for i, c in enumerate(self.challenge_manager.challenges)
            ],
            "wrong_answers": self.challenge_manager.wrong_answers,
            "fog_discovered": self._serialize_fog(),
            "obstacle_rotation": self._serialize_obstacle_rotation(),
            "challenge_active": self.challenge_active,
            "current_challenge": self._serialize_current_challenge(),
            "game_over": self.game_over,
            "victory": self.victory,
        }

    def _serialize_grid(self) -> list[list[str]]:
        """Serialize grid data."""
        return [
            [self.grid.get_cell(col, row) or "" for row in range(GameConstants.ROWS)]
            for col in range(GameConstants.GRID_COLS)
        ]

    def _serialize_fog(self) -> list[list[bool]]:
        """Serialize fog of war data."""
        return [
            [self.fog.is_discovered(col, row) for row in range(GameConstants.ROWS)]
            for col in range(GameConstants.GRID_COLS)
        ]

    def _serialize_obstacle_rotation(self) -> dict:
        """Serialize obstacle rotation data."""
        result = {}
        for col in range(GameConstants.GRID_COLS):
            for row in range(GameConstants.ROWS):
                if self.grid.get_cell(col, row) == "obstacle":
                    key = f"{col},{row}"
                    result[key] = {
                        "angle": self.grid.get_obstacle_rotation_angle(col, row) or 0.0,
                        "speed": self.grid.get_obstacle_rotation_speed(col, row) or 0.0,
                        "active": self.grid.get_obstacle_rotation_active(col, row) or False,
                        "dir": self.grid.get_obstacle_rotation_dir(col, row) or 1,
                        "texture": self.grid.get_obstacle_texture(col, row) or 0,
                    }
        return result

    def _serialize_current_challenge(self) -> dict | None:
        """Serialize current challenge."""
        if self.current_challenge is None:
            return None
        return {
            "question": self.current_challenge.question,
            "correct_answer": self.current_challenge.correct_answer,
            "type": "multiple_choice" if hasattr(self.current_challenge, "options") else "text",
            "options": getattr(self.current_challenge, "options", None),
        }

    # ── Internal game logic ─────────────────────────────────────

    def _is_terminal(self) -> bool:
        """Check if game is in a terminal state."""
        return self.game_over or self.victory

    def _check_collision(self, next_col: int, row: int) -> bool:
        """Check for obstacle collision.

        Args:
            next_col: Column to check.
            row: Row to check.

        Returns:
            True if collision occurred.
        """
        cell = self.grid.get_cell(next_col, row)
        if cell == "obstacle":
            self.lives_manager.lose_life()
            if not self.lives_manager.is_alive():
                self._game_over()
            else:
                self._respawn()
            return True
        return False

    def _respawn(self):
        """Respawn rocket at start after collision."""
        self.rocket.reset(0, self.start_row)
        self.fog.reset()
        self.fog.update(0, self.start_row)
        self.previous_col = 0
        self._activated_columns = set()
        for col in range(GameConstants.GRID_COLS):
            for r in range(GameConstants.ROWS):
                if self.grid.get_cell(col, r) == "obstacle":
                    self.grid.set_obstacle_rotation_angle(col, r, 0.0)
                    self.grid.set_obstacle_rotation_speed(col, r, 0.0)
                    self.grid.set_obstacle_rotation_active(col, r, False)

    def _start_challenge(self):
        """Start a challenge."""
        self.challenge_active = True
        self.current_challenge = self.challenge_manager.get_random_challenge()

    def _check_victory(self):
        """Check victory condition."""
        if self.challenge_manager.all_questions_answered_correctly():
            self.victory = True

    def _game_over(self):
        """Handle game over."""
        self.game_over = True

    def _next_level(self):
        """Advance to next level with a new maze."""
        self.level += 1
        new_start_row = random.randint(0, GameConstants.ROWS - 1)

        self.rocket.reset(0, new_start_row)
        self.fog.reset()
        self.fog.update(0, new_start_row)

        grid_data = MazeGenerator().generate(new_start_row)
        self.grid = GameGrid(grid_data)
        self.grid.update_rotation_dirs_for_rocket(new_start_row)

        self.previous_col = 0
        self._activated_columns = set()
        self.start_row = new_start_row
