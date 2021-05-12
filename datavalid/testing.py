from unittest import TestCase

from pandas.testing import assert_frame_equal


class BaseTestCase(TestCase):
    def assert_frames_equal(self, frames_a, frames_b):
        self.assertEqual(len(frames_a), len(frames_b))
        for i, frame in enumerate(frames_a):
            assert_frame_equal(frame, frames_b[i])
