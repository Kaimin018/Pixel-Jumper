import pygame
import numpy as np
import torch
import os
import time
import sys
import signal
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.env import PixelJumperEnv
from ai.ai_model import GameAI
from game.settings import *

def save_training_data(episode, ai, episode_rewards, episode_steps, avg_reward):
    """保存训练数据"""
    # 保存模型
    torch.save(ai.model.state_dict(), f'models/dqn_model_episode_{episode+1}.pth')
    
    # 保存训练统计信息
    training_data = {
        'episode': episode + 1,
        'episode_rewards': episode_rewards,
        'episode_steps': episode_steps,
        'avg_reward': avg_reward,
        'epsilon': ai.epsilon,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open('models/training_data.json', 'w') as f:
        json.dump(training_data, f)

def train_ai():
    # 检查是否有GPU可用
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")
    
    # 初始化环境
    env = PixelJumperEnv()
    
    # 初始化AI
    ai = GameAI()
    ai.model.to(device)
    ai.target_model.to(device)
    
    # 嘗試載入已訓練模型和訓練數據（如果存在）
    model_path = "models/dqn_model_final.pth"
    training_data_path = "models/training_data.json"
    
    if os.path.exists(model_path):
        ai.load(model_path)
        if os.path.exists(training_data_path):
            with open(training_data_path, 'r') as f:
                training_data = json.load(f)
                episode_rewards = training_data['episode_rewards']
                episode_steps = training_data['episode_steps']
                start_episode = training_data['episode']
                print(f"從第 {start_episode} 回合繼續訓練")
    else:
        episode_rewards = []
        episode_steps = []
        start_episode = 0
    
    # 训练参数
    batch_size = 64
    episodes = 1000
    max_steps = 1000
    target_update_frequency = 50
    render_frequency = 5
    training_frequency = 2
    
    # 创建保存模型的目录
    if not os.path.exists('models'):
        os.makedirs('models')
    
    # 记录训练统计信息
    start_time = time.time()
    
    def signal_handler(signum, frame):
        print("\n檢測到中斷信號，正在保存訓練數據...")
        avg_reward = np.mean(episode_rewards[-100:]) if len(episode_rewards) >= 100 else np.mean(episode_rewards)
        save_training_data(current_episode, ai, episode_rewards, episode_steps, avg_reward)
        print("訓練數據已保存！")
        env.close()
        sys.exit(0)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    current_episode = start_episode
    for episode in range(start_episode, episodes):
        current_episode = episode
        state = env.reset()
        total_reward = 0
        steps = 0
        
        while steps < max_steps:
            # 选择动作
            action = ai.get_action(state)
            
            # 执行动作
            next_state, reward, done, info = env.step(action)
            
            # 存储经验
            ai.remember(state, action, reward, next_state, done)
            
            # 训练
            if steps % training_frequency == 0:
                ai.train(batch_size)
            
            # 更新目标网络
            if steps % target_update_frequency == 0:
                ai.update_target_model()
            
            # 渲染
            if steps % render_frequency == 0:
                env.render()
            
            state = next_state
            total_reward += reward
            steps += 1
            
            if done:
                break
            
            # 控制帧率
            pygame.time.Clock().tick(120)
        
        # 记录统计信息
        episode_rewards.append(total_reward)
        episode_steps.append(steps)
        
        # 每10回合保存一次训练数据
        if (episode + 1) % 10 == 0:
            avg_reward = np.mean(episode_rewards[-100:]) if len(episode_rewards) >= 100 else np.mean(episode_rewards)
            save_training_data(episode, ai, episode_rewards, episode_steps, avg_reward)
        
        # 计算平均奖励和步数
        avg_reward = np.mean(episode_rewards[-100:]) if len(episode_rewards) >= 100 else np.mean(episode_rewards)
        avg_steps = np.mean(episode_steps[-100:]) if len(episode_steps) >= 100 else np.mean(episode_steps)
        
        # 计算训练时间
        elapsed_time = time.time() - start_time
        episodes_per_hour = (episode + 1) / (elapsed_time / 3600)
        
        print(f"回合: {episode + 1}/{episodes}, "
              f"总奖励: {total_reward:.2f}, "
              f"步数: {steps}, "
              f"探索率: {ai.epsilon:.2f}, "
              f"平均奖励: {avg_reward:.2f}, "
              f"平均步数: {avg_steps:.1f}, "
              f"训练速度: {episodes_per_hour:.1f}回合/小时")
        
        # 如果平均奖励足够好，提前结束训练
        if avg_reward > 100 and len(episode_rewards) >= 100:
            print("训练完成！AI表现足够好。")
            break
    
    # 保存最终模型和训练数据
    avg_reward = np.mean(episode_rewards[-100:]) if len(episode_rewards) >= 100 else np.mean(episode_rewards)
    save_training_data(current_episode, ai, episode_rewards, episode_steps, avg_reward)
    env.close()

if __name__ == "__main__":
    train_ai() 