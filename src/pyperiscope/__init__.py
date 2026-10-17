"""Pyperiscope v2: visual GUI automation for software that has no API,
written as plain Python workflows by coding agents and repaired by them
(then by a human operator) when the screen changes.

    from pyperiscope import Workflow
"""
__version__ = "2.0.0.dev0"

from .errors import (AmbiguousTarget, PeriscopeError, PermissionMissing, StoppedByUser,
                     TargetNotFound, ValidationFailed)
from .project import Project
from .screen import Shot, capture
from .session import Session
from .target import Detail, Match, Target
from .workflow import Workflow

__all__ = ["Workflow", "Session", "Project", "Target", "Detail", "Match", "Shot", "capture",
           "PeriscopeError", "TargetNotFound", "AmbiguousTarget", "ValidationFailed",
           "StoppedByUser", "PermissionMissing"]
