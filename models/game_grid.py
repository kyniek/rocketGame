import random
from typing import Optional

from game_constants import GameConstants


class GameGrid:
    """Wrapper for the maze grid that provides cell access and collision checking."""

    def __init__(self, grid: list[list[str]]):
        """Initialize with a maze grid.

        Args:
            grid: 30x3 grid from MazeGenerator.
        """
        self._grid = grid
        # Assign a random texture index (0-4) to each obstacle cell
        self._obstacle_textures: dict[tuple[int, int], int] = {}
        # Store rotation angle (in degrees) for each obstacle
        self._obstacle_rotation_angles: dict[tuple[int, int], float] = {}
        # Store rotation direction (+1 for clockwise, -1 for counterclockwise)
        self._obstacle_rotation_dirs: dict[tuple[int, int], int] = {}
        # Store current rotation speed (deg/s) for each obstacle
        self._obstacle_rotation_speeds: dict[tuple[int, int], float] = {}
        # Store rotation active flag for each obstacle
        self._obstacle_rotation_active: dict[tuple[int, int], bool] = {}
        for col in range(GameConstants.COLS):
            for row in range(GameConstants.ROWS):
                if self._grid[col][row] == 'obstacle':
                    self._obstacle_textures[(col, row)] = random.randint(0, 4)
                    self._obstacle_rotation_angles[(col, row)] = 0.0
                    self._obstacle_rotation_dirs[(col, row)] = 0  # Will be set later based on rocket
                    # Initialize speed to 0 (will be set when rotation starts)
                    self._obstacle_rotation_speeds[(col, row)] = 0.0
                    # Initialize active flag to False (will be set when rotation starts)
                    self._obstacle_rotation_active[(col, row)] = False

    def get_cell(self, col: int, row: int) -> Optional[str]:
        """Get the value of a cell.

        Args:
            col: Column index (0-29).
            row: Row index (0-2).

        Returns:
            Cell value ('empty', 'obstacle', 'start', 'goal') or None if out of bounds.
        """
        if not self._is_valid_position(col, row):
            return None
        return self._grid[col][row]

    def set_cell(self, col: int, row: int, value: str) -> bool:
        """Set the value of a cell.

        Args:
            col: Column index (0-29).
            row: Row index (0-2).
            value: New cell value.

        Returns:
            True if successful, False if out of bounds.
        """
        if not self._is_valid_position(col, row):
            return False
        self._grid[col][row] = value
        return True

    def is_walkable(self, col: int, row: int) -> bool:
        """Check if a cell is walkable.

        Args:
            col: Column index (0-29).
            row: Row index (0-2).

        Returns:
            True if the cell exists and is not an obstacle.
        """
        cell = self.get_cell(col, row)
        if cell is None:
            return False
        return cell != 'obstacle'

    def get_obstacle_texture(self, col: int, row: int) -> Optional[int]:
        """Get the texture index for an obstacle at the given position.

        Args:
            col: Column index (0-29).
            row: Row index (0-2).

        Returns:
            Texture index (0-4) if cell is an obstacle, None otherwise.
        """
        return self._obstacle_textures.get((col, row))

    def get_obstacle_rotation_angle(self, col: int, row: int) -> Optional[float]:
        """Get the rotation angle for an obstacle at the given position.

        Args:
            col: Column index (0-29).
            row: Row index (0-2).

        Returns:
            Rotation angle in degrees if cell is an obstacle, None otherwise.
        """
        return self._obstacle_rotation_angles.get((col, row))

    def get_obstacle_rotation_dir(self, col: int, row: int) -> Optional[int]:
        """Get the rotation direction for an obstacle at the given position.

        Args:
            col: Column index (0-29).
            row: Row index (0-2).

        Returns:
            Rotation direction (+1 for clockwise, -1 for counterclockwise) if cell is an obstacle, None otherwise.
        """
        return self._obstacle_rotation_dirs.get((col, row))

    def set_obstacle_rotation_angle(self, col: int, row: int, angle: float) -> bool:
        """Set the rotation angle for an obstacle at the given position.

        Args:
            col: Column index (0-29).
            row: Row index (0-2).
            angle: New rotation angle in degrees.

        Returns:
            True if successful (cell is an obstacle), False otherwise.
        """
        if (col, row) in self._obstacle_rotation_angles:
            self._obstacle_rotation_angles[(col, row)] = angle
            return True
        return False

    def get_obstacle_rotation_speed(self, col: int, row: int) -> Optional[float]:
        """Get the current rotation speed for an obstacle at the given position.

        Args:
            col: Column index (0-29).
            row: Row index (0-2).

        Returns:
            Current rotation speed in deg/s, or None if not an obstacle.
        """
        return self._obstacle_rotation_speeds.get((col, row))

    def set_obstacle_rotation_speed(self, col: int, row: int, speed: float) -> bool:
        """Set the rotation speed for an obstacle at the given position.

        Args:
            col: Column index (0-29).
            row: Row index (0-2).
            speed: New rotation speed in deg/s.

        Returns:
            True if successful (cell is an obstacle), False otherwise.
        """
        if (col, row) in self._obstacle_rotation_speeds:
            self._obstacle_rotation_speeds[(col, row)] = speed
            return True
        return False

    def get_obstacle_rotation_active(self, col: int, row: int) -> Optional[bool]:
        """Get the rotation active flag for an obstacle at the given position.

        Args:
            col: Column index (0-29).
            row: Row index (0-2).

        Returns:
            Rotation active flag if cell is an obstacle, None otherwise.
        """
        return self._obstacle_rotation_active.get((col, row))

    def set_obstacle_rotation_active(self, col: int, row: int, active: bool) -> bool:
        """Set the rotation active flag for an obstacle at the given position.

        Args:
            col: Column index (0-29).
            row: Row index (0-2).
            active: New rotation active flag.

        Returns:
            True if successful (cell is an obstacle), False otherwise.
        """
        if (col, row) in self._obstacle_rotation_active:
            self._obstacle_rotation_active[(col, row)] = active
            return True
        return False

    def update_rotation_dirs_for_rocket(self, rocket_row: int) -> None:
        """Update rotation direction for all obstacles based on rocket's current row.

        Obstacles above the rocket rotate clockwise (+1),
        obstacles below rotate counterclockwise (-1).

        Args:
            rocket_row: The row index of the rocket.
        """
        for col in range(GameConstants.COLS):
            for row in range(GameConstants.ROWS):
                if self._grid[col][row] == 'obstacle':
                    if row < rocket_row:
                        # Obstacle is above rocket - clockwise rotation
                        self._obstacle_rotation_dirs[(col, row)] = 1
                    elif row > rocket_row:
                        # Obstacle is below rocket - counterclockwise rotation
                        self._obstacle_rotation_dirs[(col, row)] = -1
                    else:
                        # Same row - default clockwise
                        self._obstacle_rotation_dirs[(col, row)] = 1

    def _is_valid_position(self, col: int, row: int) -> bool:
        """Check if position is within grid bounds."""
        return 0 <= col < GameConstants.COLS and 0 <= row < GameConstants.ROWS
