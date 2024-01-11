"""
fourier_math_utils
==================

This module contains utility functions needed for doing the math behind Fourier analysis.
It allows a user to extract 1-period-long audio signals from original audio files, calculate
the Fourier series coefficients for the extracted signals, reconstruct the original signals
from the Fourier coefficients, write a mathematical function representing the reconstructed
signal, and calculate the relative power spectrum of harmonic components in the signal.

Public functions:
-----------------

-   extract_periods_and_data_rates: Extracts 1-period-long audio signals and their corresponding
    data rates.
-   calculate_fourier_coefficients: Calculates the Fourier series coefficients for a given
    periodic signal represented as a discrete set of data points (amplitudes).
-   calculate_harmonic_power_spectrum: Calculates the relative power spectrum of harmonic
    components in a signal.
-   reconstruct_original_signal: Reconstructs the original signal from its Fourier coefficients.
-   get_mathematical_representation_of_signal: Generates the mathematical representation of
    the signal.

For more information on the functions, refer to their docstrings.

Notes:
------

Author: Duje Giljanović (giljanovic.duje@gmail.com)
License: MIT License

If you use PyToneAnalyzer in your research or any other publication, please acknowledge it by
citing as follows:

@software{PyToneAnalyzer,
    title = {PyToneAnalyzer: Fourier Analysis of Musical Instruments},
    author = {Duje Giljanović},
    year = {2024},
    url = {github.com/gilja/instruments_fourier_analysis},
}
"""

import numpy as np
from .config_manager import ConfigManager


def extract_periods_and_data_rates(sounds):
    """
    Extracts 1-period-long audio signals and their corresponding data rates.

    The function extracts 1-period-long audio signals and their corresponding data rates
    from a list of sound data and period bounds. It uses the provided sounds and period
    bounds (defined in the config file) to calculate the one-period audio signals.

    Args:
        sounds (list of tuple):
            -   Each tuple contains sound data and its associated sample rate.

    Returns:
        tuple:
            -   A tuple containing two lists:
                *   List of numpy arrays, each representing a 1-period-long audio signal.
                *   List of integers, each representing the data rate of the corresponding
                    1-period-long audio signal.
    """

    periods, data_rates = [], []
    cfg = ConfigManager.get_instance().config

    for (data, data_rate), (period_start, period_end) in zip(
        sounds, cfg.PERIOD_BOUNDS.values()
    ):
        sample_start = int(period_start * data_rate)
        sample_end = int(period_end * data_rate)

        period = data[sample_start:sample_end]
        periods.append(period)
        data_rates.append(data_rate)

    return periods, data_rates


def calculate_fourier_coefficients(one_period_signal, n_harmonics):
    """
    Calculates the Fourier series coefficients for a given periodic signal represented
    as a discrete set of data points (amplitudes).

    The Fourier series of a periodic function f(t) with period T is given by

    f(t) = a0 + ∑(an * cos(2 * pi * n * t / T) + bn * sin(2 * pi * n * t / T)),

    where a0 is the average value of f(t) over one period, and an and bn are the coefficients
    for the cosine and sine terms, respectively. The coefficients an and bn are calculated
    using the following formulas:

    an = (2/T) * ∑(f(t) * cos(2 * pi * n * t / T))
    bn = (2/T) * ∑(f(t) * sin(2 * pi * n * t / T))

    Parameters:
        one_period_signal (numpy.ndarray):
            -   1-period audio signal.

        n_harmonics (int):
            -   The number of harmonics used to approximate the input signal.

    Returns:
        fourier_coefficients (numpy.ndarray):
            -   Fourier series coefficients (an, bn) up to the Nth harmonic plus the average
                term a0.
    """

    fourier_coefficients = []

    T = len(one_period_signal)
    t = np.arange(T)

    for n in range(n_harmonics + 1):
        an = 2 / T * (one_period_signal * np.cos(2 * np.pi * n * t / T)).sum()
        bn = 2 / T * (one_period_signal * np.sin(2 * np.pi * n * t / T)).sum()
        fourier_coefficients.append((an, bn))

    return np.array(fourier_coefficients)


def calculate_harmonic_power_spectrum(fourier_coefficients):
    """
    Calculates the relative power spectrum of harmonic components in a signal.

    The function takes a set of Fourier coefficients representing the harmonic components
    of a signal and calculates the relative power of each component. The relative power
    spectrum expresses the power of each harmonic as a fraction of the total signal power.
    The first term is excluded from the calculation because it represents the average
    value of the signal.

    Args:
        fourier_coefficients (numpy.ndarray):
            -   A 2D array containing Fourier coefficients for the harmonic components.
                This array is obtained from the calculate_fourier_coefficients function
                and has the following structure: [[a0, b0], [a1, b1], [a2, b2], ...].

    Returns:
        relative_harmonic_powers (numpy.ndarray):
            -   Relative harmonic powers rounded to 4 decimal places. The first element
                is excluded because it represents the average value of the signal.
    """

    absolute_harmonic_powers = np.sqrt(np.sum(fourier_coefficients**2, axis=1))
    total_signal_power = np.sum(absolute_harmonic_powers)
    relative_harmonic_powers = absolute_harmonic_powers / total_signal_power

    # rounding to 4 decimal places
    relative_harmonic_powers = np.round(relative_harmonic_powers, 4)

    return relative_harmonic_powers[1:]


def reconstruct_original_signal(one_period_signal, fourier_coefficients):
    """
    Reconstructs the original signal from its Fourier coefficients.

    The function reconstructs the original signal using the provided Fourier coefficients
    and 1-period signal following the steps below:

    1. Initialize an array for the reconstructed signal.

    2. For each harmonic component (n), including both sine (b) and cosine (a) terms:

        -   If n is 0 (DC component):
                *   Divide the cosine term (a) by 2.
        -   Calculate the contribution of the harmonic component to the reconstructed signal
            using the formula:
                reconstructed_signal =  reconstructed_signal
                                        + a * cos(2 * pi * n * t / N)
                                        + b * sin(2 * pi * n * t / N)
            where:
                *   a and b are the Fourier coefficients for the current harmonic component.
                *   t is the time variable.
                *   N is the length of the 1-period signal.

    Args:
        one_period_signal (numpy.ndarray):
            -   A 1-period signal represented as an array of amplitudes.

        fourier_coefficients (numpy.ndarray):
            -   A 2D array containing Fourier coefficients for the harmonic components.
                This array is obtained from the calculate_fourier_coefficients function
                and has the following structure: [[a0, b0], [a1, b1], [a2, b2], ...].

    Returns:
        numpy.ndarray: A reconstructed signal obtained from the Fourier coefficients.
    """

    reconstructed_signal = np.zeros(len(one_period_signal))
    t = np.arange(0, len(one_period_signal))

    for n, (a, b) in enumerate(fourier_coefficients):
        if n == 0:
            a = a / 2

        reconstructed_signal = (
            reconstructed_signal
            + a * np.cos(2 * np.pi * n * t / len(one_period_signal))
            + b * np.sin(2 * np.pi * n * t / len(one_period_signal))
        )

    return reconstructed_signal


def get_mathematical_representation_of_signal(fourier_coefficients, T):
    """
    Generates the mathematical representation of a signal from its Fourier coefficients.

    The function takes Fourier coefficients representing the harmonic components of a signal
    and generates a mathematical formula (a function y(t)) of the signal in terms of cosine
    and sine functions.

    Args:
        fourier_coefficients (numpy.ndarray):
            -   A 2D array containing Fourier coefficients for the harmonic components.
                This array is obtained from the calculate_fourier_coefficients function
                and has the following structure: [[a0, b0], [a1, b1], [a2, b2], ...].
        T (float):
            -   The period of the signal in seconds. The function converts the period
                to milliseconds.

    Returns:
        str: A string containing the mathematical representation of the signal.
    """

    representation = ""
    T *= 1000  # convert period to milliseconds

    for n, (a, b) in enumerate(fourier_coefficients):
        if n == 0:
            representation += f"{a/2:.3f}\n"
        else:
            representation += f" + {a:.3f}*cos(2*pi*{n}*t/{T:.3f}) + {b:.3f}*sin(2*pi*{n}*t/{T:.3f})\n"

    # Polishing the output
    representation = representation.replace(" + -", " - ")

    return representation
