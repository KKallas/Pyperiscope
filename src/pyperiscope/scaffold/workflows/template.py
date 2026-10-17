"""Describe what this workflow does, its start state and its end state."""
from pyperiscope import Workflow

wf = Workflow(__file__, app=APP_NAME)


@wf.step
def start(s):
    # Every step begins by waiting for a screen state it recognises.
    # s.wait_for("app.main_window", timeout=10)
    pass


if __name__ == "__main__":
    wf.main()
