import pygame
from settings import *
import os


def draw_text(text, x, y, color=WHITE, font=font_medium):
    img = font.render(text, True, color)
    screen = pygame.display.get_surface()
    screen.blit(img, (x, y))

def draw_centered_text(text, y, color=WHITE, font=font_medium):
    img = font.render(text, True, color)
    x = WIDTH // 2 - img.get_width() // 2
    screen = pygame.display.get_surface()
    screen.blit(img, (x, y))
    
def draw_text_left(text, x, y, color=WHITE, font=font_medium):
    img = font.render(text, True, color)
    screen = pygame.display.get_surface()
    screen.blit(img, (x, y))
    return img.get_width(), img.get_height() 

def draw_key_highlight_line(full_text, key, y, base_color, key_color, font):
    """
    將文字中出現的按鍵 key 突顯顏色（居中顯示）。
    full_text: 字串，如 "Press H for How to Play"
    key: 要突顯的字，如 "H"
    y: 垂直座標
    base_color: 一般文字顏色
    key_color: 要突顯的按鍵顏色
    font: 使用的字型
    """
    screen = pygame.display.get_surface()

    # 分段處理
    parts = full_text.split(key, 1)
    before, after = parts[0], parts[1] if len(parts) > 1 else ""

    # 渲染各段
    img1 = font.render(before, True, base_color)
    img2 = font.render(key, True, key_color)
    img3 = font.render(after, True, base_color)

    # 計算置中 X 座標
    total_width = img1.get_width() + img2.get_width() + img3.get_width()
    x = WIDTH // 2 - total_width // 2

    # 繪製
    screen.blit(img1, (x, y))
    screen.blit(img2, (x + img1.get_width(), y))
    screen.blit(img3, (x + img1.get_width() + img2.get_width(), y))


def show_help_screen():
    screen = pygame.display.get_surface()
    while True:
        x = 40
        screen.fill((20, 20, 20))
        draw_text_left("- HOW TO PLAY", x, 80, (255, 255, 0), font_large)
        draw_text_left("- ← / → to move", x, 160, WHITE, font_medium)
        draw_text_left("- Space to jump (double jump supported)", x, 200, WHITE, font_medium)
        draw_text_left("- Avoid falling off or hitting obstacles", x, 240, WHITE, font_medium)
        draw_text_left("- You have 3 HP. You lose 1 if hit or fall.", x, 280, WHITE, font_medium)
        draw_text_left("- ESC to pause / Q to quit while paused", x, 320, WHITE, font_medium)
        draw_text_left("- Press B to go back", x, 450, LIGHT_GRAY, font_small)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                return

def show_about_screen():
    screen = pygame.display.get_surface()
    while True:
        screen.fill((20, 20, 20))

        draw_centered_text("ABOUT / CREDITS", 60, (255, 255, 0), font_large)
        draw_centered_text("Game: Pixel Jumper", 140, WHITE, font_medium)
        draw_centered_text("Created by: Kaimin Liao", 180, WHITE, font_medium)

        draw_centered_text("Music: 'Title Screen' by Juhani Junkala", 240, LIGHT_GRAY, font_small)
        draw_centered_text("Licensed under CC BY 4.0", 270, LIGHT_GRAY, font_small)
        draw_centered_text("https://opengameart.org/content/5-chiptunes-action", 300, LIGHT_GRAY, font_small)

        draw_centered_text("Press B to go back", 460, NORMAL_GRAY, font_small)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                return


def show_main_menu():
    screen = pygame.display.get_surface()
    pygame.mixer.music.load(os.path.join(MUSIC_PATH, "CDMIxVintage.mp3"))
    pygame.mixer.music.play(-1)  # 無限循環播放
    
    while True:
        screen.fill((30, 30, 30))

        # 🎮 標題
        draw_centered_text("Pixel Jumper", 80, WHITE, font_large)

        # ▶️ 主功能選項
        draw_key_highlight_line("Press ENTER to Start", "ENTER", 180, LIGHT_GRAY, KEY_HIGHLIGHT, font_medium)
        draw_key_highlight_line(
            "Press H for How to Play",
            "H",
            230,
            NORMAL_GRAY,
            KEY_HIGHLIGHT,
            font_small
        )
        draw_key_highlight_line(
            "Press C for Credits",  
            "C",                   
            270,     
            NORMAL_GRAY,            
            (255, 180, 100),        
            font_small              
        )

        draw_key_highlight_line("Press ESC to Exit", "ESC", 330, NORMAL_GRAY, (100, 255, 200), font_small)


        # 左下角 How to Play 小標題
        text_x = 30
        text_y = HEIGHT - 150
        title_width, title_height = draw_text_left("How to Play (Simple)", text_x, text_y, (200, 200, 200), font_medium)

        # 加底線
        pygame.draw.line(
            screen,
            (80, 80, 80),
            (text_x, text_y + title_height + 3),
            (text_x + title_width, text_y + title_height + 3),
            2,
        )
        # 左下角操作說明（靠左對齊）
        draw_text_left("← / → to move", text_x, text_y + 40, LIGHT_GRAY, font_small)
        draw_text_left("Space to jump (double jump)", text_x, text_y + 70, LIGHT_GRAY, font_small)
        draw_text_left("ESC to pause | Q to quit", text_x, text_y + 100, LIGHT_GRAY, font_small)

        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                if event.key == pygame.K_h:
                    show_help_screen()
                if event.key == pygame.K_c:
                    show_about_screen()
                if  event.key == pygame.K_RETURN:
                    return


def show_game_over(distance, total_time, highscores):
    screen = pygame.display.get_surface()
    pygame.mixer.music.load(os.path.join(MUSIC_PATH, "Woodland Fantasy.mp3"))    
    pygame.mixer.music.play(-1)  # 可選用 -1 代表無限迴圈，或 0 播一次
    while True:
        screen.fill((20, 20, 20))
        draw_centered_text("Game Over", 100, (255, 100, 100), font_large)
        draw_centered_text(f"Distance: {distance} m", 180, WHITE, font_medium)
        draw_centered_text(f"Time: {int(total_time)} s", 230, LIGHT_GRAY, font_medium)
        draw_centered_text("Top 5 Scores:", 290, (255, 255, 0), font_medium)
        for i, score in enumerate(highscores):
            draw_centered_text(f"{i+1}. {score} m", 330 + i * 30, WHITE, font_small)
        draw_centered_text("Press R to Restart", 500, LIGHT_GRAY, font_small)
        draw_centered_text("Press B back to Main Manu", 550, LIGHT_GRAY, font_small)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                if event.key == pygame.K_b:
                    show_main_menu()
                if event.key == pygame.K_r:
                    return


def show_pause_menu():
    screen = pygame.display.get_surface()

    # 畫半透明遮罩
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 64))
    screen.blit(overlay, (0, 0))

    # --- 中央置中的對話框 ---
    box_width, box_height = 400, 200
    box_x = WIDTH // 2 - box_width // 2
    box_y = HEIGHT // 2 - box_height // 2
    pygame.draw.rect(screen, (50, 50, 50), (box_x, box_y, box_width, box_height))
    pygame.draw.rect(screen, (200, 200, 200), (box_x, box_y, box_width, box_height), 2)

    # --- 左對齊文字（以框的左側為基準 + padding）---
    padding_x = 20
    padding_y = 20
    draw_text_left("Paused", box_x + padding_x, box_y + padding_y, WHITE, font_large)
    draw_text_left("Press ESC to Resume", box_x + padding_x, box_y + padding_y + 90, LIGHT_GRAY, font_small)
    draw_text_left("Press Q to Quit", box_x + padding_x, box_y + padding_y + 120, LIGHT_GRAY, font_small)

    pygame.display.flip()

