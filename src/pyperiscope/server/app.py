"""The setup/operator web server: standard library only.

    pyperiscope serve                      # http://127.0.0.1:8765
    pyperiscope serve --host 0.0.0.0       # reachable from a phone/laptop; a token is required

Serves the single-page UI (static/), a small JSON API, and read-only project
files (screenshots, target patches, run reports) under /files/.
"""
import json
import re
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .routes import ROUTES, STATUS, TYPES

STATIC = Path(__file__).parent / "static"


class Handler(BaseHTTPRequestHandler):
    project, token = None, None

    def log_message(self, fmt, *args):
        pass

    def send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def authorized(self, query):
        given = self.headers.get("X-Token") or query.get("token", [None])[0]
        return not self.token or (given and secrets.compare_digest(given, self.token))

    def handle_any(self, method):
        url = urlparse(self.path)
        if url.path in ("/", "/index.html"):
            return self.send(200, (STATIC / "index.html").read_bytes(), "text/html")
        if url.path.startswith("/static/"):
            path = STATIC / Path(url.path).name
            return self.send(200, path.read_bytes(), TYPES.get(path.suffix, "text/plain")) if path.exists() \
                else self.send(404, {"error": "not found"})
        if not self.authorized(parse_qs(url.query)):
            return self.send(401, {"error": "missing or wrong token"})
        if url.path.startswith("/files/") and method == "GET":
            return self.send_file(url.path[len("/files/"):])
        for verb, pattern, fn in ROUTES:
            found = re.fullmatch(pattern, url.path)
            if verb == method and found:
                return self.call(fn, found.groups())
        self.send(404, {"error": f"no route {method} {url.path}"})

    def call(self, fn, args):
        try:
            length = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(length) or b"{}") if length else {}
            self.send(200, fn(self.project, body, *args))
        except Exception as error:
            code = next((c for t, c in STATUS.items() if isinstance(error, t)), 500)
            payload = {"error": str(error), "kind": getattr(error, "kind", type(error).__name__)}
            if getattr(error, "matches", None):
                payload["matches"] = [m.to_dict() for m in error.matches]
            self.send(code, payload)

    def send_file(self, relative):
        try:
            path = self.project.resolve(relative)
        except PermissionError:
            return self.send(403, {"error": "outside project"})
        if not path.is_file() or path.suffix not in TYPES:
            return self.send(404, {"error": "not found"})
        self.send(200, path.read_bytes(), TYPES[path.suffix])

    def do_GET(self):
        self.handle_any("GET")

    def do_POST(self):
        self.handle_any("POST")

    def do_PATCH(self):
        self.handle_any("PATCH")

    def do_DELETE(self):
        self.handle_any("DELETE")


def serve(project, host="127.0.0.1", port=8765, token=None):
    if host not in ("127.0.0.1", "localhost") and not token:
        token = secrets.token_urlsafe(16)
    handler = type("BoundHandler", (Handler,), {"project": project, "token": token})
    server = ThreadingHTTPServer((host, port), handler)
    shown = "127.0.0.1" if host in ("0.0.0.0", "") else host
    print(f"Pyperiscope UI: http://{shown}:{port}/" + (f"?token={token}" if token else ""))
    print(f"project: {project.root}")
    return server
