"""Flattened game logic package for web version."""

import sys
import os

# Ensure web/ is on sys.path so flat imports (from constants import ...) resolve
# when modules are accessed via game.constants, game.maze_generator, etc.
_web_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _web_root not in sys.path:
    sys.path.insert(0, _web_root)
