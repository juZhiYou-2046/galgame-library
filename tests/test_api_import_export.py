"""导入导出 API 测试"""

import io
import json


def test_export_json(client, sample_game):
    """测试 JSON 导出"""
    response = client.get("/api/games/export", params={"format": "json"})
    assert response.status_code == 200
    data = json.loads(response.content)
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["title"] == "CLANNAD"


def test_export_csv(client, sample_game):
    """测试 CSV 导出"""
    response = client.get("/api/games/export", params={"format": "csv"})
    assert response.status_code == 200
    content = response.content.decode("utf-8-sig")
    assert "title" in content
    assert "CLANNAD" in content


def test_export_invalid_format(client):
    """测试无效导出格式"""
    response = client.get("/api/games/export", params={"format": "xml"})
    assert response.status_code == 400


def test_import_json(client, sample_game):
    """测试 JSON 导入"""
    import_data = json.dumps([
        {"title": "AIR", "developer": "Key", "tags": "催泪"},
        {"title": "Kanon", "developer": "Key", "tags": "恋爱"},
    ]).encode("utf-8")

    response = client.post(
        "/api/games/import",
        files={"file": ("games.json", io.BytesIO(import_data), "application/json")},
        data={"conflict_strategy": "skip"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 2
    assert data["skipped"] == 0


def test_import_skip_conflict(client, sample_game):
    """测试导入时跳过已存在的"""
    import_data = json.dumps([
        {"title": "CLANNAD", "developer": "Updated Key"},  # 已存在
        {"title": "New Game", "developer": "New Dev"},
    ]).encode("utf-8")

    response = client.post(
        "/api/games/import",
        files={"file": ("games.json", io.BytesIO(import_data), "application/json")},
        data={"conflict_strategy": "skip"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 1
    assert data["skipped"] == 1


def test_import_update_conflict(client, sample_game):
    """测试导入时覆盖已存在的"""
    import_data = json.dumps([
        {"title": "CLANNAD", "developer": "Updated Key"},
    ]).encode("utf-8")

    response = client.post(
        "/api/games/import",
        files={"file": ("games.json", io.BytesIO(import_data), "application/json")},
        data={"conflict_strategy": "update"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["updated"] == 1

    # 验证已更新
    game_id = sample_game["id"]
    response = client.get(f"/api/games/{game_id}")
    assert response.json()["developer"] == "Updated Key"


def test_import_csv(client):
    """测试 CSV 导入"""
    csv_content = "title,developer,tags\nRewrite,Key,奇幻\nLittle Busters,Key,校园"
    response = client.post(
        "/api/games/import",
        files={"file": ("games.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")},
        data={"conflict_strategy": "skip"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["created"] == 2
