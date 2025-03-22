## v0.2.0 - 開發中
- feat: 地形生成邏輯提升為可支持多層與隨機變化
- feat: 補血機制與血量上限系統初版完成

## [v0.2.1] - 2025-03-22

### 🛠 Improvements
- Prevent scores from being recorded to the leaderboard when Debug Mode is active.
- Added in-game message to indicate when a score is not saved due to Debug Mode.

### ✨ Features
- Rebuilt procedural level generation system using `Tile` and `Obstacle` sprite-based architecture.
- Added dynamic platform width and height variation based on difficulty level.
- Introduced floating platforms and stair-like structures to enrich terrain diversity.

### 🛠 Improvements
- Implemented `occupied_tiles` tracking system to prevent overlapping between platforms, stairs, and obstacles.
- Refactored all tile generation functions (`add_base_platform`, `add_floating_platforms`, `add_stairs`) for modularity and consistency.
- Improved obstacle placement logic to ensure obstacles are not placed at walkable platform level.
- Removed outdated `level[][]` array-based tile structure in favor of full sprite group management.

### 🐞 Bug Fixes
- Fixed issue where player could stand on obstacles due to overlapping tile placement.

## [v0.1.0] - 2025-03-22
- feat: 實作角色移動、跳躍、雙跳邏輯
- feat: 隨機生成平台與初步障礙（刺）
- feat: 遊戲暫停 / 結束 / 重新開始功能
- feat: 角色死亡與生命值
- feat: 背景音樂與音效初步整合
- feat: 高分儲存、排行榜顯示
- feat: ESC 暫停、Q 離開、R 重新開始控制鍵位
- chore: 新增 .gitignore

## [v0.0.3] - 2025-03-22
- 加入不同背景音樂

## [v0.0.2] - 2025-03-21
- 加入主畫面、結算畫面、暫停等

## [v0.0.1] - 初始版本
- 完成角色跳躍與平台判定