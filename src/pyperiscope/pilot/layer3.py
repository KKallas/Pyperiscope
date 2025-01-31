from .layer2 import Pilot
import pyautogui

class Pilot(Pilot):
    # run the steps in global namespace so it would work like running the worksheet on the worksheet
    def run_code(self, code_str):
        self.last_run_code = code_str
        current_globals = globals()  # Get fresh globals each time
        exec(code_str, current_globals)

    # run single cell from notebook
    def run_cell(self, cell_number):
        self.last_error = None
        # get cell content
        current_cell = self.get_cell(cell_number)
        # if docstring cell update the variable
        if not current_cell['cell_type'] == 'code':
                if current_cell['cell_type'] == 'markdown':
                    content = "".join(current_cell['source'])
                    self.current_doc = self.current_doc + content
                else:
                    print("cell in not excecutable in 'code' mode, current mode: "+str(current_cell['cell_type']))
                return
        # join code into single string from line list
        current_code = "".join(current_cell['source'])
        # if the cell contains scope deffintion
        if current_code.find("# comment: Automated step") > -1:
            self.scope_cell_id = current_cell['id']
        # remove render preview
        code = current_code.replace("step.render_preview()\n","")
        # after all run the code
        try:
            self.run_code(code)
        except Exception as e:
            self.last_error = str(e)
        # stop if there was an error
        if self.last_error:
            return

    # run one step end to end
    def run_step(self, step_no):
        print("Staring step: " + str(step_no))
        self.current_doc = ""
        current_screenshot = pyautogui.screenshot()
        for active_cell in range(self.steps[step_no][0], self.steps[step_no][1]):
            self.current_step = step_no
            self.run_cell(active_cell)
            if self.last_error:
                print(self.last_error)
                break
        try:
            if type(automation_payload) == dict:
                self.payload_out = automation_payload
            else:
                self.payload_out = {}
        except:
            self.payload_out = {}
        self.save_screenshot_with_data(current_screenshot, step, step_no, self.payload_out)

    # select and run a workbook
    def run_workbook(self, firstStep = -1):
        # run all the steps in the workbook
        for step in range(0, len(self.steps)):
            # if the workflow broke donw the continue from the last step
            if firstStep > 0:
                if firstStep == step:
                    firstStep = -1
                else:
                    continue
            # run the indivdual step
            self.run_step(step)  
                    
            # if error then stop, error is printed in the step process
            if self.last_error:
                return

            # cleanup the previous step and use timeout
            self.del_previous(step)    
            time.sleep(self.step_timeout)
        # delete the last log image if all was sucessfull
        self.del_previous(len(self.steps)) 