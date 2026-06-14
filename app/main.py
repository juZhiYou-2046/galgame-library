"""FastAPI 应用入口"""

from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import games, import_export, reviews, scanner, tags
from app.config import settings
from app.database import init_db

app = FastAPI(
    title="Galgame Library",
    description="本地 Galgame 游戏库管理 API",
    version="1.0.0",
)

# CORS 配置（从环境变量读取白名单）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """应用启动时初始化数据库"""
    init_db()


# 静态文件路由（封面图片）
covers_path = settings.covers_path
if covers_path.is_dir():
    app.mount("/covers", StaticFiles(directory=str(covers_path)), name="covers")


# 注册路由（import_export 必须在 games 之前，避免 /export 被 /{game_id} 捕获）
app.include_router(import_export.router)
app.include_router(games.router)
app.include_router(reviews.router)
app.include_router(scanner.router)
app.include_router(tags.router)


# 查找前端构建产物目录
def _find_frontend_dist() -> Path | None:
    """查找前端 dist 目录（兼容多种部署方式）"""
    candidates = [
        Path(__file__).resolve().parent.parent / "frontend" / "dist",
        Path(__file__).resolve().parent / "frontend_dist",
        Path.cwd() / "frontend" / "dist",
    ]
    for c in candidates:
        if c.is_dir() and (c / "index.html").exists():
            return c
    return None


_frontend_dist = _find_frontend_dist()

if _frontend_dist:
    # 挂载静态资源目录
    app.mount("/assets", StaticFiles(directory=str(_frontend_dist / "assets")), name="frontend_assets")

    # SPA 路由回退：所有非 API、非静态文件的请求返回 index.html
    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """为 SPA 提供路由回退，所有前端路由都返回 index.html"""
        # 尝试返回静态文件
        file_path = _frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        # 回退到 index.html（Vue Router 处理）
        return FileResponse(str(_frontend_dist / "index.html"))
else:
    @app.get("/")
    def root():
        """API 根路径（开发模式，前端独立运行）"""
        return {
            "message": "Galgame Library API",
            "docs": "/docs",
            "version": "1.0.0",
        }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)