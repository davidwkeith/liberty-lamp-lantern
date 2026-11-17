import unittest

import numpy as np

import check
from check import PX, panel_canvas, art_box


def blank():
    """Panel-sized canvas: False = metal, True = cut."""
    return panel_canvas()


def rect(m, x0, y0, x1, y1, value=True):
    """Set a mm-rectangle (origin top-left of panel)."""
    m[int(y0 * PX):int(y1 * PX), int(x0 * PX):int(x1 * PX)] = value
    return m


def bird_ok():
    m = blank()
    bx = art_box()
    cx, cy = (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2
    return rect(m, cx - 15, cy - 20, cx + 15, cy + 20)  # a 30 × 40 mm cut-out


class CheckTest(unittest.TestCase):
    def test_valid_panel_passes(self):
        self.assertEqual(check.problems(bird_ok()), [])

    def test_island_flagged(self):
        m = bird_ok()
        bx = art_box()
        cx, cy = (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2
        rect(m, cx - 2, cy - 2, cx + 2, cy + 2, value=False)  # metal "eye" floating in the cut
        self.assertTrue(any("island" in p for p in check.problems(m)))

    def test_thin_metal_flagged(self):
        m = bird_ok()
        bx = art_box()
        cx, cy = (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2
        # second cut-out leaving a 0.6 mm metal web between them
        rect(m, cx + 15.6, cy - 20, cx + 25, cy + 20)
        self.assertTrue(any("thin metal" in p for p in check.problems(m)))

    def test_thin_cut_flagged(self):
        m = bird_ok()
        bx = art_box()
        cx, cy = (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2
        rect(m, cx + 15, cy, cx + 25, cy + 0.6)  # 0.6 mm wide slot sticking out
        self.assertTrue(any("thin cut" in p for p in check.problems(m)))

    def test_sharp_corners_not_flagged(self):
        """A plain rectangle's corners are not 'thin features'."""
        self.assertFalse(any("thin" in p for p in check.problems(bird_ok())))

    def test_outside_art_box_flagged(self):
        m = bird_ok()
        rect(m, 1, 1, 5, 5)  # cut near the panel corner, under the frame
        self.assertTrue(any("art box" in p for p in check.problems(m)))


if __name__ == "__main__":
    unittest.main()
