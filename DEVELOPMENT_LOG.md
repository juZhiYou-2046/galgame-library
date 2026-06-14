# 开发日志

## Step 1: 标签系统增强

**日期:** 2026-06-14

**目标:** 增强标签管理、展示和过滤功能，保持逗号分隔文本字段的设计。

### 后端改动

- **新增 `app/services/tag_service.py`:** 标签聚合服务，从所有游戏的 tags 字段解析并统计标签出现次数，支持自动补全建议
- **新增 `app/api/tags.py`:** 标签 API 路由，`GET /api/tags` 返回标签列表及计数，`GET /api/tags/suggestions?q=` 返回自动补全建议
- **修改 `app/main.py`:** 注册 tags router
- **修改 `app/services/game_service.py`:** 标签过滤从 ILIKE 子串匹配改为精确匹配（使用 `',' || tags || ','` LIKE 模式避免子串误匹配）

### 前端改动

- **新增 `frontend/src/api/tags.js`:** 标签 API 调用封装
- **新增 `frontend/src/views/TagCloud.vue`:** 标签云视图，展示所有标签及计数，字号根据使用频率变化，点击标签跳转到列表页筛选
- **修改 `frontend/src/views/GameList.vue`:** 列表中的标签改为可点击，点击后触发筛选；支持从 URL query 参数读取初始标签筛选
- **修改 `frontend/src/views/GameForm.vue`:** 标签输入改为 el-autocomplete，支持从已有标签中自动补全
- **修改 `frontend/src/router/index.js`:** 新增 `/tags` 路由
- **修改 `frontend/src/App.vue`:** 侧栏导航新增"标签管理"项

### 技术决策

- 保持逗号分隔文本存储而非新建标签表，降低改动复杂度
- 精确匹配通过 SQL 字符串拼接实现，兼容 SQLite 且无需全文索引

## Step 2: 扫描增强（macOS 格式支持）

**日期:** 2026-06-14

**目标:** 扩展文件扫描器，支持 macOS 常见游戏文件格式。

### 后端改动

- **修改 `app/config.py`:** 扩展 `GAME_FILE_EXTENSIONS` 新增 `.pkg`, `.dmg`, `.zip`, `.rar`, `.7z`；新增 `MACOS_APP_BUNDLE` 常量用于 .app 目录检测
- **修改 `app/services/scanner.py`:** 新增 .app 应用包检测（作为目录处理，计算内部文件大小）；新增 `_clean_title()` 方法清理文件名中的版本号等噪音；扫描时不再深入 .app 包内部

### 前端改动

- **修改 `frontend/src/views/ScannerView.vue`:** 扩展 `getFileIcon()` 支持新格式（.app 用 Monitor，.dmg 用 Coin，.pkg 用 Box，压缩包用 Files）；重写 `guessTitleFromPath()` 接受完整 item 对象，清理版本号标记并智能提取标题

### 技术决策

- .app 是目录而非文件，使用 `rglob` 计算包内文件大小
- 标题清理使用正则去除版本号、括号标记等噪音，提升自动识别准确率
