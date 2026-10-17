import pytest
from notebook_runner import notebook_outputs

def test_scope_creation():
    outputs = notebook_outputs("tests/test - calc win.ipynb")
    
    expected = {
        'calc_answer':'16'
    }
    
    assert outputs == expected, \
        f"Expected {expected}, but got {outputs}"
    
    assert outputs['calc_answer'] == '16', \
        "Incorrect answer from the calculator"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
