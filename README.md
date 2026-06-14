# Galgame Library

本地 Galgame 游戏库管理工具 —— FastAPI 后端 + Vue 3 前端。

## 下载使用（普通用户）

从 [GitHub Releases](https://github.com/juZhiYou-2046/galgame-library/releases) 下载对应平台的安装包：

| 平台 | 文件 | 使用方式 |
|------|------|----------|
| macOS | `GalgameLibrary-v*-macOS.zip` | 解压后双击 `启动.command` |
| Windows | `GalgameLibrary-v*-Windows.zip` | 解压后双击 `启动.bat` |

启动后浏览器自动打开 `http://localhost:8000`，无需安装 Python 或 Node.js。

## 功能

- **游戏管理**：添加、编辑、删除本地 galgame 游戏记录
- **评价系统**：1-10 打分 + 评论，自动计算平均分
- **标签系统**：标签云、精确匹配筛选、自动补全
- **高级搜索**：关键词、评分范围、发行日期、排序
- **本地扫描**：扫描文件夹中的游戏文件（支持 .exe/.iso/.dmg/.pkg/.app 等格式）
- **封面管理**：游戏封面图片上传与展示
- **导入导出**：JSON/CSV 批量导入导出

## 开发者启动

### Docker（推荐）

```bash
docker compose up -d
```

打开浏览器访问 `http://localhost:8000`。

### 本地运行

后端：

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

打开浏览器访问 `http://localhost:3000`（前端）或 `http://localhost:8000/docs`（API 文档）。

### 桌面模式（单命令）

先构建前端，再一键启动服务 + 自动打开浏览器：

```bash
cd frontend && npm install && npm run build && cd ..
python desktop_launcher.py
```

### 运行测试

```bash
# 后端
pytest tests/ -v

# 前端
cd frontend && npx vitest run
```

### 数据库迁移

```bash
alembic upgrade head
```

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/games` | 游戏列表（搜索、筛选、排序） |
| POST | `/api/games` | 添加游戏 |
| GET | `/api/games/{id}` | 游戏详情 |
| PUT | `/api/games/{id}` | 更新游戏 |
| DELETE | `/api/games/{id}` | 删除游戏 |
| POST | `/api/games/{id}/cover` | 上传封面 |
| POST | `/api/games/{id}/reviews` | 添加评价 |
| GET | `/api/games/{id}/reviews` | 评价列表 |
| DELETE | `/api/games/{id}/reviews/{rid}` | 删除评价 |
| GET | `/api/games/export` | 导出 JSON/CSV |
| POST | `/api/games/import` | 批量导入 |
| GET | `/api/games/developers` | 开发商列表 |
| GET | `/api/tags` | 标签列表及计数 |
| POST | `/api/scan` | 扫描本地目录 |

## 环境变量

复制 `.env.example` 为 `.env` 可自定义配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | 数据库连接 | `sqlite:///./data/galgame.db` |
| `CORS_ORIGINS` | 跨域白名单 | `http://localhost:3000,...` |
| `DATA_DIR` | 数据目录 | `./data` |
| `COVERS_DIR` | 封面目录 | `./covers` |

## 项目结构

```
galgame-library/
├── app/                    # FastAPI 后端
│   ├── main.py             # 应用入口 + 前端静态文件托管
│   ├── config.py           # 配置（pydantic-settings）
│   ├── database.py         # 数据库
│   ├── models.py           # 数据模型（Game + Review）
│   ├── schemas.py          # Pydantic 请求/响应模型
│   ├── api/                # API 路由
│   └── services/           # 业务逻辑
├── frontend/               # Vue 3 前端
│   └── src/
│       ├── views/          # 页面组件
│       ├── api/            # API 调用
│       └── router/         # 路由配置
├── alembic/                # 数据库迁移
├── tests/                  # 后端测试（pytest）
├── data/                   # SQLite 数据库
├── covers/                 # 游戏封面图片
├── Dockerfile              # 多阶段构建
├── docker-compose.yml      # Docker Compose
├── .github/workflows/      # CI/CD（桌面安装包构建）
├── requirements.txt
└── README.md
```