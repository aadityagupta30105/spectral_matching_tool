import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import spectral
from core.config import DB_PATH


class DatabaseCreator:

    def __init__(self, root):
        self.root = root
        self.root.title("Create Spectral Database")
        self.root.geometry("500x200")

        self.ascii_path = tk.StringVar()

        frame = ttk.Frame(root, padding=20)
        frame.pack(fill="both", expand=True)

        label = ttk.Label(
            frame,
            text="Select the USGS ASCII Spectral Library Folder"
        )
        label.pack(pady=10)

        entry = ttk.Entry(frame, textvariable=self.ascii_path, width=50)
        entry.pack(pady=5)

        browse_btn = ttk.Button(frame, text="Browse", command=self.browse)
        browse_btn.pack(pady=5)

        create_btn = ttk.Button(
            frame,
            text="Create Database",
            command=self.create_database
        )
        create_btn.pack(pady=10)

    def browse(self):
        path = filedialog.askdirectory()
        if path:
            self.ascii_path.set(path)

    def create_database(self):

        ascii_dir = Path(self.ascii_path.get())

        if not ascii_dir.exists():
            messagebox.showerror("Error", "Invalid directory selected")
            return

        db_path = Path("data/usgs_splib07a.db")

        db_path.parent.mkdir(exist_ok=True)

        try:
            spectral.USGSDatabase.create(
                str(db_path),
                usgs_data_dir=str(ascii_dir)
            )

            messagebox.showinfo(
                "Success",
                f"Database created at:\n{db_path}"
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_all_minerals(self):
        sql = """
        SELECT LibName, SampleID, Description
        FROM Samples
        WHERE Chapter LIKE '%ChapterM_Minerals%'
        """
        return list(self.db.query(sql))

    def search(self, keyword):
        sql = """
        SELECT LibName, SampleID, Description
        FROM Samples
        WHERE Description LIKE ?
        """
        return list(self.db.query(sql, (f"%{keyword}%",)))


def main():
    root = tk.Tk()
    DatabaseCreator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
