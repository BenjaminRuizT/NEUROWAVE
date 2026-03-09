"""
NeuroWave AI — FastAPI Backend
================================
Railway-ready server. Handles:
  - REST API for session/config management
  - WebSocket for real-time EEG streaming (10 Hz)
  - Static file serving (SPA frontend)

Audio synthesis runs 100% in the browser via Web Audio API.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as api_router
from api.websocket_handler import router as ws_router
from core.eeg_biofeedback import BiofeedbackManager
from core.session_manager import SessionManager


# ── Global app state ───────────────────────────────────────────
biofeedback: BiofeedbackManager = None
session_mgr: SessionManager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start/stop background services."""
    global biofeedback, session_mgr

    session_mgr = SessionManager()
    biofeedback = BiofeedbackManager(use_simulator=True)
    biofeedback.start(sample_rate_hz=10.0)

    # Make available to route handlers
    app.state.biofeedback = biofeedback
    app.state.session_mgr = session_mgr

    print("[NeuroWave] Backend online")
    yield

    biofeedback.stop()
    print("[NeuroWave] Backend shutdown")


# ── App setup ──────────────────────────────────────────────────
app = FastAPI(
    title="NeuroWave AI",
    description="Neuroacoustic AI Platform API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ─────────────────────────────────────────────────────
app.include_router(api_router,  prefix="/api")
app.include_router(ws_router)

# ── Static files ───────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
async def serve_spa():
    return FileResponse("static/index.html")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "NeuroWave AI"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
