"""macOS input, layer 3: keyboard. Keys go to the app that was last clicked
(or the bound app); modifiers are set as event flags, so keys the user is
holding at the same moment do not leak into ours (and ours not into theirs)."""
import time

import Quartz as Q

from ..keys import KEYCODES, parse_combo
from .layer2 import QuartzInput as Base

FLAGS = {
    "cmd": Q.kCGEventFlagMaskCommand, "shift": Q.kCGEventFlagMaskShift,
    "alt": Q.kCGEventFlagMaskAlternate, "ctrl": Q.kCGEventFlagMaskControl,
}
SPECIAL_CHARS = {"\n": "return", "\r": "return", "\t": "tab"}
KEY_DELAY = 0.008


class QuartzInput(Base):
    def _key_event(self, code, down, flags=0, text=None):
        event = Q.CGEventCreateKeyboardEvent(self.source, code, down)
        Q.CGEventSetFlags(event, flags)
        if text is not None:
            Q.CGEventKeyboardSetUnicodeString(event, len(text), text)
        self.post(event)
        time.sleep(KEY_DELAY)

    def key(self, combo):
        mods, key = parse_combo(combo)
        flags = 0
        for mod in mods:
            flags |= FLAGS[mod]
        code = KEYCODES[key]
        with self.user_paused():
            self._key_event(code, True, flags)
            self._key_event(code, False, flags)

    def type_text(self, text):
        """Types characters as unicode, so any layout/language works. Newline
        and tab are sent as the real Return/Tab keys."""
        with self.user_paused():
            for char in text:
                if char in SPECIAL_CHARS:
                    code = KEYCODES[SPECIAL_CHARS[char]]
                    self._key_event(code, True)
                    self._key_event(code, False)
                    continue
                code = KEYCODES.get(char.lower(), 0)
                flags = Q.kCGEventFlagMaskShift if char.isupper() else 0
                self._key_event(code, True, flags, char)
                self._key_event(code, False, flags, char)
