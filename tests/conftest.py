"""测试配置和 fixtures"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Game, Review  # noqa: F401

# 使用内存 SQLite 测试数据库
TEST_DATABASE_URL = "sqlite:///./data/test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """测试用的数据库会话覆盖"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """每个测试前创建表，测试后清理"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """FastAPI 测试客户端"""
    return TestClient(app)


@pytest.fixture
def db_session():
    """数据库会话 fixture"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_game(client):
    """创建一个示例游戏"""
    response = client.post("/api/games", json={
        "title": "CLANNAD",
        "original_title": "クラナド",
        "developer": "Key",
        "release_date": "2004-04-28",
        "tags": "催泪,恋爱,校园",
        "description": "Key 社经典催泪作品",
        "rating": 0.0,
        "folder_path": "/Games/CLANNAD",
    })
    return response.json()
