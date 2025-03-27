import pygame
import numpy as np
import torch
import os
import time
import sys
import signal
import json
import csv
from datetime import datetime

# 添加專案根目錄到Python路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai.env import PixelJumperEnv
from ai.ai_model import GameAI
from game.settings import *


REWARD_VERSION = "v3-platform-tune"
model_dir = f"models/{REWARD_VERSION}"
os.makedirs(model_dir, exist_ok=True)


def save_training_data(episode, ai, episode_rewards, episode_steps, avg_reward, best_avg_reward, losses):
    """儲存訓練數據"""
    
    # 儲存模型
    torch.save(ai.model.state_dict(), f"{model_dir}/dqn_model_episode_{episode+1}.pth")
    
    # 儲存訓練統計資訊
    training_data = {
        'episode': episode + 1,
        'episode_rewards': episode_rewards,
        'episode_steps': episode_steps,
        "best_avg_reward": best_avg_reward,
        'avg_reward': avg_reward,
        'epsilon': ai.epsilon,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(f'{model_dir}/training_data.json', 'w') as f:
        json.dump(training_data, f)
    
    # 儲存CSV格式的訓練數據
    csv_filename = f"{model_dir}/training_history.csv"
    file_exists = os.path.exists(csv_filename) and os.path.getsize(csv_filename) > 0

    with open(f'{model_dir}/training_history.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            # 寫入表頭
            writer.writerow([
                'Episode', 'Reward', 'Steps', 'Epsilon', 
                'Avg_Reward', 'Avg_Steps', 'Avg_Loss', 'Timestamp'
            ])
        
        # 計算平均步數
        avg_steps = np.mean(episode_steps[-100:]) if len(episode_steps) >= 100 else np.mean(episode_steps)
        avg_loss = np.mean(losses[-100:]) if len(losses) >= 100 else (np.mean(losses) if losses else 0)
        
        # 寫入當前回合的數據
        writer.writerow([
            episode + 1,
            episode_rewards[-1],
            episode_steps[-1],
            ai.epsilon,            
            avg_reward,
            avg_steps,
            avg_loss,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])

def train_ai():
    # 檢查是否有GPU可用
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用設備: {device}")
    
    # 初始化環境
    env = PixelJumperEnv()
    
    # 初始化AI
    ai = GameAI(device=device)
    
    best_avg_reward = -float("inf")
    
    episode_rewards = []
    episode_steps = []
    losses = []
    start_episode = 0    

    if os.path.exists(f"{model_dir}/training_data.json"):
        with open(f"{model_dir}/training_data.json", "r") as f:
            data = json.load(f)
            best_avg_reward = data.get("best_avg_reward", -float("inf"))
            start_episode = data.get("episode", 0)
            episode_rewards = data.get("episode_rewards", [])
            episode_steps = data.get("episode_steps", [])
            print(f"➡️ 從第 {start_episode} 回合繼續訓練")
        
    
    # 訓練參數
    batch_size = 64
    episodes = 50000
    max_steps = 1000
    target_update_frequency = 50
    render_frequency = 5
    training_frequency = 2
    save_every_n_episodes  = 1000  # 每n步儲存一次模型
    
    model_path = f"{model_dir}/dqn_model_episode_{start_episode}.pth"
    if os.path.exists(model_path):
        ai.load(model_path)
        print(f"✅ 已載入模型參數：{model_path}")
    
    # 記錄訓練統計資訊
    start_time = time.time()
    
    def signal_handler(signum, frame):
        print("\n檢測到中斷信號，正在儲存訓練數據...")
        avg_reward = np.mean(episode_rewards[-100:]) if len(episode_rewards) >= 100 else np.mean(episode_rewards)
        save_training_data(current_episode, ai, episode_rewards, episode_steps, avg_reward, best_avg_reward, losses)
        print("訓練數據已儲存！")
        env.close()
        sys.exit(0)
    
    # 註冊信號處理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    current_episode = start_episode
    for episode in range(start_episode, episodes):
        current_episode = episode
        state = env.reset()
        total_reward = 0
        steps = 0
        
        while steps < max_steps:
            # 選擇動作
            action = ai.get_action(state)
            
            # 執行動作
            next_state, reward, done, info = env.step(action)
            
            # 儲存經驗
            ai.remember(state, action, reward, next_state, done)
            
            # 訓練
            if steps % training_frequency == 0:
                ai.train(batch_size)
            
            # 更新目標網路
            if steps % target_update_frequency == 0:
                ai.update_target_model()
            
            # 渲染
            if steps % render_frequency == 0:
                env.render()
            
            state = next_state
            total_reward += reward
            steps += 1
            loss = ai.train(batch_size)
            if loss is not None:
                losses.append(loss)
            
            if done:
                break
            
            # 控制幀率
            pygame.time.Clock().tick(120)
        
        # 記錄統計資訊
        episode_rewards.append(total_reward)
        episode_steps.append(steps)
        
        if (episode + 1) % save_every_n_episodes  == 0:
            avg_reward = np.mean(episode_rewards[-100:]) if len(episode_rewards) >= 100 else np.mean(episode_rewards)
            save_training_data(episode, ai, episode_rewards, episode_steps, avg_reward, best_avg_reward, losses)
        
        # 計算平均獎勵和步數
        avg_reward = np.mean(episode_rewards[-100:]) if len(episode_rewards) >= 100 else np.mean(episode_rewards)
        if avg_reward > best_avg_reward:
            best_avg_reward = avg_reward
            torch.save(ai.model.state_dict(), f"{model_dir}/best_model.pth")
            torch.save(ai.model.state_dict(), f"{model_dir}/best_model_ep{episode+1}_reward{avg_reward:.2f}.pth")
            print(f"✅ 新最佳模型! AvgReward = {avg_reward:.2f}，已儲存。")
        avg_steps = np.mean(episode_steps[-100:]) if len(episode_steps) >= 100 else np.mean(episode_steps)
        
        # 計算訓練時間
        elapsed_time = time.time() - start_time
        episodes_per_hour = (episode + 1) / (elapsed_time / 3600)
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"[{current_time}] 回合: {episode + 1}/{episodes}, "
              f"總獎勵: {total_reward:.2f}, "
              f"步數: {steps}, "
              f"探索率: {ai.epsilon:.2f}, "
              f"平均獎勵: {avg_reward:.2f}, "
              f"平均步數: {avg_steps:.1f}, "
              f"訓練速度: {episodes_per_hour:.1f}回合/小時")
        
        # 如果平均獎勵足夠好，提前結束訓練
        if avg_reward > 100 and len(episode_rewards) >= 100:
            print("訓練完成!AI表現足夠好。")
            break
    
    # 儲存最終模型和訓練數據
    avg_reward = np.mean(episode_rewards[-100:]) if len(episode_rewards) >= 100 else np.mean(episode_rewards)
    save_training_data(current_episode, ai, episode_rewards, episode_steps, avg_reward, best_avg_reward, losses)
    torch.save(ai.model.state_dict(), f"{model_dir}/dqn_model_final.pth")
    env.close()

if __name__ == "__main__":
    train_ai() 