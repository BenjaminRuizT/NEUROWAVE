"""NeuroWave AI — Session Manager (Railway version)"""

import json, time
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path

SESSIONS_DIR = Path("sessions")
CONFIG_FILE  = Path("config/user_config.json")


@dataclass
class UserSettings:
    tuning_hz: float = 432.0
    master_volume: float = 0.7
    default_mode: str = "study"
    binaural_enabled: bool = True
    music_enabled: bool = True
    eeg_simulator: bool = True
    theme: str = "dark"
    onboarding_done: bool = False


@dataclass
class SessionRecord:
    session_id: str
    mode: str
    start_time: float
    end_time: float = 0.0
    duration_min: float = 0.0
    avg_stress: float = 0.0
    avg_focus: float = 0.0
    dominant_state: str = "alpha"


class SessionManager:
    def __init__(self):
        SESSIONS_DIR.mkdir(exist_ok=True)
        CONFIG_FILE.parent.mkdir(exist_ok=True)
        self.settings = self._load_settings()
        self._current: Optional[SessionRecord] = None

    def _load_settings(self) -> UserSettings:
        if CONFIG_FILE.exists():
            try:
                return UserSettings(**json.loads(CONFIG_FILE.read_text()))
            except Exception:
                pass
        return UserSettings()

    def save_settings(self):
        CONFIG_FILE.write_text(json.dumps(asdict(self.settings), indent=2))

    def start_session(self, mode: str) -> str:
        sid = f"session_{int(time.time())}"
        self._current = SessionRecord(session_id=sid, mode=mode, start_time=time.time())
        return sid

    def end_session(self, summary: Dict = None) -> Optional[SessionRecord]:
        if not self._current:
            return None
        s = self._current
        s.end_time = time.time()
        s.duration_min = round((s.end_time - s.start_time) / 60, 1)
        if summary:
            s.avg_stress = summary.get("avg_stress", 0.0)
            s.avg_focus  = summary.get("avg_focus", 0.0)
            s.dominant_state = summary.get("dominant_state", "alpha")
        path = SESSIONS_DIR / f"{s.session_id}.json"
        path.write_text(json.dumps(asdict(s), indent=2))
        self._current = None
        return s

    def get_history(self, limit: int = 10) -> List[Dict]:
        files = sorted(SESSIONS_DIR.glob("session_*.json"), reverse=True)[:limit]
        result = []
        for f in files:
            try:
                result.append(json.loads(f.read_text()))
            except Exception:
                pass
        return result

    @property
    def current_session(self):
        return self._current
