"""Galgame Library 桌面启动器

双击运行即可启动本地服务并打开浏览器。
用于 PyInstaller 打包成桌面应用。
"""

import os
import sys
import threading
import webbrowser
from pathlib import Path


def get_base_dir():
    """获取应用根目录（兼容 PyInstaller 打包后的路径）"""
    if getattr(sys, "frozen", False):
        # PyInstaller 打包后的可执行文件所在目录
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def ensure_dirs():
    """确保数据和封面目录存在"""
    base = get_base_dir()
    (base / "data").mkdir(parents=True, exist_ok=True)
    (base / "covers").mkdir(parents=True, exist_ok=True)


def open_browser(port: int, delay: float = 1.5):
    """延迟后打开浏览器"""
    import time
    time.sleep(delay)
    webbrowser.open(f"http://localhost:{port}")


def main():
    ensure_dirs()

    # 设置环境变量，让 config.py 使用可执行文件所在目录
    base_dir = get_base_dir()
    os.environ["DATA_DIR"] = str(base_dir / "data")
    os.environ["COVERS_DIR"] = str(base_dir / "covers")

    port = 8000
    host = "127.0.0.1"

    print(f"Galgame Library 正在启动...")
    print(f"访问地址: http://{host}:{port}")
    print(f"按 Ctrl+C 退出")

    # 延迟打开浏览器
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    # 启动 uvicorn
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        log_level="info",
        access_log=False,
    )


if __name__ == "__main__":
    main()
