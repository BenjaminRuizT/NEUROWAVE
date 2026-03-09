"""
NeuroWave AI — EEG Biofeedback (Railway version)
=================================================
No audio output dependencies. Pure Python + numpy only.
"""

import numpy as np
import threading
import time
from typing import Dict, Optional, Callable, List
from dataclasses import dataclass, field
from core.audio_engine_stub import BrainwaveState


@dataclass
class EEGSample:
    timestamp: float
    channels: List[float]
    band_powers: Dict[str, float] = field(default_factory=dict)
    dominant_state: BrainwaveState = BrainwaveState.ALPHA
    stress_level: float = 0.0
    focus_score: float = 0.5
    meditation_score: float = 0.5


@dataclass
class CognitiveProfile:
    state: BrainwaveState = BrainwaveState.ALPHA
    stress: float = 0.0
    focus: float = 0.5
    meditation: float = 0.5
    arousal: float = 0.5
    valence: float = 0.5
    confidence: float = 0.0


class EEGSimulator:
    BAND_RANGES = {
        "delta": (0.5, 4.0), "theta": (4.0, 8.0), "alpha": (8.0, 12.0),
        "beta":  (12.0, 30.0), "gamma": (30.0, 80.0),
    }
    STATE_PROFILES = {
        BrainwaveState.DELTA: {"delta": 0.65, "theta": 0.15, "alpha": 0.10, "beta": 0.08, "gamma": 0.02},
        BrainwaveState.THETA: {"delta": 0.15, "theta": 0.55, "alpha": 0.20, "beta": 0.08, "gamma": 0.02},
        BrainwaveState.ALPHA: {"delta": 0.08, "theta": 0.15, "alpha": 0.55, "beta": 0.18, "gamma": 0.04},
        BrainwaveState.BETA:  {"delta": 0.05, "theta": 0.10, "alpha": 0.20, "beta": 0.55, "gamma": 0.10},
        BrainwaveState.GAMMA: {"delta": 0.03, "theta": 0.07, "alpha": 0.15, "beta": 0.35, "gamma": 0.40},
    }

    def __init__(self):
        self._target_state = BrainwaveState.ALPHA
        self._current_powers = dict(self.STATE_PROFILES[BrainwaveState.ALPHA])
        self._transition_speed = 0.02
        self._time = 0.0
        self._pink_rows = np.zeros(16)
        self._pink_idx = 0

    def set_state(self, state: BrainwaveState, transition_seconds: float = 5.0):
        self._target_state = state
        self._transition_speed = max(0.001, 1.0 / (transition_seconds * 10))

    def _update_powers(self):
        target = self.STATE_PROFILES[self._target_state]
        for band in self._current_powers:
            diff = target[band] - self._current_powers[band]
            self._current_powers[band] += diff * self._transition_speed * 5
            noise = np.random.normal(0, 0.002)
            self._current_powers[band] = max(0.001, self._current_powers[band] + noise)
        total = sum(self._current_powers.values())
        if total > 0:
            for b in self._current_powers:
                self._current_powers[b] /= total

    def get_sample(self) -> EEGSample:
        self._update_powers()
        self._time += 0.1

        channels = [
            sum(np.sqrt(p) * 50 * np.sin(2 * np.pi * np.random.uniform(*self.BAND_RANGES[b]) * self._time)
                for b, p in self._current_powers.items()) + np.random.normal(0, 2)
            for _ in range(4)
        ]

        bp = self._current_powers
        dominant = max(bp, key=bp.get)
        state_map = {"delta": BrainwaveState.DELTA, "theta": BrainwaveState.THETA,
                     "alpha": BrainwaveState.ALPHA, "beta": BrainwaveState.BETA,
                     "gamma": BrainwaveState.GAMMA}

        stress = float(np.clip((bp.get("beta", 0) - bp.get("alpha", 0) * 0.5) * 2, 0, 1))
        focus  = float(np.clip((bp.get("beta", 0) + bp.get("alpha", 0) * 0.5 - bp.get("delta", 0)) * 1.5, 0, 1))
        meditation = float(np.clip((bp.get("theta", 0) + bp.get("alpha", 0) - bp.get("beta", 0)) * 1.5, 0, 1))

        return EEGSample(
            timestamp=time.time(), channels=channels,
            band_powers=dict(self._current_powers),
            dominant_state=state_map[dominant],
            stress_level=stress, focus_score=focus, meditation_score=meditation,
        )


class MuseInterface:
    def __init__(self):
        self._available = False
        try:
            import pylsl
            self._available = True
        except ImportError:
            pass

    @property
    def available(self):
        return self._available


class BiofeedbackManager:
    def __init__(self, use_simulator: bool = True):
        self._simulator = EEGSimulator()
        self._muse = MuseInterface()
        self._use_simulator = use_simulator or not self._muse.available
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable] = []
        self._latest_sample: Optional[EEGSample] = None
        self._profile = CognitiveProfile()

    @property
    def latest(self):
        return self._latest_sample

    @property
    def profile(self):
        return self._profile

    def set_simulator_state(self, state: BrainwaveState, duration: float = 5.0):
        self._simulator.set_state(state, duration)

    def register_callback(self, fn: Callable):
        self._callbacks.append(fn)

    def start(self, sample_rate_hz: float = 10.0):
        self._running = True
        self._thread = threading.Thread(target=self._loop, args=(sample_rate_hz,), daemon=True)
        self._thread.start()
        print(f"[BiofeedbackManager] Started (simulator)")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _loop(self, rate_hz: float):
        interval = 1.0 / rate_hz
        while self._running:
            sample = self._simulator.get_sample()
            if sample:
                self._latest_sample = sample
                self._update_profile(sample)
                for cb in self._callbacks:
                    try:
                        cb(sample)
                    except Exception:
                        pass
            time.sleep(interval)

    def _update_profile(self, sample: EEGSample):
        alpha = 0.15
        self._profile.state      = sample.dominant_state
        self._profile.stress     += alpha * (sample.stress_level - self._profile.stress)
        self._profile.focus      += alpha * (sample.focus_score  - self._profile.focus)
        self._profile.meditation += alpha * (sample.meditation_score - self._profile.meditation)
        self._profile.confidence  = min(1.0, self._profile.confidence + 0.005)
