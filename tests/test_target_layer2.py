import cv2

from conftest import BUTTON, LABEL, ROW_Y, make_image
from pyperiscope import Shot
from pyperiscope.target.layer1 import Detail
from pyperiscope.target.layer2 import Target, match_all


def button_target(shot, details=()):
    x, y, w, h = BUTTON(1)
    return Target("edit", shot.crop(BUTTON(1)), (w / 2, h / 2), 1.0, 0.9, list(details))


def test_match_all_finds_each_repeat_once(shot):
    found = match_all(shot.image, shot.crop(BUTTON(0)), 0.9)
    assert sorted(y for _, y, _ in found) == [y - 5 for y in ROW_Y]


def test_repeated_button_gives_three_matches(shot):
    matches = button_target(shot).find(shot)
    assert len(matches) == 3
    assert all(m.score > 0.99 for m in matches)


def test_detail_narrows_to_its_row(shot):
    bx, by, *_ = BUTTON(1)
    lx, ly, *_ = LABEL(1)
    detail = Detail(shot.crop(LABEL(1)), (lx - bx, ly - by))
    matches = button_target(shot, [detail]).find(shot)
    assert len(matches) == 1
    assert matches[0].box[:2] == (bx, by)
    assert matches[0].click == (bx + 65, by + 27.5)


def test_detail_tolerates_small_drift(shot):
    bx, by, *_ = BUTTON(1)
    lx, ly, *_ = LABEL(1)
    target = button_target(shot, [Detail(shot.crop(LABEL(1)), (lx - bx, ly - by), tolerance=6)])
    drifted = make_image()
    drifted[:, 30:300] = make_image(shift=(4, 0))[:, 30:300]   # labels moved 4 px right
    assert len(target.find(Shot(drifted))) == 1


def test_points_use_scale_and_origin(shot):
    retina = Shot(cv2.resize(shot.image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC), origin=(100, 0), scale=2.0)
    matches = button_target(shot).find(retina)          # target captured at scale 1, screen at 2
    assert len(matches) == 3
    top = min(matches, key=lambda m: m.box[1])
    bx, by, w, h = BUTTON(0)
    assert abs(top.point[0] - (100 + bx + w / 2)) <= 1.5
    assert abs(top.point[1] - (by + h / 2)) <= 1.5


def test_best_reports_near_miss(shot):
    target = button_target(shot)
    target.confidence = 0.999
    other = Shot(make_image(rows=["A", "B", "C"]))
    best = target.best(other)
    assert best["score"] > 0.9 and len(best["at"]) == 2


def test_template_bigger_than_screen():
    small = Shot(make_image()[:20, :20])
    assert button_target(Shot(make_image())).find(small) == []
