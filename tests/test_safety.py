import threading
import time

import pytest

from pyperiscope.input.keys import parse_combo
from pyperiscope.safety import killswitch
from pyperiscope.safety.killswitch import KillSwitch


@pytest.fixture(autouse=True)
def no_interrupt(monkeypatch):
    monkeypatch.setattr(killswitch._thread, "interrupt_main", lambda: None)


def test_hold_stops_after_hold_time():
    pressed_at = time.monotonic()
    progress = []
    ks = KillSwitch(hold=0.3, on_progress=progress.append, key_down=lambda: True).start(check=False)
    assert ks.stop.wait(2)
    assert time.monotonic() - pressed_at >= 0.3
    assert progress and progress[-1] > 0
    ks.close()


def test_short_taps_do_not_stop():
    state = {"down": False}
    ks = KillSwitch(hold=0.3, key_down=lambda: state["down"]).start(check=False)
    for _ in range(5):                 # 5 taps of 0.1 s each = 0.5 s total, never 0.3 s in one go
        state["down"] = True
        time.sleep(0.1)
        state["down"] = False
        time.sleep(0.08)
    assert not ks.stop.is_set()
    ks.close()


def test_release_reports_zero():
    state = {"down": True}
    seen = []
    ks = KillSwitch(hold=5, on_progress=seen.append, key_down=lambda: state["down"]).start(check=False)
    time.sleep(0.4)
    state["down"] = False
    time.sleep(0.2)
    ks.close()
    assert seen[-1] == 0 and max(seen) > 0


@pytest.mark.parametrize("combo,expected", [
    ("Return", ([], "return")), ("ctrl+s", (["ctrl"], "s")), ("cmd+shift+T", (["cmd", "shift"], "t")),
    ("Page_Down", ([], "page_down")), ("super+a", (["cmd"], "a")), ("esc", ([], "escape")),
])
def test_combos(combo, expected):
    assert parse_combo(combo) == expected


@pytest.mark.parametrize("combo", ["a+b", "ctrl+nosuchkey", ""])
def test_bad_combos(combo):
    with pytest.raises(ValueError):
        parse_combo(combo)
