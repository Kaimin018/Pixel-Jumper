import pygame
import random
import time

# --- 初始化 ---
pygame.init()
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --- 音樂 ---
pygame.mixer.init()
try:
    pygame.mixer.music.load("CDMIxVintage.mp3")
    pygame.mixer.music.play(-1)
    print("音樂載入成功！")
except Exception as e:
    print("音樂載入失敗：", e)

pygame.mixer.music.set_volume(1.0)


# --- 顏色 ---
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLUE = (50, 50, 255)
RED = (200, 0, 0)
BLACK = (0, 0, 0)

# --- 字型 ---
font = pygame.font.SysFont(None, 48)


# --- 玩家類別 ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 40))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.on_ground = False
        self.health = 3

    def update(self, tiles, scroll):
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -5
        if keys[pygame.K_RIGHT]:
            dx = 5
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -15

        self.vel_y += 1  # gravity
        if self.vel_y > 10:
            self.vel_y = 10

        self.rect.x += dx
        self.collision(dx, 0, tiles)
        self.rect.y += self.vel_y
        self.on_ground = False
        self.collision(0, self.vel_y, tiles)

        scroll[0] = -(self.rect.x - WIDTH // 2)
        scroll[0] = min(0, scroll[0])
        scroll[0] = max(-(len(level_data[0]) * TILE_SIZE - WIDTH), scroll[0])

    def collision(self, dx, dy, tiles):
        for tile in tiles:
            if self.rect.colliderect(tile):
                if dy > 0:
                    self.rect.bottom = tile.top
                    self.vel_y = 0
                    self.on_ground = True
                elif dy < 0:
                    self.rect.top = tile.bottom
                    self.vel_y = 0
                elif dx > 0:
                    self.rect.right = tile.left
                elif dx < 0:
                    self.rect.left = tile.right


# --- 地圖生成 ---
def generate_level(cols, rows):
    level = [[0 for _ in range(cols)] for _ in range(rows)]
    y = rows - 3
    for x in range(0, cols, 3):
        y += random.choice([-1, 0, 1])
        y = max(2, min(rows - 2, y))
        for i in range(2):
            if x + i < cols:
                level[y][x + i] = 1
    return level


# --- 建立地圖與平台 ---
def create_tiles(level):
    tiles = []
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            if tile == 1:
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                tiles.append(rect)
    return tiles


# --- 顯示文字 ---
def draw_text(text, x, y, color=BLACK):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


# --- 主選單函數 ---
def show_main_menu():
    while True:
        screen.fill(WHITE)
        draw_text("PLATFORMER GAME", WIDTH // 2 - 160, HEIGHT // 2 - 100)
        draw_text("Press ENTER to Start", WIDTH // 2 - 180, HEIGHT // 2 - 20)
        draw_text("Press ESC to Exit", WIDTH // 2 - 160, HEIGHT // 2 + 40)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()


# --- 遊戲初始化 ---
def start_game():
    global level_data, tiles, player, all_sprites, scroll, start_time
    level_data = generate_level(50, 15)
    tiles = create_tiles(level_data)
    player = Player(100, 100)
    all_sprites = pygame.sprite.Group(player)
    scroll = [0, 0]
    start_time = time.time()


# --- 執行主選單 ---
show_main_menu()
start_game()

# --- 遊戲狀態 ---
running = True
game_over = False

while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            game_over = False
            start_game()

    if not game_over:
        all_sprites.update(tiles, scroll)

        if player.rect.top > HEIGHT:
            player.health -= 1
            if player.health > 0:
                player.rect.topleft = (100, 100)
                player.vel_y = 0
            else:
                game_over = True
                end_time = time.time()
                total_time = end_time - start_time

        for tile in tiles:
            shifted_tile = tile.move(scroll[0], scroll[1])
            pygame.draw.rect(screen, GREEN, shifted_tile)

        screen.blit(
            player.image, (player.rect.x + scroll[0], player.rect.y + scroll[1])
        )

        for i in range(player.health):
            pygame.draw.rect(screen, RED, (10 + i * 30, 10, 20, 20))

    else:
        draw_text("GAME OVER", WIDTH // 2 - 120, HEIGHT // 2 - 60)
        draw_text(f"Time Survived: {int(total_time)}s", WIDTH // 2 - 160, HEIGHT // 2)
        draw_text("Press R to Restart", WIDTH // 2 - 160, HEIGHT // 2 + 60)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
