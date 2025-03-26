import pygame
from game.settings import *
from game.entities import Player
from game.level import generate_chunk, ensure_starting_platforms

class GameState:
    def __init__(self):
        # 初始化pygame
        if not pygame.get_init():
            pygame.init()
            
        self.tiles = None
        self.obstacles = None
        self.player = None
        self.all_sprites = None
        self.scroll = [0, 0]
        self.start_time = 0
        self.max_distance = 0
        self.generated_chunks = 0
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.paused = False
        self.game_over = False
        
    def initialize(self):
        """初始化游戏状态"""
        self.tiles, self.obstacles = generate_chunk(0)
        ensure_starting_platforms(self.tiles)
        self.player = Player(100, 100)
        self.all_sprites = pygame.sprite.Group(self.player)
        self.scroll = [0, 0]
        self.start_time = pygame.time.get_ticks()
        self.max_distance = 0
        self.generated_chunks = 1
        self.paused = False
        self.game_over = False
        
    def get_state(self):
        """获取当前游戏状态，供AI使用"""
        return {
            'player_pos': (self.player.rect.x, self.player.rect.y),
            'player_health': self.player.health,
            'max_distance': self.max_distance,
            'current_chunk': self.generated_chunks,
            'scroll': self.scroll,
            'obstacles': [(obs.rect.x, obs.rect.y) for obs in self.obstacles],
            'tiles': [(tile.rect.x, tile.rect.y) for tile in self.tiles]
        }
        
    def update(self):
        """更新游戏状态"""
        if not self.paused and not self.game_over:
            self.all_sprites.update(self.tiles, self.scroll, self.obstacles)
            
            # 生成新地形
            right_edge = (self.generated_chunks * 30 - 10) * TILE_SIZE
            if self.player.rect.right > right_edge:
                new_tiles, new_obs = generate_chunk(self.generated_chunks * 30)
                self.tiles.add(*new_tiles)
                self.obstacles.add(*new_obs)
                self.generated_chunks += 1
                
            # 更新最大距离
            distance = self.player.rect.x // TILE_SIZE
            self.max_distance = max(self.max_distance, distance)
            
            # 检查游戏结束条件
            if self.player.rect.top > HEIGHT or self.player.health <= 0:
                self.game_over = True
                
    def draw(self):
        """绘制游戏画面"""
        if self.screen:
            self.screen.fill(WHITE)
            
            # 绘制地形
            for tile in self.tiles:
                shifted_tile = tile.rect.move(self.scroll[0], self.scroll[1])
                pygame.draw.rect(self.screen, GREEN, shifted_tile)
                
            # 绘制障碍物
            for obs in self.obstacles:
                shifted_obs = obs.rect.move(self.scroll[0], self.scroll[1])
                self.screen.blit(obs.image, shifted_obs)
                
            # 绘制玩家
            self.screen.blit(self.player.image, 
                           (self.player.rect.x + self.scroll[0], 
                            self.player.rect.y + self.scroll[1]))
            
            # 绘制UI
            self._draw_ui()
            
    def _draw_ui(self):
        """绘制UI元素"""
        # 绘制血量
        for i in range(self.player.max_health):
            x = 10 + i * 30
            y = 10
            pygame.draw.rect(self.screen, GRAY, (x, y, 20, 20), 2)
            if i < self.player.health:
                pygame.draw.rect(self.screen, RED, (x + 2, y + 2, 16, 16))
                
        # 绘制距离
        from common.ui import draw_text
        draw_text(f"Distance: {self.max_distance} m", WIDTH - 250, 10, BLACK)
