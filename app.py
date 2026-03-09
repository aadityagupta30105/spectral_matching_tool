import tkinter as tk
from ui.database_selector import DatabaseSelector
from ui.main_window import MainWindow


def main():
    selector_root = tk.Tk()
    selector = DatabaseSelector(selector_root)
    selector_root.mainloop()

    if not selector.db_path:
        return

    root = tk.Tk()
    MainWindow(root, selector.db_path)
    root.mainloop()


if __name__ == "__main__":
    main()
