"""标签 API 路由"""

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.tag_service import TagService

router = APIRouter(prefix="/api/tags", tags=["标签"])


@router.get("")
def list_tags(db: Session = Depends(get_db)):
    """获取所有标签及其计数"""
    return TagService.get_all_tags_with_counts(db)


@router.get("/suggestions")
def tag_suggestions(q: Optional[str] = "", db: Session = Depends(get_db)):
    """获取标签自动补全建议"""
    return TagService.get_tag_suggestions(db, q)
