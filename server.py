import socket

REQUEST_BUFFER_SIZE = 4096
REQUEST_SEPARATOR = b"\r\n\r\n"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 8080))
server.listen()

while True:
    conn, addr = server.accept()
    request = b""
    is_incomplete_request = False
    while REQUEST_SEPARATOR not in request:
        request_chunk = conn.recv(REQUEST_BUFFER_SIZE)
        if request_chunk == b"":
            is_incomplete_request = True
            break
        request += request_chunk
    print(request.decode())

    if is_incomplete_request:
        conn.close()
        continue

    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/plain\r\n"
        "Content-Length: 13\r\n"
        "\r\n"
        "Hello, World!"
    )

    conn.sendall(response.encode())
    conn.close()
