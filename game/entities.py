import pygame
from game.settings import *

_dflag_ = False
typed_code = ""

# --- 障礙物類別 ---
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(GRAY)
        self.rect = self.image.get_rect(topleft=(x, y))

# --- 地形類別 ---
class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(GREEN)
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
        self.max_health = 3
        self.health = self.max_health
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
            if not _dflag_:
                self.health -= 1
            self.rect.y = -100  # 從畫面上方掉下來
            self.vel_y = 0

        # 碰撞障礙物（加上無敵時間）
        if not _dflag_ and not self.invincible:
            for obs in obstacles:
                if self.rect.colliderect(obs.rect):
                    print("碰到障礙物！", obs.rect.topleft)
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
            if hasattr(tile, "type") and tile.type == "obstacle":
                continue  # 忽略障礙物
            if self.rect.colliderect(tile.rect):
                if dy > 0:  # 玩家往下掉，碰到地板
                    self.rect.bottom = tile.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jump_count = 0  # 落地時重置跳躍次數
                elif dy < 0:
                    self.rect.top = tile.rect.bottom
                    self.vel_y = 0
                elif dx > 0:
                    self.rect.right = tile.rect.left
                elif dx < 0:
                    self.rect.left = tile.rect.right
