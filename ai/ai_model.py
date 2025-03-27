import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
from game.settings import *
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
    def __init__(self, device):
        self.state_size = 8  # 玩家位置(x,y)、速度(x,y)、是否在地面、跳跃次数、最近平台距离、最近障碍物距离
        self.action_size = 4  # 左移、右移、跳跃、不動
        self.memory = deque(maxlen=10000)
        self.gamma = 0.95    # 折扣因子
        self.epsilon = 1.0   # 探索率
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.device = device
        self.model = DQN(self.state_size, self.action_size).to(self.device)
        self.target_model = DQN(self.state_size, self.action_size).to(self.device)
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
            state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.model(state)
            return q_values.argmax().item()
    
    def train(self, batch_size):
        if len(self.memory) < batch_size:
            return
        
        minibatch = random.sample(self.memory, batch_size)
        states = torch.FloatTensor(np.array([data[0] for data in minibatch])).to(self.device)
        actions = torch.LongTensor([data[1] for data in minibatch]).to(self.device)
        rewards = torch.FloatTensor([data[2] for data in minibatch]).to(self.device)
        next_states = torch.FloatTensor([data[3] for data in minibatch]).to(self.device)
        dones = torch.FloatTensor([data[4] for data in minibatch]).to(self.device)
        
        current_q_values = self.model(states).gather(1, actions.unsqueeze(1))
        next_q_values = self.target_model(next_states).max(1)[0].detach().to(self.device)
        target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
        
        loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def train_episodes(self, env, episodes=2000, max_steps=1000, batch_size=64, reward_version="default"):
        best_avg_reward = -float("inf")
        reward_history = []

        save_dir = f"checkpoints/{reward_version}"
        os.makedirs(save_dir, exist_ok=True)

        for ep in range(episodes):
            state = env.reset()
            total_reward = 0

            for step in range(max_steps):
                action = self.get_action(state)
                next_state, reward, done, _ = env.step(action)

                self.remember(state, action, reward, next_state, done)
                self.train(batch_size)  # 單步訓練
                state = next_state
                total_reward += reward

                if done:
                    break

            reward_history.append(total_reward)

            if (ep + 1) % 10 == 0:
                self.update_target_model()

            avg_reward = np.mean(reward_history[-50:])
            print(f"[EP {ep}] Reward: {total_reward:.2f} | Avg50: {avg_reward:.2f} | Epsilon: {self.epsilon:.3f}")

            if avg_reward > best_avg_reward:
                best_avg_reward = avg_reward
                self.save_model(ep, avg_reward, reward_version)

    
    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) 
            
    def save_model(self, episode, avg_reward, reward_version):
        save_dir = f"checkpoints/{reward_version}"
        os.makedirs(save_dir, exist_ok=True)
        torch.save(self.model.state_dict(), f"{save_dir}/best_ep{episode}_reward{avg_reward:.2f}.pth")
        print(f"✅ 模型已儲存：{save_dir}/best_ep{episode}_reward{avg_reward:.2f}.pth")

    def load_model(self, path):
        if os.path.exists(path):
            self.model.load_state_dict(torch.load(path, map_location=self.device))
            self.target_model.load_state_dict(self.model.state_dict())
            print(f"✅ 已載入模型：{path}")
        else:
            print(f"❌ 模型路徑不存在：{path}")
