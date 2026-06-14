"""标签业务逻辑"""

from collections import Counter

from sqlalchemy.orm import Session

from app.models import Game


class TagService:
    """标签聚合与查询"""

    @staticmethod
    def get_all_tags_with_counts(db: Session) -> list[dict]:
        """从所有游戏的 tags 字段聚合标签，返回标签名和计数"""
        games = db.query(Game).all()
        counter = Counter()
        for game in games:
            if game.tags:
                for tag in game.tags.split(","):
                    tag = tag.strip()
                    if tag:
                        counter[tag] += 1
        # 按计数降序排列
        return [{"name": name, "count": count} for name, count in counter.most_common()]

    @staticmethod
    def get_tag_suggestions(db: Session, query: str = "") -> list[str]:
        """获取标签自动补全建议"""
        tags = TagService.get_all_tags_with_counts(db)
        if query:
            query_lower = query.lower()
            tags = [t for t in tags if query_lower in t["name"].lower()]
        return [t["name"] for t in tags]
