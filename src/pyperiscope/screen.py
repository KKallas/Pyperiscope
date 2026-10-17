"""Screen capture. Images are BGR numpy arrays in physical pixels (Retina = 2x).
A Shot remembers how its pixels map back to global screen points, which is the
coordinate space mouse events use. Every saved PNG gets a sidecar <name>.png.json
with that mapping, so a screenshot on disk is enough to validate a target edit."""
import json
from dataclasses import dataclass
from pathlib import Path

import cv2
import mss
import numpy as np


@dataclass
class Shot:
    image: np.ndarray
    origin: tuple = (0, 0)   # top-left of the captured monitor, in points
    scale: float = 1.0       # pixels per point

    @property
    def size(self):
        h, w = self.image.shape[:2]
        return (w, h)

    def to_points(self, x, y):
        return (self.origin[0] + x / self.scale, self.origin[1] + y / self.scale)

    def to_pixels(self, x, y):
        return ((x - self.origin[0]) * self.scale, (y - self.origin[1]) * self.scale)

    def crop(self, box):
        x, y, w, h = (int(v) for v in box)
        if w <= 0 or h <= 0 or x < 0 or y < 0 or x + w > self.size[0] or y + h > self.size[1]:
            raise ValueError(f"box {box} is outside the {self.size[0]}x{self.size[1]} screenshot")
        return self.image[y:y + h, x:x + w].copy()

    def save(self, png_path):
        path = Path(png_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(path), self.image)
        meta = {"origin": list(self.origin), "scale": self.scale, "size": list(self.size)}
        meta_path(path).write_text(json.dumps(meta))
        return path

    @classmethod
    def load(cls, png_path):
        path = Path(png_path)
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            raise FileNotFoundError(f"cannot read screenshot {path}")
        sidecar = meta_path(path)
        meta = json.loads(sidecar.read_text()) if sidecar.exists() else {}
        return cls(image, tuple(meta.get("origin", (0, 0))), float(meta.get("scale", 1.0)))


def meta_path(png_path):
    """failure.png -> failure.png.json (never clashes with report files)."""
    return Path(png_path).with_name(Path(png_path).name + ".json")


def capture(monitor=1):
    """Grab one monitor (1 = main). Windows marked NSWindowSharingNone, like our
    own overlay, are left out by macOS, so they never pollute matching."""
    with mss.MSS() as sct:
        area = sct.monitors[monitor]
        raw = sct.grab(area)
    image = np.ascontiguousarray(np.asarray(raw)[:, :, :3])
    return Shot(image, (area["left"], area["top"]), raw.width / area["width"])
