import os
import socket  # noqa: F401
import threading
import argparse


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
        print(f"Closing connection to {client_socket.getpeername()}")
        client_socket.close()


def parse_request(data: bytes) -> str:
    try:
        request_data = data.decode().split("\r\n")
        # Request Line
        request_line = request_data[0]
        method, path, http_ver = request_line.split()

        if method == "GET" and path == "/":
            return http_response_generator(200)
        elif path.startswith("/echo/"):
            text = path[6:]
            return http_response_generator(200, has_headers=True, content_type="text/plain", content_body=text)
        elif path.startswith("/user-agent"):
            # Request: User-Agent
            user_agent = get_user_agent(request_data)
            return http_response_generator(200, has_headers=True, content_type="text/plain", content_body=user_agent)
        elif path.startswith("/files/"):
            # Request: File
            args = parse_arguments()
            file_path = os.path.join(args.directory, path[7:])
            if file_content := get_file_content(file_path):
                return http_response_generator(200, has_headers=True, content_type="application/octet-stream",
                                               content_body=file_content)
            else:
                return http_response_generator(404)
        else:
            return http_response_generator(404)

    except Exception as e:
        print(f"Error parsing request: {e}")
        return http_response_generator(400)


def http_response_generator(code: int = None, has_headers: bool = False, content_type: str = None,
                            content_body: str = None) -> str:
    if code == 200:
        response = "HTTP/1.1 200 OK\r\n\r\n"
        if has_headers:
            response = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(content_body)}\r\n\r\n{content_body}"
    elif code == 400:
        response = "HTTP/1.1 400 Bad Request\r\n\r\n"
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n"

    return response


def get_user_agent(request_data: list[str]) -> str | None:
    try:
        for request in request_data:
            if "User-Agent" in request:
                return request.split(': ')[1]

        # This catches requests without User-Agent
        raise Exception("User-Agent not found")
    except Exception as e:
        print(f"User-Agent Error: {e}")
        return None


def get_file_content(filename: str) -> str | None:
    try:
        with open(filename, "r") as f:
            if content := f.read():
                return content

            # This catches if file is empty
            raise Exception("File is Empty!")
    except Exception as e:
        print(f"File Error: {e}")
        return None


def parse_arguments():
    parser = argparse.ArgumentParser(description="Simple HTTP Server")
    parser.add_argument("--directory", help="Absolute directory path.", required=False)
    return parser.parse_args()


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
            thrd = threading.Thread(target=handle_request, args=(client_socket,))
            thrd.start()
    except KeyboardInterrupt:
        print("Shutting down Server ...")
    except Exception as e:
        print(f"Server Error: {e}")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
