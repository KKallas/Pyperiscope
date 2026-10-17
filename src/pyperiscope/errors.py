"""Errors a workflow can raise. Each has a `kind` that ends up in failure.json,
so the fixing agent (or human) knows which repair recipe applies."""


class PeriscopeError(Exception):
    kind = "error"

    def __init__(self, message, target=None, matches=None, shot=None, best=None):
        super().__init__(message)
        self.target = target          # target name, if the error is about one
        self.matches = matches or []  # Match list seen at failure time
        self.shot = shot              # Shot the decision was made on
        self.best = best              # best below-threshold main score, for not_found


class TargetNotFound(PeriscopeError):
    """Zero matches where one was expected (after waiting `timeout`)."""
    kind = "not_found"


class AmbiguousTarget(PeriscopeError):
    """Several matches where one was expected. Fix: add a detail patch."""
    kind = "ambiguous"


class ValidationFailed(PeriscopeError):
    """A target edit was rejected because it does not match exactly once."""
    kind = "validation_failed"


class StoppedByUser(PeriscopeError):
    """Esc was held (or Ctrl-C). Never escalated to an agent."""
    kind = "stopped"


class PermissionMissing(PeriscopeError):
    """A macOS privacy permission is missing; run `pyperiscope doctor`."""
    kind = "permission"
