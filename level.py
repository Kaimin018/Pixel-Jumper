import pygame
import random
from settings import WIDTH, HEIGHT, TILE_SIZE
from entities import Obstacle


# --- 地圖生成（延伸） ---
def ensure_starting_platforms(tiles):
    y_base = HEIGHT // TILE_SIZE - 3
    for i in range(5):
        x = i * TILE_SIZE
        tile_rect = pygame.Rect(x, y_base * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        tiles.append(tile_rect)


def generate_chunk(start_x, height=15, width=30):
    level = []
    y = height - 3
    for _ in range(height):
        level.append([0] * width)

    for x in range(0, width, random.randint(3, 5)):
        y += random.choice([-2, -1, 0, 1, 2])
        y = max(2, min(height - 2, y))

        # 隨機決定這次平台寬度
        platform_width = random.randint(2, 5)
        for i in range(platform_width):
            if x + i < width:
                level[y][x + i] = 1

        # 懸空平台（浮台）
        if random.random() < 0.2:
            fy = max(2, y - random.randint(2, 4))
            if x < width:
                level[fy][x] = 1

        # 階梯坡道
        if random.random() < 0.3:
            for step in range(3):
                sy = max(2, y - step)
                if x + step < width:
                    level[sy][x + step] = 1

    tiles = []
    obstacles = []
    for y_idx, row in enumerate(level):
        for x_idx, tile in enumerate(row):
            if tile == 1:
                rect = pygame.Rect(
                    (start_x + x_idx) * TILE_SIZE,
                    y_idx * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE,
                )
                tiles.append(rect)

                # 生成障礙物（避開前五格）
                if rect.x >= 5 * TILE_SIZE and random.random() < 0.1:
                    obs = Obstacle(rect.x, rect.y - TILE_SIZE)
                    obstacles.append(obs)

    return tiles, obstacles
