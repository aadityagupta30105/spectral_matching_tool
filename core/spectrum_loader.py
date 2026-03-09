from functools import lru_cache
from core.config import DB_PATH
from core import my_module


@lru_cache(maxsize=128)
def load_spectrum(sample_id):
    x, y, fwhm, description, sample_id, lib_name = \
        my_module.get_usgs_splib07a_spectrum(
            SampleID=int(sample_id),
            library_path=str(DB_PATH)
        )

    return x, y
