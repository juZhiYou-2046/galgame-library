"""游戏 CRUD API 路由"""

import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.config import ALLOWED_EXTENSIONS, COVERS_DIR, COVERS_URL
from app.database import get_db
from app.schemas import GameCreate, GameListResponse, GameResponse, GameUpdate
from app.services.game_service import GameService

router = APIRouter(prefix="/api/games", tags=["游戏管理"])


@router.get("", response_model=GameListResponse)
def list_games(
    search: Optional[str] = Query(None, description="搜索关键词"),
    developer: Optional[str] = Query(None, description="按开发商筛选"),
    tag: Optional[str] = Query(None, description="按标签筛选"),
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(100, ge=1, le=500, description="每页条数"),
    db: Session = Depends(get_db),
):
    """获取游戏列表，支持搜索和筛选"""
    items, total = GameService.list_games(
        db, search=search, developer=developer, tag=tag, skip=skip, limit=limit
    )
    return GameListResponse(total=total, items=items)


@router.get("/{game_id}", response_model=GameResponse)
def get_game(game_id: int, db: Session = Depends(get_db)):
    """获取单个游戏详情"""
    game = GameService.get_game(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
    return game


@router.post("", response_model=GameResponse, status_code=201)
def create_game(data: GameCreate, db: Session = Depends(get_db)):
    """添加新游戏"""
    return GameService.create_game(db, data)


@router.put("/{game_id}", response_model=GameResponse)
def update_game(game_id: int, data: GameUpdate, db: Session = Depends(get_db)):
    """更新游戏信息"""
    game = GameService.update_game(db, game_id, data)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
    return game


@router.delete("/{game_id}", status_code=204)
def delete_game(game_id: int, db: Session = Depends(get_db)):
    """删除游戏"""
    success = GameService.delete_game(db, game_id)
    if not success:
        raise HTTPException(status_code=404, detail="游戏不存在")


@router.post("/{game_id}/cover", response_model=GameResponse)
def upload_cover(game_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """上传游戏封面图片"""
    game = GameService.get_game(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")

    # 验证文件类型
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {ext}，仅支持 {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # 生成唯一文件名，避免覆盖
    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path = COVERS_DIR / unique_name

    # 保存文件
    content = file.read()
    save_path.write_bytes(content)

    # 删除旧封面文件
    if game.cover:
        old_path = COVERS_DIR / Path(game.cover).name
        if old_path.exists():
            try:
                old_path.unlink()
            except OSError:
                pass

    # 更新数据库中的封面路径
    cover_url = f"{COVERS_URL}/{unique_name}"
    game.cover = cover_url
    db.commit()
    db.refresh(game)

    return game