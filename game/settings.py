import pygame
import os

# 根目錄
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Assets 資料夾
ASSETS_PATH = os.path.join(ROOT_DIR, 'assets')
MUSIC_PATH = os.path.join(ASSETS_PATH, 'music')

# 畫面尺寸
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40

# --- 顏色 ---
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLUE = (50, 50, 255)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
NORMAL_GRAY= (150, 150, 150)
ORANGE = (255, 165, 0)
KEY_HIGHLIGHT = (100, 180, 255)

# --- 音樂 ---
pygame.mixer.init()


# --- 字型 ---
pygame.font.init()
FONTS_PATH = os.path.join(ASSETS_PATH, 'fonts/DejaVuSans.ttf')
font = pygame.font.Font(FONTS_PATH, 20)
font_large = pygame.font.Font(FONTS_PATH, 60)    # 定義大字型
font_medium = pygame.font.Font(FONTS_PATH, 30)   # 定義中等字型
font_small = pygame.font.Font(FONTS_PATH, 20)    # 定義小字型

