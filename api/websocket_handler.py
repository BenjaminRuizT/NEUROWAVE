"""
NeuroWave AI — WebSocket Handler
==================================
Streams real-time EEG + cognitive state data to the browser at 10 Hz.
The frontend uses this to update the visualizer and adapt audio parameters.
"""

import asyncio
import json
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set

router = APIRouter(tags=["WebSocket"])

# Track all connected clients
_clients: Set[WebSocket] = set()


@router.websocket("/ws/eeg")
async def eeg_stream(websocket: WebSocket):
    """
    Streams EEG samples and cognitive profile at 10 Hz.

    Message format (JSON):
    {
      "type": "eeg",
      "ts": 1234567890.123,
      "state": "alpha",
      "stress": 0.23,
      "focus": 0.71,
      "meditation": 0.55,
      "confidence": 0.82,
      "band_powers": {
        "delta": 0.08, "theta": 0.15,
        "alpha": 0.55, "beta": 0.18, "gamma": 0.04
      },
      "beat_freq": 10.0,
      "audio_params": {
        "carrier_freq": 200.0,
        "binaural_volume": 0.35
      }
    }
    """
    await websocket.accept()
    _clients.add(websocket)

    try:
        bio = websocket.app.state.biofeedback

        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "NeuroWave AI stream active",
            "sample_rate_hz": 10,
        })

        while True:
            sample  = bio.latest
            profile = bio.profile

            if sample:
                msg = {
                    "type": "eeg",
                    "ts":   round(time.time(), 3),
                    "state": profile.state.value,
                    "stress":     round(profile.stress, 3),
                    "focus":      round(profile.focus, 3),
                    "meditation": round(profile.meditation, 3),
                    "confidence": round(profile.confidence, 3),
                    "band_powers": {
                        k: round(v, 4) for k, v in sample.band_powers.items()
                    },
                    "channels": [round(c, 2) for c in sample.channels[:4]],
                }
                await websocket.send_json(msg)

            await asyncio.sleep(0.1)   # 10 Hz

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[WS] Error: {e}")
    finally:
        _clients.discard(websocket)


@router.websocket("/ws/ping")
async def ping(websocket: WebSocket):
    """Latency test endpoint."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(data)
    except WebSocketDisconnect:
        pass
