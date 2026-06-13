# galgame-library

本地 Galgame 游戏库管理工具 —— FastAPI 后端 + Vue 3 前端。

## 功能

- **游戏管理**：添加、编辑、删除本地的 galgame 游戏记录
- **信息展示与搜索**：查看游戏列表、详情，支持按名称、会社、标签等筛选
- **本地扫描**：扫描本地文件夹中的游戏资源
- **封面管理**：支持游戏封面图片上传与展示

## 快速启动

### 后端

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

打开浏览器访问 `http://localhost:3000`（前端）或 `http://localhost:8000/docs`（API 文档）。

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/games` | 获取游戏列表（支持搜索和筛选） |
| POST | `/api/games` | 添加新游戏 |
| GET | `/api/games/{id}` | 获取游戏详情 |
| PUT | `/api/games/{id}` | 更新游戏信息 |
| DELETE | `/api/games/{id}` | 删除游戏 |
| POST | `/api/games/{id}/cover` | 上传游戏封面 |
| POST | `/api/scan` | 扫描本地目录 |

## 项目结构

```
galgame-library/
├── app/                    # FastAPI 后端
│   ├── main.py             # 应用入口
│   ├── config.py           # 配置
│   ├── database.py         # 数据库
│   ├── models.py           # 数据模型
│   ├── schemas.py          # Pydantic 模型
│   ├── api/
│   │   ├── games.py        # 游戏 CRUD API
│   │   └── scanner.py      # 扫描 API
│   └── services/
│       ├── scanner.py      # 本地扫描逻辑
│       └── game_service.py # 业务逻辑
├── frontend/               # Vue 3 前端
│   └── src/
│       ├── views/          # 页面组件
│       ├── api/            # API 调用
│       └── router/         # 路由配置
├── data/                   # SQLite 数据库
├── covers/                 # 游戏封面图片
├── requirements.txt
└── README.md
```