"""
period_bounds.py

This configuration file provides the period bounds for each instrument used
in the Fourier analysis. The bounds were obtained manually
by plotting the Fourier transform of each audio file and identifying the
periods visually.
"""


PERIOD_BOUNDS = {
    "cello": [0.8284, 0.83604],
    "clarinet": [2.09145, 2.09334],
    "double_bass": [0.63845, 0.64609],
    "female_vocal": [0.65874, 0.66064],
    "flute": [0.78051, 0.78146],
    "guitar_nylon": [0.441767, 0.44559],
    "oboe": [0.54717, 0.55097],
    "piano": [0.75141, 0.75521],
    "piccolo": [0.69282, 0.69377],
    "sax_alto": [1.2636, 1.2655],
    "sax_baritone": [2.1363, 2.1515],
    "sax_soprano": [1.51283, 1.51472],
    "sax_tenor": [1.08718, 1.09096],
    "guitar_metal": [0.59473, 0.59853],
    "trombone": [0.5417, 0.5455],
    "trumpet": [1.12869, 1.130605],
    "violin": [1.28755, 1.28945],
}
