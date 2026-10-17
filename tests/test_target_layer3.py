import pytest

from conftest import BUTTON, LABEL
from pyperiscope import ValidationFailed
from pyperiscope.target.layer3 import Target


def test_from_shot_defaults_click_to_centre(shot):
    t = Target.from_shot("edit", shot, BUTTON(1))
    assert t.click == (65, 27.5)
    assert t.size == (130, 55)


def test_from_shot_rejects_flat_and_tiny_boxes(shot):
    with pytest.raises(ValueError):
        Target.from_shot("flat", shot, (300, 470, 60, 30))     # empty background
    with pytest.raises(ValueError):
        Target.from_shot("tiny", shot, (500, 100, 3, 3))


def test_validate_refuses_ambiguous(shot):
    t = Target.from_shot("edit", shot, BUTTON(1))
    with pytest.raises(ValidationFailed) as err:
        t.validate(shot)
    assert len(err.value.matches) == 3


@pytest.mark.parametrize("row", [0, 1, 2])
def test_add_detail_makes_chosen_candidate_unique(shot, row):
    t = Target.from_shot("edit", shot, BUTTON(1))
    candidates = t.find(shot)
    index = next(i for i, m in enumerate(candidates) if m.box[:2] == BUTTON(row)[:2])
    fixed = t.add_detail(shot, index, LABEL(row))
    assert len(fixed.details) == 1
    only = fixed.find(shot)
    assert len(only) == 1 and only[0].box[:2] == BUTTON(row)[:2]
    assert len(t.details) == 0          # original untouched


def test_add_detail_refuses_detail_that_does_not_disambiguate(shot):
    t = Target.from_shot("edit", shot, BUTTON(1))
    with pytest.raises(ValidationFailed):
        t.add_detail(shot, 0, (505, 100, 110, 40))   # another copy of the button itself


def test_add_detail_refuses_bad_candidate(shot):
    t = Target.from_shot("edit", shot, BUTTON(1))
    with pytest.raises(ValidationFailed):
        t.add_detail(shot, 7, LABEL(0))


def test_max_four_details(shot):
    t = Target.from_shot("edit", shot, BUTTON(1))
    for _ in range(4):
        t = t.with_detail(shot, BUTTON(1), LABEL(1))
    with pytest.raises(ValidationFailed):
        t.with_detail(shot, BUTTON(1), LABEL(1))


def test_drop_detail(shot):
    t = Target.from_shot("edit", shot, BUTTON(1)).add_detail(shot, 1, LABEL(1))
    assert len(t.drop_detail(1).details) == 0
