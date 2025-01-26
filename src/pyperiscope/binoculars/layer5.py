from .layer3 import Binoculars
from .layer4 import FileWatcher
from PIL import Image
from pyperiscope import Scope
import pickle

class Binoculars(Binoculars):
    def _update_from_screenshot(self, filepath):
        image = Image.open(filepath)
        
        try:
            # Extract serialized data from metadata
            serialized_data = bytes.fromhex(image.info.get("custom_data", ""))
            data_dict = pickle.loads(serialized_data)
        except (KeyError, pickle.UnpicklingError):
            data_dict = {}  # Return empty dict if no valid data found

        # set default values
        left_image = self.error_image
        right_image = self.error_image
        description = str(filepath)[-4:]+"ERROR loading data"
        error_desc =  "could not read the data portion from: "+str(filepath)

        # try to override the values with actual data
        if not data_dict == {}:
            step = Scope(saved_dict=data_dict['step'])
            step.found_locations = data_dict['last_found']
            #self.current_step = data_dict['current_step']
            last_error = data_dict['last_error']
            #self.scope_cell_id = data_dict['scope_cell_id']
            current_doc = data_dict['current_doc']
            current = Scope(mouse_offset=step.found_locations[0]['mouse_offset'], area_offset=step.area_offset, area_size=step.area_size, saved_image=image)
            left_image = step.render_preview()
            right_image = current.render_preview()
            if current_doc:
                description = current_doc
            if last_error:
                error_desc = last_error
            
        # update UI
        self.update_both(left_image, right_image)
        self.set_description(current_doc)
        self.set_error(last_error)
        
    def start_monitoring(self, filepath):
        print("to stop the monitoring use Bincoulars_instance.watcher.stop()")
        if hasattr(self, 'watcher'):
            self.watcher.stop()
        self.watcher = FileWatcher(self, filepath)
        self.watcher.start()