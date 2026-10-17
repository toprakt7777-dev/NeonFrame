import os
import tempfile
import unittest
import numpy as np
from detector import detect_people, draw_detections
from settings import load_settings, save_settings


class CoreTests(unittest.TestCase):
    def test_empty_image_has_no_detections(self):
        self.assertEqual(detect_people(None), [])
        self.assertEqual(detect_people(np.zeros((0, 0, 3), dtype=np.uint8)), [])

    def test_draw_returns_independent_frame(self):
        frame = np.zeros((40, 40, 3), dtype=np.uint8)
        out = draw_detections(frame, [(5, 5, 20, 25, 1.0)])
        self.assertEqual(out.shape, frame.shape)
        self.assertFalse(np.array_equal(out, frame))

    def test_settings_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'settings.json')
            save_settings({'confidence': 77, 'box_color': '#ff00aa'}, path)
            loaded = load_settings(path)
            self.assertEqual(loaded['confidence'], 77)
            self.assertEqual(loaded['box_color'], '#ff00aa')
            self.assertTrue(loaded['detection_enabled'])


if __name__ == '__main__': unittest.main()
