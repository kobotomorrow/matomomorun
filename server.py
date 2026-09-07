import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 8080))
server.listen()

while True:
    conn, addr = server.accept()
    request = conn.recv(4096)
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
