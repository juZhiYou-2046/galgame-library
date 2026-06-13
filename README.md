# galgame-library

本地 Galgame 游戏库管理工具 —— 基于 FastAPI 的后端服务。

## 功能

- 🎮 **游戏管理**：添加、编辑、删除本地的 galgame 游戏记录
- 🔍 **信息展示与搜索**：查看游戏列表、详情，支持按名称、会社、标签等筛选
- 📁 **本地扫描**：扫描本地文件夹中的游戏资源
- 🖼️ **封面管理**：支持游戏封面图片上传与展示

## 快速启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --port 8000

# 打开浏览器访问
# http://localhost:8000/docs  — API 文档
# http://localhost:8000       — 主页
```

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/games` | 获取游戏列表（支持搜索和筛选） |
| POST | `/api/games` | 添加新游戏 |
| GET | `/api/games/{id}` | 获取游戏详情 |
| PUT | `/api/games/{id}` | 更新游戏信息 |
| DELETE | `/api/games/{id}` | 删除游戏 |
| POST | `/api/scan` | 扫描本地目录 |

## 项目结构

```
galgame-library/
├── app/
│   ├── main.py          # 应用入口
│   ├── config.py        # 配置
│   ├── database.py      # 数据库
│   ├── models.py        # 数据模型
│   ├── schemas.py       # Pydantic 模型
│   ├── api/
│   │   ├── games.py     # 游戏 CRUD API
│   │   └── scanner.py   # 扫描 API
│   └── services/
│       ├── scanner.py   # 本地扫描逻辑
│       └── game_service.py  # 业务逻辑
├── data/                # SQLite 数据库
├── covers/              # 游戏封面图片
├── requirements.txt
└── README.md
```