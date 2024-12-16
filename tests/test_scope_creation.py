import pytest
from notebook_runner import notebook_outputs

def test_scope_creation():
    outputs = notebook_outputs("tests/test - create step.ipynb")
    
    expected = {
        'found_on_screen': '1',
        'preview_image_data_type': "<class 'PIL.Image.Image'>"
    }
    
    assert outputs == expected, \
        f"Expected {expected}, but got {outputs}"
    
    assert outputs['found_on_screen'] == '1', \
        "Scope was not found on screen"
    
    assert outputs['preview_image_data_type'] == "<class 'PIL.Image.Image'>", \
        "Preview image is not a PIL Image"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
