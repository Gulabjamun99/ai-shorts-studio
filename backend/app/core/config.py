import os
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage"
VIDEOS_DIR = STORAGE_DIR / "videos"
ASSETS_DIR = STORAGE_DIR / "assets"
FRAMES_DIR = STORAGE_DIR / "frames"
AUDIO_DIR = STORAGE_DIR / "audio"
SUBTITLES_DIR = STORAGE_DIR / "subtitles"

for d in [STORAGE_DIR, VIDEOS_DIR, ASSETS_DIR, FRAMES_DIR, AUDIO_DIR, SUBTITLES_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class Settings(BaseModel):
    APP_NAME: str = "AI Shorts & Reels Studio"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{STORAGE_DIR / 'app.db'}"
    
    # Video Generation Defaults
    DEFAULT_DURATION_SEC: float = 22.0  # 20-23 second target
    DEFAULT_ASPECT_RATIO: str = "9:16"  # Vertical portrait
    DEFAULT_RESOLUTION: str = "1080p"   # 1080x1920
    DEFAULT_FPS: int = 24
    
    # Provider Settings
    # DEFAULT_VIDEO_PROVIDER can be 'mock' (default for dev/cost control) or 'veo'
    DEFAULT_VIDEO_PROVIDER: str = Field(default_factory=lambda: os.getenv("DEFAULT_VIDEO_PROVIDER", "mock"))
    GEMINI_API_KEY: Optional[str] = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", None))
    VEO_MODEL: str = "veo-3.1-generate-preview"
    VEO_FALLBACK_MODEL: str = "veo-2.0-generate-001"
    
    # Voice Settings
    DEFAULT_VOICE_PROVIDER: str = "edge_tts"  # 'edge_tts', 'gemini_audio', 'gtts'
    
    # Security
    SECRET_ENCRYPTION_KEY: str = Field(
        default_factory=lambda: os.getenv("SECRET_ENCRYPTION_KEY", "u27Vz5N6r8o4Q1x3W9y7Z2a4C6e8G0i2K4m6O8q0S2u=")
    )
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".png", ".jpg", ".jpeg", ".webp"]
    
    # Storage Paths
    BASE_DIR: Path = BASE_DIR
    STORAGE_DIR: Path = STORAGE_DIR
    VIDEOS_DIR: Path = VIDEOS_DIR
    ASSETS_DIR: Path = ASSETS_DIR
    FRAMES_DIR: Path = FRAMES_DIR
    AUDIO_DIR: Path = AUDIO_DIR
    SUBTITLES_DIR: Path = SUBTITLES_DIR


settings = Settings()
