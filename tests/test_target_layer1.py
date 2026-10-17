import numpy as np
import pytest

from pyperiscope.target.layer1 import Detail, Target


def test_save_load_roundtrip(tmp_path, shot):
    image = shot.crop((495, 95, 130, 55))
    detail = Detail(shot.crop((35, 102, 190, 38)), (-460, 7), 4, 0.88)
    target = Target("customers.edit", image, (65, 27), 2.0, 0.92, [detail], "edit button", {"box": [1, 2, 3, 4]})
    target.save(tmp_path)
    loaded = Target.load(tmp_path, "customers.edit")
    assert np.array_equal(loaded.image, image)
    assert loaded.click == (65, 27) and loaded.scale == 2.0 and loaded.confidence == 0.92
    assert loaded.note == "edit button" and loaded.source == {"box": [1, 2, 3, 4]}
    assert len(loaded.details) == 1
    assert loaded.details[0].offset == (-460, 7) and loaded.details[0].tolerance == 4
    assert np.array_equal(loaded.details[0].image, detail.image)


def test_resave_removes_stale_detail_files(tmp_path, shot):
    image = shot.crop((495, 95, 130, 55))
    d = Detail(shot.crop((35, 102, 190, 38)), (0, 0))
    Target("t", image, (1, 1), details=[d, d]).save(tmp_path)
    Target("t", image, (1, 1), details=[d]).save(tmp_path)
    assert sorted(p.name for p in (tmp_path / "t").glob("detail*.png")) == ["detail1.png"]


@pytest.mark.parametrize("name", ["", "../evil", "a b", ".hidden"])
def test_bad_names_rejected(shot, name):
    with pytest.raises(ValueError):
        Target(name, shot.image[:10, :10], (0, 0))


def test_at_most_four_details(shot):
    d = Detail(shot.image[:10, :10], (0, 0))
    with pytest.raises(ValueError):
        Target("t", shot.image[:10, :10], (0, 0), details=[d] * 5)


def test_missing_target(tmp_path):
    with pytest.raises(FileNotFoundError):
        Target.load(tmp_path, "nope")
