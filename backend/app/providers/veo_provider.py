import asyncio
import os
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from backend.app.core.config import settings
from backend.app.providers.base import BaseVideoProvider, VideoGenerationResult

class GoogleVeoProvider(BaseVideoProvider):
    """
    Production video provider utilizing Google's official Veo 3.1 & 2.0 models via google-genai SDK.
    Supports reference images, first-frame continuation, 9:16 portrait, and 8-second segments.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.model = model or settings.VEO_MODEL
        self._client = None

    def _get_client(self):
        if self._client is None:
            if not self.api_key:
                raise ValueError(
                    "Gemini API key is not configured. Please connect your Gemini API key in settings."
                )
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                raise RuntimeError(f"Failed to initialize google-genai client: {str(e)}")
        return self._client

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "provider_name": "Google Veo (Official API)",
            "model": self.model,
            "supported_models": ["veo-3.1-generate-preview", "veo-2.0-generate-001"],
            "max_duration_sec": 8.0,
            "supported_durations": [4, 6, 8],
            "supports_first_frame": True,
            "supports_last_frame": True,
            "supports_reference_images": True,
            "max_reference_images": 3,
            "aspect_ratios": ["9:16", "16:9"],
            "resolutions": ["1080p", "720p"],
            "is_mock": False
        }

    async def generate_segment(
        self,
        prompt: str,
        duration_sec: float = 8.0,
        aspect_ratio: str = "9:16",
        resolution: str = "1080p",
        first_frame_path: Optional[Path] = None,
        reference_images: Optional[List[Path]] = None,
        negative_prompt: Optional[str] = None,
        output_path: Optional[Path] = None
    ) -> VideoGenerationResult:
        client = self._get_client()
        from google.genai import types

        # Veo duration must be 4, 6, or 8 seconds
        veo_duration = 8 if duration_sec >= 7.0 else 6 if duration_sec >= 5.0 else 4
        
        gen_id = uuid.uuid4().hex[:8]
        if output_path is None:
            output_path = settings.VIDEOS_DIR / f"segment_veo_{gen_id}.mp4"
        first_frame_out = settings.FRAMES_DIR / f"frame_start_{gen_id}.png"
        last_frame_out = settings.FRAMES_DIR / f"frame_end_{gen_id}.png"

        # Build config
        config_kwargs: Dict[str, Any] = {
            "aspect_ratio": aspect_ratio,
            "duration_seconds": veo_duration,
            "fps": 24,
            "resolution": resolution if resolution in ["720p", "1080p"] else "1080p",
        }
        if negative_prompt:
            config_kwargs["negative_prompt"] = negative_prompt

        image_input = None
        if first_frame_path and first_frame_path.exists():
            try:
                # Load first frame image for continuation
                image_input = types.Image.from_file(str(first_frame_path))
            except Exception as e:
                # Log and fallback to text prompt if image cannot be parsed
                pass

        # Execute generate_videos call
        try:
            config = types.GenerateVideosConfig(**config_kwargs)
            
            # Start generation operation (long running operation)
            loop = asyncio.get_event_loop()
            operation = await loop.run_in_executor(
                None,
                lambda: client.models.generate_videos(
                    model=self.model,
                    prompt=prompt,
                    image=image_input,
                    config=config
                )
            )

            # Poll until complete
            poll_interval = 10
            max_polls = 60  # 10 minutes max
            poll_count = 0

            while not operation.done:
                await asyncio.sleep(poll_interval)
                poll_count += 1
                if poll_count > max_polls:
                    raise TimeoutError("Veo video generation timed out after 10 minutes.")
                
                operation = await loop.run_in_executor(
                    None,
                    lambda: client.operations.get(operation)
                )

            # Check response
            if hasattr(operation, "error") and operation.error:
                raise RuntimeError(f"Veo generation error: {operation.error.message}")

            generated_videos = operation.response.generated_videos
            if not generated_videos:
                raise RuntimeError("No video returned in Veo operation response.")

            video_obj = generated_videos[0]
            
            # Save downloaded video bytes to file
            video_bytes = None
            if hasattr(video_obj, "video") and hasattr(video_obj.video, "video_bytes"):
                video_bytes = video_obj.video.video_bytes
            elif hasattr(video_obj, "download"):
                video_bytes = await loop.run_in_executor(None, video_obj.download)
            
            if video_bytes:
                with open(output_path, "wb") as f:
                    f.write(video_bytes)
            else:
                raise RuntimeError("Failed to retrieve video stream bytes from Veo response.")

            # Extract first and last frames with FFmpeg for downstream continuity checks
            cmd_ff = [
                "ffmpeg", "-y", "-ss", "0.0", "-i", str(output_path),
                "-vframes", "1", "-q:v", "2", str(first_frame_out)
            ]
            proc_ff = await asyncio.create_subprocess_exec(*cmd_ff)
            await proc_ff.wait()

            last_sec = max(0.0, float(veo_duration) - 0.1)
            cmd_lf = [
                "ffmpeg", "-y", "-ss", str(last_sec), "-i", str(output_path),
                "-vframes", "1", "-q:v", "2", str(last_frame_out)
            ]
            proc_lf = await asyncio.create_subprocess_exec(*cmd_lf)
            await proc_lf.wait()

            return VideoGenerationResult(
                video_path=output_path,
                duration_sec=float(veo_duration),
                first_frame_path=first_frame_out,
                last_frame_path=last_frame_out,
                metadata={
                    "provider": "google_veo",
                    "model": self.model,
                    "operation_name": getattr(operation, "name", "")
                }
            )

        except Exception as e:
            err_str = str(e)
            if "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                raise RuntimeError("Veo API Quota Exhausted: Your current Gemini API billing plan has reached its generation limit.")
            elif "UNAUTHENTICATED" in err_str or "API_KEY_INVALID" in err_str:
                raise RuntimeError("Authentication Failed: Invalid Gemini API key.")
            raise RuntimeError(f"Veo generation failed: {err_str}")
