import pytest
from ..models.fog_of_war import FogOfWar


class TestFogOfWar:
    """Tests for FogOfWar class."""

    def test_fog_of_war_initial_state(self):
        """Only columns 0 and 1 should be discovered initially."""
        fog = FogOfWar()

        for col in range(2):
            for row in range(3):
                assert fog.is_discovered(col, row) is True

        for col in range(2, 30):
            for row in range(3):
                assert fog.is_discovered(col, row) is False

    def test_fog_of_war_update(self):
        """Should mark cells correctly when moving forward."""
        fog = FogOfWar()

        # After update at col 5, all cells up to col 6 should be visible
        fog.update(5, 1)

        for col in range(7):  # cols 0-6
            for row in range(3):
                assert fog.is_discovered(col, row) is True

        for col in range(7, 30):
            for row in range(3):
                assert fog.is_discovered(col, row) is False

    def test_fog_of_war_see_current_column(self):
        """Current column should be fully visible."""
        fog = FogOfWar()
        fog.update(10, 2)

        for row in range(3):
            assert fog.is_discovered(10, row) is True

    def test_fog_of_war_see_next_column(self):
        """Next column should be visible (one ahead)."""
        fog = FogOfWar()
        fog.update(10, 2)

        for row in range(3):
            assert fog.is_discovered(11, row) is True

    def test_fog_of_war_reset(self):
        """Should reset to initial state."""
        fog = FogOfWar()
        fog.update(15, 1)  # Discover many cells
        fog.reset()

        for col in range(2):
            for row in range(3):
                assert fog.is_discovered(col, row) is True

        for col in range(2, 30):
            for row in range(3):
                assert fog.is_discovered(col, row) is False

    def test_fog_of_war_is_discovered(self):
        """Should return correct visibility status."""
        fog = FogOfWar()
        assert fog.is_discovered(0, 0) is True
        assert fog.is_discovered(29, 0) is False

    def test_fog_of_war_out_of_bounds(self):
        """Should return False for out-of-bounds coordinates."""
        fog = FogOfWar()

        assert fog.is_discovered(-1, 0) is False
        assert fog.is_discovered(30, 0) is False
        assert fog.is_discovered(0, -1) is False
        assert fog.is_discovered(0, 3) is False
