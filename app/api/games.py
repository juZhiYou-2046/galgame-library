"""游戏 CRUD API 路由"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

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