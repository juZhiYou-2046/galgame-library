"""游戏 API 测试"""


def test_create_game(client):
    """测试创建游戏"""
    response = client.post("/api/games", json={
        "title": "AIR",
        "developer": "Key",
        "tags": "催泪,恋爱",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "AIR"
    assert data["developer"] == "Key"
    assert data["tags"] == "催泪,恋爱"
    assert data["id"] is not None


def test_create_game_missing_title(client):
    """测试创建游戏 - 缺少标题"""
    response = client.post("/api/games", json={"developer": "Key"})
    assert response.status_code == 422


def test_get_game(client, sample_game):
    """测试获取游戏详情"""
    game_id = sample_game["id"]
    response = client.get(f"/api/games/{game_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "CLANNAD"


def test_get_game_not_found(client):
    """测试获取不存在的游戏"""
    response = client.get("/api/games/99999")
    assert response.status_code == 404


def test_list_games(client, sample_game):
    """测试游戏列表"""
    response = client.get("/api/games")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


def test_search_games(client, sample_game):
    """测试搜索游戏"""
    response = client.get("/api/games", params={"search": "CLANNAD"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(g["title"] == "CLANNAD" for g in data["items"])


def test_search_by_tag(client, sample_game):
    """测试按标签搜索"""
    response = client.get("/api/games", params={"tag": "催泪"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


def test_update_game(client, sample_game):
    """测试更新游戏"""
    game_id = sample_game["id"]
    response = client.put(f"/api/games/{game_id}", json={
        "description": "更新后的简介",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "更新后的简介"


def test_delete_game(client, sample_game):
    """测试删除游戏"""
    game_id = sample_game["id"]
    response = client.delete(f"/api/games/{game_id}")
    assert response.status_code == 204

    # 验证已删除
    response = client.get(f"/api/games/{game_id}")
    assert response.status_code == 404


def test_sort_by_rating(client):
    """测试按评分排序"""
    # 创建两个游戏，不同评分
    client.post("/api/games", json={"title": "Game A", "rating": 9.0})
    client.post("/api/games", json={"title": "Game B", "rating": 5.0})

    response = client.get("/api/games", params={"sort_by": "rating", "sort_order": "desc"})
    assert response.status_code == 200
    data = response.json()
    ratings = [g["rating"] for g in data["items"]]
    assert ratings == sorted(ratings, reverse=True)


def test_developers_autocomplete(client, sample_game):
    """测试开发商自动补全"""
    response = client.get("/api/games/developers", params={"q": "Key"})
    assert response.status_code == 200
    data = response.json()
    assert "Key" in data
