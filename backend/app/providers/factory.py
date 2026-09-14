from typing import Optional
from backend.app.core.config import settings
from backend.app.providers.base import BaseVideoProvider
from backend.app.providers.mock_provider import MockVideoProvider
from backend.app.providers.veo_provider import GoogleVeoProvider
from backend.app.providers.stock_video_provider import StockVideoProvider

class ProviderFactory:
    """Factory to instantiate the appropriate VideoProvider."""

    @staticmethod
    def get_video_provider(provider_name: Optional[str] = None, api_key: Optional[str] = None) -> BaseVideoProvider:
        name = (provider_name or settings.DEFAULT_VIDEO_PROVIDER).lower()
        if name in ["veo", "google", "google_veo"]:
            return GoogleVeoProvider(api_key=api_key)
        if name in ["stock", "stock_video", "google_vids", "action", "broll"]:
            return StockVideoProvider()
        return MockVideoProvider()

