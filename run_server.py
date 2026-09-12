import uvicorn
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"============================================================")
    print(f"🎬 AI Shorts & Reels Automatic Video Creation Platform")
    print(f"⚡ Server starting at: http://{host}:{port}")
    print(f"⚡ UI & API available at: http://{host}:{port}")
    print(f"⚡ Health check: http://{host}:{port}/api/health")
    print(f"============================================================")
    uvicorn.run("backend.app.main:app", host=host, port=port, reload=False)
