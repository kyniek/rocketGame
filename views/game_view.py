import arcade
import random

from models.maze_generator import MazeGenerator
from models.game_grid import GameGrid
from models.rocket import Rocket
from models.fog_of_war import FogOfWar
from game_constants import GameConstants
from managers.lives_manager import LivesManager
from managers.score_manager import ScoreManager
from managers.challenge_manager import ChallengeManager

from views.challenge_view import ChallengeView

ROCKET_MARGIN = 8
CELL_MARGIN = 4


def get_cell_size() -> int:
    """Get the current cell size, recomputing from window width."""
    return GameConstants.WINDOW_WIDTH / GameConstants.GRID_COLS


def get_cell_margin() -> float:
    """Get cell margin, computed as fraction of cell size."""
    return get_cell_size() / 10


def get_rocket_margin() -> float:
    """Get rocket margin, computed as fraction of cell size."""
    return get_cell_size() / 5


class GameView(arcade.View):
    """Main game view with grid, rocket, and gameplay logic."""

    def __init__(self, start_row: int):
        """Initialize game view.

        Args:
            start_row: Row index (0-2) for the starting position.
        """
        super().__init__()

        self.start_row = start_row
        # Initialize game components
        grid_data = MazeGenerator().generate(start_row)
        self.grid = GameGrid(grid_data)
        self.grid.update_rotation_dirs_for_rocket(start_row)
        self.rocket = Rocket(col=0, row=start_row)
        self.fog = FogOfWar()
        self.fog.update(0, start_row)
        self.lives_manager = LivesManager()
        self.score_manager = ScoreManager()
        # Track previous column for rotation trigger
        self.previous_col = 0
        # Track which columns have been activated for rotation
        self._activated_columns: set[int] = set()
        # Load challenges
        try:
            self.challenge_manager = ChallengeManager("questions.json")
        except FileNotFoundError:
            self.challenge_manager = ChallengeManager("challenges/questions.json")
        # Game state
        self.challenge_active = False
        self.game_over = False
        self.victory = False
        self.current_challenge = None
        # Load obstacle textures (5 different rock images)
        self.obstacle_textures = [
            arcade.load_texture(f"assets/rock_{i}.png")
            for i in range(1, 6)
        ]
        # Load rocket texture
        self.rocket_texture = arcade.load_texture("assets/rocket_small.png")
        self.background_texture = arcade.load_texture("assets/ingame_background.jpg")

    def on_show(self):
        """Called when this view is shown."""
        arcade.set_background_color(arcade.color.DARK_GRAY)

    def on_draw(self):
        """Draw the game."""
        self.window.clear()
        # Tło – obrazek rozciągnięty na całe okno
        arcade.draw_texture_rect(
            self.background_texture,
            arcade.types.LBWH(0, 0, self.window.width, self.window.height)
        )

        cell_size = get_cell_size()

        # Calculate drawing offsets to center the grid
        grid_width = GameConstants.COLS * cell_size
        grid_height = GameConstants.ROWS * cell_size
        offset_x = (self.window.width - grid_width) / 2
        offset_y = (self.window.height - grid_height) / 2

        # Draw grid and cells
        for col in range(GameConstants.COLS):
            for row in range(GameConstants.ROWS):
                x = offset_x + col * cell_size
                y = offset_y + row * cell_size

                # Check if cell is discovered (fog of war)
                if not self.fog.is_discovered(col, row):
                    # Draw hidden area as black
                    if (self.rocket.x +  3 * cell_size) >= x:
                        arcade.draw_lbwh_rectangle_filled(self.rocket.x +  2 * cell_size, y + 0,
                                                          cell_size, cell_size, arcade.color.BLACK)
                        arcade.draw_lbwh_rectangle_filled(x + 0, y + 0,
                                                          cell_size, cell_size, arcade.color.BLACK)
                    else:
                        arcade.draw_lbwh_rectangle_filled(x + 0, y + 0,
                                                      cell_size, cell_size, arcade.color.BLACK)
                    continue

                # Get cell type
                cell = self.grid.get_cell(col, row)

                # Draw background
                arcade.draw_lbwh_rectangle_filled(x + 0, y + 0,
                                              cell_size, cell_size, arcade.color.DARK_GRAY)
                # Draw grid lines
                arcade.draw_lbwh_rectangle_outline(x + 0, y + 0,
                                               cell_size, cell_size, arcade.color.DARK_GRAY)

                # Draw cell content
                if cell == 'obstacle':
                    self._draw_obstacle(col, row, x, y, cell_size)
                elif cell == 'start':
                    self._draw_start(x, y, cell_size)

        # Draw rocket
        self._draw_rocket(offset_x, offset_y, cell_size)

        # Draw UI (lives and score)
        self._draw_ui(offset_x, offset_y)

    def _draw_obstacle(self, col: int, row: int, x: int, y: int, cell_size: float):
        """Draw an obstacle at the given position using its assigned rock texture."""
        margin = get_cell_margin()
        texture_index = self.grid.get_obstacle_texture(col, row)
        if texture_index is not None:
            selected_texture = self.obstacle_textures[texture_index]
            # Get rotation angle for this obstacle
            rotation_angle = self.grid.get_obstacle_rotation_angle(col, row)
            # Calculate center position for the obstacle
            center_x = x + margin/2 + (cell_size - margin) / 2
            center_y = y + margin/2 + (cell_size - margin) / 2
            # Draw with rotation using sprite-based approach
            # Create a temporary sprite for each obstacle (rotation requires sprites)
            from arcade import Sprite
            sprite = Sprite(center_x=center_x, center_y=center_y)
            sprite.texture = selected_texture
            sprite.width = cell_size - margin
            sprite.height = cell_size - margin
            sprite.angle = rotation_angle if rotation_angle is not None else 0
            # Use SpriteList to draw with proper rendering context
            from arcade import SpriteList
            sprite_list = SpriteList()
            sprite_list.append(sprite)
            sprite_list.draw()

    def _draw_start(self, x: int, y: int, cell_size: float):
        """Draw the start point at the given position."""
        # arcade.draw_lbwh_rectangle_filled(x + get_cell_margin()/2, y + get_cell_margin()/2,
        #                                   cell_size - get_cell_margin(), cell_size - get_cell_margin(),
        #                                   arcade.color.GREEN)

    def _draw_rocket(self, offset_x: int, offset_y: int, cell_size: float):
        """Draw the rocket at its current position using animated x, y coordinates."""
        rocket_x = offset_x + self.rocket.x
        rocket_y = offset_y + self.rocket.y
        margin = get_rocket_margin() / 2
        arcade.draw_texture_rect(
            self.rocket_texture,
            arcade.types.LBWH(rocket_x + margin, rocket_y + margin,
                              cell_size - get_rocket_margin(), cell_size - get_rocket_margin())
        )

    def on_update(self, dt: float):
        """Called every frame to update animation state."""
        self.rocket.update_animation(dt)

        start_speed = GameConstants.OBSTACLE_ROTATION_START_SPEED
        decay_rate = GameConstants.OBSTACLE_ROTATION_DECAY

        # Check if rocket moved to a new column - activate that column's obstacles
        if self.rocket.col != self.previous_col:
            # Always activate the column the rocket just moved to
            if self.rocket.col not in self._activated_columns:
                self._activated_columns.add(self.rocket.col)
                for row in range(GameConstants.ROWS):
                    if self.grid.get_cell(self.rocket.col, row) == 'obstacle':
                        prev_active = self.grid.get_obstacle_rotation_active(self.rocket.col, row)
                        if abs(self.rocket.row - row) > 1 :
                            continue

                        self.grid.set_obstacle_rotation_speed(self.rocket.col, row, start_speed)
                        self.grid.set_obstacle_rotation_active(self.rocket.col, row, True)
            self.previous_col = self.rocket.col

        # Update rotation for ALL activated columns
        for col in self._activated_columns:
            for row in range(GameConstants.ROWS):
                if self.grid.get_cell(col, row) == 'obstacle':
                    angle = self.grid.get_obstacle_rotation_angle(col, row)
                    direction = self.grid.get_obstacle_rotation_dir(col, row)
                    speed = self.grid.get_obstacle_rotation_speed(col, row)
                    active = self.grid.get_obstacle_rotation_active(col, row)

                    if angle is not None and direction is not None and active is not None:
                        # Only rotate if active and speed > 0
                        if active and speed > 0:
                            # Update angle based on direction and speed
                            new_angle = angle + speed * direction * dt
                            # Apply deceleration
                            new_speed = max(0, speed - decay_rate * dt)
                            # Wrap to 0-360 range
                            new_angle = new_angle % 360

                            self.grid.set_obstacle_rotation_angle(col, row, new_angle)
                            self.grid.set_obstacle_rotation_speed(col, row, new_speed)

                            # Deactivate when speed reaches 0
                            if new_speed <= 0:
                                self.grid.set_obstacle_rotation_active(col, row, False)

    def _draw_ui(self, offset_x: int, offset_y: int):
        """Draw UI elements (lives, score) in top-left corner."""
        # Position in top-left corner
        ui_x = offset_x + GameConstants.GAME_UI_X_OFFSET
        ui_y = self.window.height - GameConstants.GAME_UI_Y_OFFSET

        arcade.draw_text(f"Score: {self.score_manager.score}",
                         ui_x, ui_y,
                         arcade.color.WHITE, GameConstants.GAME_UI_SCORE_SIZE)
        arcade.draw_text(f"Lives: {self.lives_manager.lives}",
                         ui_x, ui_y - GameConstants.GAME_UI_LIVES_Y_SPACING,
                         arcade.color.GREEN, GameConstants.GAME_UI_LIVES_SIZE)

    def on_key_press(self, key: int, modifiers: int):
        """Handle keyboard input."""
        if self.challenge_active or self.game_over or self.victory:
            return

        # Prevent input during animation
        if self.rocket.is_animating:
            return

        if key == arcade.key.RIGHT:
            self._move_forward()
        elif key == arcade.key.UP:
            self._move_up()
        elif key == arcade.key.DOWN:
            self._move_down()

    def _start_rocket_animation(self, target_col: int, target_row: int):
        """Start smooth animation for rocket to a new position.

        Args:
            target_col: Target column index.
            target_row: Target row index.
        """
        self.rocket.start_animation(target_col, target_row)

    def _move_down(self):
        """Move down animation."""
        # Check if we're in last column before moving
        if self.rocket.col == GameConstants.COLS - 1:
            # In last column, moving up/down checks for victory condition
            self._check_victory_condition()
        else:
            self.rocket.move_down()
            self.fog.update(self.rocket.col, self.rocket.row)
            self.grid.update_rotation_dirs_for_rocket(self.rocket.row)
            # Check for collision after moving
            if not self._check_collision(self.rocket.col, self.rocket.row):
                # No collision, start animation
                self._start_rocket_animation(self.rocket.col, self.rocket.row)


    def _move_up(self):
        """Move up animation."""
        # Check if we're in last column before moving
        if self.rocket.col == GameConstants.COLS - 1:
            # In last column, moving up/down checks for victory condition
            self._check_victory_condition()
        else:
            self.rocket.move_up()
            self.fog.update(self.rocket.col, self.rocket.row)
            self.grid.update_rotation_dirs_for_rocket(self.rocket.row)
            # Check for collision after moving
            if not self._check_collision(self.rocket.col, self.rocket.row):
                # No collision, start animation
                self._start_rocket_animation(self.rocket.col, self.rocket.row)


    def _move_forward(self):
        """Attempt to move the rocket forward."""
        next_col = self.rocket.move_forward()

        # Check if out of bounds
        if next_col >= GameConstants.COLS:
            return

        # Check if reached the last column (goal area)
        if next_col == GameConstants.COLS - 1:
            # Move to last column first
            self.rocket.col = next_col
            self.fog.update(self.rocket.col, self.rocket.row)
            # Start animation to the last column before advancing level
            self._start_rocket_animation(self.rocket.col, self.rocket.row)
            # Reaching last column always advances to next level
            self._next_level()
            return

        # Check for obstacle using extracted collision detection method
        if not self._check_collision(next_col, self.rocket.row):
            # Move successful - no collision
            self.rocket.col = next_col
            self.fog.update(self.rocket.col, self.rocket.row)

            # Start smooth animation to new position
            self._start_rocket_animation(self.rocket.col, self.rocket.row)

            # CHALLENGE_CHANCE chance for challenge
            if random.random() < GameConstants.CHALLENGE_CHANCE:
                self._start_challenge()

    def _start_challenge(self):
        """Start a challenge modal."""
        self.challenge_active = True

        # Store the current challenge to remove it later if answered correctly
        self.current_challenge = self.challenge_manager.get_random_challenge()

        def handle_challenge_result(is_correct: bool):
            """Handle challenge result and return to game."""
            self.challenge_active = False

            # Add points for correct answer
            if is_correct:
                self.score_manager.add_points(GameConstants.POINTS_PER_CORRECT_ANSWER)
                # Remove the answered challenge from the list
                if self.current_challenge and self.current_challenge in self.challenge_manager.challenges:
                    self.challenge_manager.challenges.remove(self.current_challenge)
                # Check win condition: all questions answered correctly
                if self.challenge_manager.all_questions_answered_correctly():
                    self._check_victory_condition()
                    return
            else:
                # Subtract points for wrong answer
                self.score_manager.subtract_points(GameConstants.POINTS_PER_CORRECT_ANSWER)

            # Check if player died from wrong answer
            if not is_correct and not self.lives_manager.is_alive():
                self._game_over()
            else:
                # Return to main game screen
                self.window.show_view(self)

        challenge_view = ChallengeView(
            self.current_challenge,
            handle_challenge_result
        )
        self.window.show_view(challenge_view)

    def _check_collision(self, next_col: int, row: int) -> bool:
        """Check for obstacle collision at given position.
        
        Args:
            next_col: Column index to check.
            row: Row index to check.
        
        Returns:
            True if collision detected, False otherwise.
        """
        cell = self.grid.get_cell(next_col, row)
        if cell == 'obstacle':
            # Collision - lose life
            self.lives_manager.lose_life()
            if not self.lives_manager.is_alive():
                self._game_over()
            else:
                # Respawn at start
                self.rocket.reset(0, self.start_row)
                self.fog.reset()
                self.fog.update(0, self.start_row)
                # Reset rotation tracking so column 0 triggers rotation again
                self.previous_col = 0
                self._activated_columns = set()
                # Reset all obstacle rotation states for fresh start
                for col in range(GameConstants.COLS):
                    for r in range(GameConstants.ROWS):
                        if self.grid.get_cell(col, r) == 'obstacle':
                            self.grid.set_obstacle_rotation_angle(col, r, 0.0)
                            self.grid.set_obstacle_rotation_speed(col, r, 0.0)
                            self.grid.set_obstacle_rotation_active(col, r, False)
                return True
        return False

    def _check_victory_condition(self):
        """Check if victory condition is met (all questions answered correctly)."""
        if self.challenge_manager.all_questions_answered_correctly():
            self.victory = True
            from .victory_view import VictoryView
            victory_view = VictoryView(self.score_manager.score,
                                       self.challenge_manager.wrong_answers,
                                       self.window)
            self.window.show_view(victory_view)

    def _next_level(self):
        """Generate a new maze and continue with accumulated score."""

        # Generate new maze with random start row
        new_start_row = random.randint(0, GameConstants.ROWS - 1)

        # Reset rocket position (this sets x, y directly without animation)
        self.rocket.reset(0, new_start_row)

        # Reset fog of war
        self.fog.reset()
        self.fog.update(0, new_start_row)

        # Generate new maze
        grid_data = MazeGenerator().generate(new_start_row)
        self.grid = GameGrid(grid_data)
        self.grid.update_rotation_dirs_for_rocket(new_start_row)
        # Reset previous column so column 0 triggers rotation on new level
        self.previous_col = 0
        # Reset activated columns for new level
        self._activated_columns = set()

        # Update start row for next level
        self.start_row = new_start_row

    def _game_over(self):
        """Handle game over state."""
        self.game_over = True
        from .game_over_view import GameOverView
        game_over_view = GameOverView(self.score_manager.score, self.window)
        self.window.show_view(game_over_view)
