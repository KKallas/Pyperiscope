"""Key names -> macOS virtual key codes (ANSI layout).

Names follow the computer-use / xdotool convention the models already know
("Return", "ctrl+s", "Page_Down", "cmd+shift+t"); matching is case-insensitive
and a few common aliases are accepted.
"""
KEYCODES = {
    "a": 0, "s": 1, "d": 2, "f": 3, "h": 4, "g": 5, "z": 6, "x": 7, "c": 8, "v": 9,
    "b": 11, "q": 12, "w": 13, "e": 14, "r": 15, "y": 16, "t": 17, "1": 18, "2": 19,
    "3": 20, "4": 21, "6": 22, "5": 23, "=": 24, "9": 25, "7": 26, "-": 27, "8": 28,
    "0": 29, "]": 30, "o": 31, "u": 32, "[": 33, "i": 34, "p": 35, "l": 37, "j": 38,
    "'": 39, "k": 40, ";": 41, "\\": 42, ",": 43, "/": 44, "n": 45, "m": 46, ".": 47,
    "`": 50,
    "return": 36, "tab": 48, "space": 49, "backspace": 51, "escape": 53,
    "cmd": 55, "shift": 56, "capslock": 57, "alt": 58, "ctrl": 59,
    "kp_enter": 76, "help": 114, "home": 115, "page_up": 116, "delete": 117,
    "end": 119, "page_down": 121, "left": 123, "right": 124, "down": 125, "up": 126,
    "f1": 122, "f2": 120, "f3": 99, "f4": 118, "f5": 96, "f6": 97, "f7": 98, "f8": 100,
    "f9": 101, "f10": 109, "f11": 103, "f12": 111,
}

ALIASES = {
    "enter": "return", "esc": "escape", "back_space": "backspace", "bksp": "backspace",
    "del": "delete", "forwarddelete": "delete", "pageup": "page_up", "prior": "page_up",
    "pagedown": "page_down", "next": "page_down", "arrowleft": "left", "arrowright": "right",
    "arrowup": "up", "arrowdown": "down", "command": "cmd", "super": "cmd", "meta": "cmd",
    "win": "cmd", "option": "alt", "opt": "alt", "control": "ctrl", "spacebar": "space",
    "minus": "-", "equal": "=", "comma": ",", "period": ".", "slash": "/",
}

MODIFIERS = ("cmd", "shift", "alt", "ctrl")


def normalize(name):
    key = name.strip().lower().replace(" ", "_")
    key = ALIASES.get(key, key)
    if key not in KEYCODES:
        raise ValueError(f"unknown key {name!r}")
    return key


def parse_combo(combo):
    """'ctrl+shift+Tab' -> (['ctrl', 'shift'], 'tab'). A lone '+' is the plus key's
    shifted '=' and is not supported as a combo part; type('+') instead."""
    parts = [normalize(p) for p in combo.split("+") if p]
    if not parts:
        raise ValueError(f"empty key combo {combo!r}")
    *mods, key = parts
    bad = [m for m in mods if m not in MODIFIERS]
    if bad:
        raise ValueError(f"{combo!r}: {bad} are not modifiers {MODIFIERS}")
    return mods, key
