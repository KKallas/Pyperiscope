Scope Find and Draw Class Extension Usage Guide
===============================================

This extension to the `Scope` class adds functionality for detecting and marking patterns on the screen. It uses `pyautogui` to search for instances of a specific area of interest (`area_image`) within the screen and highlights these occurrences. Additionally, it provides methods to render the found locations on the captured screen.


Pattern Detection
-----------------

The `find()` method identifies all occurrences of the predefined `area_image` on the screen with a confidence threshold. The detected locations are stored and can be visually rendered.

### Usage:

```python
scope.find()
```

### How It Works:

*   Captures the current screen using `pyautogui.screenshot()`.
*   Searches for occurrences of `self.area_image` on the screen using `pyautogui.locateAllOnScreen()` with a 90% confidence level.
*   For each occurrence, it generates metadata for the location (bounding box, mouse offset, and label).
*   Ensures non-overlapping areas by checking with the `overlap()` method.
*   The number of detected patterns is printed at the end.

Drawing Detected Patterns
-------------------------

Once patterns are detected, the `draw_found()` method renders all found locations onto the screenshot. Each occurrence is labeled and marked on the screen, allowing users to visually identify the detected areas.

### Usage:

```python
found_image = scope.draw_found(found_id=0)
found_image.show()
```

### Parameters:

*   `found_id`: Index of the found location to render. Defaults to `0`, which is the first found location.

### How It Works:

*   The base screenshot is used to overlay detected patterns.
*   The method calls `render_preview()` to draw the label and highlight each found location.
*   The final image can be cropped to the original area defined by `self.crop_box`.


    

Output and Display
------------------

The `draw_found()` method generates an annotated screenshot with all found patterns highlighted. You can crop the image or display it using Pillow's `Image.show()` method, or save it for further analysis.

This extension is especially useful in automating the process of detecting patterns on the screen and providing clear visual feedback on the results.

[python](../src/pyperiscope/layer4.py)