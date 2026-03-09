import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

from core.database import SpectralDatabase
from core.spectrum_loader import load_spectrum
from core.continuum import apply_continuum


class MainWindow:

    def __init__(self, root, db_path):
        self.root = root
        self.root.title("Spectral Library Explorer")
        self.root.geometry("1400x800")

        self.db = SpectralDatabase(db_path)

        self.continuum_on = False
        self.current_sample_id = None

        self._build_ui()
        self._load_minerals()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # Left panel
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="y")
        left_frame.config(width=450)
        left_frame.pack_propagate(False)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._update_search)

        search_entry = ttk.Entry(left_frame, textvariable=self.search_var)
        search_entry.pack(fill="x", padx=10, pady=10)

        self.listbox = tk.Listbox(left_frame)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        self.continuum_var = tk.BooleanVar()

        continuum_cb = ttk.Checkbutton(
            left_frame,
            text="Continuum Removal",
            variable=self.continuum_var,
            command=self._toggle_continuum
        )

        continuum_cb.pack(pady=10)

        # Right panel
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        self.fig, self.ax = plt.subplots()

        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, right_frame)
        toolbar.update()

    def _load_minerals(self):
        self.entries = self.db.get_all_minerals()
        self.filtered = self.entries
        self._refresh_listbox()

    def _refresh_listbox(self):
        self.listbox.delete(0, tk.END)

        for lib, sid, desc in self.filtered:
            self.listbox.insert(tk.END, f"{desc} ({sid})")

    def _update_search(self, *args):
        keyword = self.search_var.get().strip()

        if keyword:
            self.filtered = self.db.search(keyword)
        else:
            self.filtered = self.entries

        self._refresh_listbox()

    def _plot_spectrum(self, sample_id):

        x, y = load_spectrum(sample_id)

        if self.continuum_on:
            x, y = apply_continuum(x, y)

        self.ax.clear()

        self.ax.plot(x, y, linewidth=1.5)

        self.ax.set_xlabel("Wavelength (µm)")
        self.ax.set_ylabel("Reflectance")

        self.ax.relim()
        self.ax.autoscale_view()

        self.canvas.draw()

    def _on_select(self, event):

        selection = self.listbox.curselection()

        if not selection:
            return

        index = selection[0]
        lib, sample_id, desc = self.filtered[index]

        self.current_sample_id = sample_id

        self._plot_spectrum(sample_id)

    def _toggle_continuum(self):

        self.continuum_on = self.continuum_var.get()

        if self.current_sample_id is not None:
            self._plot_spectrum(self.current_sample_id)
