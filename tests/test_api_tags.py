"""标签 API 测试"""


def test_list_tags(client, sample_game):
    """测试获取标签列表"""
    response = client.get("/api/tags")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # sample_game 有标签 "催泪,恋爱,校园"
    tag_names = [t["name"] for t in data]
    assert "催泪" in tag_names
    assert "恋爱" in tag_names


def test_tag_counts(client, sample_game):
    """测试标签计数"""
    # 再创建一个有相同标签的游戏
    client.post("/api/games", json={"title": "AIR", "tags": "催泪,恋爱"})

    response = client.get("/api/tags")
    data = response.json()
    tag_map = {t["name"]: t["count"] for t in data}
    assert tag_map.get("催泪", 0) >= 2
    assert tag_map.get("恋爱", 0) >= 2


def test_tag_suggestions(client, sample_game):
    """测试标签自动补全"""
    response = client.get("/api/tags/suggestions", params={"q": "催"})
    assert response.status_code == 200
    data = response.json()
    assert "催泪" in data


def test_tag_suggestions_empty(client, sample_game):
    """测试空查询的标签建议"""
    response = client.get("/api/tags/suggestions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3  # sample_game 有 3 个标签
