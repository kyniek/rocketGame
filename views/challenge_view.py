import arcade
from typing import Callable

from challenges.challenge import MultipleChoiceChallenge, TextChallenge
from game_constants import GameConstants


class ChallengeView(arcade.View):
    """Modal view for presenting challenges."""

    def __init__(self, challenge, callback: Callable[[bool], None]):
        """Initialize challenge view.

        Args:
            challenge: The Challenge object to present.
            callback: Function to call with result (True=correct, False=wrong).
        """
        super().__init__()
        self.challenge = challenge
        self.callback = callback
        self.input_text = ""
        self.error_message = ""
        # Feedback state: None, True (correct), False (wrong)
        self.feedback_state = None
        self.feedback_time = 0

    def on_show(self):
        """Called when this view is shown."""
        arcade.set_background_color(arcade.color.DARK_GRAY)

    def on_update(self, delta_time: float):
        """Update timing for feedback state."""
        if self.feedback_state is not None:
            # Check if feedback duration has passed
            current_time = self.window.time * 1000  # Convert seconds to milliseconds
            if current_time - self.feedback_time >= GameConstants.FEEDBACK_DURATION_MS:
                # Return to main game screen
                self.callback(self.feedback_state)

    def on_draw(self):
        """Draw the challenge view."""
        self.window.clear()

        # Set background color based on feedback state
        if self.feedback_state is True:
            arcade.set_background_color(arcade.color.GREEN)
        elif self.feedback_state is False:
            arcade.set_background_color(arcade.color.RED)
        else:
            arcade.set_background_color(arcade.color.DARK_GRAY)

        # Question box
        question_y = self.window.height - GameConstants.CHALLENGE_QUESTION_Y_OFFSET
        # arcade.draw_lbwh_rectangle_filled(
        #     self.window.width / 2,
        #     question_y + 50,
        #     GameConstants.CHALLENGE_INPUT_WIDTH,
        #     GameConstants.CHALLENGE_INPUT_HEIGHT,
        #     arcade.color.LIGHT_GRAY
        # )
        arcade.draw_text(
            self.challenge.question,
            self.window.width / 2,
            question_y,
            arcade.color.BLACK,
            GameConstants.CHALLENGE_QUESTION_SIZE,
            anchor_x="center",
            anchor_y="center"
        )

        if isinstance(self.challenge, MultipleChoiceChallenge):
            self._draw_multiple_choice(question_y - GameConstants.CHALLENGE_OPTIONS_Y_OFFSET)
        elif isinstance(self.challenge, TextChallenge):
            self._draw_text_challenge(question_y - GameConstants.CHALLENGE_OPTIONS_Y_OFFSET)

        # Error message
        if self.error_message:
            arcade.draw_text(
                self.error_message,
                self.window.width / 2,
                GameConstants.CHALLENGE_ERROR_Y,
                arcade.color.RED,
                GameConstants.CHALLENGE_ERROR_SIZE,
                anchor_x="center"
            )

        # Instructions
        arcade.draw_text(
            "Press 1, 2, 3 to answer (or Enter for text)",
            self.window.width / 2,
            GameConstants.CHALLENGE_INSTRUCTIONS_Y,
            arcade.color.LIGHT_GRAY,
            GameConstants.CHALLENGE_INSTRUCTIONS_SIZE,
            anchor_x="center"
        )

    def _draw_multiple_choice(self, y_start: int):
        """Draw multiple choice options."""
        for i, option in enumerate(self.challenge.options):
            y = y_start - (i * GameConstants.CHALLENGE_OPTION_SPACING)
            # arcade.draw_lbwh_rectangle_filled(
            #     self.window.width / 2,
            #     y,
            #     GameConstants.CHALLENGE_OPTION_WIDTH,
            #     GameConstants.CHALLENGE_OPTION_HEIGHT,
            #     arcade.color.LIGHT_BLUE
            # )
            arcade.draw_text(
                f"{i + 1}. {option}",
                self.window.width / 2 - GameConstants.CHALLENGE_OPTION_OFFSET_X,
                y,
                arcade.color.BLACK,
                GameConstants.CHALLENGE_OPTION_SIZE,
                anchor_y="center"
            )

    def _draw_text_challenge(self, y_start: int):
        """Draw text input field."""
        # Input box
        # arcade.draw_lbwh_rectangle_filled(
        #     self.window.width / 2,
        #     y_start,
        #     GameConstants.CHALLENGE_INPUT_WIDTH,
        #     GameConstants.CHALLENGE_INPUT_HEIGHT,
        #     arcade.color.WHITE
        # )
        arcade.draw_text(
            self.input_text + ("_" if len(self.input_text) < GameConstants.GRID_COLS else ""),
            self.window.width / 2 - GameConstants.CHALLENGE_OPTION_OFFSET_X,
            y_start,
            arcade.color.BLACK,
            GameConstants.CHALLENGE_OPTION_SIZE,
            anchor_y="center"
        )

    def on_key_press(self, key: int, modifiers: int):
        """Handle keyboard input."""
        if isinstance(self.challenge, MultipleChoiceChallenge):
            self._handle_multiple_choice_input(key)
        elif isinstance(self.challenge, TextChallenge):
            self._handle_text_input(key)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Handle mouse click on options."""
        if isinstance(self.challenge, MultipleChoiceChallenge):
            self._handle_mouse_click(x, y)

    def _handle_multiple_choice_input(self, key: int):
        """Handle numeric key presses for multiple choice."""
        if isinstance(self.challenge, MultipleChoiceChallenge):
            selected_index = None
            if key in (arcade.key.KEY_1, arcade.key.NUM_1):
                selected_index = 0
            elif key in (arcade.key.KEY_2, arcade.key.NUM_2):
                selected_index = 1
            elif key in (arcade.key.KEY_3, arcade.key.NUM_3):
                selected_index = 2

            if selected_index is not None and selected_index < len(self.challenge.options):
                self._submit_answer(self.challenge.options[selected_index])

    def _handle_text_input(self, key: int):
        """Handle text input."""
        if key == arcade.key.ENTER:
            self._submit_answer(self.input_text)
        elif key == arcade.key.BACKSPACE:
            self.input_text = self.input_text[:-1]
        elif key == arcade.key.SPACE:
            self.input_text += " "
        elif len(self.input_text) < GameConstants.GRID_COLS:
            # Get character from key
            char = self._key_to_char(key)
            if char:
                self.input_text += char

    def _handle_mouse_click(self, x: int, y: int):
        """Handle mouse click on multiple choice options."""
        width = self.window.width
        height = self.window.height

        # Calculate option positions (same as _draw_multiple_choice)
        question_y = height - GameConstants.CHALLENGE_QUESTION_Y_OFFSET
        y_start = question_y - GameConstants.CHALLENGE_OPTIONS_Y_OFFSET

        for i, option in enumerate(self.challenge.options):
            opt_y = y_start - (i * GameConstants.CHALLENGE_OPTION_SPACING)
            opt_left = width / 2 - GameConstants.CHALLENGE_OPTION_OFFSET_X
            opt_right = width / 2 + GameConstants.CHALLENGE_OPTION_OFFSET_X

            if opt_left <= x <= opt_right and opt_y - GameConstants.CHALLENGE_CLICK_Y_MARGIN <= y <= opt_y + GameConstants.CHALLENGE_CLICK_Y_MARGIN:
                self._submit_answer(option)
                return

    def _key_to_char(self, key: int) -> str:
        """Convert key code to character."""
        if arcade.key.A <= key <= arcade.key.Z:
            return chr(key)
        # Handle numbers
        if arcade.key.NUM_0 <= key <= arcade.key.NUM_9:
            return str(key - arcade.key.NUM_0)
        if arcade.key.KEY_0 <= key <= arcade.key.KEY_9:
            return str(key - arcade.key.KEY_0)
        # Handle common punctuation and space-like chars
        if key == arcade.key.SPACE:
            return " "
        if key == arcade.key.PERIOD:
            return "."
        if key == arcade.key.COMMA:
            return ","
        if key == arcade.key.MINUS:
            return "-"
        if key == arcade.key.EQUAL:
            return "="
        return ""

    def _submit_answer(self, answer: str):
        """Submit the answer and show feedback."""
        try:
            is_correct = self.challenge.check_answer(answer)
            # Show feedback state and start timer
            self.feedback_state = is_correct
            self.feedback_time = self.window.time * 1000  # Convert seconds to milliseconds
        except Exception as e:
            self.error_message = f"Error: {e}"
