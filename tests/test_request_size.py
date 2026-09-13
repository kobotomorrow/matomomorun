"""4096バイトを超えるサイズの大きいリクエストをサーバーが受け取れるか確認するテスト。
"""

import socket
import unittest
from helpers import ServerTestCase, HOST, PORT

class RequestSizeProbe(ServerTestCase):
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

        conn = socket.create_connection((HOST, PORT), timeout=1)
        with conn:
            conn.sendall(request)
            try:
                while conn.recv(4096):
                    pass
            except ConnectionResetError:
                # リクエストが全て処理される前にサーバーの接続が閉じられる
                # エラーによる処理終了ではなく、後続のassertionで確認するため、ここでは握りつぶす
                pass

        received_log = self._stop_server().decode("utf-8", errors="replace")
        self.assertIn(
            marker.decode(),
            received_log,
            f"server log did not contain the end marker; sent {len(request)} bytes.\n"
            "This reproduces the one-recv limitation in server.py:\n"
            f"{received_log[-300:]}",
        )

if __name__ == "__main__":
    unittest.main()
