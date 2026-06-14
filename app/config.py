"""应用配置"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
COVERS_DIR = BASE_DIR / "covers"

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)
COVERS_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR / 'galgame.db'}"
COVERS_URL = "/covers"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# 扫描时识别的游戏文件扩展名
GAME_FILE_EXTENSIONS = {
    ".exe", ".iso", ".mdf", ".mds", ".ccd", ".cue", ".bin",
    # macOS 格式
    ".pkg", ".dmg", ".zip", ".rar", ".7z",
}

# .app 是 macOS 应用程序包（目录而非文件），需要特殊处理
MACOS_APP_BUNDLE = ".app"