#include <stdio.h>
#include <sys/socket.h>
#include <unistd.h>
#include <netinet/in.h>
#include <string.h>
#include <stdbool.h>

int main() {
    int socket_fd, accept_fd;
    char r_buf[1024];
    struct sockaddr_in socket_addr, accept_addr;

    // IPv4, Stream通信 のデフォルトのプロトコルがTCP
    socket_fd = socket(AF_INET, SOCK_STREAM, 0);
    printf("socket_fd: %d\n", socket_fd);
    if (socket_fd == -1) {
        perror("socket");
        return 1;
    }

    int yes = 1;
    // ソケットレベルで、アドレスの再利用を許可
    // 再起動時のポート競合によるバインドのエラーを回避する
    if (setsockopt(socket_fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes)) == -1) {
        perror("setsockopt");
        return 1;
    }

    socket_addr.sin_family = AF_INET;
    // ポート番号をネットワークバイトオーダーに変換
    socket_addr.sin_port = htons(8080);
    // ループバックアドレスをネットワークバイトオーダーに変換
    // ローカルホストからの接続のみを受け付ける
    socket_addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    // ソケットをアドレスにバインドする
    if (bind(socket_fd, (struct sockaddr *)&socket_addr, sizeof(socket_addr)) == -1) {
        perror("bind");
        return 1;
    }

    // accept待ちのキューの最大数を5に設定
    if (listen(socket_fd, 5) == -1) {
        perror("listen");
        return 1;
    }

    while(1) {
        socklen_t accept_addr_len = sizeof(accept_addr);
        // ソケットから接続済みコネクションを取り出し、コネクションを読み書きするための新しいファイルディスクリプタを返す
        // 通信元のアドレス情報をaccept_addrに格納する
        accept_fd = accept(socket_fd, (struct sockaddr *)&accept_addr, &accept_addr_len);
        printf("accept_fd: %d\n", accept_fd);
        if (accept_fd == -1) {
            perror("accept");
            return 1;
        }

        ssize_t used = 0;
        ssize_t read_len = 0;
        size_t request_len_limit = sizeof(r_buf) - 1;
        bool request_completed = false;
        while (1) {
            read_len = read(accept_fd, r_buf + used, request_len_limit);
            if (read_len == -1) {
                perror("read");
                return 1;
            }
            used += read_len;
            request_len_limit -= read_len;
            r_buf[used] = '\0';
            if (strstr(r_buf, "\r\n\r\n") != NULL) {
                request_completed = true;
                break;
            }

            // バッファの上限を超過した場合
            if (request_len_limit <= 0) {
                break;
            }

            // 途中で接続が切れた場合
            if (read_len == 0) {
                break;
            }
        }

        if (!request_completed) {
            fprintf(stderr, "incomplete HTTP request\n");
            close(accept_fd);
            continue;
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
