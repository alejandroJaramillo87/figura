"""Phase 1 spike: TimeDriver scrub correctness and determinism.

Fixture: box1 animates left->right (translateX 0 -> 800px) over 1000ms linear;
box2 same path over 500ms with a 400ms delay (idle-phase scrub case).
Boxes are 100x100; box1 at top=100, box2 at top=300.
"""

from pathlib import Path

import numpy as np
import pytest
from PIL import Image
from skimage.metrics import structural_similarity

from slidegen.browser import TimeDriver

FIXTURE = Path(__file__).parent / "fixtures" / "spike.html"
TIMES_MS = [0, 200, 500, 900]

RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)


def px(frame: Path, x: int, y: int) -> tuple[int, int, int]:
    return Image.open(frame).convert("RGB").getpixel((x, y))


def close(actual, expected, tol=12) -> bool:
    return all(abs(a - e) <= tol for a, e in zip(actual, expected))


@pytest.fixture(scope="module")
def frames(tmp_path_factory) -> list[Path]:
    out = tmp_path_factory.mktemp("frames")
    return TimeDriver().capture(FIXTURE, TIMES_MS, out)


def test_midpoint(frames):
    # At t=500ms box1 (linear, 0->800 over 1000ms) is at x=400; its center
    # is (450, 150). Its start position must be vacated.
    f500 = frames[2]
    assert close(px(f500, 450, 150), RED), "box1 not at midpoint at t=500ms"
    assert close(px(f500, 50, 150), WHITE), "box1 still at start at t=500ms"


def test_delayed_start(frames):
    # box2 has a 400ms delay: at t=200ms it must sit at its initial position;
    # at t=900ms (animation end) it must be fully at x=800.
    f200, f900 = frames[1], frames[3]
    assert close(px(f200, 50, 350), BLUE), "box2 moved during its delay"
    assert close(px(f900, 850, 350), BLUE), "box2 not at end position at t=900ms"
    assert close(px(f900, 50, 350), WHITE), "box2 still at start at t=900ms"


def test_determinism(frames, tmp_path):
    second = TimeDriver().capture(FIXTURE, TIMES_MS, tmp_path / "again")
    for a, b in zip(frames, second):
        ga = np.asarray(Image.open(a).convert("L"))
        gb = np.asarray(Image.open(b).convert("L"))
        score = structural_similarity(ga, gb)
        assert score >= 0.99, f"SSIM {score:.4f} between renders of {a.name}"
