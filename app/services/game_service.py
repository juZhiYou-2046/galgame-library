"""游戏业务逻辑"""

import os
import re
from typing import Optional

from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.models import Game
from app.schemas import GameCreate, GameUpdate

# 允许的排序字段
SORT_FIELDS = {
    "updated_at": Game.updated_at,
    "created_at": Game.created_at,
    "rating": Game.rating,
    "title": Game.title,
}


class GameService:
    """游戏 CRUD 业务逻辑"""

    @staticmethod
    def list_games(
        db: Session,
        search: Optional[str] = None,
        developer: Optional[str] = None,
        tag: Optional[str] = None,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Game], int]:
        """查询游戏列表，支持搜索、筛选和排序"""
        query = db.query(Game)

        if search:
            keyword = f"%{search}%"
            query = query.filter(
                or_(
                    Game.title.ilike(keyword),
                    Game.original_title.ilike(keyword),
                    Game.developer.ilike(keyword),
                    Game.description.ilike(keyword),
                    Game.tags.ilike(keyword),
                )
            )

        if developer:
            query = query.filter(Game.developer.ilike(f"%{developer}%"))

        if tag:
            # 精确标签匹配
            padded = "," + func.coalesce(Game.tags, "") + ","
            query = query.filter(padded.ilike(f"%,{tag},%"))

        # 评分范围过滤
        if min_rating is not None:
            query = query.filter(Game.rating >= min_rating)
        if max_rating is not None:
            query = query.filter(Game.rating <= max_rating)

        # 日期范围过滤（字符串比较，格式 YYYY-MM-DD）
        if start_date:
            query = query.filter(Game.release_date >= start_date)
        if end_date:
            query = query.filter(Game.release_date <= end_date)

        total = query.count()

        # 排序
        sort_column = SORT_FIELDS.get(sort_by, Game.updated_at)
        if sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        items = query.offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def get_developers(db: Session, query: str = "") -> list[str]:
        """获取开发商列表（去重），支持关键词过滤"""
        developers = (
            db.query(Game.developer)
            .filter(Game.developer != "")
            .distinct()
            .order_by(Game.developer)
            .all()
        )
        result = [d[0] for d in developers]
        if query:
            query_lower = query.lower()
            result = [d for d in result if query_lower in d.lower()]
        return result

    @staticmethod
    def highlight_text(text: str, keyword: str) -> str:
        """在文本中高亮关键词"""
        if not keyword or not text:
            return text
        pattern = re.compile(f"({re.escape(keyword)})", re.IGNORECASE)
        return pattern.sub(r"<mark>\1</mark>", text)

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