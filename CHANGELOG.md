## [v0.3.1] - 2025-03-27
feat(ai): 支援 device 傳遞與視窗穩定性處理

- GameAI 類別改為接受外部 device（支援 CUDA / CPU 切換）
- 修正所有 tensor 操作，確保訓練過程不發生 device mismatch 錯誤
- 使用 np.array(...) 解決建立 tensor 時的效率警告
- get_action() 中加入 .to(device) 避免 CPU/GPU 衝突
- load model 時加入 map_location，確保跨設備載入穩定
- env.render() 中加入 pygame.event.pump()，避免 PyGame 視窗無回應


## v0.2.0 - 開發中
- feat: 地形生成邏輯提升為可支持多層與隨機變化
- feat: 補血機制與血量上限系統初版完成

## [v0.2.3] - 2025-03-23
fix: use GameState.generated_chunks instead of local variable

Previously, terrain generation used a separate global `generated_chunks` counter,
which desynchronized from the actual GameState and caused missing tiles in later chunks.
This change ensures chunk tracking is fully tied to GameState.

BREAKING CHANGE: Removed global `generated_chunks`, replaced all references with `state.generated_chunks`.


## [v0.2.2] - 2025-03-23

### ✨ Features
- feat: introduce GameState class to encapsulate global game variables
- feat: enable R key to restart game instantly from game over screen
- feat: implement developer debug mode (via secret key input)
- feat: exclude debug scores from highscore leaderboard
- feat: convert highscore storage to JSON format with score, time, and mode
- feat: highlight key actions in menu with draw_key_highlight_line()
- feat: allow pausing game with ESC and displaying semi-transparent overlay
- feat: show player health with border + filled hearts (max health mechanic)

### 🛠 Improvements
- refactor: replace global variables with GameState encapsulation
- refactor: modularize draw_game_screen and game loop logic
- refactor: enhance level generation functions and prevent overlapping obstacles
- refactor: reorganize code into ui.py, level.py, entities.py for clarity
- ui: improve main menu layout and help screen with Unicode arrow keys
- ui: show debug message when debug score is not saved

### 🐞 Bug Fixes
- fix: player could stand on obstacles (obstacles treated as platforms)
- fix: game crashes on restart due to uninitialized max_distance
- fix: prevent jump-reset bug when jumping while falling
- fix: restart from game over no longer returns to wrong screen state

### ⚠ Breaking Changes
- change: highscore.txt is deprecated, now using highscores.json


## [v0.2.1] - 2025-03-22

### ✨ Features
- feat: Add instant restart option (press `R` on Game Over screen)
- Rebuilt procedural level generation using `Tile` and `Obstacle` sprite architecture
- Introduced dynamic platform width/height based on difficulty
- Added floating platforms and stair-like structures for varied terrain

### 🛠 Improvements
- Prevented score from being saved to leaderboard when Debug Mode is active
- Show in-game message when score is excluded due to Debug Mode
- Implemented `occupied_tiles` system to avoid overlaps between terrain and obstacles
- Refactored platform generation into modular functions (`add_base_platform`, `add_stairs`, `add_floating_platforms`)
- Replaced legacy 2D `level[][]` array with sprite groups (`tiles`, `obstacles`)
- Improved obstacle placement logic to avoid placing them on walkable tiles

### 🐞 Bug Fixes
- Fixed issue where player could stand on obstacles due to overlap with tile rects

---

## [v0.1.0] - 2025-03-22

### ✨ Features
- feat: Implemented player movement, jump, and double jump
- feat: Randomly generate platforms and basic obstacles
- feat: Pause / Game Over / Restart mechanics
- feat: Health system and life loss handling
- feat: Background music & basic SFX support
- feat: High score saving and top 5 leaderboard
- feat: Key bindings: `ESC` to pause, `Q` to quit, `R` to restart
- chore: Added `.gitignore`

---

## [v0.0.3] - 2025-03-22

### ✨ Features
- Added different background music per game state

---

## [v0.0.2] - 2025-03-21

### ✨ Features
- Added Main Menu, Game Over screen, Pause Menu

---

## [v0.0.1] - 2025-03-21

### ✨ Features
- Initial version: implemented player jump and basic platform collisions