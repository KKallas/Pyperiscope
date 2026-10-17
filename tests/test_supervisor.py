"""The escalation ladder with a workflow that needs no screen: step `check`
fails until a file `fixed` exists. A fake agent (or the 'human') creates it."""
import json
import sys
import threading
import time

from pyperiscope.supervisor import Supervisor

WORKFLOW = '''
from pathlib import Path
from pyperiscope import Workflow
wf = Workflow(__file__)

@wf.step
def prepare(s):
    Path("prepared").touch()

@wf.step
def check(s):
    if not Path("fixed").exists():
        raise RuntimeError("not fixed yet")

if __name__ == "__main__":
    wf.main()
'''


class FakeAgent(Supervisor):
    def __init__(self, *a, fixes=True, **kw):
        super().__init__(*a, **kw)
        self.fixes = fixes

    def agent_command(self, prompt, images):
        assert "failure.json" in prompt and images[0].endswith("failure-annotated.png")
        action = "open('fixed', 'w')" if self.fixes else "pass"
        return [sys.executable, "-c", action]


def setup(project):
    (project.workflows / "flaky.py").write_text(WORKFLOW)


def test_agent_fix_then_rerun_from_failed_step(project):
    setup(project)
    state = FakeAgent(project, "flaky", agent="claude", human=False).run()
    assert state["status"] == "done"
    first, second = state["attempts"]
    assert first["result"] == "failed" and first["step"] == "check" and first["fixed_by"].startswith("claude")
    assert second["from_step"] == "check" and second["result"] == "ok"


def test_agent_fails_then_no_human_means_failed(project):
    setup(project)
    state = FakeAgent(project, "flaky", agent="claude", agent_attempts=2, human=False, fixes=False).run()
    assert state["status"] == "failed"
    assert len(state["attempts"]) == 3        # run, fix, run, fix, run


def test_human_retry_after_agent_gives_up(project):
    setup(project)
    sup = FakeAgent(project, "flaky", agent="claude", agent_attempts=1, fixes=False)

    def operator():
        run_json = sup.dir / "run.json"
        while json.loads(run_json.read_text())["status"] != "needs_human":
            time.sleep(0.05)
        (project.root / "fixed").touch()
        (sup.dir / "decision.json").write_text(json.dumps({"action": "retry", "from_step": "check"}))

    threading.Thread(target=operator, daemon=True).start()
    state = sup.run()
    assert state["status"] == "done"
    assert [a["fixed_by"].split(" ")[0] for a in state["attempts"][:-1]] == ["claude", "human"]


def test_human_abort(project):
    setup(project)
    sup = Supervisor(project, "flaky", agent="none")
    threading.Timer(0.5, lambda: (sup.dir / "decision.json").write_text('{"action": "abort"}')).start()
    assert sup.run()["status"] == "aborted"


def test_agent_prompt_names_checklist_and_tools_exclude_run(project):
    setup(project)
    sup = Supervisor(project, "flaky", agent="claude", human=False)
    attempt = {"dir": "runs/x/attempt-1", "kind": "ambiguous", "step": "check"}
    sup.state["attempts"].append(attempt)
    from pyperiscope.supervisor import layer2
    prompt = layer2.PROMPT.format(workflow="flaky", attempt=attempt["dir"], checklist=layer2.QRH["ambiguous"],
                                  step="check", notes="runs/x/fix-1.md")
    assert "Q1 TARGET AMBIGUOUS" in prompt and "manual/4-qrh.md" in prompt
    cmd = sup.agent_command(prompt, [])
    tools = cmd[cmd.index("--allowedTools") + 1]
    assert "pyperiscope target" in tools and "pyperiscope run" not in tools and "Bash(pyperiscope:*)" not in tools
