import socket  # noqa: F401


def handle_request(client_socket: socket.socket) -> None:
    try:
        data = client_socket.recv(1024)
        if not data:
            return
        response = parse_request(data)
        client_socket.sendall(response.encode())
    except Exception as e:
        print(f"Error handling request: {e}")
    finally:
        client_socket.close()


def parse_request(data: bytes) -> str:
    try:
        request_data = data.decode().split("\r\n")
        request_line = request_data[0]
        method, path, http_ver = request_line.split()

        if method == "GET" and path == "/":
            return "HTTP/1.1 200 OK\r\n\r\n"
        elif path.startswith("/echo/"):
            return f"HTTP/1.1 200 OK\r\nContent - Type: text / plain\r\nContent - Length: {len(path[6:])}\r\n\r\n{path[6:]}"
        else:
            return "HTTP/1.1 404 Not Found\r\n\r\n"

    except Exception as e:
        print(f"Error parsing request: {e}")
        return "HTTP/1.1 400 Bad Request\r\n\r\n"


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")

    print("Starting Server ...")
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()

    try:
        while True:
            client_socket, address = server_socket.accept()
            print(f"Connection from {address}")
            handle_request(client_socket)
    except KeyboardInterrupt:
        print("Shutting down Server ...")
    except Exception as e:
        print(f"Server Error: {e}")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
