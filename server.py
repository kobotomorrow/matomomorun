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
    while REQUEST_SEPARATOR not in request:
        request += conn.recv(REQUEST_BUFFER_SIZE)
    print(request.decode())

    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/plain\r\n"
        "Content-Length: 13\r\n"
        "\r\n"
        "Hello, World!"
    )

    conn.sendall(response.encode())
    conn.close()
