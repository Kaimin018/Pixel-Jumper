from ai_model import GameAI
from env import PixelJumperEnv
import torch
import time

# 初始化
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
env = PixelJumperEnv()
ai = GameAI(device)

# 載入最佳模型
ai.load("models/v3-platform-tune/best_model.pth")

state = env.reset()
total_reward = 0
done = False

while not done:
    env.render()  # 可選：顯示畫面
    time.sleep(1/60)   # 控制遊戲速度
    action = ai.get_action(state, force_exploit=True)  # 👈 禁用 epsilon，強制使用訓練結果
    state, reward, done, _ = env.step(action)
    total_reward += reward

print(f"🎉 AI 完成一局，總獎勵：{total_reward:.2f}")
env.close()
