"""
NeuroWave AI — REST API Routes
"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from core.adaptive_engine import COGNITIVE_MODES
from core.audio_engine_stub import BrainwaveState

router = APIRouter(tags=["NeuroWave"])


# ── Schemas ────────────────────────────────────────────────────

class ModeRequest(BaseModel):
    mode: str

class SimulatorStateRequest(BaseModel):
    state: str   # delta | theta | alpha | beta | gamma
    transition_seconds: float = 5.0

class SessionStartRequest(BaseModel):
    mode: str = "study"

class SettingsRequest(BaseModel):
    tuning_hz: Optional[float] = None
    master_volume: Optional[float] = None
    default_mode: Optional[str] = None
    theme: Optional[str] = None


# ── EEG / Biofeedback ─────────────────────────────────────────

@router.get("/eeg/state")
async def get_eeg_state(request: Request):
    """Current cognitive profile snapshot."""
    bio = request.app.state.biofeedback
    profile = bio.profile
    sample  = bio.latest

    band_powers = {}
    if sample:
        band_powers = sample.band_powers

    return {
        "state":      profile.state.value,
        "stress":     round(profile.stress, 3),
        "focus":      round(profile.focus, 3),
        "meditation": round(profile.meditation, 3),
        "confidence": round(profile.confidence, 3),
        "band_powers": {k: round(v, 4) for k, v in band_powers.items()},
    }


@router.post("/eeg/simulate")
async def set_simulator_state(body: SimulatorStateRequest, request: Request):
    """Drive the EEG simulator to a specific brain state."""
    state_map = {
        "delta": BrainwaveState.DELTA,
        "theta": BrainwaveState.THETA,
        "alpha": BrainwaveState.ALPHA,
        "beta":  BrainwaveState.BETA,
        "gamma": BrainwaveState.GAMMA,
    }
    state = state_map.get(body.state.lower())
    if not state:
        raise HTTPException(400, f"Unknown state: {body.state}")

    bio = request.app.state.biofeedback
    bio.set_simulator_state(state, body.transition_seconds)
    return {"ok": True, "target_state": body.state}


# ── Cognitive Modes ───────────────────────────────────────────

@router.get("/modes")
async def list_modes():
    """Return all available cognitive modes."""
    return {
        key: {
            "name": mode.name,
            "description": mode.description,
            "target_state": mode.target_state.value,
            "binaural_volume": mode.binaural_volume,
            "carrier_freq": mode.carrier_freq,
            "ambient_config": mode.ambient_config,
        }
        for key, mode in COGNITIVE_MODES.items()
    }


@router.get("/modes/{mode_key}")
async def get_mode(mode_key: str):
    """Return configuration for a specific mode."""
    mode = COGNITIVE_MODES.get(mode_key)
    if not mode:
        raise HTTPException(404, f"Mode '{mode_key}' not found")
    return {
        "key": mode_key,
        "name": mode.name,
        "description": mode.description,
        "target_state": mode.target_state.value,
        "binaural_volume": mode.binaural_volume,
        "carrier_freq": mode.carrier_freq,
        "ambient_config": mode.ambient_config,
        "beat_freq": _beat_for_state(mode.target_state),
    }


def _beat_for_state(state: BrainwaveState) -> float:
    from core.audio_engine_stub import BRAINWAVE_FREQUENCIES
    return BRAINWAVE_FREQUENCIES.get(state, 10.0)


# ── Sessions ──────────────────────────────────────────────────

@router.post("/sessions/start")
async def start_session(body: SessionStartRequest, request: Request):
    mgr = request.app.state.session_mgr
    sid = mgr.start_session(body.mode)
    return {"session_id": sid, "mode": body.mode}


@router.post("/sessions/end")
async def end_session(request: Request):
    mgr = request.app.state.session_mgr
    bio = request.app.state.biofeedback

    profile = bio.profile
    summary = {
        "avg_stress":     round(profile.stress, 2),
        "avg_focus":      round(profile.focus, 2),
        "dominant_state": profile.state.value,
    }
    record = mgr.end_session(summary)
    if not record:
        raise HTTPException(400, "No active session")
    return {
        "session_id":     record.session_id,
        "duration_min":   record.duration_min,
        "avg_stress":     record.avg_stress,
        "avg_focus":      record.avg_focus,
        "dominant_state": record.dominant_state,
    }


@router.get("/sessions/history")
async def session_history(request: Request, limit: int = 10):
    mgr = request.app.state.session_mgr
    return {"sessions": mgr.get_history(limit)}


# ── Settings ──────────────────────────────────────────────────

@router.get("/settings")
async def get_settings(request: Request):
    mgr = request.app.state.session_mgr
    from dataclasses import asdict
    return asdict(mgr.settings)


@router.patch("/settings")
async def update_settings(body: SettingsRequest, request: Request):
    mgr = request.app.state.session_mgr
    s = mgr.settings
    if body.tuning_hz is not None:
        s.tuning_hz = body.tuning_hz
    if body.master_volume is not None:
        s.master_volume = max(0.0, min(1.0, body.master_volume))
    if body.default_mode is not None:
        s.default_mode = body.default_mode
    if body.theme is not None:
        s.theme = body.theme
    mgr.save_settings()
    from dataclasses import asdict
    return asdict(s)
