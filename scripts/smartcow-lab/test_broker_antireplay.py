#!/usr/bin/env python3
"""Uji anti-replay broker MQTT tanpa membuka soket.

Jalankan dari folder ini: python3 test_broker_antireplay.py
"""
import json
import unittest

import broker


class ReplayTest(unittest.TestCase):
    def setUp(self):
        broker.ANTI_REPLAY = True
        broker.TS_WINDOW_S = 120.0
        broker._last_ts.clear()

    def check(self, topic, body, now):
        return broker.replay_problem(topic, json.dumps(body).encode("utf-8"), now_s=now)

    def test_off_mode_accepts_anything(self):
        broker.ANTI_REPLAY = False
        self.assertIsNone(broker.replay_problem("t", b"bukan json", now_s=1.0))

    def test_fresh_timestamp_accepted(self):
        self.assertIsNone(self.check("t", {"ts": 1700000000000}, 1700000001.0))

    def test_duplicate_rejected(self):
        body = {"ts": 1700000000000}
        self.assertIsNone(self.check("t", body, 1700000001.0))
        self.assertIn("duplikat", self.check("t", body, 1700000002.0))

    def test_older_timestamp_rejected(self):
        self.assertIsNone(self.check("t", {"ts": 1700000005000}, 1700000006.0))
        self.assertIn("mundur", self.check("t", {"ts": 1700000001000}, 1700000007.0))

    def test_expired_rejected(self):
        self.assertIn("kedaluwarsa", self.check("t", {"ts": 1700000000000}, 1700001000.0))

    def test_missing_timestamp_rejected(self):
        self.assertIn("tanpa stempel", self.check("t", {"t1": 29.0}, 1700000000.0))

    def test_seconds_timestamp_accepted(self):
        self.assertIsNone(self.check("t", {"ts": 1700000000}, 1700000001.0))

    def test_counter_per_topic(self):
        self.assertIsNone(self.check("a", {"ts": 1700000000000}, 1700000001.0))
        self.assertIsNone(self.check("b", {"ts": 1700000000000}, 1700000001.0))


if __name__ == "__main__":
    unittest.main()
