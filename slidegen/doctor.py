"""Environment checks: ffmpeg on PATH, a usable Chromium for Playwright."""

import os
import shutil
import sys
from pathlib import Path


def ffmpeg_path() -> Path | None:
    """Resolve the ffmpeg executable encode.py will run.

    Order: SLIDEGEN_FFMPEG override, ffmpeg on PATH, then the static
    binary bundled with the imageio-ffmpeg package.
    """
    override = os.environ.get("SLIDEGEN_FFMPEG")
    if override:
        p = Path(override)
        return p if p.exists() else None
    found = shutil.which("ffmpeg")
    if found:
        return Path(found)
    try:
        import imageio_ffmpeg

        return Path(imageio_ffmpeg.get_ffmpeg_exe())
    except Exception:
        return None


def check_ffmpeg() -> str | None:
    if ffmpeg_path() is None:
        return (
            "No usable ffmpeg found.\n"
            "  Fix: pip install imageio-ffmpeg  (bundles a static ffmpeg)\n"
            "  Or install system ffmpeg (apt-get install ffmpeg / brew install ffmpeg)\n"
            "  Or point SLIDEGEN_FFMPEG at an existing ffmpeg binary."
        )
    return None


def chromium_path() -> Path | None:
    """Resolve the Chromium executable TimeDriver will launch.

    SLIDEGEN_CHROMIUM overrides Playwright's bundled browser, for
    environments that pre-install Chromium at a fixed path.
    """
    override = os.environ.get("SLIDEGEN_CHROMIUM")
    if override:
        p = Path(override)
        return p if p.exists() else None
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            p = Path(pw.chromium.executable_path)
        return p if p.exists() else None
    except Exception:
        return None


def check_chromium() -> str | None:
    if chromium_path() is None:
        return (
            "No usable Chromium found for Playwright.\n"
            "  Fix: playwright install chromium\n"
            "  Or point SLIDEGEN_CHROMIUM at an existing Chromium binary."
        )
    return None


def run_doctor(quiet: bool = False) -> bool:
    """Run all checks. Prints results; returns True if healthy."""
    problems = [p for p in (check_ffmpeg(), check_chromium()) if p]
    if problems:
        for p in problems:
            print(f"ERROR: {p}", file=sys.stderr)
        return False
    if not quiet:
        print("slidegen doctor: all checks passed (ffmpeg, Chromium)")
    return True
