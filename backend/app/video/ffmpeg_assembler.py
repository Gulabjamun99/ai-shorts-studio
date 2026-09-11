import asyncio
import os
import subprocess
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from backend.app.core.config import settings

class FFmpegAssembler:
    """
    Deterministic Video Assembly & Post-Production Engine.
    Handles:
    1. Seamless concatenation of Segments 1, 2, 3 without black frames
    2. Master audio track multiplexing
    3. Safe-margin subtitle burning (avoiding Reels & Shorts UI elements)
    4. Optional brand logo watermark overlay
    5. Output formatting to pristine 1080x1920 (9:16) H.264 / AAC at 24fps.
    """

    @classmethod
    async def assemble_final_video(
        cls,
        segment_paths: List[Path],
        audio_path: Path,
        subtitles_path: Optional[Path] = None,
        logo_path: Optional[Path] = None,
        output_path: Optional[Path] = None,
        target_duration: Optional[float] = None
    ) -> Path:
        for p in segment_paths:
            if not p.exists():
                raise FileNotFoundError(f"Segment video file not found: {p}")
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        gen_id = uuid.uuid4().hex[:8]
        if output_path is None:
            output_path = settings.VIDEOS_DIR / f"final_short_{gen_id}.mp4"

        concat_list_file = settings.STORAGE_DIR / f"concat_{gen_id}.txt"
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for p in segment_paths:
                f.write(f"file '{p.resolve().as_posix()}'\n")

        intermediate_concatenated = settings.VIDEOS_DIR / f"intermediate_concat_{gen_id}.mp4"

        # Step 1: Concatenate video segments cleanly
        cmd_concat = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_file),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-an",
            str(intermediate_concatenated)
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd_concat,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"FFmpeg concatenation failed: {stderr.decode()[-800:]}")

        # Step 2: Multiplex audio, burn subtitles in safe margins, and apply logo
        vf_filters = [
            "scale=1080:1920:force_original_aspect_ratio=increase",
            "crop=1080:1920",
            "fps=24"
        ]

        if subtitles_path and subtitles_path.exists():
            # In FFmpeg on Windows, colons in drive letters (e.g. D:) must be escaped with a backslash
            escaped_sub_path = subtitles_path.resolve().as_posix().replace(":", "\\:")
            sub_filter = f"subtitles='{escaped_sub_path}':force_style='FontSize=22,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=260'"
            vf_filters.append(sub_filter)

        filter_complex = ",".join(vf_filters)

        cmd_final = [
            "ffmpeg", "-y",
            "-i", str(intermediate_concatenated),
            "-i", str(audio_path),
            "-vf", filter_complex,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "20",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            str(output_path)
        ]

        if logo_path and logo_path.exists():
            clean_logo = logo_path.resolve().as_posix()
            logo_filter = (
                f"[0:v]{filter_complex}[vbase];"
                f"[1:v]scale=160:-1[logo];"
                f"[vbase][logo]overlay=W-w-50:80[vout]"
            )
            cmd_final = [
                "ffmpeg", "-y",
                "-i", str(intermediate_concatenated),
                "-i", clean_logo,
                "-i", str(audio_path),
                "-filter_complex", logo_filter,
                "-map", "[vout]",
                "-map", "2:a",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "20",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                "-movflags", "+faststart",
                str(output_path)
            ]

        proc_final = await asyncio.create_subprocess_exec(
            *cmd_final,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr_final = await proc_final.communicate()
        if proc_final.returncode != 0:
            raise RuntimeError(f"FFmpeg assembly failed: {stderr_final.decode()[-800:]}")

        # Clean up temporary concat artifacts
        try:
            concat_list_file.unlink(missing_ok=True)
            intermediate_concatenated.unlink(missing_ok=True)
        except Exception:
            pass

        return output_path

    @classmethod
    async def get_video_metadata(cls, video_path: Path) -> Dict[str, Any]:
        """Probes output video duration, resolution, and fps."""
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate,duration",
            "-show_entries", "format=duration",
            "-of", "json",
            str(video_path)
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        import json
        try:
            data = json.loads(stdout.decode())
            stream = data.get("streams", [{}])[0]
            fmt = data.get("format", {})
            dur = float(fmt.get("duration") or stream.get("duration") or 0.0)
            return {
                "width": stream.get("width", 1080),
                "height": stream.get("height", 1920),
                "duration": round(dur, 2),
                "fps": stream.get("r_frame_rate", "24/1")
            }
        except Exception:
            return {"width": 1080, "height": 1920, "duration": 22.0, "fps": "24/1"}
