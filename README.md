# Advanced-Chat-Client-Application
Advanced Chat Client is a real-time multi-user chat application built with Python, Tkinter, Socket Programming, and Threading. It features instant messaging, a GUI-based interface, live user lists, and timestamped messages for smooth real-time communication.


# Python Socket Chat (Tkinter GUI)

A minimal multi-user chat app using **Python sockets** + **Tkinter**.

## Files
- `server.py` — multi-threaded TCP chat server
- `client.py` — Tkinter GUI chat client

## Requirements
- Python 3.10+ (uses `X | None` type hints)
- No external packages — everything is standard library

## Run

### 1. Start the server
```bash
python server.py
```
Server listens on `0.0.0.0:5555`.

### 2. Start one or more clients
```bash
python client.py
```
You'll be prompted for a username. Open multiple clients to chat between them.

## Connecting from another machine
In `client.py`, change:
```python
SERVER_HOST = "127.0.0.1"
```
to the server machine's LAN IP (e.g. `"192.168.1.42"`).
Make sure port `5555` is open in the server's firewall.

## Protocol
Plain text, newline-delimited UTF-8.

- First message from client: `username\n`
- Chat messages: `text\n` (server prefixes with `username:`)
- Server broadcasts user list as: `USERLIST:alice,bob,carol\n`

## Possible extensions
- Private/direct messages (`/msg user hello`)
- TLS encryption via `ssl.wrap_socket`
- File transfer
- Persistent message history
- Authentication
