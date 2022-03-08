import unittest
import numpy as np
from vibration_peak_detector.src.analyzer import AnalyzerLogic


class TestAnalyzer(unittest.TestCase):
    def test_calculate_rms(self):
        x = np.linspace(-np.pi, np.pi, 201)
        y = np.sin(x)
        rms = AnalyzerLogic._calculate_rms(y)
        self.assertGreater(rms, 0.705)
        self.assertLess(rms, 0.708)

    def test_analyze_chunk(self):
        x = np.linspace(-np.pi, np.pi, 201)
        y = np.sin(x)
        accel = np.ndarray((201, 2))
        accel[:, 1] = y
        rms = AnalyzerLogic._analyze_chunk(accel)
        # RMS over differential of sin wave = RMS of wave / (n samples * 2 *  PI)
        self.assertGreater(rms, 0.020)
        self.assertLess(rms, 0.023)

    def test_has_time_gaps_good_case(self):
        logic = AnalyzerLogic(100, 0.01)
        accel = np.ndarray((100, 2))
        accel[:, 0] = np.linspace(1, 1.99, 100)
        self.assertFalse(logic._has_time_gaps(accel))

    def test_has_time_gaps_bad_case(self):
        logic = AnalyzerLogic(100, 0.01)
        accel = np.ndarray((100, 2))
        accel[:, 0] = np.linspace(1, 2.2, 100)
        self.assertTrue(logic._has_time_gaps(accel))
