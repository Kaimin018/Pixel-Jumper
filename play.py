# play.py
import argparse
from game.main import main
from game.gamestate import GameState

def run_ai_mode():
    """AI模式运行游戏"""
    state = GameState()
    state.initialize()
    return state

def run_player_mode():
    """玩家模式运行游戏"""
    main()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='运行平台游戏')
    parser.add_argument('--mode', choices=['player', 'ai'], default='player',
                      help='选择游戏模式：player（玩家模式）或 ai（AI模式）')
    args = parser.parse_args()
    
    if args.mode == 'player':
        run_player_mode()
    else:
        state = run_ai_mode()
        print("AI模式已启动，游戏状态已准备就绪")
