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
        logic = AnalyzerLogic(100, 0.01, None)
        accel = np.ndarray((100, 2))
        accel[:, 0] = np.linspace(1, 1.99, 100)
        self.assertFalse(logic._has_time_gaps(accel))

    def test_has_time_gaps_bad_case(self):
        logic = AnalyzerLogic(100, 0.01, None)
        accel = np.ndarray((100, 2))
        accel[:, 0] = np.linspace(1, 2.2, 100)
        self.assertTrue(logic._has_time_gaps(accel))

    def test_map_timestamp_to_location(self):
        location_records = np.array(
            [
                [1.0, 49.1, 11.4],
                [2.0, 49.4, 11.3],
                [3.0, 49.8, 11.2],
                [4.0, 49.6, 11.4],
            ]
        )

        lat, lon, status = AnalyzerLogic._map_timestamp_to_location(
            1.0, location_records
        )
        self.assertEqual(round(lat, 2), 49.1)
        self.assertEqual(round(lon, 2), 11.4)
        self.assertEqual(status, "ok")

        lat, lon, status = AnalyzerLogic._map_timestamp_to_location(
            3.5, location_records
        )
        self.assertEqual(round(lat, 2), 49.7)
        self.assertEqual(round(lon, 2), 11.3)
        self.assertEqual(status, "ok")

        lat, lon, status = AnalyzerLogic._map_timestamp_to_location(5, location_records)
        self.assertEqual(status, "ts-too-new")

        lat, lon, status = AnalyzerLogic._map_timestamp_to_location(
            0.5, location_records
        )
        self.assertEqual(status, "ts-too-old")

        # no entries in fifo
        location_records = np.array([])
        lat, lon, status = AnalyzerLogic._map_timestamp_to_location(
            0.5, location_records
        )
        self.assertEqual(status, "ts-too-new")

    def test_find_last_unused_location_entry(self):
        location_records = np.array(
            [
                [1.0, 49.1, 11.4],
                [2.0, 49.4, 11.3],
                [3.0, 49.8, 11.2],
                [4.0, 49.6, 11.4],
            ]
        )

        idx = AnalyzerLogic._find_last_unused_location_entry(1.0, location_records)
        self.assertIsNone(idx)

        idx = AnalyzerLogic._find_last_unused_location_entry(2.0, location_records)
        self.assertEqual(idx, 0)

        idx = AnalyzerLogic._find_last_unused_location_entry(3.1, location_records)
        self.assertEqual(idx, 1)

        idx = AnalyzerLogic._find_last_unused_location_entry(4.0, location_records)
        self.assertEqual(idx, 2)

        idx = AnalyzerLogic._find_last_unused_location_entry(5.0, location_records)
        self.assertEqual(idx, 2)

        # no entries in fifo
        location_records = np.array([])
        idx = AnalyzerLogic._find_last_unused_location_entry(1.0, location_records)
        self.assertIsNone(idx)
