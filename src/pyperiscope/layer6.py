import pyautogui
from .layer5 import Scope

class Scope(Scope):
    def get_locations(self):
        scaled_locations = []
        scale = pyautogui.screenshot().size[0]/pyautogui.size()[0]
        if self.found_locations:
            for location in self.found_locations:
                scaled_locations.append((location['mouse_offset'][0]/2,location['mouse_offset'][1]/2))
        return scaled_locations