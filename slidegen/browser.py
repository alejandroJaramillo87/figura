"""TimeDriver: deterministic time-stepped frame capture.

The pinned contract every level builds on:

    TimeDriver.capture(slide_path, times_ms, out_dir) -> list[Path]
"""

from pathlib import Path

from slidegen.doctor import chromium_path

VIEWPORT = {"width": 1600, "height": 900}

LAUNCH_ARGS = [
    "--force-color-profile=srgb",
    "--disable-lcd-text",
    "--hide-scrollbars",
    "--force-device-scale-factor=1",
]

# Freeze all CSS animations before first paint. Runs at document creation,
# when documentElement may not exist yet, hence the observer fallback.
FREEZE_SCRIPT = """
(() => {
  const inject = () => {
    const st = document.createElement('style');
    st.textContent = '* { animation-play-state: paused !important; }';
    document.documentElement.appendChild(st);
  };
  if (document.documentElement) inject();
  else new MutationObserver((_, obs) => {
    if (document.documentElement) { inject(); obs.disconnect(); }
  }).observe(document, { childList: true });
})();
"""

SETTLE = "() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => r(0))))"

SCRUB = "t => document.getAnimations().forEach(a => { a.currentTime = t; })"


class TimeDriver:
    def capture(self, slide_path: Path, times_ms: list[int], out_dir: Path) -> list[Path]:
        """Load the slide once, freeze animations before first paint, then for
        each t in times_ms scrub all animations to t and screenshot. Returns
        PNG paths in times_ms order."""
        exe = chromium_path()
        if exe is None:
            raise RuntimeError(
                "No usable Chromium found — run `slidegen doctor` for fix hints."
            )
        out_dir.mkdir(parents=True, exist_ok=True)

        from playwright.sync_api import sync_playwright

        paths: list[Path] = []
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=str(exe), args=LAUNCH_ARGS)
            try:
                page = browser.new_page(viewport=VIEWPORT)
                page.add_init_script(FREEZE_SCRIPT)
                page.goto(slide_path.resolve().as_uri())
                page.evaluate("async () => { await document.fonts.ready; return 0; }")
                page.evaluate(SETTLE)
                for i, t in enumerate(times_ms):
                    page.evaluate(SCRUB, t)
                    page.evaluate(SETTLE)
                    frame = out_dir / f"{i:04d}.png"
                    page.screenshot(path=str(frame))
                    paths.append(frame)
            finally:
                browser.close()
        return paths
