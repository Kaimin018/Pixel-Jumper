import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
from game.settings import *

class DQN(nn.Module):
    def __init__(self, input_size, output_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, output_size)
        
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

class GameAI:
    def __init__(self):
        self.state_size = 8  # 玩家位置(x,y)、速度(x,y)、是否在地面、跳跃次数、最近平台距离、最近障碍物距离
        self.action_size = 3  # 左移、右移、跳跃
        self.memory = deque(maxlen=10000)
        self.gamma = 0.95    # 折扣因子
        self.epsilon = 1.0   # 探索率
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = DQN(self.state_size, self.action_size)
        self.target_model = DQN(self.state_size, self.action_size)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        
    def get_state(self, player, tiles, obstacles):
        # 获取最近平台的距离
        nearest_platform = float('inf')
        for tile in tiles:
            if tile.rect.top > player.rect.bottom:  # 只考虑玩家下方的平台
                dist = abs(tile.rect.centerx - player.rect.centerx)
                nearest_platform = min(nearest_platform, dist)
        
        # 获取最近障碍物的距离
        nearest_obstacle = float('inf')
        for obs in obstacles:
            if obs.rect.top > player.rect.bottom:  # 只考虑玩家前方的障碍物
                dist = abs(obs.rect.centerx - player.rect.centerx)
                nearest_obstacle = min(nearest_obstacle, dist)
        
        state = np.array([
            player.rect.x / WIDTH,  # 归一化位置
            player.rect.y / HEIGHT,
            player.vel_y / 10.0,    # 归一化速度
            1.0 if player.on_ground else 0.0,
            player.jump_count / player.max_jump_count,
            nearest_platform / WIDTH if nearest_platform != float('inf') else 1.0,
            nearest_obstacle / WIDTH if nearest_obstacle != float('inf') else 1.0,
            player.health / player.max_health
        ])
        return state
    
    def get_action(self, state):
        if random.random() < self.epsilon:
            return random.randrange(self.action_size)
        
        with torch.no_grad():
            state = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.model(state)
            return q_values.argmax().item()
    
    def train(self, batch_size):
        if len(self.memory) < batch_size:
            return
        
        minibatch = random.sample(self.memory, batch_size)
        states = torch.FloatTensor([data[0] for data in minibatch])
        actions = torch.LongTensor([data[1] for data in minibatch])
        rewards = torch.FloatTensor([data[2] for data in minibatch])
        next_states = torch.FloatTensor([data[3] for data in minibatch])
        dones = torch.FloatTensor([data[4] for data in minibatch])
        
        current_q_values = self.model(states).gather(1, actions.unsqueeze(1))
        next_q_values = self.target_model(next_states).max(1)[0].detach()
        target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
        
        loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) 
        
    def load(self, path):
        if os.path.exists(path):
            self.model.load_state_dict(torch.load(path))
            self.target_model.load_state_dict(self.model.state_dict())
            print(f"✅ 已載入模型：{path}")
        else:
            print(f"❌ 模型路徑不存在：{path}")
