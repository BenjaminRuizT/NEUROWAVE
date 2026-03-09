"""
NeuroWave AI — Audio Engine Stub (Server Side)
================================================
On Railway, audio synthesis runs in the browser via Web Audio API.
This module provides constants and data structures shared between
the backend logic and the frontend configuration.

No sounddevice, no PyAudio, no OS audio dependencies.
"""

from enum import Enum
from typing import Dict


class BrainwaveState(Enum):
    DELTA = "delta"
    THETA = "theta"
    ALPHA = "alpha"
    BETA  = "beta"
    GAMMA = "gamma"


BRAINWAVE_FREQUENCIES: Dict[BrainwaveState, float] = {
    BrainwaveState.DELTA: 2.0,
    BrainwaveState.THETA: 6.0,
    BrainwaveState.ALPHA: 10.0,
    BrainwaveState.BETA:  18.0,
    BrainwaveState.GAMMA: 40.0,
}

TUNING_STANDARD = 440.0
TUNING_HEALING  = 432.0

STATE_COLORS = {
    BrainwaveState.DELTA: "#7C4DFF",
    BrainwaveState.THETA: "#2979FF",
    BrainwaveState.ALPHA: "#00BCD4",
    BrainwaveState.BETA:  "#00E676",
    BrainwaveState.GAMMA: "#FFD740",
}
