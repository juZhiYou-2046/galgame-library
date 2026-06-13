"""游戏业务逻辑"""

import os
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Game
from app.schemas import GameCreate, GameUpdate


class GameService:
    """游戏 CRUD 业务逻辑"""

    @staticmethod
    def list_games(
        db: Session,
        search: Optional[str] = None,
        developer: Optional[str] = None,
        tag: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Game], int]:
        """查询游戏列表，支持搜索和筛选"""
        query = db.query(Game)

        if search:
            keyword = f"%{search}%"
            query = query.filter(
                or_(
                    Game.title.ilike(keyword),
                    Game.original_title.ilike(keyword),
                    Game.developer.ilike(keyword),
                    Game.description.ilike(keyword),
                )
            )

        if developer:
            query = query.filter(Game.developer.ilike(f"%{developer}%"))

        if tag:
            query = query.filter(Game.tags.ilike(f"%{tag}%"))

        total = query.count()
        items = query.order_by(Game.updated_at.desc()).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def get_game(db: Session, game_id: int) -> Optional[Game]:
        """获取单个游戏详情"""
        return db.query(Game).filter(Game.id == game_id).first()

    @staticmethod
    def create_game(db: Session, data: GameCreate) -> Game:
        """创建游戏记录"""
        game = Game(**data.model_dump())
        db.add(game)
        db.commit()
        db.refresh(game)
        return game

    @staticmethod
    def update_game(db: Session, game_id: int, data: GameUpdate) -> Optional[Game]:
        """更新游戏记录"""
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(game, key, value)

        db.commit()
        db.refresh(game)
        return game

    @staticmethod
    def delete_game(db: Session, game_id: int) -> bool:
        """删除游戏记录"""
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            return False

        # 删除关联的封面文件
        if game.cover and os.path.exists(game.cover):
            try:
                os.remove(game.cover)
            except OSError:
                pass

        db.delete(game)
        db.commit()
        return True