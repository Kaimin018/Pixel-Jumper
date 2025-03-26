import pygame
import numpy as np
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.settings import WIDTH, HEIGHT
import gym
from gym import spaces
from game.gamestate import GameState

class PixelJumperEnv(gym.Env):
    def __init__(self):
        super(PixelJumperEnv, self).__init__()

        # 初始化遊戲
        self.game = GameState()
        self.game.initialize()

        # 定義動作空間 (0 = 不動，1 = 左，2 = 右，3 = 跳)
        self.action_space = spaces.Discrete(4)
        self.last_x = 0

        # 定義觀察空間（8個特徵）
        self.observation_space = spaces.Box(
            low=np.array([0, 0, -1, 0, 0, 0, 0, 0], dtype=np.float32),
            high=np.array([1, 1, 1, 1, 1, 1, 1, 1], dtype=np.float32),
            dtype=np.float32
        )

    def reset(self):
        self.game.initialize()
        self.last_x = self.game.player.rect.x
        obs = self._get_obs()
        return obs

    def step(self, action):
        # 執行動作
        if action == 1:  # 左移
            self.game.player.rect.x -= 5
        elif action == 2:  # 右移
            self.game.player.rect.x += 5
        elif action == 3:  # 跳躍
            if self.game.player.jump_count < self.game.player.max_jump_count:
                self.game.player.vel_y = -15
                self.game.player.jump_count += 1

        # 更新遊戲狀態
        self.game.update()

        # 獲取觀察和獎勵
        obs = self._get_obs()
        reward = self._get_reward()
        done = self.game.game_over
        info = {
            'distance': self.game.max_distance,
            'health': self.game.player.health
        }

        return obs, reward, done, info

    def _get_obs(self):
        # 獲取最近平台和障礙物的距離
        nearest_platform = float('inf')
        for tile in self.game.tiles:
            if tile.rect.top > self.game.player.rect.bottom:
                dist = abs(tile.rect.centerx - self.game.player.rect.centerx)
                nearest_platform = min(nearest_platform, dist)

        nearest_obstacle = float('inf')
        for obs in self.game.obstacles:
            if obs.rect.top > self.game.player.rect.bottom:
                dist = abs(obs.rect.centerx - self.game.player.rect.centerx)
                nearest_obstacle = min(nearest_obstacle, dist)

        # 構建觀察向量
        obs = np.array([
            self.game.player.rect.x / WIDTH,  # 歸一化位置
            self.game.player.rect.y / HEIGHT,
            self.game.player.vel_y / 10.0,    # 歸一化速度
            1.0 if self.game.player.on_ground else 0.0,
            self.game.player.jump_count / self.game.player.max_jump_count,
            nearest_platform / WIDTH if nearest_platform != float('inf') else 1.0,
            nearest_obstacle / WIDTH if nearest_obstacle != float('inf') else 1.0,
            self.game.player.health / self.game.player.max_health
        ], dtype=np.float32)
        return obs

    def _get_reward(self):
        # 計算水平位移差作為前進獎勵
        current_x = self.game.player.rect.x
        delta_x = current_x - self.last_x
        self.last_x = current_x

        reward = max(delta_x * 0.08, 0)  # 每往右移一格給 0.1 分，倒退不給分

        if not self.game.player.on_ground:
            reward -= 0.01  # 空中太久就扣分（防止亂跳）
        
        reward -= 0.05  # 每步小小扣分，逼它更快學會前進
        
        # 死亡懲罰
        if self.game.game_over:
            reward = -10
            
        return reward


    def render(self, mode="human"):
        if self.game.screen:
            self.game.draw()
            pygame.display.flip()
            pygame.event.pump()

    def close(self):
        pygame.quit()
