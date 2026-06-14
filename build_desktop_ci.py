"""CI 环境下的 PyInstaller 打包脚本

前端已在 workflow 中预先构建，此脚本只负责 PyInstaller 打包和创建安装包。
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

APP_NAME = "GalgameLibrary"
VERSION = os.environ.get("GITHUB_REF_NAME", "1.0.0")
BASE_DIR = Path(__file__).resolve().parent


def collect_data_files():
    """收集需要打包的数据文件"""
    data_files = []

    dist_dir = BASE_DIR / "frontend" / "dist"
    if dist_dir.exists():
        for f in dist_dir.rglob("*"):
            if f.is_file():
                rel = f.relative_to(dist_dir)
                data_files.append((str(f), str(Path("frontend_dist") / rel.parent)))

    return data_files


def build_executable():
    """使用 PyInstaller 构建可执行文件"""
    print("[1/3] 收集数据文件...")
    data_files = collect_data_files()
    print(f"  共 {len(data_files)} 个文件")

    print("[2/3] PyInstaller 打包...")

    add_data_args = []
    for src, dest in data_files:
        sep = ";" if platform.system() == "Windows" else ":"
        add_data_args.extend(["--add-data", f"{src}{sep}{dest}"])

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--onefile",
        "--clean",
        "--noconfirm",
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols",
        "--hidden-import", "uvicorn.protocols.http",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.websockets",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.lifespan",
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "sqlalchemy.dialects.sqlite",
        "--hidden-import", "aiofiles",
        "--hidden-import", "multipart",
        *add_data_args,
        "desktop_launcher.py",
    ]

    subprocess.run(cmd, check=True)
    print("  打包完成")


def create_package():
    """创建最终的安装包"""
    print("[3/3] 创建安装包...")

    system = platform.system()
    dist_dir = BASE_DIR / "dist"

    if system == "Darwin":
        pkg_name = f"{APP_NAME}-macOS"
        pkg_dir = dist_dir / pkg_name
        pkg_dir.mkdir(exist_ok=True)

        exe = dist_dir / APP_NAME
        shutil.copy2(exe, pkg_dir / APP_NAME)
        (pkg_dir / "data").mkdir(exist_ok=True)
        (pkg_dir / "covers").mkdir(exist_ok=True)

        launch_script = pkg_dir / "启动.command"
        launch_script.write_text(f'#!/bin/bash\ncd "$(dirname "$0")"\n./{APP_NAME}\n')
        launch_script.chmod(0o755)

        # 创建 README
        readme = pkg_dir / "README.txt"
        readme.write_text(
            "Galgame Library - macOS\n"
            "========================\n\n"
            "使用方式: 双击 '启动.command' 文件即可运行。\n\n"
            "如果 macOS 提示无法打开, 请右键点击文件 -> 打开。\n"
            "首次运行会自动创建 data/ 和 covers/ 文件夹。\n"
        )

        zip_name = f"GalgameLibrary-v{VERSION}-macOS"
        shutil.make_archive(str(dist_dir / zip_name), "zip", dist_dir, pkg_name)
        print(f"  安装包: dist/{zip_name}.zip")

    elif system == "Windows":
        pkg_name = f"{APP_NAME}-Windows"
        pkg_dir = dist_dir / pkg_name
        pkg_dir.mkdir(exist_ok=True)

        exe = dist_dir / f"{APP_NAME}.exe"
        shutil.copy2(exe, pkg_dir / f"{APP_NAME}.exe")
        (pkg_dir / "data").mkdir(exist_ok=True)
        (pkg_dir / "covers").mkdir(exist_ok=True)

        bat = pkg_dir / "启动.bat"
        bat.write_text(f'@echo off\ncd /d "%~dp0"\n{APP_NAME}.exe\npause\n')

        readme = pkg_dir / "README.txt"
        readme.write_text(
            "Galgame Library - Windows\n"
            "==========================\n\n"
            "使用方式: 双击 '启动.bat' 文件即可运行。\n\n"
            "首次运行会自动创建 data/ 和 covers/ 文件夹。\n"
        )

        zip_name = f"GalgameLibrary-v{VERSION}-Windows"
        shutil.make_archive(str(dist_dir / zip_name), "zip", dist_dir, pkg_name)
        print(f"  安装包: dist/{zip_name}.zip")

    else:
        print(f"  不支持的平台: {system}")
        sys.exit(1)


if __name__ == "__main__":
    build_executable()
    create_package()
    print("\n打包完成!")
