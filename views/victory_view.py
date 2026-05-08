import arcade

from game_constants import GameConstants


class VictoryView(arcade.View):
    """Victory screen shown when player reaches the goal."""

    def __init__(self, score: int, wrong_answers: list, window=None):
        """Initialize victory view.

        Args:
            score: Final score.
            wrong_answers: List of dictionaries with question, user_answer, correct_answer.
            window: Optional arcade Window instance (uses current window if None).
        """
        super().__init__(window)
        self.score = score
        self.wrong_answers = wrong_answers

    def on_show(self):
        """Called when this view is shown."""
        arcade.set_background_color(arcade.color.GREEN)

    def on_draw(self):
        """Draw the victory screen."""
        self.window.clear()
        arcade.set_background_color(arcade.color.GREEN)

        # Victory message
        arcade.draw_text(
            "VICTORY!",
            self.window.width / 2,
            self.window.height - GameConstants.VICTORY_TITLE_Y_OFFSET,
            arcade.color.WHITE,
            GameConstants.VICTORY_TITLE_SIZE,
            anchor_x="center"
        )

        # Score
        arcade.draw_text(
            f"Final Score: {self.score}",
            self.window.width / 2,
            self.window.height - GameConstants.VICTORY_SCORE_Y_OFFSET,
            arcade.color.WHITE,
            GameConstants.VICTORY_SCORE_SIZE,
            anchor_x="center"
        )

        # Wrong answers section
        if self.wrong_answers:
            arcade.draw_text(
                "Questions you missed:",
                self.window.width / 2,
                self.window.height - GameConstants.VICTORY_MISSED_Y_OFFSET,
                arcade.color.YELLOW,
                GameConstants.VICTORY_MISSED_LABEL_SIZE,
                anchor_x="center"
            )

            y_pos = self.window.height - GameConstants.VICTORY_MISSED_START_Y_OFFSET
            for i, wrong in enumerate(self.wrong_answers[:GameConstants.VICTORY_MAX_MISSED]):
                arcade.draw_text(
                    f"{i + 1}. {wrong['question']}",
                    self.window.width / 2,
                    y_pos,
                    arcade.color.WHITE,
                    GameConstants.VICTORY_MISSED_ITEM_SIZE,
                    anchor_x="center"
                )
                y_pos -= GameConstants.VICTORY_MISSED_SPACING

        # Restart button
        # arcade.draw_lbwh_rectangle_filled(
        #     self.window.width / 2,
        #     GameConstants.VICTORY_BUTTON_Y,
        #     GameConstants.VICTORY_BUTTON_WIDTH,
        #     GameConstants.VICTORY_BUTTON_HEIGHT,
        #     arcade.color.BLUE
        # )
        arcade.draw_text(
            "NEW GAME",
            self.window.width / 2,
            GameConstants.VICTORY_BUTTON_Y,
            arcade.color.WHITE,
            GameConstants.VICTORY_MISSED_LABEL_SIZE,
            anchor_x="center",
            anchor_y="center"
        )

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Handle mouse click to restart."""
        btn_width = GameConstants.VICTORY_BUTTON_WIDTH
        btn_height = GameConstants.VICTORY_BUTTON_HEIGHT
        btn_x = self.window.width / 2
        btn_y = GameConstants.VICTORY_BUTTON_Y

        if (btn_x - btn_width/2 <= x <= btn_x + btn_width/2 and
            btn_y - btn_height/2 <= y <= btn_y + btn_height/2):
            from .start_view import StartView
            start_view = StartView()
            self.window.show_view(start_view)
