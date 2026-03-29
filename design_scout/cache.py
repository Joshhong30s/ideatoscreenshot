"""Simple file-based cache to avoid re-processing the same URLs."""

import json
from pathlib import Path
from typing import Dict, Optional, Any


CACHE_FILENAME = ".design_scout_cache.json"


class Cache:
    """File-based cache for screenshots and scores.

    Stores results keyed by normalized URL so repeated runs
    skip already-processed sites.
    """

    def __init__(self, output_dir: str):
        self.path = Path(output_dir) / CACHE_FILENAME
        self.data: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self.data = {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # -- screenshots --
    def get_screenshots(self, url: str) -> Optional[Dict[str, str]]:
        """Return cached screenshot paths if they still exist on disk."""
        entry = self.data.get(url, {})
        shots = entry.get("screenshots")
        if not shots:
            return None
        # Verify files still exist
        for path in shots.values():
            if not Path(path).exists():
                return None
        return shots

    def set_screenshots(self, url: str, screenshots: Dict[str, str]) -> None:
        self.data.setdefault(url, {})["screenshots"] = screenshots

    # -- scores --
    def get_score(self, url: str) -> Optional[Dict]:
        return self.data.get(url, {}).get("score")

    def set_score(self, url: str, score: Dict) -> None:
        self.data.setdefault(url, {})["score"] = score
