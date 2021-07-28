import unittest
import numpy as np
from vibration_peak_detector.src.fifo import Fifo


class TestFifo(unittest.TestCase):
    def data_2d(self, cols, start, n, step):
        a = np.ndarray((n, cols))
        stop = start + step * n
        a[:, 0] = np.arange(start, stop, step)
        a[:, 1] = np.arange(start * 1000, stop * 1000, step * 1000)
        return a

    def test_2d_basic(self):
        cols = 2
        f = Fifo((10, cols))
        self.assertEqual(f.free_entries(), 10)

        f.push(self.data_2d(cols, 0, 2, 1))
        self.assertEqual(f.entries(), 2)
        self.assertEqual(f.free_entries(), 8)

        f.push(self.data_2d(cols, 2, 8, 1))
        self.assertEqual(f.entries(), 10)
        self.assertEqual(f.free_entries(), 0)

        with self.assertRaises(BufferError):
            f.push(self.data_2d(cols, 10, 1, 1))

        a = f.pop(1)
        self.assertTrue(np.array_equal(a, [[0, 0]]))
        self.assertEqual(f.entries(), 9)
        self.assertEqual(f.free_entries(), 1)

        a = f.peek(1)
        self.assertTrue(np.array_equal(a, [[1, 1000]]))
        a = f.peek(1)
        self.assertTrue(np.array_equal(a, [[1, 1000]]))

        a = f.pop(8)
        self.assertTrue(
            np.array_equal(
                a,
                [
                    [1, 1000],
                    [2, 2000],
                    [3, 3000],
                    [4, 4000],
                    [5, 5000],
                    [6, 6000],
                    [7, 7000],
                    [8, 8000],
                ],
            )
        )

        with self.assertRaises(BufferError):
            a = f.pop(2)
