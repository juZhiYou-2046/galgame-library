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
