"""Web API for screenshots and targets. Every edit is validated against a
screenshot before it is saved (see target/layer3.py)."""
import shutil
import time

from ..errors import ValidationFailed
from ..screen import Shot, capture
from ..target import Target


class Conflict(Exception):
    pass


def take_screenshot(project, body):
    delay = min(float(body.get("delay", 0)), 30)
    time.sleep(delay)
    shot = capture(project.config["monitor"])
    path = shot.save(project.screens / f"{project.new_id('screen')}.png")
    return {"shot": project.relative(path), "size": list(shot.size), "scale": shot.scale}


def _shot(project, body):
    if body.get("shot"):
        return Shot.load(project.resolve(body["shot"])), body["shot"]
    live = take_screenshot(project, {})
    return Shot.load(project.resolve(live["shot"])), live["shot"]


def list_targets(project):
    return [Target.load(project.targets, n).to_dict() for n in project.target_names()]


def create_target(project, body):
    """body: name, shot, box [x,y,w,h], click [x,y]?, confidence?, note?,
    details [{box, tolerance?}]?, force?  (all coordinates in shot pixels)"""
    name = body["name"]
    if name in project.target_names() and not body.get("force"):
        raise Conflict(f"target {name!r} exists; send force=true to replace it")
    shot, shot_path = _shot(project, body)
    box = [int(v) for v in body["box"]]
    target = Target.from_shot(name, shot, box, body.get("click"),
                              float(body.get("confidence", project.config["confidence"])),
                              body.get("note", ""), shot_path)
    for detail in body.get("details", []):
        target = target.with_detail(shot, box, [int(v) for v in detail["box"]],
                                    int(detail.get("tolerance", project.config["detail_tolerance"])))
    match = target.validate(shot, expect_box=box)
    target.save(project.targets)
    return {"target": target.to_dict(), "match": match.to_dict()}


def add_detail(project, name, body):
    """body: shot, candidate (index into matches on that shot), box, tolerance?"""
    shot, _ = _shot(project, body)
    target = Target.load(project.targets, name)
    tolerance = int(body.get("tolerance", project.config["detail_tolerance"]))
    new = target.add_detail(shot, int(body["candidate"]), [int(v) for v in body["box"]], tolerance)
    new.save(project.targets)
    return {"target": new.to_dict(), "match": new.find(shot)[0].to_dict()}


def test_target(project, name, body):
    shot, shot_path = _shot(project, body)
    target = Target.load(project.targets, name)
    matches = target.find(shot)
    return {"shot": shot_path, "matches": [m.to_dict() for m in matches],
            "best": None if matches else target.best(shot), "size": list(target.size)}


def update_target(project, name, body):
    """body: confidence?, note?, drop_detail? (1-based). Re-tested on the
    target's source screenshot when there is one; refused if that breaks it."""
    target = Target.load(project.targets, name)
    if "confidence" in body:
        target.confidence = float(body["confidence"])
    if "note" in body:
        target.note = body["note"]
    if body.get("drop_detail"):
        target = target.drop_detail(int(body["drop_detail"]))
    source = target.source.get("screenshot")
    if source and project.resolve(source).exists() and not body.get("force"):
        try:
            target.validate(Shot.load(project.resolve(source)), target.source.get("box"))
        except ValidationFailed as error:
            raise ValidationFailed(f"{error} (on its source screenshot); send force=true to save anyway",
                                   target=name, matches=error.matches)
    target.save(project.targets)
    return {"target": target.to_dict()}


def delete_target(project, name):
    folder = project.targets / name
    if not (folder / "target.json").exists():
        raise FileNotFoundError(f"no target {name!r}")
    shutil.rmtree(folder)
    return {"deleted": name}
