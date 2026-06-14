"""评价 API 测试"""


def test_create_review(client, sample_game):
    """测试创建评价"""
    game_id = sample_game["id"]
    response = client.post(f"/api/games/{game_id}/reviews", json={
        "rating": 9,
        "content": "神作，催泪弹十足",
        "reviewer": "测试用户",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 9
    assert data["content"] == "神作，催泪弹十足"


def test_create_review_updates_rating(client, sample_game):
    """测试创建评价后自动更新游戏平均分"""
    game_id = sample_game["id"]

    # 添加两个评价
    client.post(f"/api/games/{game_id}/reviews", json={"rating": 8, "content": "好评"})
    client.post(f"/api/games/{game_id}/reviews", json={"rating": 10, "content": "神作"})

    # 检查游戏平均分
    response = client.get(f"/api/games/{game_id}")
    data = response.json()
    assert data["rating"] == 9.0  # (8+10)/2


def test_list_reviews(client, sample_game):
    """测试获取评价列表"""
    game_id = sample_game["id"]

    # 创建评价
    client.post(f"/api/games/{game_id}/reviews", json={"rating": 8, "content": "评价1"})
    client.post(f"/api/games/{game_id}/reviews", json={"rating": 9, "content": "评价2"})

    response = client.get(f"/api/games/{game_id}/reviews")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_delete_review(client, sample_game):
    """测试删除评价"""
    game_id = sample_game["id"]

    # 创建评价
    create_response = client.post(f"/api/games/{game_id}/reviews", json={
        "rating": 8,
        "content": "要删除的评价",
    })
    review_id = create_response.json()["id"]

    # 删除评价
    response = client.delete(f"/api/games/{game_id}/reviews/{review_id}")
    assert response.status_code == 204

    # 验证已删除
    response = client.get(f"/api/games/{game_id}/reviews")
    assert len(response.json()) == 0


def test_delete_review_updates_rating(client, sample_game):
    """测试删除评价后重新计算平均分"""
    game_id = sample_game["id"]

    r1 = client.post(f"/api/games/{game_id}/reviews", json={"rating": 6}).json()
    client.post(f"/api/games/{game_id}/reviews", json={"rating": 10})

    # 删除低分评价
    client.delete(f"/api/games/{game_id}/reviews/{r1['id']}")

    response = client.get(f"/api/games/{game_id}")
    assert response.json()["rating"] == 10.0


def test_create_review_game_not_found(client):
    """测试为不存在的游戏创建评价"""
    response = client.post("/api/games/99999/reviews", json={
        "rating": 8,
        "content": "test",
    })
    assert response.status_code == 404


def test_review_rating_validation(client, sample_game):
    """测试评分范围验证"""
    game_id = sample_game["id"]

    # 评分超过 10
    response = client.post(f"/api/games/{game_id}/reviews", json={"rating": 11})
    assert response.status_code == 422

    # 评分低于 1
    response = client.post(f"/api/games/{game_id}/reviews", json={"rating": 0})
    assert response.status_code == 422
