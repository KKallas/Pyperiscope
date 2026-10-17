"""Supervisor, layer 3: the escalation ladder.

    run ──ok──▶ done
     │ failed
     ▼
    agent fix (up to agent_attempts per failing step) ──▶ run again
     │ still failing / agent gave up / setup problem
     ▼
    human: run.json status = needs_human, notification, web UI shows the
    failure; the person fixes targets there (validated the same way) and
    presses Retry (or Abort). The supervisor waits for runs/<id>/decision.json.

Esc (stopped) ends the run immediately and never escalates.
"""
import json
import time

from ..safety import notify
from ..workflow import EXIT_OK, EXIT_SETUP, EXIT_STOPPED
from .layer2 import Supervisor as Base

HUMAN_POLL_SECONDS = 1.0


class Supervisor(Base):
    def run(self, from_step=None, input=None):
        tries, last_step = 0, object()
        while True:
            attempt = self.launch(from_step, input)
            if attempt["exit"] == EXIT_OK:
                return self.finish("done", f"{self.state['workflow']} finished")
            if attempt["exit"] == EXIT_STOPPED:
                return self.finish("stopped", "stopped by Esc")
            from_step = attempt["step"] or from_step
            if attempt["step"] != last_step:
                tries, last_step = 0, attempt["step"]
            fixable = attempt["exit"] != EXIT_SETUP
            if fixable and self.agent != "none" and tries < self.agent_attempts:
                tries += 1
                code = self.fix_with_agent(attempt, len(self.state["attempts"]))
                attempt["fixed_by"] = f"{self.agent} (exit {code})"
                self.save()
                if code >= 0:
                    continue            # re-run to prove the fix
                tries = self.agent_attempts  # agent missing or timed out: go to a human
            if not self.human:
                return self.finish("failed", attempt["message"] or "failed")
            decision = self.ask_human(attempt)
            if decision.get("action") != "retry":
                return self.finish("aborted", "aborted by operator")
            attempt["fixed_by"] = "human"
            from_step = decision.get("from_step") or from_step
            tries = 0

    def ask_human(self, attempt):
        decision_path = self.dir / "decision.json"
        decision_path.unlink(missing_ok=True)
        self.save(status="needs_human", waiting_since=time.time())
        notify("Pyperiscope needs a human",
               f"{self.state['workflow']}: {attempt['kind']} in step {attempt['step']} — open the web UI")
        print(f"[pyperiscope] needs a human: run {self.id} ({attempt['message']})")
        while not decision_path.exists():
            time.sleep(HUMAN_POLL_SECONDS)
        decision = json.loads(decision_path.read_text() or "{}")
        decision_path.unlink(missing_ok=True)
        self.save(status="running", waiting_since=None, last_decision=decision)
        return decision

    def finish(self, status, message):
        self.save(status=status, message=message, finished=time.time())
        if status != "done":
            notify("Pyperiscope", f"{self.state['workflow']}: {message}")
        print(f"[pyperiscope] run {self.id}: {status} — {message}")
        return self.state
