import pygame

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


# --- 字型 ---
pygame.font.init()
font = pygame.font.SysFont(None, 48)
font_large = pygame.font.SysFont(None, 72)  # 定義大字型
font_medium = pygame.font.SysFont(None, 48)  # 定義中等字型
font_small = pygame.font.SysFont(None, 32)  # 定義小字型
