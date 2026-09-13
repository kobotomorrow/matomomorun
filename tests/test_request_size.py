"""4096バイトを超えるサイズの大きいリクエストをサーバーが受け取れるか確認するテスト。
"""

import socket
import subprocess
import sys
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server.py"
HOST = "127.0.0.1"
PORT = 8080


class RequestSizeProbe(unittest.TestCase):
    def test_server_receives_large_request(self):
        marker = b"X-End-Marker: reached-the-end"
        padding = b"a" * 5000
        request = (
            b"GET / HTTP/1.1\r\n"
            b"Host: localhost\r\n"
            b"X-Padding: " + padding + b"\r\n"
            + marker + b"\r\n\r\n"
        )
        self.assertGreater(len(request), 4096)

        server = subprocess.Popen(
            [sys.executable, "-u", str(SERVER)],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        # サーバーのリッスン待ち
        time.sleep(0.1)

        try:
            conn = socket.create_connection((HOST, PORT), timeout=1)
            with conn:
                conn.sendall(request)
                try:
                    while conn.recv(4096):
                        pass
                except ConnectionResetError:
                    # リクエストが全て処理される前にサーバーの接続が閉じられる
                    # エラーによる処理終了ではなく、後続のfailed assertionで確認するため、ここでは握りつぶしている
                    pass
            server.terminate()
            output, _ = server.communicate(timeout=3)
        finally:
            if server.poll() is None:
                server.kill()
                server.wait(timeout=3)

        received_log = output.decode("utf-8", errors="replace")
        self.assertIn(
            marker.decode(),
            received_log,
            f"server log did not contain the end marker; sent {len(request)} bytes.\n"
            "This reproduces the one-recv limitation in server.py:\n"
            f"{received_log[-300:]}",
        )

if __name__ == "__main__":
    unittest.main()
