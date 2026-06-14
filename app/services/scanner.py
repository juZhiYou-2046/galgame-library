"""本地游戏扫描服务"""

import os
import re
from pathlib import Path

from app.config import GAME_FILE_EXTENSIONS, MACOS_APP_BUNDLE


class ScannerService:
    """扫描本地目录，发现可能的游戏资源"""

    @staticmethod
    def _clean_title(name: str) -> str:
        """从文件名或目录名中提取清洁的标题"""
        # 去除扩展名
        title = Path(name).stem if "." in name else name
        # 去除常见版本标记：[v1.0], (Build 1234), v1.0.2 等
        title = re.sub(r'\s*[\[\(][^\]\)]*[\]\)]\s*', ' ', title)
        title = re.sub(r'\s*v?\d+\.\d+(\.\d+)*\s*', ' ', title)
        # 将下划线、连字符替换为空格
        title = re.sub(r'[_\-]+', ' ', title)
        # 清理多余空格
        title = re.sub(r'\s+', ' ', title).strip()
        return title if title else name

    @staticmethod
    def _get_directory_size(path: Path) -> int:
        """计算目录大小"""
        total = 0
        try:
            for f in path.rglob("*"):
                if f.is_file():
                    total += f.stat().st_size
        except (PermissionError, OSError):
            pass
        return total

    @staticmethod
    def scan_directory(directory: str, max_depth: int = 3) -> list[dict]:
        """
        扫描指定目录，返回找到的游戏文件和 macOS 应用包信息。
        """
        base_path = Path(directory).resolve()
        if not base_path.is_dir():
            return []

        results = []

        # 限制扫描深度
        for root, dirs, files in os.walk(str(base_path)):
            rel_path = Path(root).relative_to(base_path)
            depth = len(rel_path.parts)

            if depth > max_depth:
                dirs.clear()
                continue

            # 检测 .app 应用包（macOS 目录格式）
            app_dirs = [d for d in dirs if d.endswith(MACOS_APP_BUNDLE)]
            for app_dir in app_dirs:
                app_path = Path(root) / app_dir
                results.append({
                    "name": app_dir,
                    "path": str(app_path),
                    "folder": str(root),
                    "extension": MACOS_APP_BUNDLE,
                    "size": ScannerService._get_directory_size(app_path),
                    "is_bundle": True,
                })
                dirs.remove(app_dir)  # 不再深入 .app 包内部

            # 检测普通游戏文件
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in GAME_FILE_EXTENSIONS:
                    full_path = Path(root) / file
                    results.append({
                        "name": file,
                        "path": str(full_path),
                        "folder": str(root),
                        "extension": ext,
                        "size": full_path.stat().st_size if full_path.exists() else 0,
                        "is_bundle": False,
                    })

        return results