"""Web API for workflows and supervised runs (including the human step)."""
import ast
import json
import subprocess
import sys

from ..supervisor.layer1 import tool_env


def workflow_steps(path):
    """Step names, read from the source (functions decorated with *.step)."""
    tree = ast.parse(path.read_text())
    return [node.name for node in tree.body if isinstance(node, ast.FunctionDef)
            and any(isinstance(d, ast.Attribute) and d.attr == "step" for d in node.decorator_list)]


def list_workflows(project):
    out = []
    for name in project.workflow_names():
        try:
            steps = workflow_steps(project.workflows / f"{name}.py")
        except SyntaxError as error:
            steps = [f"(syntax error: {error.msg} line {error.lineno})"]
        out.append({"name": name, "steps": steps})
    return out


def list_runs(project, limit=30):
    runs = []
    for path in project.runs.glob("*/run.json"):
        try:
            runs.append(json.loads(path.read_text()))
        except json.JSONDecodeError:
            continue
    runs.sort(key=lambda r: r.get("created", 0), reverse=True)
    return [{k: r.get(k) for k in ("id", "workflow", "status", "step", "message", "created", "updated")}
            for r in runs[:limit]]


def get_run(project, run_id):
    folder = project.resolve(f"runs/{run_id}")
    run = json.loads((folder / "run.json").read_text())
    last = run["attempts"][-1] if run.get("attempts") else None
    if last:
        failure = project.resolve(last["dir"]) / "failure.json"
        run["failure"] = json.loads(failure.read_text()) if failure.exists() else None
    run["notes"] = {p.name: p.read_text() for p in sorted(folder.glob("fix-*.md"))}
    path = project.workflows / f"{run['workflow']}.py"
    run["steps"] = workflow_steps(path) if path.exists() else []
    return run


def decide(project, run_id, body):
    """The operator's answer for a run waiting on a human: retry or abort."""
    action = body.get("action")
    if action not in ("retry", "abort"):
        raise ValueError("action must be 'retry' or 'abort'")
    run = get_run(project, run_id)
    if run["status"] != "needs_human":
        raise ValueError(f"run {run_id} is {run['status']}, not waiting for a human")
    decision = {"action": action, "from_step": body.get("from_step")}
    (project.resolve(f"runs/{run_id}") / "decision.json").write_text(json.dumps(decision))
    return decision


def start_run(project, name, body):
    """Start `pyperiscope run` in the background; returns its run id."""
    if name not in project.workflow_names():
        raise FileNotFoundError(f"no workflow {name!r}")
    run_id = project.new_id(name)
    cmd = [sys.executable, "-m", "pyperiscope.cli", "run", name, "--run-id", run_id]
    for flag in ("agent", "from_step", "input"):
        if body.get(flag):
            cmd += [f"--{flag.replace('_', '-')}", str(body[flag])]
    log = open(project.runs / f"{run_id}.log", "w")
    subprocess.Popen(cmd, cwd=project.root, env=tool_env(), stdout=log, stderr=subprocess.STDOUT,
                     stdin=subprocess.DEVNULL, start_new_session=True)
    return {"run_id": run_id}
