import pygame
import random
from game.settings import WIDTH, HEIGHT, TILE_SIZE
from game.entities import Tile, Obstacle


# --- 地圖生成（延伸） ---
def ensure_starting_platforms(tiles):
    y_base = HEIGHT // TILE_SIZE - 3
    for i in range(5):
        x = i * TILE_SIZE
        y = y_base * TILE_SIZE
        tile = Tile(x, y)
        tiles.add(tile)

  
  
# 隨機決定這次平台寬度
def add_base_platform(x, y, platform_width, width, tiles, obstacles, start_x, difficulty, occupied_tiles):
    for i in range(platform_width):
        if x + i < width:
            tx = (start_x + x + i) * TILE_SIZE
            ty = y * TILE_SIZE
            grid_pos = ((start_x + x + i), y)

            if grid_pos not in occupied_tiles:
                tile = Tile(tx, ty)
                tiles.add(tile)
                occupied_tiles.add(grid_pos)

                # 障礙物檢查不要重疊
                if tx >= 5 * TILE_SIZE and random.random() < 0.3 * difficulty:
                    obstacle_pos = (grid_pos[0], grid_pos[1] - 1)
                    if obstacle_pos not in occupied_tiles:
                        obs = Obstacle(tx, ty - TILE_SIZE)
                        obstacles.add(obs)
                        occupied_tiles.add(obstacle_pos)


# 懸空平台（浮台）
def add_floating_platforms(x, y, width, tiles, start_x, occupied_tiles):
    if random.random() < 0.2:
        for i in range(random.randint(1, 3)):
            fy = max(2, y - random.randint(2, 4))
            fx = x + i * random.randint(2, 4)
            grid_pos = (start_x + fx, fy)
            if fx < width and grid_pos not in occupied_tiles:
                tx = (start_x + fx) * TILE_SIZE
                ty = fy * TILE_SIZE
                tile = Tile(tx, ty)
                tiles.add(tile)
                occupied_tiles.add(grid_pos)


# 階梯坡道
def add_stairs(x, y, width, tiles, start_x, occupied_tiles):
    if random.random() < 0.3:
        for step in range(3):
            sy = max(2, y - step)            
            if x + step < width and (start_x + x + step, sy) not in occupied_tiles:
                tx = (start_x + x + step) * TILE_SIZE
                ty = sy * TILE_SIZE
                grid_pos = (start_x + x + step, sy)
                tile = Tile(tx, ty)
                tiles.add(tile)
                occupied_tiles.add(grid_pos)



def generate_chunk(start_x, height=15, width=30, difficulty=1.0):

    x = 0
    y = height - 3
    step_range = max(2, int(5 - difficulty))  # 間距小 = 更密集地形
    height_variation = min(int(difficulty * 2), 3)  # 高低差更劇烈
    occupied_tiles = set() 
    
    tiles = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    
    platform_width = random.randint(2, 5) if difficulty < 2 else random.randint(1, 3)

    while x < width:
        y += random.choice([-height_variation, 0, height_variation])
        y = max(2, min(height - 2, y))
        
        add_base_platform(x, y, platform_width, width, tiles, obstacles, start_x, difficulty, occupied_tiles)
        add_floating_platforms(x, y, width, tiles, start_x, occupied_tiles)
        add_stairs(x, y, width, tiles, start_x, occupied_tiles)
                        
        x += random.randint(step_range, step_range + 2)
        # print(f"Chunk at {start_x}: {len(tiles)} tiles, {len(obstacles)} obstacles")
                
    return tiles, obstacles
