import uvicorn
import os
import sys

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "127.0.0.1")
    print(f"============================================================")
    print(f"🎬 AI Shorts & Reels Automatic Video Creation Platform")
    print(f"⚡ Server starting at: http://{host}:{port}")
    print(f"⚡ UI & API available at: http://{host}:{port}")
    print(f"⚡ Health check: http://{host}:{port}/api/health")
    print(f"============================================================")
    uvicorn.run("backend.app.main:app", host=host, port=port, reload=False)
