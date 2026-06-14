"""评价 API 路由"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ReviewCreate, ReviewResponse
from app.services.review_service import ReviewService

router = APIRouter(prefix="/api/games/{game_id}/reviews", tags=["评价"])


@router.get("", response_model=list[ReviewResponse])
def list_reviews(game_id: int, db: Session = Depends(get_db)):
    """获取某游戏的所有评价"""
    return ReviewService.list_reviews(db, game_id)


@router.post("", response_model=ReviewResponse, status_code=201)
def create_review(game_id: int, data: ReviewCreate, db: Session = Depends(get_db)):
    """创建评价"""
    review = ReviewService.create_review(db, game_id, data)
    if not review:
        raise HTTPException(status_code=404, detail="游戏不存在")
    return review


@router.delete("/{review_id}", status_code=204)
def delete_review(game_id: int, review_id: int, db: Session = Depends(get_db)):
    """删除评价"""
    success = ReviewService.delete_review(db, game_id, review_id)
    if not success:
        raise HTTPException(status_code=404, detail="评价不存在")
