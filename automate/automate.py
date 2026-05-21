"""ARC README automation — screenshots and GIFs.

Captures screenshots and animated GIFs of the running ARC application
for use in the project README. Uses Playwright with Firefox (headless).

Usage:
    python automate.py all             # Everything (app must be running)
    python automate.py screenshots     # Static PNG screenshots only
    python automate.py gifs            # Animated GIFs only
    python automate.py gifs --only overview
    python automate.py gifs --only use-cases

    python automate.py all --frontend http://localhost:8081 --backend http://localhost:8000

Environment variables (used in Docker):
    FRONTEND_URL     Frontend URL           (default: http://localhost:5173)
    BACKEND_URL      Backend URL            (default: http://localhost:8000)
    MEDIA_DIR        Output directory       (default: ../media)
    DATA_DIR         Test data directory    (default: ../data)
    HTMLCOV_DIR      Coverage report dir    (default: ../htmlcov)

Configuration:
    VIEWPORT         Browser viewport size  (1280 x 900)
    GIF_FPS          Frames per second      (15)
    TEST_IMAGES      Dict mapping class labels to image paths inside DATA_DIR.
                     Change the file names here to pick different test images.
                     Each must produce the correct prediction for its class.

Requirements:
    uv sync && .venv/bin/playwright install firefox
"""

from __future__ import annotations

import argparse
import functools
import http.server
import io
import os
import socketserver
import sys
import threading
from pathlib import Path

from PIL import Image
from playwright.sync_api import Page, sync_playwright

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_SCRIPT_DIR = Path(__file__).resolve().parent
_DEFAULT_ROOT = _SCRIPT_DIR.parent

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
MEDIA_DIR = Path(os.environ.get("MEDIA_DIR", str(_DEFAULT_ROOT / "media")))
DATA_DIR = Path(os.environ.get("DATA_DIR", str(_DEFAULT_ROOT / "data")))
HTMLCOV_DIR = Path(os.environ.get("HTMLCOV_DIR", str(_DEFAULT_ROOT / "htmlcov")))

VIEWPORT = {"width": 1280, "height": 900}
GIF_FPS = 15

# ── Test images ──────────────────────────────────────────────────────────
# One representative image per class.  Change the file name to use a
# different sample — just make sure the model predicts the correct label.
#
# Available files live under  data/testing/<class_folder>/.
TEST_IMAGES = {
    "glioma": "testing/glioma_tumor/G_0002.jpg",
    "meningioma": "testing/meningioma_tumor/M_0021.jpg",
    "no-tumor": "testing/no_tumor/N_0009.jpg",
    "pituitary": "testing/pituitary_tumor/P_2603.jpg",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _log(msg: str) -> None:
    print(f"  {msg}")


def _wait(page: Page, ms: int = 500) -> None:
    """Wait for the page load event, then an extra pause."""
    page.wait_for_load_state("load", timeout=30_000)
    page.wait_for_timeout(ms)


def _wait_for_fonts(page: Page) -> None:
    """Block until all web fonts have finished loading."""
    page.evaluate("() => document.fonts.ready")
    page.wait_for_timeout(300)


def _capture(page: Page) -> Image.Image:
    """Capture the current viewport as a PIL Image."""
    return Image.open(io.BytesIO(page.screenshot()))


def _scroll_to(page: Page, y: int) -> None:
    """Instant scroll to a specific Y offset."""
    page.evaluate(f"window.scrollTo({{top: {y}, behavior: 'instant'}})")
    page.wait_for_timeout(50)


def _center_on(page: Page, selector: str) -> None:
    """Scroll so that the element matching *selector* is vertically centred."""
    page.evaluate(
        f"""(() => {{
            const el = document.querySelector('{selector}');
            if (!el) return;
            const rect = el.getBoundingClientRect();
            const absTop = rect.top + window.scrollY;
            const center = absTop + rect.height / 2 - window.innerHeight / 2;
            window.scrollTo({{top: Math.max(0, center), behavior: 'instant'}});
        }})()"""
    )
    page.wait_for_timeout(100)


def _upload_image(page: Page, image_path: Path) -> None:
    """Upload an image via the file input."""
    page.locator("#file-input").set_input_files(str(image_path))
    page.wait_for_selector(".preview-image", timeout=10_000)
    page.wait_for_timeout(500)


def _click_predict(page: Page) -> None:
    """Click the predict button and wait for a result."""
    page.click("button.primary-action")
    page.wait_for_selector(".status-value strong", timeout=60_000)
    page.wait_for_timeout(500)


# ---------------------------------------------------------------------------
# GIF recorder
# ---------------------------------------------------------------------------

class GifRecorder:
    """Collects (frame, duration_ms) pairs and writes an optimized GIF."""

    def __init__(self) -> None:
        self.frames: list[tuple[Image.Image, int]] = []

    def hold(self, page: Page, duration_ms: int, *, count: int = 1) -> None:
        """Capture one frame and display it for *duration_ms*."""
        img = _capture(page)
        for _ in range(count):
            self.frames.append((img, duration_ms // count if count > 1 else duration_ms))

    def smooth_scroll(
        self,
        page: Page,
        target_y: int,
        *,
        duration_s: float = 3.0,
    ) -> None:
        """Smooth scroll from current position to *target_y*, capturing at GIF_FPS."""
        frame_count = max(1, int(duration_s * GIF_FPS))
        frame_ms = 1000 // GIF_FPS
        start_y = page.evaluate("window.scrollY")
        delta = target_y - start_y

        for i in range(frame_count):
            # Ease in-out cubic for natural feel
            t = (i + 1) / frame_count
            ease = t * t * (3 - 2 * t)
            y = start_y + delta * ease
            _scroll_to(page, int(y))
            self.frames.append((_capture(page), frame_ms))

    def save(self, path: Path) -> None:
        """Write frames as a GIF."""
        if not self.frames:
            return

        images = [f.convert("RGBA") for f, _ in self.frames]
        durations = [d for _, d in self.frames]

        images[0].save(
            str(path),
            save_all=True,
            append_images=images[1:],
            duration=durations,
            loop=0,
            optimize=False,
            disposal=2,
        )

        size_mb = path.stat().st_size / (1024 * 1024)
        _log(f"saved {path.name}  ({size_mb:.1f} MB, {len(images)} frames)")


# ---------------------------------------------------------------------------
# Static screenshots
# ---------------------------------------------------------------------------

def take_screenshots(page: Page) -> None:
    """Capture all static PNG screenshots."""
    print("\n[screenshots]")

    # Leaderboard table
    page.goto(FRONTEND_URL)
    _wait(page, 2000)
    _wait_for_fonts(page)
    section = page.locator(".leaderboard-section")
    try:
        section.wait_for(timeout=30_000)
    except Exception:
        page.screenshot(path=str(MEDIA_DIR / "_debug-failure.png"), full_page=True)
        _log("FAIL  .leaderboard-section not found -- saved _debug-failure.png")
        raise
    section.screenshot(path=str(MEDIA_DIR / "metrics-leaderboard.png"))
    _log("saved metrics-leaderboard.png")

    # Swagger UI full-page
    page.goto(f"{BACKEND_URL}/docs")
    _wait(page, 2000)
    page.wait_for_selector(".swagger-ui", timeout=15_000)
    page.screenshot(path=str(MEDIA_DIR / "app-swagger-ui.png"), full_page=True)
    _log("saved app-swagger-ui.png")

    # Pytest coverage report
    _take_coverage_screenshot(page)


def _take_coverage_screenshot(page: Page) -> None:
    """Screenshot htmlcov/index.html by serving it via a temporary HTTP server."""
    index = HTMLCOV_DIR / "index.html"
    if not index.exists():
        _log("skip  htmlcov not found (run pytest --cov --cov-report=html)")
        return

    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
        directory=str(HTMLCOV_DIR),
    )
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as srv:
        port = srv.server_address[1]
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        try:
            page.goto(f"http://127.0.0.1:{port}/index.html")
            _wait(page)
            page.screenshot(path=str(MEDIA_DIR / "pytest-html.png"), full_page=True)
            _log("saved pytest-html.png")
        finally:
            srv.shutdown()


# ---------------------------------------------------------------------------
# GIF: app overview  (~12-15 s at 15 fps)
# ---------------------------------------------------------------------------

def take_overview_gif(page: Page) -> None:
    """Full page tour then upload + predict."""
    print("\n[gif] overview")
    rec = GifRecorder()
    test_img = DATA_DIR / TEST_IMAGES["glioma"]

    if not test_img.exists():
        _log(f"skip  test image not found: {test_img}")
        return

    page.goto(FRONTEND_URL)
    _wait(page, 1000)
    _wait_for_fonts(page)

    page_height = page.evaluate("document.body.scrollHeight")
    viewport_h = VIEWPORT["height"]
    max_scroll = max(0, page_height - viewport_h)

    # 1. Hold on hero section (top of page)
    _scroll_to(page, 0)
    rec.hold(page, 1500)

    # 2. Smooth scroll to bottom of page
    rec.smooth_scroll(page, max_scroll, duration_s=3.5)
    rec.hold(page, 1000)

    # 3. Smooth scroll back up, centred on the upload card
    upload_center = page.evaluate(
        """(() => {
            const el = document.querySelector('.upload-section');
            if (!el) return 0;
            const rect = el.getBoundingClientRect();
            const absTop = rect.top + window.scrollY;
            return Math.max(0, absTop + rect.height / 2 - window.innerHeight / 2);
        })()"""
    )
    rec.smooth_scroll(page, int(upload_center), duration_s=2.5)
    rec.hold(page, 1000)

    # 4. Upload image
    _upload_image(page, test_img)
    rec.hold(page, 1500)

    # 5. Predict
    _click_predict(page)
    rec.hold(page, 2500)

    rec.save(MEDIA_DIR / "app-overview.gif")


# ---------------------------------------------------------------------------
# GIFs: per-class use cases  (15 fps)
# ---------------------------------------------------------------------------

def take_use_case_gifs(page: Page) -> None:
    """One short GIF per tumor class, centred on the upload card."""
    print("\n[gif] use-cases")

    for label, rel_path in TEST_IMAGES.items():
        img_path = DATA_DIR / rel_path
        if not img_path.exists():
            _log(f"skip  {img_path} not found")
            continue

        rec = GifRecorder()

        page.goto(FRONTEND_URL)
        _wait(page, 800)
        _wait_for_fonts(page)

        # Centre on the upload card
        _center_on(page, ".upload-section")
        rec.hold(page, 1000)

        # Upload
        _upload_image(page, img_path)
        rec.hold(page, 1500)

        # Predict
        _click_predict(page)
        rec.hold(page, 2500)

        rec.save(MEDIA_DIR / f"app-use-case-{label}.gif")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="ARC README automation")
    parser.add_argument("--frontend", default=None, help="Override FRONTEND_URL")
    parser.add_argument("--backend", default=None, help="Override BACKEND_URL")

    sub = parser.add_subparsers(dest="command")
    sub.required = True
    sub.add_parser("all", help="Generate everything")
    sub.add_parser("screenshots", help="Static PNG screenshots only")
    gif_parser = sub.add_parser("gifs", help="Animated GIFs only")
    gif_parser.add_argument(
        "--only",
        nargs="+",
        choices=["overview", "use-cases"],
        help="Generate only specific GIF groups",
    )

    args = parser.parse_args()

    global FRONTEND_URL, BACKEND_URL
    if args.frontend:
        FRONTEND_URL = args.frontend
    if args.backend:
        BACKEND_URL = args.backend

    MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    for label, rel_path in TEST_IMAGES.items():
        path = DATA_DIR / rel_path
        if not path.exists():
            _log(f"warn  test image missing: {path}")

    print(f"Frontend : {FRONTEND_URL}")
    print(f"Backend  : {BACKEND_URL}")
    print(f"Output   : {MEDIA_DIR}")

    with sync_playwright() as pw:
        browser = pw.firefox.launch()
        ctx = browser.new_context(viewport=VIEWPORT)
        page = ctx.new_page()

        # Wait for frontend to be ready
        print("\n[waiting] frontend...")
        for attempt in range(30):
            try:
                page.goto(FRONTEND_URL, timeout=10_000)
                page.wait_for_selector(".hero-shell", timeout=10_000)
                _log(f"frontend ready  (attempt {attempt + 1})")
                break
            except Exception:
                if attempt == 29:
                    print("FAIL  frontend not reachable after 30 attempts")
                    sys.exit(1)
                page.wait_for_timeout(2000)

        try:
            if args.command in ("all", "screenshots"):
                take_screenshots(page)

            if args.command in ("all", "gifs"):
                targets = (
                    set(args.only)
                    if hasattr(args, "only") and args.only
                    else {"overview", "use-cases"}
                )
                if "overview" in targets:
                    take_overview_gif(page)
                if "use-cases" in targets:
                    take_use_case_gifs(page)
        finally:
            ctx.close()
            browser.close()

    print("\ndone")


if __name__ == "__main__":
    main()
