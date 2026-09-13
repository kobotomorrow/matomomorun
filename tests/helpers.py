import subprocess
import sys
from pathlib import Path
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server.py"
HOST = "127.0.0.1"
PORT = 8080

class ServerTestCase(unittest.TestCase):
    def setUp(self):
        self.server = subprocess.Popen(
            [sys.executable, "-u", str(SERVER)],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.server_output = None
        self.addCleanup(self._stop_server)

        # サーバーのリッスン待ち
        time.sleep(0.1)

    def _stop_server(self):
        if self.server_output is None:
            if self.server.poll() is None:
                self.server.terminate()
            self.server_output, _ = self.server.communicate(timeout=3)
        return self.server_output
