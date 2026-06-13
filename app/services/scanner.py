"""本地游戏扫描服务"""

import os
from pathlib import Path

from app.config import GAME_FILE_EXTENSIONS


class ScannerService:
    """扫描本地目录，发现可能的游戏资源"""

    @staticmethod
    def scan_directory(directory: str, max_depth: int = 3) -> list[dict]:
        """
        扫描指定目录，返回找到的可执行文件和镜像文件信息。
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
                dirs.clear()  # 不再深入子目录
                continue

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
                    })

        return results