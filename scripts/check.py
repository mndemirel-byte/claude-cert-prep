"""Smoke test with Playwright: serves dist/ over HTTP (with Range support, so <audio>
narration loads and seeks work — file:// can't load local media at all, and Python's
stdlib http.server ignores Range headers by default), toggles EN, runs a full mock exam,
and exercises the Domain Playlist / Listening Position narration features (#9)."""
import http.server
import os
import re
import sys
import threading
from contextlib import contextmanager

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")

CAPTURE_AUDIO_SCRIPT = """
    const OrigAudio = window.Audio;
    window.Audio = function(...args) {
        const a = new OrigAudio(...args);
        window.__lastAudio = a;
        return a;
    };
"""


class RangeRequestHandler(http.server.SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler with minimal Range support, so <audio> seeking works."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST, **kwargs)

    def send_head(self):
        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            return super().send_head()
        range_header = self.headers.get("Range")
        if not range_header:
            return super().send_head()
        m = re.match(r"bytes=(\d*)-(\d*)", range_header)
        if not m or not (m.group(1) or m.group(2)):
            return super().send_head()
        file_size = os.path.getsize(path)
        start = int(m.group(1)) if m.group(1) else 0
        end = int(m.group(2)) if m.group(2) else file_size - 1
        end = min(end, file_size - 1)
        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        self._range_len = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        if hasattr(self, "_range_len"):
            remaining = self._range_len
            while remaining > 0:
                chunk = source.read(min(65536, remaining))
                if not chunk:
                    break
                outputfile.write(chunk)
                remaining -= len(chunk)
        else:
            super().copyfile(source, outputfile)

    def log_message(self, format, *args):
        pass


@contextmanager
def serve_dist(port=8123):
    httpd = http.server.ThreadingHTTPServer(("localhost", port), RangeRequestHandler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        yield f"http://localhost:{port}/"
    finally:
        httpd.shutdown()


def narration_checks(pg, base_url, errs):
    """Domain Playlist auto-advance / domain-end stop / Listening Position resume (#9)."""
    # a same-origin goto that only changes the hash is a same-document navigation
    # (app.js never re-runs, so in-memory state like the active language survives);
    # force a real reload for a clean baseline.
    pg.evaluate("localStorage.clear()")
    pg.evaluate("location.hash = '#domain-2'")
    pg.reload()
    pg.wait_for_timeout(300)

    lessons = pg.query_selector_all("#domain-2 .lesson")
    ids = [l.get_attribute("data-lesson-id") for l in lessons]

    # 1) auto-advance to the next Lesson in the Domain when Narration ends
    lessons[0].query_selector(".lesson-play").click()
    pg.wait_for_timeout(500)
    src_before = pg.evaluate("window.__lastAudio.src")
    pg.evaluate("window.__lastAudio.dispatchEvent(new Event('ended'))")
    pg.wait_for_timeout(300)
    src_after = pg.evaluate("window.__lastAudio.src")
    playing_ids = pg.evaluate(
        "Array.from(document.querySelectorAll('#domain-2 .lesson'))"
        ".filter(el => el.querySelector('.lesson-play').classList.contains('playing'))"
        ".map(el => el.dataset.lessonId)"
    )
    if src_before == src_after or playing_ids != [ids[1]]:
        errs.append(f"auto-advance failed: src unchanged={src_before == src_after}, playing={playing_ids} (expected [{ids[1]!r}])")

    # 2) playback stops after the Domain's last Lesson (no cross-domain continuation)
    lessons[-1].query_selector(".lesson-play").click()
    pg.wait_for_timeout(500)
    pg.evaluate("window.__lastAudio.dispatchEvent(new Event('ended'))")
    pg.wait_for_timeout(300)
    still_playing = pg.evaluate("document.querySelectorAll('.lesson-play.playing').length")
    if still_playing != 0:
        errs.append(f"domain-end stop failed: {still_playing} lesson(s) still marked playing after the last lesson ended")

    # 3) Listening Position resume: play, seek, let the throttle window pass, reload
    pg.click("#langtoggle")  # switch to EN so restoring it on reload is a meaningful check
    pg.wait_for_timeout(200)
    lessons[1].query_selector(".lesson-play").click()  # 2.2
    pg.wait_for_timeout(800)
    pg.evaluate("window.__lastAudio.currentTime = 120")
    pg.wait_for_timeout(300)
    pg.wait_for_timeout(2800)  # pass the 3s persist throttle
    pg.evaluate("window.__lastAudio.dispatchEvent(new Event('timeupdate'))")
    pg.wait_for_timeout(200)

    # a same-origin goto that only changes the hash is a same-document navigation
    # (app.js never re-runs); force a real reload to simulate reopening the app.
    pg.evaluate("location.hash = '#domain-2'")
    pg.reload()
    pg.wait_for_timeout(300)
    lang_restored = pg.evaluate("document.documentElement.dataset.lang")
    lessons2 = pg.query_selector_all("#domain-2 .lesson")
    lessons2[1].query_selector(".lesson-play").click()
    pg.wait_for_timeout(1500)
    resumed_time = pg.evaluate("window.__lastAudio.currentTime")
    if lang_restored != "en" or resumed_time < 100:
        errs.append(f"resume failed: lang_restored={lang_restored!r} (expected 'en'), resumed_time={resumed_time} (expected >=100)")


with serve_dist() as base_url:
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 900, "height": 1000})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.add_init_script(CAPTURE_AUDIO_SCRIPT)  # must be added before the first goto
        pg.goto(base_url)
        pg.click("#langtoggle")
        missing = pg.evaluate("MOCK_POOL.filter(q=>!q.en).length")
        pg.goto(base_url + "#mock")
        pg.wait_for_timeout(200)
        pg.click("#mock-start")
        pg.wait_for_timeout(300)
        n = pg.evaluate("document.querySelectorAll('#mock-palette button').length")
        for i in range(n):
            pg.click("#mock-q .opt[data-k='B']")
            if i < n - 1:
                pg.click("#mock-next")
        pg.on("dialog", lambda d: d.accept())
        pg.click("#mock-finish")
        pg.wait_for_timeout(300)
        score = pg.evaluate("document.querySelector('.bigscore').textContent")

        narration_checks(pg, base_url, errs)

        b.close()

print(f"mock questions: {n}, score with all-B: {score}, pool items without EN: {missing}, errors: {errs}")
sys.exit(1 if errs or missing else 0)
