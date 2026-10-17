"""`pyperiscope init | doctor | serve | screenshot | run | new-workflow`."""
import sys
import time
from importlib import resources
from pathlib import Path

from ..project import Project
from .targets import emit

SCAFFOLD = resources.files("pyperiscope") / "scaffold"
SCAFFOLD_FILES = {"AGENTS.md": "AGENTS.md", "CLAUDE.md": "CLAUDE.md", ".gitignore": "gitignore.txt"}


def add_parsers(sub):
    p = sub.add_parser("init", help="create a project folder (settings, AGENTS.md, operations manual, example workflow)")
    p.add_argument("dir", nargs="?", default=".")
    sub.add_parser("doctor", help="check permissions and tools")
    p = sub.add_parser("serve", help="start the web UI")
    p.add_argument("--host", default="127.0.0.1"); p.add_argument("--port", type=int, default=8765); p.add_argument("--token")
    p = sub.add_parser("screenshot", help="capture the screen to screens/ (prints the path)")
    p.add_argument("--delay", type=float, default=0); p.add_argument("--out")
    p = sub.add_parser("run", help="run a workflow with the agent -> human escalation ladder")
    p.add_argument("workflow"); p.add_argument("--from-step"); p.add_argument("--run-id")
    p.add_argument("--agent", choices=["claude", "codex", "none"]); p.add_argument("--model")
    p.add_argument("--attempts", type=int, help="agent fix attempts per failing step")
    p.add_argument("--no-human", action="store_true", help="fail instead of waiting for an operator")
    p.add_argument("--input", choices=["isolated", "shared", "dry"])
    p = sub.add_parser("new-workflow", help="create workflows/<name>.py from the template")
    p.add_argument("name"); p.add_argument("--app")


def init(args):
    root = Path(args.dir).resolve()
    Project.create(root)
    for name, source in SCAFFOLD_FILES.items():
        if not (root / name).exists():
            (root / name).write_text((SCAFFOLD / source).read_text())
    manual = root / "manual"
    manual.mkdir(exist_ok=True)
    for page in (SCAFFOLD.parent / "manual").iterdir():
        if page.name.endswith(".md") and not (manual / page.name).exists():
            (manual / page.name).write_text(page.read_text())
    project = Project(root)
    example = project.workflows / "example_textedit.py"
    if not example.exists():
        example.write_text((SCAFFOLD / "workflows" / "example_textedit.py").read_text())
    print(f"project ready: {root}\nnext: pyperiscope doctor, then pyperiscope serve")
    return 0


def doctor(args):
    from .doctor import checks
    ok = True
    for name, passed, advice in checks():
        ok &= passed or name.startswith("optional")
        print(f"{'✓' if passed else '✗'} {name}" + ("" if passed else f"\n    → {advice}"))
    return 0 if ok else 1


def serve(project, args):
    from ..server.app import serve as make_server
    server = make_server(project, args.host, args.port, args.token)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


def screenshot(project, args):
    from ..screen import capture
    time.sleep(args.delay)
    shot = capture(project.config["monitor"])
    path = shot.save(args.out or project.screens / f"{Project.new_id('screen')}.png")
    return emit({"shot": project.relative(path) if not args.out else str(path),
                 "size": list(shot.size), "scale": shot.scale})


def run(project, args):
    from ..supervisor import Supervisor
    sup = Supervisor(project, args.workflow, args.run_id, args.agent, args.model, args.attempts, not args.no_human)
    print(f"[pyperiscope] run {sup.id} -> {project.relative(sup.dir)}")
    state = sup.run(args.from_step, args.input)
    return 0 if state["status"] == "done" else 1


def new_workflow(project, args):
    path = project.workflows / f"{args.name}.py"
    if path.exists():
        print(f"{path} exists", file=sys.stderr)
        return 1
    text = (SCAFFOLD / "workflows" / "template.py").read_text()
    path.write_text(text.replace("APP_NAME", repr(args.app) if args.app else "None"))
    print(path)
    return 0
