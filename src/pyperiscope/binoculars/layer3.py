from .layer2 import Binoculars
from PIL import Image
from pyperiscope import Scope
import pickle

class Binoculars(Binoculars):
    def debug_screenshot(self, filepath):
        global step
        image = Image.open(filepath)
        
        try:
            # Extract serialized data from metadata
            serialized_data = bytes.fromhex(image.info.get("custom_data", ""))
            data_dict = pickle.loads(serialized_data)
        except (KeyError, pickle.UnpicklingError):
            data_dict = {}  # Return empty dict if no valid data found

        if not data_dict == {}:
            step = Scope(saved_dict=data_dict['step'])
            self.current_step = data_dict['current_step']
            self.last_error = data_dict['last_error']
            self.current_doc = data_dict['current_doc']
            # update UI
            try:
                step.found_locations = data_dict['last_found']
                current = Scope(mouse_offset=step.found_locations[0]['mouse_offset'], area_offset=step.area_offset, area_size=step.area_size, saved_image=image)
                self.update_both(step.render_preview(), current.render_preview())
                self.set_description(self.current_doc)
                self.set_error(self.last_error)
            except:
                self.update_both(step.render_preview(), self.error_image)
                self.set_description(self.current_doc)
                self.set_error(self.last_error)