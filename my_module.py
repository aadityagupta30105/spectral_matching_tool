#!/usr/bin/env python
# author: Vikram KVNG
# email: kvngvikram@gmail.com
import numpy as np
from numba import njit
import spectral
import warnings

numba_cache_flag = True


@njit(cache=numba_cache_flag)
def left_turn_for_convex_hull(x1, y1, x2, y2, x3, y3):
    """Function for us in convex hull calculations. For given two points
    (x1, y1), (x2, y2) is the third point (x3, y3) turning left ?
    Parameters
    ----------
    x1 : float
    y1 : float
    x2 : float
    y2 : float
    x3 : float
    y3 : float
    Returns
    -------
    left_turn_flag : bool
    """
    slope1 = (y2 - y1)/(x2 - x1)
    slope2 = (y3 - y2)/(x3 - x2)
    left_turn_flag = slope2 > slope1
    return left_turn_flag


@njit(cache=numba_cache_flag)
def upper_convex_hull(x, y):
    """Function to return points for upper convex hull
    Parameters
    ----------
    x : numpy.ndarray
        sorted x points of the data
    y : numpy.ndarray
        corresponding y points of the data with same size as x
    Returns
    -------
    hullx : numpy.ndarray
        x values of the hull
    hully : numpy.ndarray
        y values of the hull
    """
    n = x.size
    if n != y.size:
        raise ValueError('x and y lenghts must be same')
    if n <= 2:
        raise ValueError('x and y lenghts must be grater than 2')
    hullx = np.full((n,), np.nan)  # appending when requred is not efficient !
    hully = np.full((n,), np.nan)
    hullx[0], hully[0] = x[0], y[0]
    hullx[1], hully[1] = x[1], y[1]
    # hullx = np.array([x[0], x[1]])  # alternatively
    # hully = np.array([y[0], y[1]])
    nh = 2  # hull size
    for i in range(2, n):
        while nh >= 2 and left_turn_for_convex_hull(
                                    hullx[nh-2], hully[nh-2],  # last but one
                                    hullx[nh-1], hully[nh-1],  # last point
                                    x[i], y[i]):               # upcoming point
            nh -= 1  # delete the last hull point by effectively reducing size
            # hullx = np.delete(hullx, -1)  # alternatively
            # hully = np.delete(hully, -1)
        hullx[nh] = x[i]
        hully[nh] = y[i]
        nh += 1
        # hullx = np.append(hullx, x[i])  # alternatively
        # hully = np.append(hully, y[i])
    return hullx[:nh], hully[:nh]


@njit(cache=numba_cache_flag)
def lower_convex_hull(x, y):
    """Function to return points for lower convex hull
    Parameters
    ----------
    x : numpy.ndarray
        sorted x points of the data
    y : numpy.ndarray
        corresponding y points of the data with same size as x
    Returns
    -------
    hullx : numpy.ndarray
        x values of the hull
    hully : numpy.ndarray
        y values of the hull
    """
    n = x.size
    if n != y.size:
        raise ValueError('x and y lenghts must be same')
    if n <= 2:
        raise ValueError('x and y lenghts must be grater than 2')
    hullx = np.full((n,), np.nan)  # appending when requred is not efficient !
    hully = np.full((n,), np.nan)
    hullx[0], hully[0] = x[0], y[0]
    hullx[1], hully[1] = x[1], y[1]
    nh = 2  # hull size
    for i in range(2, n):
        while nh >= 2 and not left_turn_for_convex_hull(
                                    hullx[nh-2], hully[nh-2],  # last but one
                                    hullx[nh-1], hully[nh-1],  # last point
                                    x[i], y[i]):               # upcoming point
            nh -= 1  # delete the last hull point by effectively reducing size
        hullx[nh] = x[i]
        hully[nh] = y[i]
        nh += 1
    return hullx[:nh], hully[:nh]


@njit(cache=numba_cache_flag)
def continuum_removal(x, y,
                      continuum_type,
                      left_outer_x, left_inner_x,
                      right_inner_x, right_outer_x):
    """Meta function to apply continuum removal based on the type.
    For now supporteing only upper_convex_hull as 'uh' type
    Later, function structure can be changed
    Parameters
    ----------
    x : numpy.ndarray
    y : numpy.ndarray
    continuum_type : str
        Type code for different types of continuum
    left_outer_x : float
    left_inner_x : float
    right_inner_x : float
    right_outer_x : float
    Returns
    -------
    x : numpy.ndarray
        wavelength values of the spectrum
    y : numpy.ndarray
        continuum removed y values of the spectrum
    c : numpy.ndarray
        continuum values
    """
    if continuum_type == 'uh':
        x_min, x_max = left_inner_x, right_inner_x
        flag = (x_min <= x) * (x <= x_max)
        x = x[flag]
        y = y[flag]
        hullx, hully = upper_convex_hull(x, y)
        c = np.interp(x, hullx, hully)
        Cy = y/c
    else:
        raise ValueError('''Only upper convex hull supported with inner x
        values''')
    return x, Cy, c


def get_usgs_splib07a_spectrum(
        search_str='',
        SampleID=None,
        library_path='../data/usgs_splib07a_spectral_python.db',
        ):
    """Function to fetch data from any spectral library in its original form
    for now supporteing only usgs_splib07a stored as sql database by
    spectral python.
    Either one of search_str, or SampleID should be given.
    Parameters
    ----------
    search_str : str
        string used for SQL query of usgs_splib07a 'Description' (name).
    SampleID : int
        ID for SQL query of usgs_splib07a
    Returns
    -------
    x : numpy.ndarray
        wavelength values of the spectrum
    y : numpy.ndarray
        y values of the spectrum
    Description : str
        Description of the entry in the library
    lib_name : str
        Name of library according to spectral library
    """
    if (len(search_str) == 0) and (SampleID is None):
        raise ValueError('Wrong arguments for getting library spectrum')
    db = spectral.USGSDatabase(library_path)
    if SampleID is None:
        sql_str = '''SELECT LibName, SampleID, Description, Spectrometer
                     FROM Samples WHERE Description LIKE ?'''
        query = db.query(sql_str, args=(f'%{search_str}%',))
        # list(query)
        first_result = list(query)[0]
        lib_name = first_result[0]
        SampleID = first_result[1]
        Description = first_result[2]
        Spectrometer = first_result[3]
    else:
        # Sometimes one can pass numpy.int64() type of singel integer value
        SampleID = int(SampleID) if type(SampleID) is not int else SampleID
        sql_str = '''SELECT LibName, SampleID, Description, Spectrometer
                     FROM Samples WHERE SampleID = ?'''
        query = db.query(sql_str, args=(SampleID,))
        # list(query)
        first_result = list(query)[0]  # the list size here is one anyway
        lib_name = first_result[0]
        Description = first_result[2]
        Spectrometer = first_result[3]
    x, y = db.get_spectrum(SampleID)
    x = np.array(x)
    y = np.array(y)
    flag = y > 0
    x, y = x[flag], y[flag]
    sql_str = '''SELECT ValuesArray FROM SpectrometerData
                 WHERE MeasurementType = "Bandpass" AND Name = ?'''
    query = db.query(sql_str, (Spectrometer,))
    # query = db.cursor.execute(sql_str, (Spectrometer,))
    rows = query.fetchall()
    if len(rows) > 0:
        fwhm = spectral.database.usgs.array_from_blob(rows[0][0])
        fwhm = np.array(fwhm)
        fwhm = fwhm[flag]
    else:
        warnings.warn(f'Bandpass not found for {Description} in {lib_name}')
        fwhm = np.full(x.size, np.nan)
    # return SampleID, Description, x, y, fwhm
    return x, y, fwhm, Description, SampleID, lib_name
