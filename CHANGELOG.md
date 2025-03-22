## v0.2.0 - 開發中
- feat: 地形生成邏輯提升為可支持多層與隨機變化
- feat: 補血機制與血量上限系統初版完成

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