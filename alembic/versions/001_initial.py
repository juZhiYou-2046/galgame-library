"""初始迁移 - 创建 games 和 reviews 表

Revision ID: 001_initial
Revises:
Create Date: 2026-06-14
"""

from alembic import op
import sqlalchemy as sa

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "games",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False, comment="游戏名称"),
        sa.Column("original_title", sa.String(length=255), server_default="", comment="原名 / 日文名"),
        sa.Column("developer", sa.String(length=255), server_default="", comment="开发商 / 品牌"),
        sa.Column("release_date", sa.String(length=50), server_default="", comment="发行日期"),
        sa.Column("tags", sa.Text(), server_default="", comment="标签（逗号分隔）"),
        sa.Column("description", sa.Text(), server_default="", comment="简介"),
        sa.Column("rating", sa.Float(), server_default="0.0", comment="评分"),
        sa.Column("cover", sa.String(length=512), server_default="", comment="封面图片路径"),
        sa.Column("folder_path", sa.String(length=1024), server_default="", comment="游戏文件夹路径"),
        sa.Column("created_at", sa.DateTime(), nullable=True, comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(), nullable=True, comment="更新时间"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_games_id"), "games", ["id"], unique=False)
    op.create_index(op.f("ix_games_title"), "games", ["title"], unique=False)

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False, comment="关联游戏"),
        sa.Column("rating", sa.Integer(), nullable=False, comment="评分 1-10"),
        sa.Column("content", sa.Text(), server_default="", comment="评论内容"),
        sa.Column("reviewer", sa.String(length=100), server_default="", comment="评论者"),
        sa.Column("created_at", sa.DateTime(), nullable=True, comment="评论时间"),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reviews_id"), "reviews", ["id"], unique=False)
    op.create_index(op.f("ix_reviews_game_id"), "reviews", ["game_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_reviews_game_id"), table_name="reviews")
    op.drop_index(op.f("ix_reviews_id"), table_name="reviews")
    op.drop_table("reviews")
    op.drop_index(op.f("ix_games_title"), table_name="games")
    op.drop_index(op.f("ix_games_id"), table_name="games")
    op.drop_table("games")
