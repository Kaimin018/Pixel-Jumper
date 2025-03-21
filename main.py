import pygame
import random
import time
import os

# --- 初始化 ---
pygame.init()
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --- 音樂 ---
pygame.mixer.init()
pygame.mixer.music.load("CDMIxVintage.mp3")
pygame.mixer.music.play(-1)  # 無限循環播放

# --- 顏色 ---
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLUE = (50, 50, 255)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
ORANGE = (255, 165, 0)

# --- 字型 ---
font = pygame.font.SysFont(None, 48)
font_large = pygame.font.SysFont(None, 72)  # 定義大字型
font_medium = pygame.font.SysFont(None, 48)  # 定義中等字型
font_small = pygame.font.SysFont(None, 32)  # 定義小字型


# --- 障礙物類別 ---
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(GRAY)
        self.rect = self.image.get_rect(topleft=(x, y))


# --- 玩家類別 ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 40))
        self.base_color = BLUE
        self.image.fill(self.base_color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.on_ground = False
        self.health = 3
        self.jump_count = 0
        self.max_jump_count = 2  # 最多兩段跳
        self.invincible = False
        self.invincible_timer = 0
        self.jump_pressed_last_frame = False  # 新增跳躍鍵偵測

    def update(self, tiles, scroll, obstacles):
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -5
        if keys[pygame.K_RIGHT]:
            dx = 5

        # 處理跳躍（只偵測剛按下那一幀）
        if keys[pygame.K_SPACE] and not self.jump_pressed_last_frame:
            if self.jump_count < self.max_jump_count:
                self.vel_y = -15
                self.jump_count += 1
        self.jump_pressed_last_frame = keys[pygame.K_SPACE]

        self.vel_y += 1  # gravity
        if self.vel_y > 10:
            self.vel_y = 10

        self.rect.x += dx
        self.collision(dx, 0, tiles)
        self.rect.y += self.vel_y
        self.collision(0, self.vel_y, tiles)

        # 掉出畫面處理：扣血並從上方重生在原本 X 座標
        if self.rect.top > HEIGHT:
            self.health -= 1
            self.rect.y = -100  # 從畫面上方掉下來
            self.vel_y = 0

        # 碰撞障礙物（加上無敵時間）
        if not self.invincible:
            for obs in obstacles:
                if self.rect.colliderect(obs.rect):
                    self.health -= 1
                    self.invincible = True
                    self.invincible_timer = pygame.time.get_ticks()
                    break

        # 無敵狀態持續 1 秒，並閃爍顏色
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if (current_time // 100) % 2 == 0:
                self.image.fill(ORANGE)
            else:
                self.image.fill(self.base_color)

            if current_time - self.invincible_timer > 1000:
                self.invincible = False
                self.image.fill(self.base_color)
        else:
            self.image.fill(self.base_color)

        scroll[0] = -(self.rect.x - WIDTH // 2)
        scroll[0] = min(0, scroll[0])

    def collision(self, dx, dy, tiles):
        for tile in tiles:
            if self.rect.colliderect(tile):
                if dy > 0:  # 玩家往下掉，碰到地板
                    self.rect.bottom = tile.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jump_count = 0  # 落地時重置跳躍次數
                elif dy < 0:
                    self.rect.top = tile.bottom
                    self.vel_y = 0
                elif dx > 0:
                    self.rect.right = tile.left
                elif dx < 0:
                    self.rect.left = tile.right


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


# --- 顯示文字 ---
def draw_text(text, x, y, color=BLACK):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


# --- 主選單函數 ---
def show_main_menu():
    while True:
        screen.fill((30, 30, 30))
        title = font_large.render("Pixel Jumper", True, (255, 255, 255))
        start_text = font_medium.render("Press ENTER to Start", True, (200, 200, 200))
        exit_text = font_small.render("Press ESC to Exit", True, (150, 150, 150))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 120))
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))
        screen.blit(
            exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 50)
        )
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()


# --- 結算畫面 ---
def show_game_over(max_distance, total_time, high_scores):
    while True:
        screen.fill((20, 20, 20))
        over_text = font_large.render("Game Over", True, (255, 100, 100))
        score_text = font_medium.render(
            f"Distance: {max_distance} m", True, (255, 255, 255)
        )
        time_text = font_medium.render(
            f"Time: {int(total_time)} s", True, (200, 200, 200)
        )
        restart_text = font_small.render("Press R to Restart", True, (180, 180, 180))
        highscore_title = font_medium.render("Top 5 Scores:", True, (255, 255, 0))

        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, 100))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 180))
        screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, 230))
        screen.blit(
            highscore_title, (WIDTH // 2 - highscore_title.get_width() // 2, 290)
        )

        for i, score in enumerate(high_scores):
            entry = font_small.render(f"{i+1}. {score} m", True, (255, 255, 255))
            screen.blit(entry, (WIDTH // 2 - entry.get_width() // 2, 330 + i * 30))

        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 520))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return  # 回主迴圈重新開始
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()


def start_game():
    global tiles, obstacles, player, all_sprites, scroll, start_time, max_distance, generated_chunks
    tiles, obstacles = generate_chunk(0)
    ensure_starting_platforms(tiles)  # 確保前五格有平台可站
    player = Player(100, 100)
    all_sprites = pygame.sprite.Group(player)
    scroll = [0, 0]
    start_time = time.time()
    max_distance = 0
    generated_chunks = 1


# --- 暫停選單 ---
def show_pause_menu():
    # 繪製半透明遮罩
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # 黑色 + 透明度
    screen.blit(overlay, (0, 0))

    # 顯示暫停文字與說明
    pause_box = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
    pygame.draw.rect(screen, (50, 50, 50), pause_box)
    pygame.draw.rect(screen, (200, 200, 200), pause_box, 3)

    title = font_large.render("Paused", True, WHITE)
    resume_text = font_small.render("Press ESC to Resume", True, (200, 200, 200))
    quit_text = font_small.render("Press Q to Quit", True, (200, 200, 200))

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 80))
    screen.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 40))

    pygame.display.flip()


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


# --- 遊戲初始化 ---
def start_game():
    global tiles, obstacles, player, all_sprites, scroll, start_time, max_distance, generated_chunks
    tiles, obstacles = generate_chunk(0)
    ensure_starting_platforms(tiles)  # 確保前五格有平台可站
    player = Player(100, 100)
    all_sprites = pygame.sprite.Group(player)
    scroll = [0, 0]
    start_time = time.time()
    max_distance = 0
    generated_chunks = 1


# --- 執行主選單 ---
show_main_menu()
start_game()

# --- 遊戲狀態 ---
paused = False
game_over = False
running = True

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

    if paused:
        show_pause_menu()

    if not game_over and not paused:
        all_sprites.update(tiles, scroll, obstacles)

        # 生成新地形（當角色接近邊界）
        right_edge = (generated_chunks * 30 - 10) * TILE_SIZE
        if player.rect.right > right_edge:
            new_tiles, new_obs = generate_chunk(generated_chunks * 30)
            tiles += new_tiles
            obstacles += new_obs
            generated_chunks += 1

        # 計算距離分數
        distance = player.rect.x // TILE_SIZE
        max_distance = max(max_distance, distance)

        if player.rect.top > HEIGHT or player.health <= 0:
            game_over = True
            end_time = time.time()
            total_time = end_time - start_time
            save_high_score(max_distance)
            show_game_over(max_distance, total_time, load_high_scores())

        for tile in tiles:
            shifted_tile = tile.move(scroll[0], scroll[1])
            pygame.draw.rect(screen, GREEN, shifted_tile)

        for obs in obstacles:
            shifted_obs = obs.rect.move(scroll[0], scroll[1])
            screen.blit(obs.image, shifted_obs)

        screen.blit(
            player.image, (player.rect.x + scroll[0], player.rect.y + scroll[1])
        )

        for i in range(player.health):
            pygame.draw.rect(screen, RED, (10 + i * 30, 10, 20, 20))

        draw_text(f"Distance: {max_distance} m", 520, 10)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
