Scope UI Extension Usage Guide
=================================

This extended `Scope` class builds on the base `Scope` class, introducing methods to render a visual preview of captured areas and mark specific locations on the screen capture. These enhancements allow for annotated and labeled screenshots, highlighting areas of interest.


Rendering a Preview
-------------------

The `render_preview()` method renders the preview of the screen with annotations such as highlighted areas and labels. It can either return the full screen or a cropped version.

### Usage:

```python
preview_image = scope.render_preview(marker={'area': (100, 150, 200, 250), 'mouse_offset': (120, 130), 'label': 'Highlight'})
```

### Parameters:

*   `base_image`: (Optional) Provide a custom image to overlay the preview on, otherwise uses `self.full_image`.
*   `marker`: Dictionary with keys:
    *   `area`: Coordinates of the area to highlight.
    *   `mouse_offset`: Cursor position for crosshair rendering.
    *   `label`: Label text for the highlighted area.
*   `cropped`: If `True`, returns the cropped image, otherwise returns the full image.
  
[python](../src/pyperiscope/layer2.py)