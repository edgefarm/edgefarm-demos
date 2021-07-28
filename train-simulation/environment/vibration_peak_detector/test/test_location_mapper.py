import unittest
import numpy as np
from vibration_peak_detector.src.location_mapper import (
    map_timestamp_to_location,
    find_last_unused_location_entry,
)


class TestLocationMapper(unittest.TestCase):
    def test_map_timestamp_to_location(self):
        location_records = np.array(
            [
                [1.0, 49.1, 11.4],
                [2.0, 49.4, 11.3],
                [3.0, 49.8, 11.2],
                [4.0, 49.6, 11.4],
            ]
        )

        lat, lon, status = map_timestamp_to_location(1.0, location_records)
        self.assertEqual(round(lat, 2), 49.1)
        self.assertEqual(round(lon, 2), 11.4)
        self.assertEqual(status, "ok")

        lat, lon, status = map_timestamp_to_location(3.5, location_records)
        self.assertEqual(round(lat, 2), 49.7)
        self.assertEqual(round(lon, 2), 11.3)
        self.assertEqual(status, "ok")

        lat, lon, status = map_timestamp_to_location(5, location_records)
        self.assertEqual(status, "ts-too-new")

        lat, lon, status = map_timestamp_to_location(0.5, location_records)
        self.assertEqual(status, "ts-too-old")

        # no entries in fifo
        location_records = np.array([])
        lat, lon, status = map_timestamp_to_location(0.5, location_records)
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

        idx = find_last_unused_location_entry(1.0, location_records)
        self.assertIsNone(idx)

        idx = find_last_unused_location_entry(2.0, location_records)
        self.assertEqual(idx, 0)

        idx = find_last_unused_location_entry(3.1, location_records)
        self.assertEqual(idx, 1)

        idx = find_last_unused_location_entry(4.0, location_records)
        self.assertEqual(idx, 2)

        idx = find_last_unused_location_entry(5.0, location_records)
        self.assertEqual(idx, 2)

        # no entries in fifo
        location_records = np.array([])
        idx = find_last_unused_location_entry(1.0, location_records)
        self.assertIsNone(idx)
