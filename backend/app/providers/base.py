from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List, Dict, Any

class VideoGenerationResult:
    def __init__(
        self,
        video_path: Path,
        duration_sec: float,
        first_frame_path: Optional[Path] = None,
        last_frame_path: Optional[Path] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.video_path = video_path
        self.duration_sec = duration_sec
        self.first_frame_path = first_frame_path
        self.last_frame_path = last_frame_path
        self.metadata = metadata or {}


class BaseVideoProvider(ABC):
    """
    Abstract interface for video generation engines (Veo, Mock, future models).
    Decouples the core orchestration from any single proprietary API.
    """

    @abstractmethod
    async def generate_segment(
        self,
        prompt: str,
        duration_sec: float = 7.5,
        aspect_ratio: str = "9:16",
        resolution: str = "1080p",
        first_frame_path: Optional[Path] = None,
        reference_images: Optional[List[Path]] = None,
        negative_prompt: Optional[str] = None,
        output_path: Optional[Path] = None
    ) -> VideoGenerationResult:
        """Generates an individual video segment with frame/reference continuity."""
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Returns feature support matrix (max duration, reference images, first-frame, aspect ratios)."""
        pass
