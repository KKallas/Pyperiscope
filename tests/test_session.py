import json

import cv2
import numpy as np
import pytest

from conftest import BUTTON, LABEL
from pyperiscope import AmbiguousTarget, Session, Shot, StoppedByUser, Target, TargetNotFound
from pyperiscope.input import RecordingInput


@pytest.fixture
def session(project, shot, tmp_path):
    Target.from_shot("edit", shot, BUTTON(1)).save(project.targets)
    unique = Target.from_shot("edit.gamma", shot, BUTTON(1))
    unique = unique.add_detail(shot, [m.box[1] for m in unique.find(shot)].index(BUTTON(2)[1]), LABEL(2))
    unique.save(project.targets)
    retina = Shot(cv2.resize(shot.image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC), (0, 0), 2.0)
    s = Session(project, tmp_path / "run", input_backend=RecordingInput(), capture_fn=lambda: retina)
    yield s
    s.close()


def test_click_unique_target_sends_screen_points(session):
    session.left_click("edit.gamma")
    name, (x, y), kw = session.input.calls[-1]
    bx, by, w, h = BUTTON(2)
    assert name == "click" and kw == {"button": "left", "count": 1}
    assert abs(x - (bx + w / 2)) <= 1 and abs(y - (by + h / 2)) <= 1   # points, not retina pixels


def test_ambiguous_target_raises_with_candidates(session):
    with pytest.raises(AmbiguousTarget) as err:
        session.left_click("edit", timeout=0)
    assert len(err.value.matches) == 3
    assert session.input.calls == []


def test_not_found_reports_best(session, project):
    noise = np.random.default_rng(1).integers(0, 255, (40, 60, 3), dtype=np.uint8)
    Target("ghost", noise, (5, 5)).save(project.targets)
    with pytest.raises(TargetNotFound) as err:
        session.find("ghost", timeout=0)
    assert err.value.best is not None


def test_exists_and_find_all(session):
    assert session.exists("edit") and len(session.find_all("edit")) == 3


def test_keyboard_and_combo(session):
    session.type("hi\n")
    session.key("cmd+s", repeat=2)
    assert [c[0] for c in session.input.calls] == ["type", "key", "key"]


def test_stop_flag_blocks_actions(session):
    session.stop.set()
    with pytest.raises(StoppedByUser):
        session.left_click((10, 10))


def test_failure_report_bundle(session, tmp_path):
    session.step = "pick_customer"
    try:
        session.left_click("edit", timeout=0)
    except AmbiguousTarget as error:
        report = session.report_failure(error, "tb")
    run = tmp_path / "run"
    saved = json.loads((run / "failure.json").read_text())
    assert saved["kind"] == "ambiguous" and saved["step"] == "pick_customer" and saved["target"] == "edit"
    assert len(saved["matches"]) == 3 and saved["screen"]["scale"] == 2.0
    assert (run / "failure.png").exists() and (run / "failure-annotated.png").exists()
    assert Shot.load(run / "failure.png").scale == 2.0
    assert report["kind"] == "ambiguous"
    events = [json.loads(line)["event"] for line in (run / "events.jsonl").read_text().splitlines()]
    assert events[-1] == "failure"
