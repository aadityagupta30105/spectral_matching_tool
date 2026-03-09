import numpy as np
from core import my_module


def apply_continuum(x, y):
    x_new, y_new, continuum = my_module.continuum_removal(
        x,
        y,
        'uh',
        -np.inf,
        -np.inf,
        np.inf,
        np.inf
    )

    return x_new, y_new
