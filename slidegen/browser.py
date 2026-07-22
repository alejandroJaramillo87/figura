"""TimeDriver: deterministic time-stepped frame capture.

Implemented in Phase 1. The pinned contract:

    TimeDriver.capture(slide_path, times_ms, out_dir) -> list[Path]
"""

from pathlib import Path


class TimeDriver:
    def capture(self, slide_path: Path, times_ms: list[int], out_dir: Path) -> list[Path]:
        """Load the slide once, freeze animations before first paint, then for
        each t in times_ms scrub all animations to t and screenshot. Returns
        PNG paths in times_ms order."""
        raise NotImplementedError("Phase 1")
