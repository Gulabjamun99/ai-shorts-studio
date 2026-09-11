from typing import Optional
from backend.app.core.config import settings
from backend.app.providers.base import BaseVideoProvider
from backend.app.providers.mock_provider import MockVideoProvider
from backend.app.providers.veo_provider import GoogleVeoProvider

class ProviderFactory:
    """Factory to instantiate the appropriate VideoProvider."""

    @staticmethod
    def get_video_provider(provider_name: Optional[str] = None, api_key: Optional[str] = None) -> BaseVideoProvider:
        name = (provider_name or settings.DEFAULT_VIDEO_PROVIDER).lower()
        if name in ["veo", "google", "google_veo"]:
            return GoogleVeoProvider(api_key=api_key)
        return MockVideoProvider()
