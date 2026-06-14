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
BASE_DIR = Path(__file__).resolve().parent


def get_version():
    """从环境变量或 git tag 获取版本号"""
    version = os.environ.get("GITHUB_REF_NAME", "")
    if version.startswith("v"):
        version = version[1:]
    return version or "1.0.0"


def build_executable():
    """使用 PyInstaller 构建可执行文件"""
    version = get_version()
    print(f"版本: {version}")

    dist_dir = BASE_DIR / "frontend" / "dist"
    if not dist_dir.exists():
        print(f"[ERROR] 前端 dist 目录不存在: {dist_dir}")
        sys.exit(1)

    # 收集前端文件
    data_args = []
    file_count = 0
    for f in dist_dir.rglob("*"):
        if f.is_file():
            file_count += 1
            rel = f.relative_to(dist_dir)
            sep = ";" if platform.system() == "Windows" else ":"
            dest_dir = str(Path("frontend_dist") / rel.parent)
            data_args.extend(["--add-data", f"{f}{sep}{dest_dir}"])
    print(f"  共 {file_count} 个前端文件待打包")

    # PyInstaller 打包
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--onefile",
        "--noconfirm",
        "--hidden-import", "sqlalchemy.dialects.sqlite",
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.lifespan.on",
        *data_args,
        "desktop_launcher.py",
    ]

    print(f"PyInstaller 打包中...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("STDERR:", result.stderr[-2000:])
        print("STDOUT:", result.stdout[-2000:])
        result.check_returncode()
    print("  打包完成")


def create_package():
    """创建最终的安装包"""
    version = get_version()
    system = platform.system()
    dist_dir = BASE_DIR / "dist"

    if system == "Darwin":
        pkg_dir = dist_dir / f"{APP_NAME}-macOS"
        pkg_dir.mkdir(exist_ok=True)

        exe = dist_dir / APP_NAME
        if not exe.exists():
            # PyInstaller on macOS sometimes adds no extension
            possible = list(dist_dir.glob(APP_NAME + "*"))
            print(f"  dist 目录内容: {possible}")
            if possible:
                exe = possible[0]
        shutil.copy2(exe, pkg_dir / APP_NAME)

        (pkg_dir / "data").mkdir(exist_ok=True)
        (pkg_dir / "covers").mkdir(exist_ok=True)

        launch_script = pkg_dir / "启动.command"
        launch_script.write_text(f'#!/bin/bash\ncd "$(dirname "$0")"\n./{APP_NAME}\n')
        launch_script.chmod(0o755)

        with open(pkg_dir / "README.txt", "w", encoding="utf-8") as f:
            f.write(
                "Galgame Library - macOS\n"
                "========================\n\n"
                "双击 '启动.command' 即可运行。\n"
                "若提示无法打开，右键 -> 打开。\n"
            )

        zip_name = f"GalgameLibrary-v{version}-macOS"
        p = dist_dir / zip_name
        shutil.make_archive(str(p), "zip", dist_dir, f"{APP_NAME}-macOS")
        print(f"  -> {p}.zip")

    elif system == "Windows":
        pkg_dir = dist_dir / f"{APP_NAME}-Windows"
        pkg_dir.mkdir(exist_ok=True)

        exe = dist_dir / f"{APP_NAME}.exe"
        if not exe.exists():
            possible = list(dist_dir.glob(APP_NAME + ".*"))
            print(f"  dist 目录内容: {possible}")
            exe = possible[0] if possible else dist_dir / "NO_EXE_FOUND"
        shutil.copy2(exe, pkg_dir / f"{APP_NAME}.exe")

        (pkg_dir / "data").mkdir(exist_ok=True)
        (pkg_dir / "covers").mkdir(exist_ok=True)

        with open(pkg_dir / "启动.bat", "w", encoding="utf-8") as f:
            f.write(f'@echo off\ncd /d "%~dp0"\nstart {APP_NAME}.exe\n')

        with open(pkg_dir / "README.txt", "w", encoding="utf-8") as f:
            f.write(
                "Galgame Library - Windows\n"
                "==========================\n\n"
                "双击 '启动.bat' 即可运行。\n"
            )

        zip_name = f"GalgameLibrary-v{version}-Windows"
        p = dist_dir / zip_name
        shutil.make_archive(str(p), "zip", dist_dir, f"{APP_NAME}-Windows")
        print(f"  -> {p}.zip")

    else:
        print(f"  不支持的平台: {system}")
        sys.exit(1)


if __name__ == "__main__":
    build_executable()
    create_package()
    print("打包完成!")
