import asyncio
import os
import re
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List
import edge_tts
from gtts import gTTS
from backend.app.core.config import settings

VOICE_MAP: Dict[str, Dict[str, str]] = {
    "English": {
        "Female": "en-US-AvaMultilingualNeural",
        "Male": "en-US-AndrewMultilingualNeural",
        "Neutral": "en-US-EmmaMultilingualNeural",
    },
    "Hindi": {
        "Female": "hi-IN-SwaraNeural",
        "Male": "hi-IN-MadhurNeural",
        "Neutral": "hi-IN-SwaraNeural",
    },
    "Marathi": {
        "Female": "mr-IN-AarohiNeural",
        "Male": "mr-IN-ManoharNeural",
        "Neutral": "mr-IN-AarohiNeural",
    },
    "Telugu": {
        "Female": "te-IN-ShrutiNeural",
        "Male": "te-IN-MohanNeural",
        "Neutral": "te-IN-ShrutiNeural",
    },
    "Tamil": {
        "Female": "ta-IN-PallaviNeural",
        "Male": "ta-IN-ValluvarNeural",
        "Neutral": "ta-IN-PallaviNeural",
    },
    "Bengali": {
        "Female": "bn-IN-TanishaaNeural",
        "Male": "bn-IN-BashkarNeural",
        "Neutral": "bn-IN-TanishaaNeural",
    },
    "Gujarati": {
        "Female": "gu-IN-DhwaniNeural",
        "Male": "gu-IN-NiranjanNeural",
        "Neutral": "gu-IN-DhwaniNeural",
    },
    "Kannada": {
        "Female": "kn-IN-SapnaNeural",
        "Male": "kn-IN-GaganNeural",
        "Neutral": "kn-IN-SapnaNeural",
    },
    "Malayalam": {
        "Female": "ml-IN-SobhanaNeural",
        "Male": "ml-IN-MidhunNeural",
        "Neutral": "ml-IN-SobhanaNeural",
    },
    "Punjabi": {
        "Female": "pa-IN-OjasNeural",
        "Male": "pa-IN-RaagNeural",
        "Neutral": "pa-IN-OjasNeural",
    },
}

GTTS_LANG_CODES: Dict[str, str] = {
    "English": "en",
    "Hindi": "hi",
    "Marathi": "mr",
    "Telugu": "te",
    "Tamil": "ta",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Punjabi": "pa",
}

class VoiceGenerationResult:
    def __init__(
        self,
        audio_path: Path,
        duration_sec: float,
        srt_subtitles_path: Path,
        voice_id: str,
        language: str
    ):
        self.audio_path = audio_path
        self.duration_sec = duration_sec
        self.srt_subtitles_path = srt_subtitles_path
        self.voice_id = voice_id
        self.language = language


class VoiceProvider:
    """
    High-fidelity multi-lingual neural voice generator.
    Generates unified master audio and synchronized SRT subtitles.
    """

    @classmethod
    def get_voice_id(cls, language: str, gender: str = "Female") -> str:
        lang_voices = VOICE_MAP.get(language, VOICE_MAP["English"])
        return lang_voices.get(gender, lang_voices.get("Female", "en-US-AvaMultilingualNeural"))

    @classmethod
    async def generate_speech(
        cls,
        text: str,
        language: str = "English",
        gender: str = "Female",
        output_audio_path: Optional[Path] = None,
        segment_durations: Optional[List[float]] = None
    ) -> VoiceGenerationResult:
        gen_id = uuid.uuid4().hex[:8]
        if output_audio_path is None:
            output_audio_path = settings.AUDIO_DIR / f"voice_master_{gen_id}.mp3"
        srt_path = settings.SUBTITLES_DIR / f"subs_{gen_id}.srt"

        voice_id = cls.get_voice_id(language, gender)
        
        # Primary: edge-tts
        try:
            communicate = edge_tts.Communicate(text, voice_id)
            await communicate.save(str(output_audio_path))
        except Exception as e:
            # Fallback to gTTS if edge-tts fails or is offline
            lang_code = GTTS_LANG_CODES.get(language, "en")
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: gTTS(text=text, lang=lang_code, slow=False).save(str(output_audio_path))
            )

        # Probe exact audio duration using FFprobe
        duration_sec = await cls._probe_audio_duration(output_audio_path)
        
        # Build synchronized SRT subtitles with safe split chunks
        cls._create_srt_file(text, duration_sec, srt_path, segment_durations)

        return VoiceGenerationResult(
            audio_path=output_audio_path,
            duration_sec=duration_sec,
            srt_subtitles_path=srt_path,
            voice_id=voice_id,
            language=language
        )

    @classmethod
    async def _probe_audio_duration(cls, audio_path: Path) -> float:
        """Uses ffprobe to obtain exact audio duration in seconds."""
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path)
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        try:
            return round(float(stdout.decode().strip()), 2)
        except Exception:
            return 22.0

    @classmethod
    def _create_srt_file(
        cls,
        text: str,
        total_duration: float,
        srt_path: Path,
        segment_durations: Optional[List[float]] = None
    ):
        """Creates an SRT subtitle file split cleanly across sentences with accurate timestamps."""
        sentences = [s.strip() for s in re.split(r'(?<=[.!?।])\s+', text) if s.strip()]
        if not sentences:
            sentences = [text]

        # Calculate time slice per sentence weighted by character length
        total_chars = sum(len(s) for s in sentences)
        if total_chars == 0:
            total_chars = 1

        subtitles_entries = []
        current_time = 0.0

        for i, sentence in enumerate(sentences, 1):
            sent_share = len(sentence) / total_chars
            sent_duration = total_duration * sent_share
            start_time = current_time
            end_time = min(total_duration, start_time + sent_duration)
            current_time = end_time

            start_str = cls._format_srt_timestamp(start_time)
            end_str = cls._format_srt_timestamp(end_time)

            subtitles_entries.append(f"{i}\n{start_str} --> {end_str}\n{sentence}\n")

        with open(srt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(subtitles_entries))

    @staticmethod
    def _format_srt_timestamp(seconds: float) -> str:
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"
