"""扫描 API 测试"""

import os
import tempfile


def test_scan_directory(client):
    """测试扫描目录"""
    # 创建临时目录和测试文件
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试游戏文件
        open(os.path.join(tmpdir, "game.exe"), "w").close()
        open(os.path.join(tmpdir, "disk.iso"), "w").close()
        open(os.path.join(tmpdir, "readme.txt"), "w").close()  # 不应被识别

        response = client.post("/api/scan", json={
            "directory": tmpdir,
            "max_depth": 1,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["files_found"] == 2
        extensions = {item["extension"] for item in data["items"]}
        assert ".exe" in extensions
        assert ".iso" in extensions


def test_scan_macos_formats(client):
    """测试 macOS 格式扫描"""
    with tempfile.TemporaryDirectory() as tmpdir:
        open(os.path.join(tmpdir, "game.dmg"), "w").close()
        open(os.path.join(tmpdir, "game.pkg"), "w").close()
        open(os.path.join(tmpdir, "archive.zip"), "w").close()

        response = client.post("/api/scan", json={
            "directory": tmpdir,
            "max_depth": 1,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["files_found"] == 3


def test_scan_app_bundle(client):
    """测试 .app 应用包检测"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建 .app 目录
        app_dir = os.path.join(tmpdir, "GalGame.app")
        os.makedirs(app_dir)
        os.makedirs(os.path.join(app_dir, "Contents"))
        open(os.path.join(app_dir, "Contents", "Info.plist"), "w").close()

        response = client.post("/api/scan", json={
            "directory": tmpdir,
            "max_depth": 1,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["files_found"] == 1
        assert data["items"][0]["extension"] == ".app"
        assert data["items"][0]["is_bundle"] is True


def test_scan_nonexistent_directory(client):
    """测试扫描不存在的目录"""
    response = client.post("/api/scan", json={
        "directory": "/nonexistent/path/that/does/not/exist",
        "max_depth": 1,
    })
    assert response.status_code == 400


def test_scan_system_directory(client):
    """测试拒绝扫描系统目录"""
    response = client.post("/api/scan", json={
        "directory": "/System",
        "max_depth": 1,
    })
    assert response.status_code == 403


def test_scan_depth_limit(client):
    """测试扫描深度限制"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建深层嵌套结构
        deep_dir = os.path.join(tmpdir, "level1", "level2", "level3")
        os.makedirs(deep_dir)
        open(os.path.join(deep_dir, "deep.exe"), "w").close()
        open(os.path.join(tmpdir, "root.exe"), "w").close()

        response = client.post("/api/scan", json={
            "directory": tmpdir,
            "max_depth": 1,
        })
        data = response.json()
        # 只应找到根目录的 exe，深层的不应该找到
        assert data["files_found"] == 1
