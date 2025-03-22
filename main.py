# Description: 主程式檔案，負責遊戲的初始化、遊戲迴圈、遊戲狀態的管理

# --- Python 標準函式庫 ---
import os
import time

# --- 第三方套件 ---
import pygame

# --- 專案模組 ---
import entities
from entities import Player
from settings import *
from level import generate_chunk, ensure_starting_platforms
from ui import show_main_menu, show_game_over, show_pause_menu, draw_text



# --- 初始化 ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def start_game():
    global tiles, obstacles, player, all_sprites, scroll, start_time, max_distance, generated_chunks
    tiles, obstacles = generate_chunk(0)
    
    pygame.mixer.music.load(os.path.join(MUSIC_PATH, "Title_Screen.wav"))
    pygame.mixer.music.play(-1)
    ensure_starting_platforms(tiles)  # 確保前五格有平台可站
    player = Player(100, 100)
    all_sprites = pygame.sprite.Group(player)
    scroll = [0, 0]
    start_time = time.time()
    max_distance = 0
    generated_chunks = 1


# --- 排行榜儲存 ---
def save_high_score(score):
    with open("highscores.txt", "a") as f:
        f.write(f"{score}\n")


def load_high_scores():
    if not os.path.exists("highscores.txt"):
        return []
    with open("highscores.txt", "r") as f:
        lines = f.readlines()
        return sorted([int(line.strip()) for line in lines], reverse=True)[:5]


def draw_game_screen():
    for tile in tiles:
        shifted_tile = tile.rect.move(scroll[0], scroll[1])
        pygame.draw.rect(screen, GREEN, shifted_tile)

    for obs in obstacles:
        shifted_obs = obs.rect.move(scroll[0], scroll[1])
        screen.blit(obs.image, shifted_obs)
        #pygame.draw.rect(screen, RED, obs.rect.move(scroll[0], 0), 2) # debug，畫出障礙物的碰撞框

    screen.blit(player.image, (player.rect.x + scroll[0], player.rect.y + scroll[1]))

    for i in range(player.max_health):
        x = 10 + i * 30
        y = 10
        pygame.draw.rect(screen, GRAY, (x, y, 20, 20), 2)  # 邊框寬度=2
        # 畫實心血量
        if i < player.health:
            pygame.draw.rect(screen, RED, (x + 2, y + 2, 16, 16)) 


    draw_text(f"Distance: {max_distance} m", WIDTH - 250, 10, BLACK)


# --- 執行主選單 ---
show_main_menu()
start_game()

# --- 遊戲狀態 ---
paused = False
game_over = False
running = True
typed_code = ""

while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        # 離開遊戲
        if event.type == pygame.QUIT:
            running = False            
        
        # 暫停遊戲
        if event.type == pygame.KEYDOWN:
            if paused:
                if event.key == pygame.K_ESCAPE:
                    paused = False  # 恢復遊戲
                elif event.key == pygame.K_q:
                    pygame.quit()
                    exit()

            elif game_over:
                if event.key == pygame.K_r:
                    game_over = False
                    start_game()
            else:
                if event.key == pygame.K_ESCAPE:
                    paused = True  # 進入暫停選單
                    
            if event.unicode:
                typed_code += event.unicode
                typed_code = typed_code[-15:] 
                if "1234" in typed_code:
                    entities._dflag_ = True
                    print("I'm god!")
                    typed_code = ""

    if paused:
        draw_game_screen()
        show_pause_menu()

    if not game_over and not paused:
        all_sprites.update(tiles, scroll, obstacles)

        # 生成新地形（當角色接近邊界）
        right_edge = (generated_chunks * 30 - 10) * TILE_SIZE
        if player.rect.right > right_edge:
            new_tiles, new_obs = generate_chunk(generated_chunks * 30)
            tiles.add(*new_tiles)
            obstacles.add(*new_obs)
            generated_chunks += 1

        # 計算距離分數
        distance = player.rect.x // TILE_SIZE
        max_distance = max(max_distance, distance)

        if player.rect.top > HEIGHT or player.health <= 0:
            end_time = time.time()
            total_time = end_time - start_time
            if not entities._dflag_:
                save_high_score(max_distance)
            else:
                print("God not count!")
            show_game_over(max_distance, total_time, load_high_scores())
            start_game()  # 加這行：遊戲結束後重開
            game_over = False  # 加這行：重置狀態

        draw_game_screen()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()