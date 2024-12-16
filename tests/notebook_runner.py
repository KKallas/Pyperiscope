from pathlib import Path
import pyautogui
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from typing import List, Dict, Union

class NotebookRunner:
    def __init__(self, notebook_path: Union[str, Path]):
        self.notebook_path = Path(notebook_path)
        if not self.notebook_path.exists():
            raise FileNotFoundError(f"Notebook not found: {notebook_path}")
        self.cells = None

    def run(self) -> List[nbformat.notebooknode.NotebookNode]:
        try:
            with open(self.notebook_path) as f:
                nb = nbformat.read(f, as_version=4)
            
            ep = ExecutePreprocessor(
                timeout=600,
                kernel_name='python3'
            )
            ep.preprocess(nb, {'metadata': {'path': str(self.notebook_path.parent)}})
            
            self.cells = nb.cells
            return self.cells
            
        except Exception as e:
            raise RuntimeError(f"Failed to run notebook: {str(e)}")

    def split_to_pairs(self, output_text: str) -> Dict[str, str]:
        return_dict = {}
        lines = output_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            try:
                key, value = [x.strip() for x in line.split('=', 1)]
                if not key:
                    raise ValueError("Empty key found")
                return_dict[key] = value
            except ValueError as e:
                raise ValueError(f"Invalid line format: '{line}'. Expected 'key=value'") from e
                
        return return_dict

    def get_test_outputs(self) -> Dict[str, str]:
        if not self.cells:
            self.run()
        
        test_outputs = {}
        
        for cell in self.cells:
            if cell.cell_type == 'code' and cell.outputs:
                for output in cell.outputs:
                    text = output.get('text', '')
                    if isinstance(text, str) and text.startswith("TEST output"):
                        cleaned_output = text[len("TEST output"):].strip()
                        if cleaned_output:
                            try:
                                test_outputs.update(self.split_to_pairs(cleaned_output))
                            except ValueError as e:
                                print(f"Warning: Skipping invalid output format: {str(e)}")
        
        return test_outputs

def notebook_outputs(notebook_path: Union[str, Path]) -> Dict[str, str]:
    runner = NotebookRunner(notebook_path)
    return runner.get_test_outputs()