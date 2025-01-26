import pickle
import json
import nbformat
import os
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from pyperiscope import Scope

class Pilot():
    def __init__(self, workbook, step_timeout=1):
        self.current_notebook = workbook
        self.steps = []
        self.current_step = -1
        self.steps_total = -1
        self.current_doc = ""
        self.last_run_code = ""
        self.last_error = ""
        self.scope_cell_id = -1
        self.step_timeout = step_timeout
        
        self.get_steps()

    # load the steps form automation workbook for fruthert usage
    def get_steps(self):
        with open(self.current_notebook, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        # Find all cells with the marker comment
        marker_cells = []
        for i, cell in enumerate(notebook['cells']):
            if cell['cell_type'] == 'code' and cell['source']:
                if cell['source'][0].find("# comment: Automated step generated with pyPeriscope")>-1:
                    marker_cells.append(i)
        
        if not marker_cells:
            self.steps_total = -1
            print("No marker cells found, are you sure this is the correct jupyter lab notebook?")
            return
        
        # Create step ranges
        self.steps = []
        # First step: from start to first marker
        self.steps.append((0, marker_cells[0]-1))
        
        # Middle steps: between markers
        for i in range(len(marker_cells)-1):
            self.steps.append((marker_cells[i]-1, marker_cells[i+1]-1))
        
        # Last step: from last marker to end
        if marker_cells:
            self.steps.append((marker_cells[-1]-1, len(notebook['cells'])))
    
        # Make the 1st two into one as there are some imports in front
        self.steps = self.steps[1:]
        self.steps[0] = (0,self.steps[0][1])
        
        self.steps_total = len(self.steps)

    # read one cell worth of data
    def get_cell(self, cell_number):
        with open(self.current_notebook, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        code_cells = [cell for cell in notebook['cells']]
        
        if cell_number < 0 or cell_number >= len(code_cells):
            raise ValueError(f"Cell number must be between 0 and {len(code_cells) - 1}")
        
        return code_cells[cell_number]

    # simplified view cell (remove hs object defintions and outputs, use for debug)
    def view_cell(self, cell_number):
        code = self.get_cell(cell_number)
        if 'source' in code:
            if code['source'][0].find("# comment: Automated step") > -1:
                code['source'][1] = 'payload = \'*** removed for view ***\''
        if 'outputs' in code:
            if len(code['outputs']) > 0:
                code['outputs'] = ['*** removed for view ***']
        
        return(code)