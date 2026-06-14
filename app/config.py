"""应用配置 - 使用 pydantic-settings 从环境变量读取"""

from pathlib import Path

from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """应用配置，所有值均可通过环境变量覆盖"""

    # 数据库
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'data' / 'galgame.db'}"

    # CORS 白名单（逗号分隔的 origin 列表）
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000"

    # 目录
    DATA_DIR: str = str(BASE_DIR / "data")
    COVERS_DIR: str = str(BASE_DIR / "covers")
    COVERS_URL: str = "/covers"

    # 上传限制
    ALLOWED_IMAGE_EXTENSIONS: str = ".jpg,.jpeg,.png,.webp"
    MAX_COVER_SIZE: int = 5 * 1024 * 1024  # 5MB

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def allowed_extensions(self) -> set[str]:
        return {e.strip() for e in self.ALLOWED_IMAGE_EXTENSIONS.split(",")}

    @property
    def data_path(self) -> Path:
        p = Path(self.DATA_DIR)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def covers_path(self) -> Path:
        p = Path(self.COVERS_DIR)
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()

# 扫描时识别的游戏文件扩展名（常量，不需要从环境变量读取）
GAME_FILE_EXTENSIONS = {
    ".exe", ".iso", ".mdf", ".mds", ".ccd", ".cue", ".bin",
    # macOS 格式
    ".pkg", ".dmg", ".zip", ".rar", ".7z",
}

# .app 是 macOS 应用程序包（目录而非文件），需要特殊处理
MACOS_APP_BUNDLE = ".app"