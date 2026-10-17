"""URL -> handler table for the web API. Each handler gets (project, body, *url_groups)."""
from ..errors import PeriscopeError
from . import runs, targets

TYPES = {".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".png": "image/png",
         ".json": "application/json", ".jsonl": "text/plain", ".md": "text/plain", ".log": "text/plain",
         ".py": "text/plain"}
N = r"([A-Za-z0-9][A-Za-z0-9_.-]*)"
ROUTES = [
    ("GET", r"/api/state", lambda p, b: {"root": str(p.root), "config": p.config, "targets": targets.list_targets(p),
                                         "workflows": runs.list_workflows(p), "runs": runs.list_runs(p)}),
    ("POST", r"/api/screenshot", lambda p, b: targets.take_screenshot(p, b)),
    ("POST", r"/api/targets", lambda p, b: targets.create_target(p, b)),
    ("POST", rf"/api/targets/{N}/detail", lambda p, b, n: targets.add_detail(p, n, b)),
    ("POST", rf"/api/targets/{N}/test", lambda p, b, n: targets.test_target(p, n, b)),
    ("PATCH", rf"/api/targets/{N}", lambda p, b, n: targets.update_target(p, n, b)),
    ("DELETE", rf"/api/targets/{N}", lambda p, b, n: targets.delete_target(p, n)),
    ("POST", rf"/api/workflows/{N}/run", lambda p, b, n: runs.start_run(p, n, b)),
    ("GET", rf"/api/runs/{N}", lambda p, b, n: runs.get_run(p, n)),
    ("POST", rf"/api/runs/{N}/decision", lambda p, b, n: runs.decide(p, n, b)),
]
STATUS = {FileNotFoundError: 404, targets.Conflict: 409, PermissionError: 403,
          PeriscopeError: 422, ValueError: 400, KeyError: 400}

