"""
Tkinter chat client.
Run:  python client.py
Make sure server.py is running first (locally or on a reachable host).
"""
import socket
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

SERVER_HOST = "127.0.0.1"   # change to your server's IP if remote
SERVER_PORT = 5555


class ChatClient:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Python Socket Chat")
        self.root.geometry("720x500")
        self.root.configure(bg="#1e1e2e")

        self.client_socket: socket.socket | None = None
        self.username: str | None = None
        self.running = False

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        # Defer login until window is shown
        self.root.after(100, self.login)

    # ---------- UI ----------
    def _build_ui(self) -> None:
        # Chat area (left)
        chat_frame = tk.Frame(self.root, bg="#1e1e2e")
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.chat_area = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, state="disabled",
            bg="#11111b", fg="#cdd6f4", insertbackground="#cdd6f4",
            font=("Consolas", 11), borderwidth=0, relief=tk.FLAT,
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)

        # Message input
        message_frame = tk.Frame(chat_frame, bg="#1e1e2e")
        message_frame.pack(fill=tk.X, pady=(8, 0))

        self.message_entry = tk.Entry(
            message_frame, bg="#313244", fg="#cdd6f4",
            insertbackground="#cdd6f4", font=("Segoe UI", 11),
            relief=tk.FLAT,
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        self.message_entry.bind("<Return>", lambda _e: self.send_message())

        self.send_button = tk.Button(
            message_frame, text="Send", command=self.send_message,
            bg="#89b4fa", fg="#1e1e2e", activebackground="#74c7ec",
            font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=16,
        )
        self.send_button.pack(side=tk.RIGHT, padx=(8, 0))

        # User list (right)
        user_frame = tk.Frame(self.root, bg="#1e1e2e")
        user_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 8), pady=8)

        tk.Label(
            user_frame, text="Online", bg="#1e1e2e", fg="#a6adc8",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")

        self.user_listbox = tk.Listbox(
            user_frame, width=20, bg="#11111b", fg="#cdd6f4",
            font=("Segoe UI", 10), borderwidth=0, relief=tk.FLAT,
            selectbackground="#45475a",
        )
        self.user_listbox.pack(fill=tk.Y, expand=True, pady=(4, 0))

    # ---------- Networking ----------
    def login(self) -> None:
        name = simpledialog.askstring("Login", "Enter your username:", parent=self.root)
        if not name:
            self.root.destroy()
            return
        self.username = name.strip()
        self.connect_to_server()

    def connect_to_server(self) -> None:
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVER_HOST, SERVER_PORT))
            self.client_socket.sendall(f"{self.username}\n".encode("utf-8"))
        except OSError as e:
            messagebox.showerror("Connection failed", f"Could not connect to server:\n{e}")
            self.root.destroy()
            return

        self.running = True
        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.append_chat(f"Connected as {self.username}\n")

    def send_message(self) -> None:
        if not self.client_socket:
            return
        msg = self.message_entry.get().strip()
        if not msg:
            return
        timestamp = time.strftime("%H:%M")
        try:
            self.client_socket.sendall(f"[{timestamp}] {msg}\n".encode("utf-8"))
        except OSError as e:
            self.append_chat(f"[error] {e}\n")
            return
        self.message_entry.delete(0, tk.END)

    def receive_messages(self) -> None:
        assert self.client_socket is not None
        buffer = ""
        while self.running:
            try:
                chunk = self.client_socket.recv(4096)
            except OSError:
                break
            if not chunk:
                break
            buffer += chunk.decode("utf-8", errors="replace")
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line:
                    continue
                if line.startswith("USERLIST:"):
                    users = line[len("USERLIST:"):].split(",") if line[len("USERLIST:"):] else []
                    self.root.after(0, self.update_user_list, users)
                else:
                    self.root.after(0, self.append_chat, line + "\n")

        self.root.after(0, self.append_chat, "*** Disconnected from server ***\n")

    # ---------- Helpers ----------
    def append_chat(self, text: str) -> None:
        self.chat_area.configure(state="normal")
        self.chat_area.insert(tk.END, text)
        self.chat_area.configure(state="disabled")
        self.chat_area.see(tk.END)

    def update_user_list(self, users) -> None:
        self.user_listbox.delete(0, tk.END)
        for u in users:
            u = u.strip()
            if u:
                self.user_listbox.insert(tk.END, u)

    def on_close(self) -> None:
        self.running = False
        try:
            if self.client_socket:
                self.client_socket.close()
        except OSError:
            pass
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    ChatClient(root)
    root.mainloop()


if __name__ == "__main__":
    main()
