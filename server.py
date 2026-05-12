"""
Multi-client TCP chat server.
Run:  python server.py
Listens on 0.0.0.0:5555 by default.
"""
import socket
import threading

HOST = "0.0.0.0"
PORT = 5555

clients = {}          # socket -> username
clients_lock = threading.Lock()


def broadcast(message: str, exclude: socket.socket | None = None) -> None:
    """Send a message to every connected client (optionally skipping one)."""
    data = message.encode("utf-8")
    dead = []
    with clients_lock:
        for sock in clients:
            if sock is exclude:
                continue
            try:
                sock.sendall(data)
            except OSError:
                dead.append(sock)
        for sock in dead:
            clients.pop(sock, None)


def send_userlist() -> None:
    with clients_lock:
        names = ",".join(clients.values())
    broadcast(f"USERLIST:{names}\n")


def handle_client(sock: socket.socket, addr) -> None:
    username = None
    try:
        # First message from client must be the username
        username = sock.recv(1024).decode("utf-8").strip()
        if not username:
            sock.close()
            return

        with clients_lock:
            clients[sock] = username

        print(f"[+] {username} connected from {addr}")
        broadcast(f"*** {username} joined the chat ***\n", exclude=sock)
        send_userlist()

        buffer = ""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buffer += chunk.decode("utf-8", errors="replace")
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                broadcast(f"{username}: {line}\n")
    except OSError:
        pass
    finally:
        with clients_lock:
            clients.pop(sock, None)
        try:
            sock.close()
        except OSError:
            pass
        if username:
            print(f"[-] {username} disconnected")
            broadcast(f"*** {username} left the chat ***\n")
            send_userlist()


def main() -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Chat server listening on {HOST}:{PORT}")

    try:
        while True:
            sock, addr = server.accept()
            threading.Thread(
                target=handle_client, args=(sock, addr), daemon=True
            ).start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server.close()


if __name__ == "__main__":
    main()
