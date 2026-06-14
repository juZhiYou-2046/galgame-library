"""FastAPI 应用入口"""

import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import games, reviews, scanner, tags
from app.config import COVERS_DIR
from app.database import init_db

app = FastAPI(
    title="Galgame Library",
    description="本地 Galgame 游戏库管理 API",
    version="1.0.0",
)

# CORS 配置（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """应用启动时初始化数据库"""
    init_db()


# 静态文件路由（封面图片）
if COVERS_DIR.is_dir():
    app.mount("/covers", StaticFiles(directory=str(COVERS_DIR)), name="covers")


# 注册路由
app.include_router(games.router)
app.include_router(reviews.router)
app.include_router(scanner.router)
app.include_router(tags.router)


@app.get("/")
def root():
    """API 根路径"""
    return {
        "message": "Galgame Library API",
        "docs": "/docs",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)