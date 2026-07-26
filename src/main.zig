const std = @import("std");
const linux = std.os.linux;

const ServerError = error{
    SocketCreationFailed,
    ReuseAddressFailed,
    BindSocketFailed,
    ListenSocketFailed,
    AcceptFailed,
    ReadRequestFailed,
    WriteResponseFailed,
};

pub fn main() ServerError!void {
    const socket_fd = try create_socket();
    defer _ = linux.close(socket_fd);
    std.debug.print("socket_fd: {}\n", .{socket_fd});

    try enable_reuse_address(socket_fd);
    try bind_socket(socket_fd);
    try listen_socket(socket_fd);
    try serve_forever(socket_fd);
}

// IPv4, Stream通信 のデフォルトのプロトコルがTCP
fn create_socket() ServerError!linux.fd_t {
    const rc = linux.socket(linux.AF.INET, linux.SOCK.STREAM, 0);
    return switch (linux.errno(rc)) {
        linux.E.SUCCESS => @intCast(rc),
        else => ServerError.SocketCreationFailed,
    };
}

// ソケットレベルで、アドレスの再利用を許可
// 再起動時のポート競合によるバインドのエラーを回避する
fn enable_reuse_address(fd: linux.fd_t) ServerError!void {
    const yes: i32 = 1;
    const rc = linux.setsockopt(
        fd,
        linux.SOL.SOCKET,
        linux.SO.REUSEADDR,
        @ptrCast(&yes),
        @sizeOf(@TypeOf(yes)),
    );
    return switch (linux.errno(rc)) {
        linux.E.SUCCESS => {},
        else => ServerError.ReuseAddressFailed,
    };
}

fn bind_socket(fd: linux.fd_t) ServerError!void {
    const loopback = 0x7f000001; // 127.0.0.1
    const socket_addr = linux.sockaddr.in{
        .family = linux.AF.INET,
        .port = std.mem.nativeToBig(u16, 8080),
        .addr = std.mem.nativeToBig(u32, loopback),
    };
    const rc = linux.bind(
        fd,
        @ptrCast(&socket_addr),
        @sizeOf(@TypeOf(socket_addr)),
    );
    return switch (linux.errno(rc)) {
        linux.E.SUCCESS => {},
        else => ServerError.BindSocketFailed,
    };
}

fn listen_socket(fd: linux.fd_t) ServerError!void {
    const rc = linux.listen(fd, 5);
    return switch (linux.errno(rc)) {
        linux.E.SUCCESS => {},
        else => ServerError.ListenSocketFailed,
    };
}

fn serve_forever(socket_fd: linux.fd_t) ServerError!void {
    while (true) {
        try handle_connection(socket_fd);
    }
}

fn handle_connection(socket_fd: linux.fd_t) ServerError!void {
    var accept_addr = linux.sockaddr.in{
        .family = linux.AF.INET,
        .port = undefined,
        .addr = undefined,
    };
    var accept_socket_len: linux.socklen_t = @sizeOf(@TypeOf(accept_addr));
    const accept_rc = linux.accept(
        socket_fd,
        @ptrCast(&accept_addr),
        &accept_socket_len,
    );
    const accept_fd: linux.fd_t = try switch (linux.errno(accept_rc)) {
        linux.E.SUCCESS => @as(linux.fd_t, @intCast(accept_rc)),
        else => ServerError.AcceptFailed,
    };
    defer _ = linux.close(accept_fd);
    std.debug.print("accept_fd: {}\n", .{accept_fd});

    var r_buf: [1024]u8 = undefined;
    var used: i32 = 0;
    var cur_index: usize = 0;
    var request_len_limit: i32 = @sizeOf(@TypeOf(r_buf)) - 1;
    var request_completed = false;
    while (true) {
        const read_rc = linux.read(
            accept_fd,
            r_buf[cur_index..].ptr,
            @as(usize, @intCast(request_len_limit)),
        );
        const read_len: i32 = try switch (linux.errno(read_rc)) {
            linux.E.SUCCESS => @as(i32, @intCast(read_rc)),
            else => ServerError.ReadRequestFailed,
        };
        used += read_len;
        cur_index = @intCast(used);
        request_len_limit -= read_len;
        r_buf[cur_index] = 0;

        if (std.mem.indexOf(u8, r_buf[0..cur_index], "\r\n\r\n") != null) {
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
        std.debug.print("incomplete HTTP request\n", .{});
        return;
    }

    std.debug.print("request: {s}\n", .{r_buf[0..cur_index]});

    const response =
        "HTTP/1.1 200 OK\r\n" ++
        "Content-Length: 6\r\n" ++
        "Connection: close\r\n" ++
        "\r\n" ++
        "hello\n";
    const write_rc = linux.write(accept_fd, response, response.len);
    _ = try switch (linux.errno(write_rc)) {
        linux.E.SUCCESS => {},
        else => ServerError.WriteResponseFailed,
    };
}
