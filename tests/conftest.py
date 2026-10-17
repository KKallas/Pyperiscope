"""Synthetic screens: a list with three identical blue "Edit" buttons, one per
row, each row with a different label. The button alone is ambiguous; the
button + its row label (a detail) is unique."""
import cv2
import numpy as np
import pytest

from pyperiscope import Project, Shot

FONT = cv2.FONT_HERSHEY_SIMPLEX
ROWS = ["Alpha Corp", "Beta Ltd", "Gamma AS"]
ROW_Y = [100, 220, 340]
BUTTON = lambda row: (495, ROW_Y[row] - 5, 130, 55)        # main box around "Edit" in a row
LABEL = lambda row: (35, ROW_Y[row] + 2, 190, 38)          # detail box around the row label


def make_image(rows=ROWS, shift=(0, 0)):
    img = np.full((520, 800, 3), 245, np.uint8)
    cv2.putText(img, "Customers", (40, 50), FONT, 1.1, (20, 20, 20), 2)
    for name, y in zip(rows, ROW_Y):
        y += shift[1]
        cv2.putText(img, name, (40 + shift[0], y + 30), FONT, 0.9, (30, 30, 30), 2)
        cv2.rectangle(img, (500 + shift[0], y), (620 + shift[0], y + 45), (200, 120, 40), -1)
        cv2.putText(img, "Edit", (525 + shift[0], y + 32), FONT, 0.9, (255, 255, 255), 2)
    return img


@pytest.fixture
def shot():
    return Shot(make_image(), origin=(0, 0), scale=1.0)


@pytest.fixture
def project(tmp_path):
    return Project.create(tmp_path / "proj", input="dry", overlay=False, timeout=0.3, action_delay=0)


@pytest.fixture
def saved_shot(project, shot):
    path = shot.save(project.screens / "s1.png")
    return project.relative(path)
