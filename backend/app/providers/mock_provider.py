import asyncio
import subprocess
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from backend.app.core.config import settings
from backend.app.providers.base import BaseVideoProvider, VideoGenerationResult

class MockVideoProvider(BaseVideoProvider):
    """
    High-fidelity deterministic local video generator using FFmpeg.
    Creates valid 9:16 (1080x1920) MP4 files with real extracted frames,
    allowing full local development and CI testing without burning live API credits.
    """

    def __init__(self, simulate_delay_sec: float = 0.5):
        self.simulate_delay_sec = simulate_delay_sec

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "provider_name": "Mock Video Provider (Deterministic Dev Mode)",
            "supported_models": ["mock-veo-3.1", "mock-veo-2.0"],
            "max_duration_sec": 8.0,
            "supports_first_frame": True,
            "supports_last_frame": True,
            "supports_reference_images": True,
            "max_reference_images": 3,
            "aspect_ratios": ["9:16", "16:9"],
            "resolutions": ["1080p", "720p"],
            "is_mock": True
        }

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
        if self.simulate_delay_sec > 0:
            await asyncio.sleep(self.simulate_delay_sec)

        # Determine target file paths
        gen_id = uuid.uuid4().hex[:8]
        if output_path is None:
            output_path = settings.VIDEOS_DIR / f"segment_mock_{gen_id}.mp4"
        
        first_frame_out = settings.FRAMES_DIR / f"frame_start_{gen_id}.png"
        last_frame_out = settings.FRAMES_DIR / f"frame_end_{gen_id}.png"

        width, height = (1080, 1920) if aspect_ratio == "9:16" else (1920, 1080)
        
        # Color palettes for segments to visually signify continuity
        # Smooth cinematic dark slate gradient with accent highlight
        color1 = "0x1a1a2e"
        color2 = "0x16213e"
        
        # Build FFmpeg command to render a pristine 1080x1920 24fps test video
        # We use testsrc2 or color gradients with drawtext
        filter_str = (
            f"testsrc2=size={width}x{height}:rate=24:duration={duration_sec},"
            f"drawbox=y=0:color=black@0.5:width=iw:height=ih:t=fill,"
            f"drawtext=text='AI SHORTS STUDIO':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=200,"
            f"drawtext=text='Continuous Scene':fontcolor=0x4ECCA3:fontsize=36:x=(w-text_w)/2:y=280,"
            f"drawtext=text='Duration\\: %{{pts\\:hms}}':fontcolor=white:fontsize=32:x=(w-text_w)/2:y=h-300"
        )

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", filter_str,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            "-t", str(duration_sec),
            str(output_path)
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await proc.wait()

        # Extract real first frame
        cmd_ff = [
            "ffmpeg", "-y",
            "-ss", "0.0",
            "-i", str(output_path),
            "-vframes", "1",
            "-q:v", "2",
            str(first_frame_out)
        ]
        proc_ff = await asyncio.create_subprocess_exec(
            *cmd_ff,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await proc_ff.wait()

        # Extract real last frame
        last_sec = max(0.0, duration_sec - 0.1)
        cmd_lf = [
            "ffmpeg", "-y",
            "-ss", str(last_sec),
            "-i", str(output_path),
            "-vframes", "1",
            "-q:v", "2",
            str(last_frame_out)
        ]
        proc_lf = await asyncio.create_subprocess_exec(
            *cmd_lf,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await proc_lf.wait()

        return VideoGenerationResult(
            video_path=output_path,
            duration_sec=duration_sec,
            first_frame_path=first_frame_out,
            last_frame_path=last_frame_out,
            metadata={
                "provider": "mock",
                "resolution": f"{width}x{height}",
                "aspect_ratio": aspect_ratio,
                "fps": 24
            }
        )
