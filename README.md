# AI Shorts & Reels Automatic Video Creation Platform

An enterprise-grade, full-stack video creation platform designed to transform raw concepts, tutorials, household tips, product descriptions, or advertisement ideas into coherent approximately 20–23 second vertical short-form videos (9:16 portrait) optimized for **Instagram Reels** and **YouTube Shorts**.

---

## 🌟 Key Architecture & Non-Negotiables

Unlike naive tools that assemble 3 unrelated AI clips, this platform treats the output as **ONE unified 20–23 second story**:

```
MASTER STORY → MASTER SCRIPT → MASTER BLUEPRINT → CONTINUITY PLAN
    ↓
SEGMENT 1 (Hook / Problem, ~7.3s)
    ↓ (Extract ending frame F1_end)
SEGMENT 2 (Action / Demo with F1_end frame-anchoring, ~7.3s)
    ↓ (Extract ending frame F2_end)
SEGMENT 3 (Result / CTA with F2_end frame-anchoring, ~7.4s)
    ↓
CONTINUOUS MASTER VOICE GENERATION & WORD-TIMED SUBTITLES
    ↓
DETERMINISTIC FFMPEG 8.0 ASSEMBLY (Concat, Safe Margins, Subtitle Burning, Watermark)
    ↓
12-DIMENSIONAL AUTOMATED QA GATE & AUTO-REPAIR
    ↓
FINAL 1080x1920 9:16 VERTICAL SHORT
```

---

## 🚀 Features

1. **Content Truth Layer & Anti-Hallucination Engine**:
   - Isolates user-verified facts from creative interpretation.
   - Strictly prevents hallucination of fake prices, discounts, medical guarantees, awards, or false URLs.
2. **Speech-Rate Calibrated Script Engine**:
   - Accurately estimates spoken length for 10+ languages (English, Hindi, Marathi, Telugu, Tamil, Bengali, Gujarati, Kannada, Malayalam, Punjabi).
   - Enforces the 20–23 second spoken limit *before* expensive video generation begins.
3. **Mandatory Script Approval Gate**:
   - Displays Master Script, duration estimate, and 3 segment breakdowns (narration, camera/action directive, on-screen text).
   - Empowers users to edit, regenerate, or approve before rendering.
4. **Character, Product & Environment Continuity**:
   - Persistent Character ID, Product ID, and Environment profiles.
   - Veo 3.1 reference image injection (up to 3 images) and frame-to-frame continuation anchoring ($F_{\text{end}} \to F_{\text{start}}$).
5. **Multi-Lingual Neural Voice & Word-Timed Subtitles**:
   - High-fidelity neural voice synthesis (Edge-TTS / gTTS fallback).
   - Generates synchronized SRT subtitles burnt with safe margins (avoiding TikTok/Reels UI headers and footers).
6. **Deterministic FFmpeg Post-Production Engine**:
   - No distorted AI text: exact brand titles, CTAs, and captions are burnt deterministically.
   - Clean concatenation without accidental black frames or audio gaps.
7. **12-Point Automated QA Gate**:
   - Evaluates Content Match, Visual Match, Character Continuity, Product Continuity, Environment Continuity, Voice Continuity, Script-Audio Sync, Audio-Visual Sync, Language Quality, Timing, Text Quality, and Platform Format.
   - Automatically repairs failing segments without regenerating the entire video.
8. **Provider Abstraction**:
   - `GoogleVeoProvider`: Official Google Veo 3.1 (`veo-3.1-generate-preview`) and Veo 2.0 (`veo-2.0-generate-001`) via `google-genai` SDK.
   - `MockVideoProvider`: High-fidelity local video generator producing valid 9:16 MP4s and frame extractions for zero-cost dev/testing.

---

## 🛠️ Quick Start

### 1. Requirements
- Python 3.12+
- Node.js v18+ (tested with v24.12)
- FFmpeg 6.0+ (installed and available in system PATH)

### 2. Run the Application
Launch the unified server (serves both FastAPI API and React Studio UI):
```bash
python run_server.py
```
Open **`http://127.0.0.1:8000`** in your browser.

### 3. Optional: Live Google Veo Mode
To generate using live Google Veo rather than the local dev provider:
1. Set environment variable:
   ```bash
   export GEMINI_API_KEY="AIzaSy..."
   export DEFAULT_VIDEO_PROVIDER="veo"
   ```
2. Or enter your Gemini API key under **Advanced Options** in the Studio dashboard.

---

## 🧪 Automated Test Suite (All 28 Scenarios A through AB)

Execute the full pytest suite covering all 28 required test matrices from Section 50 of the prompt:
```bash
python -m pytest backend/tests/test_master_suite.py -v
```

### Verified Test Matrix:
- `Test A`: Educational video
- `Test B`: Product advertisement
- `Test C`: Company advertisement
- `Test D`: App promotion
- `Test E`: Household tip
- `Test F`: Tutorial
- `Test G`: Storytelling
- `Test H`: Hindi video
- `Test I`: English video
- `Test J`: Additional supported languages (Marathi & Telugu)
- `Test K`: Character-based video
- `Test L`: Product-based video
- `Test M`: No-character video (First-person POV / hands only)
- `Test N`: User-provided image validation
- `Test O`: User-provided logo validation
- `Test P`: User-provided screenshot validation
- `Test Q`: Custom CTA preservation
- `Test R`: No CTA safe fallback
- `Test S`: User edits Scene 1
- `Test T`: User edits Scene 2
- `Test U`: User changes language
- `Test V`: User changes voice gender
- `Test W`: Generation failure handling
- `Test X`: API timeout handling
- `Test Y`: Quota exhaustion detection
- `Test Z`: Invalid asset extension handling
- `Test AA`: Corrupted asset file handling
- `Test AB`: Provider unavailable graceful fallback

---

## 🔒 Security & Privacy

- **Zero credential scraping**: The system never asks for or stores Google/Gmail passwords, cookies, or browser session tokens.
- **Encrypted Secret Storage**: Sensitive API keys and OAuth tokens are encrypted at rest using AES/Fernet encryption.
- **Sanitized Uploads**: Image files are strictly validated for MIME headers, file sizes (< 25MB), and structural integrity via PIL before processing.
