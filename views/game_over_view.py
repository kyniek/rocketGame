import arcade

from game_constants import GameConstants


class GameOverView(arcade.View):
    """Game over screen shown when player runs out of lives."""

    def __init__(self, score: int, window=None):
        """Initialize game over view.

        Args:
            score: Final score.
            window: Optional arcade Window instance (uses current window if None).
        """
        super().__init__(window)
        self.score = score

    def on_show(self):
        """Called when this view is shown."""
        arcade.set_background_color(arcade.color.RED)

    def on_draw(self):
        """Draw the game over screen."""
        self.window.clear()
        arcade.set_background_color(arcade.color.RED)

        # Game Over message
        arcade.draw_text(
            "GAME OVER",
            self.window.width / 2,
            self.window.height - GameConstants.GAME_OVER_TITLE_Y_OFFSET,
            arcade.color.WHITE,
            GameConstants.GAME_OVER_TITLE_SIZE,
            anchor_x="center"
        )

        # Score
        arcade.draw_text(
            f"Final Score: {self.score}",
            self.window.width / 2,
            self.window.height - GameConstants.GAME_OVER_SCORE_Y_OFFSET,
            arcade.color.WHITE,
            GameConstants.GAME_OVER_SCORE_SIZE,
            anchor_x="center"
        )

        # # Restart button
        # arcade.draw_lbwh_rectangle_filled(
        #     self.window.width / 2,
        #     GameConstants.GAME_OVER_BUTTON_Y,
        #     GameConstants.GAME_OVER_BUTTON_WIDTH,
        #     GameConstants.GAME_OVER_BUTTON_HEIGHT,
        #     arcade.color.BLUE
        # )
        arcade.draw_text(
            "RESTART",
            self.window.width / 2,
            GameConstants.GAME_OVER_BUTTON_Y,
            arcade.color.WHITE,
            GameConstants.GAME_OVER_SCORE_SIZE,
            anchor_x="center",
            anchor_y="center"
        )

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Handle mouse click to restart."""
        btn_width = GameConstants.GAME_OVER_BUTTON_WIDTH
        btn_height = GameConstants.GAME_OVER_BUTTON_HEIGHT
        btn_x = self.window.width / 2
        btn_y = GameConstants.GAME_OVER_BUTTON_Y

        if (btn_x - btn_width/2 <= x <= btn_x + btn_width/2 and
            btn_y - btn_height/2 <= y <= btn_y + btn_height/2):
            from .start_view import StartView
            start_view = StartView()
            self.window.show_view(start_view)
