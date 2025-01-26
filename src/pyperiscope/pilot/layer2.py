from .layer1 import Pilot
from PIL.PngImagePlugin import PngInfo
import pickle

class Pilot(Pilot):
    # save screenshot with step and data
    def save_screenshot_with_data(self, screenshot, step, step_no):
        data_dict = {}
        # save the step dict
        data_dict['step'] = step.save_dict()
        data_dict['last_found'] = step.found_locations
        # save current step
        data_dict['current_step'] = self.current_step
        # save last error
        data_dict['last_error'] = self.last_error
        # last step scope cell id
        data_dict['scope_cell_id'] = self.scope_cell_id
        # docstring into saved png
        data_dict['current_doc'] = self.current_doc
        
        metadata = PngInfo()
        # Convert dict to bytes using pickle
        serialized_data = pickle.dumps(data_dict)
        # Store in PNG metadata with custom key
        metadata.add_text("custom_data", serialized_data.hex())
        screenshot.save("_"+self.current_notebook[:-6]+"-"+str(step_no)+".png", "PNG", pnginfo=metadata)

    # replace the scope object in the current step
    def replace_scope(self, scope_in):
        with open(self.current_notebook, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Find and edit the cell with matching ID
        for cell in nb.cells:
            if cell.get('id') == self.scope_cell_id:
                cell.source = scope_in.get_string()
                break
        
        with open(self.current_notebook, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)

    # delete previous workbook
    def del_previous(self, current):
        if current > 0:
                previous_file = "_" + self.current_notebook[:-6] + "-" + str(current - 1) + ".png"
                if os.path.exists(previous_file):
                    os.remove(previous_file)