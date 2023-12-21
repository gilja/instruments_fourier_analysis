import os

# Define the list of variables and functions to be imported
__all__ = [
    "PATH_BASE",
    "PATH_DATA",
    "PATH_RESULTS",
    "PATH_INSTRUMENT_SAMPLES",
]

# Path constants
PATH_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH_DATA = PATH_BASE + "/data/"
PATH_RESULTS = PATH_BASE + "/results/analysed/"
PATH_INSTRUMENT_SAMPLES = PATH_DATA + "instrument_samples/"

# Set figure size for all plots
FIGURE_WIDTH = 1600  # width for the whole figure
FIGURE_HEIGHT_PER_PLOT = 400  # height for each individual plot

# Set horizontal and vertical spacing between subplots
HSPACING = 0.08
VSPACING = 0.2
