Scope Class and Usage Guide
=======================

The `Scope` class is designed for capturing and processing screenshots using Python's `pyautogui` and image manipulation libraries. It allows users to capture a portion of their screen, define specific areas of interest, and save or load these areas as base64-encoded images. Below is an overview of how to use the class.

Initialization
--------------

To initialize the `Scope` class:

```python
scope = Scope(mouse_offset=(100, 100), crop_size=(640, 480), area_offset=(50, 50), area_size=(64, 64))
```

### Parameters:

*   `mouse_offset`: Tuple of x, y coordinates for the mouse position offset.
*   `crop_size`: The dimensions of the captured cropped area.
*   `area_offset`: The offset for the smaller focus area relative to the cursor.
*   `area_size`: The size of the area of interest for finer control.
*   `cursor_size`: Size of the cursor for alignment.

Saving the Data
---------------

You can save the captured images and metadata in a dictionary using `save_dict()`:

```python
data = scope.save_dict()
```

This returns a dictionary containing base64-encoded images and metadata of the screen.

Loading Saved Data
------------------

To reload the saved screenshot and area data, use:

```python
scope.load_from_dict(saved_dict)
```

This restores the screen capture and focus area from previously saved data.

[python](../src/pyperiscope/layer1.py)