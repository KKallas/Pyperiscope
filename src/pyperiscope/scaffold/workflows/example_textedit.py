"""Example: type a line into a new TextEdit document.

Before the first run, create these targets in the web UI (pyperiscope serve):
  textedit.new_document  the "New Document" button in TextEdit's open panel
  textedit.body          an empty area of a fresh document window
"""
from pyperiscope import Workflow

wf = Workflow(__file__, app="TextEdit")


@wf.step
def open_textedit(s):
    s.open_app("TextEdit")
    if s.exists("textedit.new_document", timeout=3):
        s.left_click("textedit.new_document")
    s.wait_for("textedit.body", timeout=10)


@wf.step
def write_line(s):
    s.left_click("textedit.body")
    s.type("Hello from Pyperiscope\n")


if __name__ == "__main__":
    wf.main()
