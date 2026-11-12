#!/usr/bin/env python3
"""Uji start bersih smartcow-lab: DATA_DIR kosong tidak boleh crash.

Dijalankan: python3 test_app_fresh_start.py
Hanya memakai stdlib. Fokus pada jalur yang pernah gagal:
- init_dummy_data() memakai math.sin saat history.json belum ada (NameError),
- otentikasi token harus fail-closed saat SMARTCOW_TOKEN kosong,
- body JSON non-objek harus ditolak 400, bukan 500.
"""
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(HERE, "app.py")
TOKEN = "test-token-fresh-start"


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def request(port, path, method="GET", body=None, headers=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request("http://127.0.0.1:%d%s" % (port, path), data=data, method=method)
    req.add_header("Content-Type", "application/json")
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()


class FreshStartTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.port = free_port()
        cls.data = os.path.join(cls.tmp.name, "data")
        env = dict(os.environ)
        env.update({
            "SMARTCOW_DATA": cls.data + "/",  # akhiran "/" ikut diuji
            "SMARTCOW_BIND": "127.0.0.1",
            "SMARTCOW_PORT": str(cls.port),
            "SMARTCOW_TOKEN": TOKEN,
            "SMARTCOW_VALIDATE": "1",
        })
        env.pop("SMARTCOW_LOG", None)
        cls.proc = subprocess.Popen([sys.executable, APP], env=env,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        deadline = time.time() + 20
        while time.time() < deadline:
            if cls.proc.poll() is not None:
                break
            try:
                if request(cls.port, "/health")[0] == 200:
                    return
            except OSError:
                pass
            time.sleep(0.2)
        out = b""
        if cls.proc.poll() is not None:
            out = cls.proc.stdout.read()
        cls.tearDownClass()
        raise AssertionError("app gagal start pada DATA_DIR kosong:\n%s" % out.decode("utf-8", "replace"))

    @classmethod
    def tearDownClass(cls):
        if cls.proc.poll() is None:
            cls.proc.terminate()
            try:
                cls.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                cls.proc.kill()
        cls.tmp.cleanup()

    def test_health_ok(self):
        status, body = request(self.port, "/health")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["status"], "ok")

    def test_fresh_history_written_by_math_branch(self):
        with open(os.path.join(self.data, "history.json"), encoding="utf-8") as fh:
            history = json.load(fh)
        self.assertEqual(len(history), 60)
        self.assertAlmostEqual(history[0]["avg"], round(29.8 + 1.2 * __import__("math").sin(0), 2), places=2)

    def test_secret_seeded_next_to_data_dir(self):
        path = os.path.join(self.tmp.name, "secrets", "admin_password")
        self.assertTrue(os.path.exists(path), "admin_password harus di <dir(DATA_DIR)>/secrets")

    def test_telemetry_requires_token(self):
        path = "/api/devices/cow-sprinkler-01/telemetry/latest"
        self.assertEqual(request(self.port, path)[0], 401)
        self.assertEqual(request(self.port, path, headers={"Authorization": "Bearer "})[0], 401)

    def test_telemetry_with_token_ok(self):
        status, _ = request(self.port, "/api/devices/cow-sprinkler-01/telemetry/latest",
                            headers={"Authorization": "Bearer " + TOKEN})
        self.assertEqual(status, 200)

    def test_non_object_body_rejected(self):
        status, _ = request(self.port, "/api/auth/login", method="POST", body=[1, 2, 3])
        self.assertEqual(status, 400)


class NoTokenFailClosedTest(unittest.TestCase):
    """SMARTCOW_TOKEN kosong: header 'Bearer ' tidak boleh lolos (fail-closed)."""

    def test_empty_token_rejects_blank_bearer(self):
        tmp = tempfile.TemporaryDirectory()
        port = free_port()
        env = dict(os.environ)
        env.update({"SMARTCOW_DATA": os.path.join(tmp.name, "data"), "SMARTCOW_BIND": "127.0.0.1",
                    "SMARTCOW_PORT": str(port)})
        env.pop("SMARTCOW_TOKEN", None)
        proc = subprocess.Popen([sys.executable, APP], env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            deadline = time.time() + 20
            while time.time() < deadline:
                if proc.poll() is not None:
                    self.fail("app mati: %s" % proc.stdout.read().decode("utf-8", "replace"))
                try:
                    if request(port, "/health")[0] == 200:
                        break
                except OSError:
                    pass
                time.sleep(0.2)
            status, _ = request(port, "/api/devices/cow-sprinkler-01/telemetry/latest",
                                headers={"Authorization": "Bearer "})
            self.assertEqual(status, 401)
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main(verbosity=2)
