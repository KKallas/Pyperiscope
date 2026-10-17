"""`pyperiscope target ...` and `pyperiscope zoom`: the commands agents use to
inspect screenshots and repair targets. They share the web UI's code path,
so every change is validated (exactly one match) before it is saved.
Output is JSON so agents can parse it; exit code 1 = refused/failed."""
import json
import sys

import cv2

from ..annotate import draw_matches, zoom
from ..screen import Shot
from ..server import targets as ops
from ..target import Target


def box(text):
    values = [int(float(v)) for v in text.replace(" ", "").split(",")]
    if len(values) != 4:
        raise ValueError(f"box must be x,y,w,h, got {text!r}")
    return values


def point(text):
    values = [float(v) for v in text.replace(" ", "").split(",")]
    if len(values) != 2:
        raise ValueError(f"point must be x,y, got {text!r}")
    return values


def add_parsers(sub):
    t = sub.add_parser("target", help="list, inspect, create and repair targets").add_subparsers(dest="action", required=True)
    t.add_parser("list")
    t.add_parser("show").add_argument("name")
    p = t.add_parser("create", help="cut a target from a screenshot (validated)")
    p.add_argument("name"); p.add_argument("--shot", help="screenshot png (default: capture now)")
    p.add_argument("--box", type=box, required=True, help="main patch x,y,w,h in screenshot pixels")
    p.add_argument("--click", type=point, help="click point x,y in screenshot pixels (default: centre)")
    p.add_argument("--detail", type=box, action="append", default=[], help="detail box x,y,w,h (repeat, max 4)")
    p.add_argument("--confidence", type=float); p.add_argument("--note", default="")
    p.add_argument("--force", action="store_true", help="replace an existing target")
    p = t.add_parser("add-detail", help="make an ambiguous target unique (validated)")
    p.add_argument("name"); p.add_argument("--shot", required=True)
    p.add_argument("--candidate", type=int, required=True, help="index [N] from the annotated screenshot")
    p.add_argument("--box", type=box, required=True); p.add_argument("--tolerance", type=int)
    p = t.add_parser("test", help="find a target on a screenshot (or the live screen)")
    p.add_argument("name"); p.add_argument("--shot"); p.add_argument("--expect", type=int, default=1)
    p = t.add_parser("set", help="change confidence / note / drop a detail")
    p.add_argument("name"); p.add_argument("--confidence", type=float); p.add_argument("--note")
    p.add_argument("--drop-detail", type=int); p.add_argument("--force", action="store_true")
    t.add_parser("delete").add_argument("name")
    z = sub.add_parser("zoom", help="enlarge part of a screenshot with a pixel grid (for reading coordinates)")
    z.add_argument("shot"); z.add_argument("--box", type=box, required=True)
    z.add_argument("--factor", type=int); z.add_argument("--out")


def run(project, args):
    if args.command == "zoom":
        shot = Shot.load(args.shot)
        out = args.out or str(project.screens / f"zoom-{'-'.join(map(str, args.box))}.png")
        cv2.imwrite(out, zoom(shot.image, args.box, args.factor))
        return emit({"zoom": out, "box": args.box, "note": "grid labels are original screenshot pixels"})
    a = args.action
    if a == "list":
        return emit([{"name": t["name"], "note": t["note"], "details": len(t["details"])} for t in ops.list_targets(project)])
    if a == "show":
        return emit(Target.load(project.targets, args.name).to_dict())
    if a == "create":
        body = {"name": args.name, "shot": args.shot, "box": args.box, "click": args.click, "note": args.note,
                "force": args.force, "details": [{"box": d} for d in args.detail]}
        if args.confidence:
            body["confidence"] = args.confidence
        return emit(ops.create_target(project, body))
    if a == "add-detail":
        body = {"shot": args.shot, "candidate": args.candidate, "box": args.box}
        if args.tolerance is not None:
            body["tolerance"] = args.tolerance
        return emit(ops.add_detail(project, args.name, body))
    if a == "test":
        result = ops.test_target(project, args.name, {"shot": args.shot})
        shot = Shot.load(project.resolve(result["shot"]))
        out = project.screens / f"test-{args.name}.png"
        cv2.imwrite(str(out), draw_matches(shot.image, Target.load(project.targets, args.name).find(shot),
                                           result["best"], result["size"]))
        result["annotated"] = project.relative(out)
        emit(result)
        return 0 if len(result["matches"]) == args.expect else 1
    if a == "set":
        body = {k: v for k, v in {"confidence": args.confidence, "note": args.note,
                                  "drop_detail": args.drop_detail, "force": args.force}.items() if v is not None}
        return emit(ops.update_target(project, args.name, body))
    if a == "delete":
        return emit(ops.delete_target(project, args.name))


def emit(data):
    json.dump(data, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")
    return 0
