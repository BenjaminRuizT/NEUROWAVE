"""
NeuroWave AI — Adaptive Engine (Railway version)
=================================================
Provides mode configurations and AI recommendations.
Audio parameters are sent to the frontend via WebSocket/REST.
"""

from dataclasses import dataclass, field
from typing import Dict
from core.audio_engine_stub import BrainwaveState


@dataclass
class CognitiveMode:
    name: str
    description: str
    target_state: BrainwaveState
    binaural_enabled: bool = True
    binaural_volume: float = 0.35
    carrier_freq: float = 200.0
    music_volume: float = 0.35
    ambient_config: Dict[str, float] = field(default_factory=dict)
    adaptation_speed: float = 0.3
    beat_freq: float = 10.0


COGNITIVE_MODES: Dict[str, CognitiveMode] = {
    "sleep": CognitiveMode(
        name="Dormir", description="Ondas delta profundas para sueño reparador",
        target_state=BrainwaveState.DELTA,
        binaural_volume=0.25, carrier_freq=120.0, music_volume=0.20,
        ambient_config={"pink": 0.3, "rain": 0.2},
        adaptation_speed=0.1, beat_freq=2.0,
    ),
    "meditate": CognitiveMode(
        name="Meditar", description="Theta-alpha para meditación profunda",
        target_state=BrainwaveState.THETA,
        binaural_volume=0.30, carrier_freq=180.0, music_volume=0.30,
        ambient_config={"pink": 0.2, "ocean": 0.25},
        adaptation_speed=0.2, beat_freq=6.0,
    ),
    "study": CognitiveMode(
        name="Estudiar", description="Alpha para aprendizaje óptimo",
        target_state=BrainwaveState.ALPHA,
        binaural_volume=0.30, carrier_freq=200.0, music_volume=0.25,
        ambient_config={"white": 0.15},
        adaptation_speed=0.3, beat_freq=10.0,
    ),
    "focus": CognitiveMode(
        name="Enfoque Profundo", description="Beta para máxima concentración",
        target_state=BrainwaveState.BETA,
        binaural_volume=0.35, carrier_freq=220.0, music_volume=0.20,
        ambient_config={"brown": 0.2},
        adaptation_speed=0.4, beat_freq=18.0,
    ),
    "flow": CognitiveMode(
        name="Flow / Gamma", description="Gamma para rendimiento cognitivo pico",
        target_state=BrainwaveState.GAMMA,
        binaural_volume=0.40, carrier_freq=250.0, music_volume=0.25,
        ambient_config={},
        adaptation_speed=0.5, beat_freq=40.0,
    ),
}
