import numpy as np
from numba import njit
import spectral
import warnings
from pathlib import Path

numba_cache_flag = True

DEFAULT_DB_PATH = Path(__file__).resolve(
).parent.parent / "data" / "usgs_splib07a.db"


@njit(cache=numba_cache_flag)
def left_turn_for_convex_hull(x1, y1, x2, y2, x3, y3):
    slope1 = (y2 - y1) / (x2 - x1)
    slope2 = (y3 - y2) / (x3 - x2)
    left_turn_flag = slope2 > slope1
    return left_turn_flag


@njit(cache=numba_cache_flag)
def upper_convex_hull(x, y):
    n = x.size

    if n != y.size:
        raise ValueError("x and y lenghts must be same")

    if n <= 2:
        raise ValueError("x and y lenghts must be grater than 2")

    hullx = np.full((n,), np.nan)
    hully = np.full((n,), np.nan)

    hullx[0], hully[0] = x[0], y[0]
    hullx[1], hully[1] = x[1], y[1]

    nh = 2

    for i in range(2, n):
        while nh >= 2 and left_turn_for_convex_hull(
            hullx[nh - 2],
            hully[nh - 2],
            hullx[nh - 1],
            hully[nh - 1],
            x[i],
            y[i],
        ):
            nh -= 1

        hullx[nh] = x[i]
        hully[nh] = y[i]
        nh += 1

    return hullx[:nh], hully[:nh]


@njit(cache=numba_cache_flag)
def lower_convex_hull(x, y):
    n = x.size

    if n != y.size:
        raise ValueError("x and y lenghts must be same")

    if n <= 2:
        raise ValueError("x and y lenghts must be grater than 2")

    hullx = np.full((n,), np.nan)
    hully = np.full((n,), np.nan)

    hullx[0], hully[0] = x[0], y[0]
    hullx[1], hully[1] = x[1], y[1]

    nh = 2

    for i in range(2, n):
        while nh >= 2 and not left_turn_for_convex_hull(
            hullx[nh - 2],
            hully[nh - 2],
            hullx[nh - 1],
            hully[nh - 1],
            x[i],
            y[i],
        ):
            nh -= 1

        hullx[nh] = x[i]
        hully[nh] = y[i]
        nh += 1

    return hullx[:nh], hully[:nh]


@njit(cache=numba_cache_flag)
def continuum_removal(
    x,
    y,
    continuum_type,
    left_outer_x,
    left_inner_x,
    right_inner_x,
    right_outer_x,
):
    if continuum_type == "uh":
        x_min, x_max = left_inner_x, right_inner_x

        flag = (x_min <= x) * (x <= x_max)

        x = x[flag]
        y = y[flag]

        hullx, hully = upper_convex_hull(x, y)

        c = np.interp(x, hullx, hully)

        Cy = y / c

    else:
        raise ValueError(
            """Only upper convex hull supported with inner x
        values"""
        )

    return x, Cy, c


def get_usgs_splib07a_spectrum(
    search_str="",
    SampleID=None,
    library_path=DEFAULT_DB_PATH,
):
    if (len(search_str) == 0) and (SampleID is None):
        raise ValueError("Wrong arguments for getting library spectrum")

    db = spectral.USGSDatabase(str(library_path))

    if SampleID is None:
        sql_str = """SELECT LibName, SampleID, Description, Spectrometer
                     FROM Samples WHERE Description LIKE ?"""

        query = db.query(sql_str, args=(f"%{search_str}%",))

        first_result = list(query)[0]

        lib_name = first_result[0]
        SampleID = first_result[1]
        Description = first_result[2]
        Spectrometer = first_result[3]

    else:
        SampleID = int(SampleID) if type(SampleID) is not int else SampleID

        sql_str = """SELECT LibName, SampleID, Description, Spectrometer
                     FROM Samples WHERE SampleID = ?"""

        query = db.query(sql_str, args=(SampleID,))

        first_result = list(query)[0]

        lib_name = first_result[0]
        Description = first_result[2]
        Spectrometer = first_result[3]

    x, y = db.get_spectrum(SampleID)

    x = np.array(x)
    y = np.array(y)

    flag = y > 0
    x, y = x[flag], y[flag]

    sql_str = """SELECT ValuesArray FROM SpectrometerData
                 WHERE MeasurementType = "Bandpass" AND Name = ?"""

    query = db.query(sql_str, (Spectrometer,))

    rows = query.fetchall()

    if len(rows) > 0:
        fwhm = spectral.database.usgs.array_from_blob(rows[0][0])
        fwhm = np.array(fwhm)
        fwhm = fwhm[flag]

    else:
        warnings.warn(f"Bandpass not found for {Description} in {lib_name}")
        fwhm = np.full(x.size, np.nan)

    return x, y, fwhm, Description, SampleID, lib_name
