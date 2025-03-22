import pygame
from settings import *


def draw_text(text, x, y, color=WHITE, font=font_medium):
    img = font.render(text, True, color)
    screen = pygame.display.get_surface()
    screen.blit(img, (x, y))

def draw_centered_text(text, y, color=WHITE, font=font_medium):
    img = font.render(text, True, color)
    x = WIDTH // 2 - img.get_width() // 2
    screen = pygame.display.get_surface()
    screen.blit(img, (x, y))


def show_main_menu():
    screen = pygame.display.get_surface()
    while True:
        screen.fill((30, 30, 30))
        draw_centered_text("Pixel Jumper", HEIGHT // 2 - 120, WHITE, font_large)
        draw_centered_text("Press ENTER to Start", HEIGHT // 2, LIGHT_GRAY, font_medium)
        draw_centered_text("Press ESC to Exit", HEIGHT // 2 + 50, NORMAL_GRAY, font_small)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return


def show_game_over(distance, total_time, highscores):
    screen = pygame.display.get_surface()
    while True:
        screen.fill((20, 20, 20))
        draw_centered_text("Game Over", 100, (255, 100, 100), font_large)
        draw_centered_text(f"Distance: {distance} m", 180, WHITE, font_medium)
        draw_centered_text(f"Time: {int(total_time)} s", 230, LIGHT_GRAY, font_medium)
        draw_centered_text("Top 5 Scores:", 290, (255, 255, 0), font_medium)
        for i, score in enumerate(highscores):
            draw_centered_text(f"{i+1}. {score} m", 330 + i * 30, WHITE, font_small)
        draw_centered_text("Press R to Restart", 500, LIGHT_GRAY, font_small)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                return


def show_pause_menu():
    screen = pygame.display.get_surface()
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 64))
    screen.blit(overlay, (0, 0))
    pygame.draw.rect(
        screen, (50, 50, 50), (WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
    )
    draw_text("Paused", WIDTH // 2 - 80, HEIGHT // 2 - 80, WHITE, font_large)
    draw_text("Press ESC to Resume", WIDTH // 2 - 140, HEIGHT // 2, LIGHT_GRAY, font_small)
    draw_text("Press Q to Quit", WIDTH // 2 - 120, HEIGHT // 2 + 40, LIGHT_GRAY, font_small)
    pygame.display.flip()
