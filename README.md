# Spectral Library Explorer

A Python application for exploring and visualizing spectra from the **USGS Spectral Library**.

---

# Features

- Browse minerals from the USGS spectral library
- Interactive spectral plotting
- Continuum removal using convex hull method
- Search functionality for minerals
- Zoom and pan functionality using Matplotlib tools
- Dynamic database loading at startup

---

# Installation

Clone the repository: 

```bash
git clone https://github.com/aadityagupta30105/spectral_matching_tool.git
```

Navigate to the project directory:

```bash
cd spectral_matching_tool
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Creating the Database

If the database does not exist, it can be generated from the USGS ASCII spectral library data using:

```bash
python database_creator.py
```

This script converts the ASCII spectral library into a SQLite database used by the application. A window will appear where you must select the USGS ASCII spectral library folder (typically named ASCIIdata, in this case specifically splib07a in the ASCII folder).

The script will generate the database:

```text
data/usgs_splib07a.db
```

---

# Running the Application

Run the application using:

```bash
python app.py
```

When the application starts, you will be prompted to select the **spectral database file (.db)**.

---

# Project Structure

```text
spectral_matching_tool/
│
├── app.py
├── database_creator.py
├── requirements.txt
├── README.md
│
├── core/
│ ├── config.py
│ ├── continuum.py
│ ├── database.py
│ ├── my_module.py
│ └── spectrum_loader.py
│
├── ui/
│ ├── database_selector.py
│ └── main_window.py
│
└── data/
  └── usgs_splib07a.db
```

---

# Core Modules

### `core/database.py`
Handles interaction with the spectral database.

### `core/spectrum_loader.py`
Loads spectral data for selected samples.

### `core/continuum.py`
Applies continuum removal using the convex hull method.

### `core/my_module.py`
Contains the main spectral processing functions including:
- Convex hull calculations
- Continuum removal
- Database spectrum retrieval

---

# UI Modules

### `ui/database_selector.py`
Startup window allowing users to select the spectral database.

### `ui/main_window.py`
Main interface containing:
- mineral list
- search functionality
- spectral plotting interface

---

# Dependencies

The main dependencies are:

- numpy
- matplotlib
- spectral
- numba
- rapidfuzz

Install them using:

```bash
pip install -r requirements.txt
```