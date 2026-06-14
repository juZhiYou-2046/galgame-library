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

## Step 3: 评分评价系统（1-10 评分 + 评论）

**日期:** 2026-06-14

**目标:** 支持用户对游戏打分和写评论，自动计算平均分。

### 后端改动

- **修改 `app/models.py`:** 新增 `Review` 模型（id, game_id FK, rating 1-10, content, reviewer, created_at），Game 模型新增 reviews relationship 并设置级联删除
- **修改 `app/schemas.py`:** 新增 `ReviewCreate` 和 `ReviewResponse` schema
- **新增 `app/services/review_service.py`:** 评价 CRUD 逻辑，创建/删除评价时自动用 SQL AVG 重算游戏平均分
- **新增 `app/api/reviews.py`:** 评价 API 路由（GET 列表、POST 创建、DELETE 删除），路径 `/api/games/{id}/reviews`
- **修改 `app/main.py`:** 注册 reviews router
- **修改 `app/database.py`:** init_db 导入 Review 模型

### 前端改动

- **新增 `frontend/src/api/reviews.js`:** 评价 API 调用封装
- **修改 `frontend/src/views/GameDetail.vue`:** 新增评价区域（评价列表 + 写评价表单），评价列表展示评分、评论者、时间、内容；提交评价后自动刷新游戏平均分

### 技术决策

- Game.rating 由评价自动计算（SQL AVG），用户不可在表单中直接修改
- 评价使用整数评分（1-10），Game.rating 存储浮点平均分

## Step 4: 批量导入导出（JSON/CSV）

**日期:** 2026-06-14

**目标:** 支持游戏库数据的完整导入和导出。

### 后端改动

- **新增 `app/api/import_export.py`:** 导入导出 API 路由
  - `GET /api/games/export?format=json|csv` 导出所有游戏数据
  - `POST /api/games/import` 接受 JSON/CSV 文件上传，支持 skip/update 冲突策略
  - JSON 导出为格式化数组，CSV 使用 utf-8-sig 编码（兼容 Excel）
- **修改 `app/main.py`:** 注册 import_export router

### 前端改动

- **新增 `frontend/src/api/importExport.js`:** 导入导出 API 调用封装
- **修改 `frontend/src/views/GameList.vue`:** 页头新增"导出"下拉按钮（JSON/CSV）和"导入"按钮；导入对话框支持文件选择、冲突策略选择（跳过/覆盖）和结果统计展示

### 技术决策

- 导出字段排除 id/cover/created_at/updated_at 等自动生成字段
- CSV 使用 utf-8-sig BOM 确保 Excel 正确识别中文
- 冲突策略基于游戏标题判断是否已存在

## Step 5: 搜索增强（模糊多字段搜索）

**日期:** 2026-06-14

**目标:** 提供更智能的搜索体验，支持多条件组合和排序。

### 后端改动

- **修改 `app/services/game_service.py`:** list_games 新增参数：sort_by/sort_order（排序）、min_rating/max_rating（评分范围）、start_date/end_date（日期范围）；新增 tags 字段到搜索范围；新增 get_developers() 方法（去重开发商列表）和 highlight_text() 工具方法
- **修改 `app/api/games.py`:** 列表 API 新增排序、评分范围、日期范围查询参数；新增 `GET /api/games/developers` 开发商自动补全接口

### 前端改动

- **修改 `frontend/src/views/GameList.vue`:** 新增可折叠的高级搜索面板，包含排序选择（更新时间/创建时间/评分/标题）、评分范围滑块、日期范围选择器；所有筛选条件联动查询

### 技术决策

- 排序使用白名单字段映射，防止 SQL 注入
- 日期过滤使用字符串比较（release_date 为 String 类型，格式 YYYY-MM-DD）
- 高级搜索面板默认折叠，不影响基础搜索的简洁体验

## Step 6: 基础设施修复

**日期:** 2026-06-14

**目标:** 补齐项目的工程化基础设施。

### 6a: CORS 白名单 + 环境变量

- **重写 `app/config.py`:** 使用 pydantic-settings 从环境变量读取所有配置（DATABASE_URL, CORS_ORIGINS, DATA_DIR, COVERS_DIR 等）
- **修改 `app/main.py`:** CORS 改为从 config 读取白名单列表；新增前端静态文件托管（SPA 路由回退）
- **修改 `app/database.py`:** DATABASE_URL 从 settings 读取
- **修改 `app/api/games.py`:** 封面上传使用 settings 配置
- **新增 `.env.example`:** 列出所有环境变量及默认值

### 6b: Alembic 数据库迁移

- **新增 `alembic.ini`:** 标准 alembic 配置
- **新增 `alembic/env.py`:** 导入 Base.metadata 和所有模型
- **新增 `alembic/versions/001_initial.py`:** 初始迁移脚本（games + reviews 表）

### 6c: Docker

- **新增 `Dockerfile`:** 多阶段构建（Node 构建前端 + Python 运行后端）
- **新增 `docker-compose.yml`:** 单服务配置，volume 挂载 data/ 和 covers/

### 6d: 测试

- **新增 `tests/conftest.py`:** 测试 fixtures（内存 SQLite、TestClient、示例数据）
- **新增 `tests/test_api_games.py`:** 11 个 Game CRUD API 测试
- **新增 `tests/test_api_tags.py`:** 4 个 Tags API 测试
- **新增 `tests/test_api_reviews.py`:** 7 个 Reviews API 测试
- **新增 `tests/test_api_import_export.py`:** 7 个导入导出测试
- **新增 `tests/test_api_scanner.py`:** 6 个 Scanner API 测试
- **新增 `frontend/vitest.config.js`:** vitest 配置
- **新增 `frontend/src/views/__tests__/GameList.test.js`:** 列表页组件基础测试
- **修改 `frontend/package.json`:** 添加 vitest、@vue/test-utils、jsdom 依赖
- **修改 `requirements.txt`:** 添加 pytest、httpx 依赖
- **总计: 35 个后端测试全部通过**

### 桌面打包 + CI/CD

- **新增 `desktop_launcher.py`:** 桌面启动器（启动 uvicorn + 自动打开浏览器）
- **新增 `build_desktop.py`:** 本地 PyInstaller 打包脚本
- **新增 `build_desktop_ci.py`:** CI 环境打包脚本
- **新增 `.github/workflows/build-desktop.yml`:** GitHub Actions CI/CD，在 macOS 和 Windows runner 上构建安装包，推送 tag 时自动创建 Release
- **修改 `app/main.py`:** FastAPI 托管前端静态文件（SPA 路由回退）
- **修改 `.gitignore`:** 新增构建产物、测试缓存等忽略规则

### Bug 修复

- **修改 `app/main.py`:** 修复 PyInstaller 打包后找不到前端文件的 bug（`_find_frontend_dist()` 新增 `sys._MEIPASS` 路径查找）
- **修改 `build_desktop_ci.py`:** 增强错误处理和版本号解析，缩短 PyInstaller hidden-import 列表
