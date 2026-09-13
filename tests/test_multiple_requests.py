"""通常の複数回のリクエストをサーバーが正しく処理できるか確認するテスト。
"""

import socket
import unittest
from helpers import ServerTestCase, HOST, PORT

class MultipleRequestsProbe(ServerTestCase):
    def test_multiple_requests(self):
        for _ in range(5):
            conn = socket.create_connection((HOST, PORT), timeout=1)
            with conn:
                conn.sendall(
                    b"GET / HTTP/1.1\r\n"
                    b"Host: localhost\r\n"
                    b"\r\n"
                )
                try:
                    response = conn.recv(4096)
                except ConnectionResetError:
                    response = b""

            self.assertTrue(response.startswith(b"HTTP/1.1 200 OK"))

if __name__ == "__main__":
    unittest.main()
