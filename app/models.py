"""SQLAlchemy 数据模型"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True, comment="游戏名称")
    original_title = Column(String(255), default="", comment="原名 / 日文名")
    developer = Column(String(255), default="", comment="开发商 / 品牌")
    release_date = Column(String(50), default="", comment="发行日期")
    tags = Column(Text, default="", comment="标签（逗号分隔）")
    description = Column(Text, default="", comment="简介")
    rating = Column(Float, default=0.0, comment="评分")
    cover = Column(String(512), default="", comment="封面图片路径")
    folder_path = Column(String(1024), default="", comment="游戏文件夹路径")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def __repr__(self):
        return f"<Game(id={self.id}, title='{self.title}')>"