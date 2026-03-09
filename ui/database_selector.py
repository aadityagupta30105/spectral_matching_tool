import tkinter as tk
from tkinter import filedialog, ttk


class DatabaseSelector:

    def __init__(self, root):
        self.root = root
        self.db_path = None

        self.root.title("Select Spectral Database")
        self.root.geometry("500x150")

        frame = ttk.Frame(root, padding=20)
        frame.pack(fill="both", expand=True)

        self.path_var = tk.StringVar()

        entry = ttk.Entry(frame, textvariable=self.path_var, width=50)
        entry.pack(pady=10)

        browse_btn = ttk.Button(frame, text="Browse", command=self.browse_db)
        browse_btn.pack()

        load_btn = ttk.Button(
            frame,
            text="Load Database",
            command=self.load_db)
        load_btn.pack(pady=10)

    def browse_db(self):
        path = filedialog.askopenfilename(
            filetypes=[("SQLite Database", "*.db")]
        )
        if path:
            self.path_var.set(path)

    def load_db(self):
        self.db_path = self.path_var.get()
        self.root.destroy()
