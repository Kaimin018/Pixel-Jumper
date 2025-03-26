# Description: 主程式檔案，負責遊戲的初始化、遊戲迴圈、遊戲狀態的管理

# --- Python 標準函式庫 ---
import os
import json
import time

# --- 第三方套件 ---
import pygame

# --- 專案模組 ---
import game.entities as entities
from game.settings import *
from game.gamestate import GameState
from common.ui import show_main_menu, show_game_over, show_pause_menu

# --- 初始化 ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

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

def main():
    running = True

    while running:
        show_main_menu()
        
        in_game = True
        while in_game:
            state = GameState()
            state.screen = screen
            state.clock = clock
            state.initialize()
            
            pygame.mixer.music.load(os.path.join(MUSIC_PATH, "Title_Screen.wav"))
            pygame.mixer.music.play(-1)
            
            typed_code = ""
            
            while not state.game_over:
                # --- 按鈕處理 ---
                for event in pygame.event.get():
                    # 離開遊戲
                    if event.type == pygame.QUIT:
                        running = False            
                    
                    # 暫停遊戲
                    if event.type == pygame.KEYDOWN:
                        if state.paused:
                            if event.key == pygame.K_ESCAPE:
                                state.paused = False  # 恢復遊戲
                            elif event.key == pygame.K_q:
                                pygame.quit()
                                exit()
                        else:
                            if event.key == pygame.K_ESCAPE:
                                state.paused = True  # 進入暫停選單
                                
                        if event.unicode:
                            typed_code += event.unicode
                            typed_code = typed_code[-15:] 
                            if "1234" in typed_code:
                                entities._dflag_ = True
                                print("I'm god!")
                                typed_code = ""

                state.update()
                state.draw()
                
                if state.paused:
                    show_pause_menu()
                    
                if state.game_over:
                    end_time = pygame.time.get_ticks()
                    total_time = (end_time - state.start_time) / 1000  # 转换为秒
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