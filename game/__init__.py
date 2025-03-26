# __init__.py

# 導出主要類別與功能，讓外部可以 from game import Player 等用法

from game.entities import Player, Obstacle
from game.level import generate_chunk, ensure_starting_platforms
from common.ui import (
    show_main_menu,
    show_game_over,
    show_pause_menu,
    draw_text,
    draw_centered_text,
    draw_text_left,
    draw_key_highlight_line
)
from .settings import (
    WIDTH,
    HEIGHT,
    TILE_SIZE,
    WHITE,
    RED,
    GREEN,
    GRAY,
    BLACK,
    LIGHT_GRAY,
    NORMAL_GRAY,
    KEY_HIGHLIGHT,
    font,
    font_small,
    font_medium,
    font_large,
    MUSIC_PATH,
)
