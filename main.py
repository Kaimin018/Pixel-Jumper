# Description: 主程式檔案，負責遊戲的初始化、遊戲迴圈、遊戲狀態的管理

# --- Python 標準函式庫 ---
import os
import time

# --- 第三方套件 ---
import pygame
import json

# --- 專案模組 ---
import entities
from entities import Player
from settings import *
from level import generate_chunk, ensure_starting_platforms
from ui import show_main_menu, show_game_over, show_pause_menu, draw_text

class GameState:
    def __init__(self):
        self.tiles = None
        self.obstacles = None
        self.player = None
        self.all_sprites = None
        self.scroll = [0, 0]
        self.start_time = 0
        self.max_distance = 0
        self.generated_chunks = 0


# --- 初始化 ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def start_game(state: GameState):
    
    state.tiles, state.obstacles = generate_chunk(0)
    ensure_starting_platforms(state.tiles)
    state.player = Player(100, 100)
    state.all_sprites = pygame.sprite.Group(state.player)
    state.scroll = [0, 0]
    state.start_time = time.time()
    state.max_distance = 0
    state.generated_chunks = 1

    
    
    pygame.mixer.music.load(os.path.join(MUSIC_PATH, "Title_Screen.wav"))
    pygame.mixer.music.play(-1)
    ensure_starting_platforms(state.tiles)  # 確保前五格有平台可站
    player = Player(100, 100)
    all_sprites = pygame.sprite.Group(player)
    scroll = [0, 0]
    start_time = time.time()
    max_distance = 0
    generated_chunks = 1


# --- 排行榜儲存 ---
def save_high_score(score, time_survived, mode="normal"):
    score_data = {
        "score": score,
        "time": int(time_survived),
        "mode": mode
    }

    try:
        with open("highscores.json", "r") as f:
            highscores = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        highscores = []

    highscores.append(score_data)
    highscores = sorted(highscores, key=lambda x: x["score"], reverse=True)[:5]

    with open("highscores.json", "w") as f:
        json.dump(highscores, f, indent=2)


def load_high_scores():
    try:
        with open("highscores.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []



def draw_game_screen(state):
    for tile in state.tiles:
        shifted_tile = tile.rect.move(state.scroll[0], state.scroll[1])
        pygame.draw.rect(screen, GREEN, shifted_tile)

    for obs in state.obstacles:
        shifted_obs = obs.rect.move(state.scroll[0], state.scroll[1])
        screen.blit(obs.image, shifted_obs)
        #pygame.draw.rect(screen, RED, obs.rect.move(scroll[0], 0), 2) # debug，畫出障礙物的碰撞框

    screen.blit(state.player.image, (state.player.rect.x + state.scroll[0], state.player.rect.y + state.scroll[1]))

    for i in range(state.player.max_health):
        x = 10 + i * 30
        y = 10
        pygame.draw.rect(screen, GRAY, (x, y, 20, 20), 2)  # 邊框寬度=2
        # 畫實心血量
        if i < state.player.health:
            pygame.draw.rect(screen, RED, (x + 2, y + 2, 16, 16))


    draw_text(f"Distance: {state.max_distance} m", WIDTH - 250, 10, BLACK)

def main():
# [while running]
#     → show_main_menu()
#     → start_game()
#     → [while not game_over]
#         → event loop / update / draw
#         → 死亡 → show_game_over() → break
#     → 回到主選單
    
    generated_chunks = 1     
    running = True

    while running:
        
        show_main_menu()
        
        in_game = True
        while in_game:
            state = GameState()
            start_game(state)
            paused = False
            game_over = False
            typed_code = ""          
        
            while not game_over:
                # --- 按鈕處理 ---
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

                if not paused:
                    state.all_sprites.update(state.tiles, state.scroll, state.obstacles)
                
                screen.fill(WHITE)
                draw_game_screen(state)
                
                if paused:
                    show_pause_menu()            

                # 生成新地形（當角色接近邊界）
                right_edge = (generated_chunks * 30 - 10) * TILE_SIZE
                if state.player.rect.right > right_edge:
                    new_tiles, new_obs = generate_chunk(generated_chunks * 30)
                    state.tiles.add(*new_tiles)
                    state.obstacles.add(*new_obs)
                    generated_chunks += 1

                # 計算距離分數
                distance = state.player.rect.x // TILE_SIZE
                state.max_distance = max(state.max_distance, distance)

                if state.player.rect.top > HEIGHT or state.player.health <= 0:
                    end_time = time.time()
                    total_time = end_time - state.start_time
                    if not entities._dflag_:
                        save_high_score(state.max_distance, total_time)
                    else:
                        print("God not count!")
                    res = show_game_over(state.max_distance, total_time, load_high_scores())
                    if res == "restart":
                        break
                    else:
                        in_game = False
                        break
                    
                pygame.display.flip()
                clock.tick(60)
    pygame.quit()
    
if __name__ == "__main__":
    main()