import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.api.routers import projects, generation, assets, publish, admin
from backend.app.services.job_orchestrator import register_listener

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB on startup
    await init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Enable CORS for local dev and frontend Vite server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static storage for video preview, subtitles, and assets
app.mount("/storage", StaticFiles(directory=str(settings.STORAGE_DIR)), name="storage")

# Mount API routers
app.include_router(projects.router)
app.include_router(generation.router)
app.include_router(assets.router)
app.include_router(publish.router)
app.include_router(admin.router)

@app.get("/api/health")
async def health_check():
    return {
        "status": "HEALTHY",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "default_provider": settings.DEFAULT_VIDEO_PROVIDER
    }

@app.websocket("/ws/jobs/{job_id}")
async def websocket_job_endpoint(websocket: WebSocket, job_id: str):
    """Real-time WebSocket streaming of generation progress to the frontend."""
    await websocket.accept()
    queue = asyncio.Queue()

    def on_progress(data: dict):
        asyncio.create_task(queue.put(data))

    register_listener(job_id, on_progress)

    try:
        while True:
            data = await queue.get()
            await websocket.send_text(json.dumps(data))
    except (WebSocketDisconnect, Exception):
        pass

# Mount frontend static distribution at root (after all API and WS routes)
project_root = settings.BASE_DIR.parent
frontend_dist = project_root / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
