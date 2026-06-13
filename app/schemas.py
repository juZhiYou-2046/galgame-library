"""Pydantic 数据模型（请求/响应）"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GameCreate(BaseModel):
    """创建游戏请求"""
    title: str = Field(..., min_length=1, max_length=255, description="游戏名称")
    original_title: Optional[str] = ""
    developer: Optional[str] = ""
    release_date: Optional[str] = ""
    tags: Optional[str] = ""
    description: Optional[str] = ""
    rating: Optional[float] = 0.0
    folder_path: Optional[str] = ""


class GameUpdate(BaseModel):
    """更新游戏请求"""
    title: Optional[str] = None
    original_title: Optional[str] = None
    developer: Optional[str] = None
    release_date: Optional[str] = None
    tags: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    folder_path: Optional[str] = None


class GameResponse(BaseModel):
    """游戏响应模型"""
    id: int
    title: str
    original_title: str
    developer: str
    release_date: str
    tags: str
    description: str
    rating: float
    cover: str
    folder_path: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GameListResponse(BaseModel):
    """游戏列表响应"""
    total: int
    items: list[GameResponse]