#include <stdio.h>
#include <sys/socket.h>
#include <unistd.h>
#include <netinet/in.h>
#include <string.h>

int main() {
    int socket_fd, accept_fd;
    char r_buf[1024];
    struct sockaddr_in socket_addr;
    struct sockaddr accept_addr;

    socket_fd = socket(AF_INET, SOCK_STREAM, 0);
    printf("socket_fd: %d\n", socket_fd);
    if (socket_fd == -1) {
        perror("socket");
        return 1;
    }

    int yes = 1;
    if (setsockopt(socket_fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes)) == -1) {
        perror("setsockopt");
        return 1;
    }

    socket_addr.sin_family = AF_INET;
    socket_addr.sin_port = htons(8080);
    socket_addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    if (bind(socket_fd, (struct sockaddr *)&socket_addr, sizeof(socket_addr)) == -1) {
        perror("bind");
        return 1;
    }

    if (listen(socket_fd, 5) == -1) {
        perror("listen");
        return 1;
    }

    while(1) {
        socklen_t accept_addr_len = sizeof(accept_addr);
        accept_fd = accept(socket_fd, &accept_addr, &accept_addr_len);
        printf("accept_fd: %d\n", accept_fd);
        if (accept_fd == -1) {
            perror("accept");
            return 1;
        }

        if (read(accept_fd, r_buf, sizeof(r_buf)) == -1) {
            perror("read");
            return 1;
        }
        printf("request: %s\n", r_buf);

        const char *response =
            "HTTP/1.1 200 OK\r\n"
            "Content-Length: 5\r\n"
            "Connection: close\r\n"
            "\r\n"
            "hello";
        if (write(accept_fd, response, strlen(response)) == -1) {
            perror("write");
            return 1;
        }

        if (close(accept_fd) == -1) {
            perror("close");
            return 1;
        }
    }

    return 0;
}
