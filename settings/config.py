import os

# Define the list of variables and functions to be imported
__all__ = [
    "PATH_BASE",
    "PATH_DATA",
    "PATH_RESULTS",
    "PATH_INSTRUMENT_SAMPLES",
]

# path constants
PATH_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH_DATA = PATH_BASE + "/data/"
PATH_RESULTS = PATH_BASE + "/results/"
PATH_INSTRUMENT_SAMPLES = PATH_DATA + "/instrument_samples/"
