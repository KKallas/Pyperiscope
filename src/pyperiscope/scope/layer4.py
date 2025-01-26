import pyautogui
import time
from .layer3 import Scope

class Scope(Scope):
    def find(self, tries=1, timeout=1, confidence=0.9):
        count = 1
        self.found_locations = []
        self.found_image = pyautogui.screenshot()

        for i in range(tries):
            try:
                found_patterns = pyautogui.locateAllOnScreen(self.area_image, confidence=confidence)
                for loc in found_patterns:
                    new_loc = {'area':(loc.left, loc.top, loc.left + self.area_size[0], loc.top + self.area_size[1]),
                                                 'mouse_offset':(loc.left - self.area_offset[0], loc.top - self.area_offset[1]), 
                                                 'label':"[0] STEP", 
                                                 'area_offset':self.area_offset}
        
                    if self.found_locations == []: 
                        self.found_locations.append(new_loc)
                        continue
        
                    if not(self.overlap(self.found_locations[-1], new_loc)):
                        new_loc['label'] = "["+str(count)+"] STEP"
                        self.found_locations.append(new_loc)
                        count = count + 1
                        continue
                break
            except Exception as e:
                if i==(tries-1):
                    raise e
                else:
                    time.sleep(timeout)
                print("try: " + str(i) + "/" + str(tries))

        print("found: " + str(count))

    def overlap(self, area1, area2):
        x1, y1, x2, y2 = area1['area']
        x3, y3, x4, y4 = area2['area']
        
        if x3 < x2: # check X overlap
            return True
        if y3 < y2: # check Y overlap
            return True
        return False
        
    def draw_found(self, found_id=0):
        base_image = self.found_image.copy()
        self.mouse_offset = self.found_locations[found_id]['mouse_offset']
        self.area_offset = self.found_locations[found_id]['area_offset']
        self.update_crop_and_area(full_image=base_image)
        
        for loc in self.found_locations:
            base_image = self.render_preview(base_image, marker=loc, cropped=False)

        return base_image.crop(self.crop_box) 