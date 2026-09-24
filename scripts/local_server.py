"""Range-capable local HTTP server for dist/ (see #9: file:// can't load local media,
and Python's stdlib http.server ignores Range headers, which breaks <audio> seeking)."""
import http.server
import os
import re
import threading
from contextlib import contextmanager

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")


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
