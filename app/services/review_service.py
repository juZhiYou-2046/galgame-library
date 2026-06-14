"""评价业务逻辑"""

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Game, Review
from app.schemas import ReviewCreate


class ReviewService:
    """评价 CRUD 业务逻辑"""

    @staticmethod
    def list_reviews(db: Session, game_id: int) -> list[Review]:
        """获取某游戏的所有评价，按时间倒序"""
        return (
            db.query(Review)
            .filter(Review.game_id == game_id)
            .order_by(Review.created_at.desc())
            .all()
        )

    @staticmethod
    def create_review(db: Session, game_id: int, data: ReviewCreate) -> Optional[Review]:
        """创建评价，并自动更新游戏平均分"""
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            return None

        review = Review(game_id=game_id, **data.model_dump())
        db.add(review)
        db.flush()

        # 重新计算平均分
        ReviewService._update_game_rating(db, game_id)

        db.commit()
        db.refresh(review)
        return review

    @staticmethod
    def delete_review(db: Session, game_id: int, review_id: int) -> bool:
        """删除评价，并重新计算游戏平均分"""
        review = (
            db.query(Review)
            .filter(Review.id == review_id, Review.game_id == game_id)
            .first()
        )
        if not review:
            return False

        db.delete(review)
        db.flush()

        # 重新计算平均分
        ReviewService._update_game_rating(db, game_id)

        db.commit()
        return True

    @staticmethod
    def _update_game_rating(db: Session, game_id: int):
        """重新计算游戏的平均分"""
        avg = (
            db.query(func.avg(Review.rating))
            .filter(Review.game_id == game_id)
            .scalar()
        )
        game = db.query(Game).filter(Game.id == game_id).first()
        if game:
            game.rating = round(avg, 1) if avg else 0.0

    @staticmethod
    def get_review_count(db: Session, game_id: int) -> int:
        """获取某游戏的评价数量"""
        return db.query(Review).filter(Review.game_id == game_id).count()
