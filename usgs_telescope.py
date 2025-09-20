import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QListWidget, QSizePolicy, QCheckBox
)
from PySide6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from rapidfuzz import process
import numpy as np
import spectral
import sys
import my_module

class SpectralExplorerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spectral Database Explorer")
        self.resize(1200,800)
        
        # Initialize database variables
        self.db = None
        self.entries = []
        self.sample_ids = {}
        self.continuum_removal_flag = False  # Flag for continuum removal
        self.current_spectrum_name = None  # Track current spectrum
        self.current_x = None  # Store current x data
        self.current_y = None  # Store current y data

        # Setup the UI
        self._init_ui()
        # Load the database
        self._load_database()

    def _init_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel for search and results
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(400)
        
        # Database info label
        self.db_info_label = QLabel("Loading database...")
        left_layout.addWidget(self.db_info_label)
        
        # Search label and input
        search_label = QLabel("Search Spectral Library:")
        left_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search...")
        self.search_input.textChanged.connect(self._update_search_results)
        left_layout.addWidget(self.search_input)
        
        # Results info label
        self.results_info_label = QLabel("Matching entries: 0")
        left_layout.addWidget(self.results_info_label)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.itemSelectionChanged.connect(self._on_selection_changed)
        left_layout.addWidget(self.results_list)
        
        # Continuum removal checkbox
        self.continuum_checkbox = QCheckBox("Apply Continuum Removal")
        self.continuum_checkbox.stateChanged.connect(self._on_continuum_toggle)
        left_layout.addWidget(self.continuum_checkbox)
        
        # Add left panel to main layout
        main_layout.addWidget(left_panel)
        
        # Right panel for plotting
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Matplotlib figure
        self.fig = plt.Figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(self.canvas)
        
        # Add right panel to main layout
        main_layout.addWidget(right_panel)

    def _load_database(self):
        """Load the spectral database and populate entries"""
        try:
            # Update with your actual database path
            library_path = 'data//usgs_spectral_python.db'
            sql_str = 'SELECT LibName, SampleID, Description, Spectrometer FROM Samples'
            
            self.db = spectral.USGSDatabase(library_path)
            query_results = self.db.query(sql_str)
            
            # Create entries list and sample ID mapping
            self.entries = []
            for lib_name, sample_id, description, spectrometer in query_results:
                entry_text = f"{description} {lib_name} {sample_id}"
                self.entries.append(entry_text)
                self.sample_ids[entry_text] = sample_id
            
            # Sort entries alphabetically
            self.entries.sort()
            
            # Update database info label
            self.db_info_label.setText(f"Database loaded: {len(self.entries)} entries")
            
            # Populate the list with all entries initially
            self._update_search_results("")
            
        except Exception as e:
            error_msg = f"Error loading database: {e}"
            print(error_msg)
            self.db_info_label.setText(error_msg)

    def _on_continuum_toggle(self, state):
        """Handle continuum removal checkbox state change"""
        # FIX: Use the checkbox's isChecked() method instead of comparing state
        self.continuum_removal_flag = self.continuum_checkbox.isChecked()
        
        # Replot the current selection if there is one
        if self.current_spectrum_name and self.current_x is not None and self.current_y is not None:
            self._plot_spectrum(self.current_spectrum_name, self.current_x, self.current_y)

    def _update_search_results(self, search_text):
        """Update the results list based on search text"""
        self.results_list.clear()
        
        if search_text.strip():
            # Use fuzzy search if there's a query
            matches = process.extract(search_text, self.entries, limit=50)
            for match, score, idx in matches:
                self.results_list.addItem(match)
            
            # Update results count
            self.results_info_label.setText(f"Matching entries: {len(matches)}/{len(self.entries)}")
        else:
            # Show all entries when search is empty
            for entry in self.entries:
                self.results_list.addItem(entry)
            
            # Update results count
            self.results_info_label.setText(f"All entries: {len(self.entries)}")

    def _on_selection_changed(self):
        """Handle selection changes in the results list"""
        selected_items = self.results_list.selectedItems()
        if not selected_items:
            return
            
        selected_item = selected_items[0].text()
        self.current_spectrum_name = selected_item
        self._load_and_plot_spectrum(selected_item)

    def _load_and_plot_spectrum(self, entry_name):
        """Load spectrum data and plot it"""
        if entry_name not in self.sample_ids:
            return
            
        sample_id = self.sample_ids[entry_name]
        
        try:
            # Get spectrum data
            x, y = self.db.get_spectrum(sample_id)
            x, y = np.asarray(x), np.asarray(y)
            
            # Filter out negative values
            flag = y >= 0
            x, y = x[flag], y[flag]
            
            # Store the original data for re-plotting
            self.current_x = x
            self.current_y = y
            
            # Plot the spectrum
            self._plot_spectrum(entry_name, x, y)
            
        except Exception as e:
            print(f"Error loading spectrum: {e}")

    def _plot_spectrum(self, entry_name, x, y):
        """Plot the spectrum with optional continuum removal"""
        try:
            # Apply continuum removal if enabled
            plot_x, plot_y = x, y
            if self.continuum_removal_flag:
                plot_x, plot_y, _ = my_module.continuum_removal(x, y, 'uh', 
                                           -np.inf, -np.inf, np.inf, np.inf)
            
            # Clear previous plot and create new one
            self.ax.clear()
            self.ax.plot(plot_x, plot_y)
            
            # Format the plot
            ylabel = "Continuum Removed Reflectance" if self.continuum_removal_flag else "Reflectance"
            self.ax.set_xlabel("Wavelength (Micrometers)")
            self.ax.set_ylabel(ylabel, fontsize=12)
            self.ax.set_title(f"Spectrum: {entry_name}")
            self.ax.grid(True)
            
            # Set x-axis ticks and limits
            self.ax.set_xticks(np.arange(0, plot_x.max(), 0.1))
            self.ax.set_xlim([plot_x.min(), plot_x.max()])
            
            # Force complete redraw of the canvas
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error plotting spectrum: {e}")


def main():
    app = QApplication(sys.argv)
    window = SpectralExplorerApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()