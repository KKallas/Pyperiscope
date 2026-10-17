"""pyperiscope command line. Run `pyperiscope -h` or `pyperiscope <cmd> -h`."""
import argparse
import sys

from ..errors import PeriscopeError
from ..project import Project
from . import system, targets


def parser():
    p = argparse.ArgumentParser(prog="pyperiscope", description="Visual GUI automation, repaired by agents.")
    p.add_argument("-C", "--project", help="project folder (default: search upwards from cwd)")
    sub = p.add_subparsers(dest="command", required=True)
    system.add_parsers(sub)
    targets.add_parsers(sub)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "init":
            return system.init(args)
        if args.command == "doctor":
            return system.doctor(args)
        project = Project(args.project) if args.project else Project()
        handlers = {"serve": system.serve, "screenshot": system.screenshot, "run": system.run,
                    "new-workflow": system.new_workflow, "target": targets.run, "zoom": targets.run}
        return handlers[args.command](project, args) or 0
    except (PeriscopeError, ValueError, FileNotFoundError, PermissionError) as error:
        payload = {"error": str(error), "kind": getattr(error, "kind", type(error).__name__)}
        if getattr(error, "matches", None):
            payload["matches"] = [m.to_dict() for m in error.matches]
        targets.emit(payload)
        return 1
    except Exception as error:  # conflicts and the rest: same shape for agents
        targets.emit({"error": str(error), "kind": type(error).__name__})
        return 1


def entry():
    sys.exit(main())
