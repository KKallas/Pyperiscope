"""Pictures for whoever fixes a failure (agent or human).

Agents see screenshots downscaled, so they cannot read exact pixels off a
3600px Retina capture. Two helpers close that gap, in the spirit of the
computer-use `zoom` action:
- draw_matches: numbered candidate boxes ([0], [1], ...) = `--candidate N`
- zoom: crop a region, enlarge it, and print a grid labelled in ORIGINAL
  screenshot pixels, so coordinates read off the zoom can be used directly.
"""
import cv2

GREEN, YELLOW, BLUE, ORANGE = (60, 200, 60), (0, 210, 255), (255, 140, 30), (0, 140, 255)
FONT = cv2.FONT_HERSHEY_SIMPLEX


def _label(image, text, x, y, color, scale=0.6):
    (w, h), _ = cv2.getTextSize(text, FONT, scale, 2)
    y = max(h + 4, y)
    cv2.rectangle(image, (x, y - h - 6), (x + w + 6, y), color, -1)
    cv2.putText(image, text, (x + 3, y - 4), FONT, scale, (0, 0, 0), 2, cv2.LINE_AA)


def draw_matches(image, matches, best=None, target_size=None):
    out = image.copy()
    for i, m in enumerate(matches):
        x, y, w, h = (int(v) for v in m.box)
        cv2.rectangle(out, (x, y), (x + w, y + h), GREEN, 3)
        cv2.drawMarker(out, (int(m.click[0]), int(m.click[1])), BLUE, cv2.MARKER_CROSS, 18, 2)
        _label(out, f"[{i}] {m.score:.2f}", x, y - 2, GREEN)
    if best and not matches and target_size:
        x, y = best["at"]
        cv2.rectangle(out, (x, y), (x + target_size[0], y + target_size[1]), YELLOW, 2)
        _label(out, f"best {best['score']:.2f} (below threshold)", x, y - 2, YELLOW)
    return out


def draw_boxes(image, boxes, color=ORANGE, prefix="D"):
    out = image.copy()
    for i, (x, y, w, h) in enumerate(boxes, 1):
        cv2.rectangle(out, (int(x), int(y)), (int(x + w), int(y + h)), color, 2)
        _label(out, f"{prefix}{i}", int(x), int(y) - 2, color)
    return out


def zoom(image, box, factor=None, grid=None):
    """Enlarged crop of `box` (x, y, w, h) with a grid in original pixels."""
    x, y, w, h = (int(v) for v in box)
    H, W = image.shape[:2]
    x, y = max(0, x), max(0, y)
    w, h = min(w, W - x), min(h, H - y)
    factor = factor or max(1, min(6, 1200 // max(w, h, 1)))
    crop = cv2.resize(image[y:y + h, x:x + w], (w * factor, h * factor), interpolation=cv2.INTER_NEAREST)
    grid = grid or _nice_step(max(w, h) / 8)
    for gx in range(x - x % grid + grid, x + w, grid):
        px = (gx - x) * factor
        cv2.line(crop, (px, 0), (px, h * factor), (255, 0, 255), 1)
        _label(crop, str(gx), px + 2, 16, (255, 180, 255), 0.45)
    for gy in range(y - y % grid + grid, y + h, grid):
        py = (gy - y) * factor
        cv2.line(crop, (0, py), (w * factor, py), (255, 0, 255), 1)
        _label(crop, str(gy), 2, py - 2, (255, 180, 255), 0.45)
    return crop


def _nice_step(raw):
    for step in (5, 10, 20, 25, 50, 100, 200, 250, 500):
        if step >= raw:
            return step
    return 1000
