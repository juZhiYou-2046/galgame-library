"""PyInstaller 打包配置

使用方式：
  1. 先构建前端: cd frontend && npm run build
  2. 运行打包: python build_desktop.py
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

APP_NAME = "GalgameLibrary"
VERSION = "1.0.0"
BASE_DIR = Path(__file__).resolve().parent


def build_frontend():
    """构建 Vue 前端"""
    frontend_dir = BASE_DIR / "frontend"
    print("[1/4] 构建前端...")
    subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
    subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
    print("  前端构建完成")


def collect_data_files():
    """收集需要打包的数据文件"""
    data_files = []

    # 前端 dist 目录
    dist_dir = BASE_DIR / "frontend" / "dist"
    if dist_dir.exists():
        for f in dist_dir.rglob("*"):
            if f.is_file():
                rel = f.relative_to(dist_dir)
                data_files.append((str(f), str(Path("frontend_dist") / rel.parent)))

    # 确保目录存在
    (BASE_DIR / "data").mkdir(exist_ok=True)
    (BASE_DIR / "covers").mkdir(exist_ok=True)

    return data_files


def build_executable():
    """使用 PyInstaller 构建可执行文件"""
    print("[2/4] 收集数据文件...")
    data_files = collect_data_files()

    print("[3/4] PyInstaller 打包...")

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

    # macOS 特定选项
    if platform.system() == "Darwin":
        cmd.extend([
            "--osx-bundle-identifier", "com.galgame-library.app",
        ])

    subprocess.run(cmd, check=True)
    print("  打包完成")


def create_package():
    """创建最终的安装包"""
    print("[4/4] 创建安装包...")

    system = platform.system()
    dist_dir = BASE_DIR / "dist"

    if system == "Darwin":
        # macOS: 创建 .zip 包（包含可执行文件 + 数据目录）
        pkg_dir = dist_dir / f"{APP_NAME}-macOS"
        pkg_dir.mkdir(exist_ok=True)

        # 复制可执行文件
        exe = dist_dir / APP_NAME
        shutil.copy2(exe, pkg_dir / APP_NAME)

        # 创建数据目录
        (pkg_dir / "data").mkdir(exist_ok=True)
        (pkg_dir / "covers").mkdir(exist_ok=True)

        # 创建启动脚本
        launch_script = pkg_dir / "启动.command"
        launch_script.write_text(f'#!/bin/bash\ncd "$(dirname "$0")"\n./{APP_NAME}\n')
        launch_script.chmod(0o755)

        # 创建 zip
        zip_name = f"GalgameLibrary-v{VERSION}-macOS.zip"
        shutil.make_archive(
            str(dist_dir / zip_name.replace(".zip", "")),
            "zip",
            dist_dir,
            f"{APP_NAME}-macOS",
        )
        print(f"  安装包: dist/{zip_name}")

    elif system == "Windows":
        # Windows: 创建 zip 包
        pkg_dir = dist_dir / f"{APP_NAME}-Windows"
        pkg_dir.mkdir(exist_ok=True)

        exe = dist_dir / f"{APP_NAME}.exe"
        shutil.copy2(exe, pkg_dir / f"{APP_NAME}.exe")

        (pkg_dir / "data").mkdir(exist_ok=True)
        (pkg_dir / "covers").mkdir(exist_ok=True)

        # 创建启动批处理
        bat = pkg_dir / "启动.bat"
        bat.write_text(f'@echo off\ncd /d "%~dp0"\n{APP_NAME}.exe\npause\n')

        zip_name = f"GalgameLibrary-v{VERSION}-Windows.zip"
        shutil.make_archive(
            str(dist_dir / zip_name.replace(".zip", "")),
            "zip",
            dist_dir,
            f"{APP_NAME}-Windows",
        )
        print(f"  安装包: dist/{zip_name}")

    else:
        print(f"  当前系统 ({system}) 暂不支持自动创建安装包")


if __name__ == "__main__":
    build_frontend()
    build_executable()
    create_package()
    print("\n打包完成! 查看 dist/ 目录获取安装包")
