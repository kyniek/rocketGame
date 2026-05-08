import arcade
from random import randint

from views.game_view import GameView
from game_constants import GameConstants


class StartView(arcade.View):
    """Start screen with instructions and start button."""

    def __init__(self):
        super().__init__()
        # Tekstura tła – wczytana tylko raz
        self.background_texture = arcade.load_texture("assets/title_rocket.png")


    def on_draw(self):
        """Draw the start screen."""
        self.window.clear()

        width = self.window.width
        height = self.window.height

        # Tło – obrazek rozciągnięty na całe okno
        arcade.draw_texture_rect(
            self.background_texture,
            arcade.types.LBWH(0, 0, self.window.width, self.window.height)
        )

        # Title - centered near top with breathing room (white with black outline)
        title_text = arcade.Text(
            "GAME ROCKET",
            width / 2,
            height - GameConstants.START_TITLE_Y_OFFSET,
            arcade.color.BLACK,
            GameConstants.START_TITLE_SIZE,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
        title_text.draw()
        title_text.color = arcade.color.WHITE
        title_text.draw()

        # Subtitle (white with black outline)
        subtitle_text = arcade.Text(
            "Educational Rocket Game",
            width / 2,
            height - GameConstants.START_SUBTITLE_Y_OFFSET,
            arcade.color.BLACK,
            GameConstants.START_SUBTITLE_SIZE,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
        subtitle_text.draw()
        subtitle_text.color = arcade.color.WHITE
        subtitle_text.draw()

        # Instructions - centered vertically in the middle area
        instructions = [
            "Use ARROW KEYS to control the rocket:",
            "  UP/DOWN - Change row",
            "  RIGHT - Move forward",
            "",
            "Avoid RED obstacles (lose life on collision)",
            "",
            f"Answer questions ({GameConstants.CHALLENGE_CHANCE * 100:.0f}% chance on forward move)",
            f"  Correct: +{GameConstants.POINTS_PER_CORRECT_ANSWER} points",
            "  Wrong: -1 life",
            "",
            "Answer ALL questions correctly to WIN!"
        ]

        # Start instructions below the title, spread out evenly (white with black outline)
        y_pos = height / 2 + GameConstants.START_INSTRUCTION_Y_OFFSET
        for line in instructions:
            line_text = arcade.Text(
                line,
                width / 2,
                y_pos,
                arcade.color.BLACK,
                GameConstants.START_INSTRUCTION_SIZE,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )
            line_text.draw()
            line_text.color = arcade.color.WHITE
            line_text.draw()
            y_pos -= GameConstants.START_INSTRUCTION_SPACING

        # Start button - positioned below instructions with clear spacing
        btn_width = GameConstants.START_BUTTON_WIDTH
        btn_height = GameConstants.START_BUTTON_HEIGHT
        btn_x = width / 2
        btn_y = GameConstants.START_BUTTON_Y

        arcade.draw_lrbt_rectangle_filled(
            btn_x - btn_width / 2,
            btn_x + btn_width / 2,
            btn_y - btn_height / 2,
            btn_y + btn_height / 2,
            arcade.color.GREEN
        )
        # Start button text (white with black outline)
        start_text = arcade.Text(
            "START GAME",
            btn_x,
            btn_y,
            arcade.color.BLACK,
            24,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
        start_text.draw()
        start_text.color = arcade.color.WHITE
        start_text.draw()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Handle mouse click on start button."""
        # Check if clicked on start button area
        btn_width = GameConstants.START_BUTTON_WIDTH
        btn_height = GameConstants.START_BUTTON_HEIGHT
        btn_x = self.window.width / 2
        btn_y = GameConstants.START_BUTTON_Y

        if (btn_x - btn_width/2 <= x <= btn_x + btn_width/2 and
            btn_y - btn_height/2 <= y <= btn_y + btn_height/2):
            # Create game with random start row
            start_row = randint(0, 2)

            game_view = GameView(start_row)
            self.window.show_view(game_view)
