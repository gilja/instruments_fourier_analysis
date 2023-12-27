import numpy as np
from settings import period_bounds as pb


def extract_periods_and_data_rates(sounds):
    """
    Extract one-period-long audio signals and their corresponding data rates.

    This function extracts one-period audio signals and their corresponding data rates
    from a list of sound data and period bounds. It uses the provided sounds and
    period bounds to calculate the one-period audio signals, and it returns two lists:
    one containing the extracted one-period audio signals and another containing the
    corresponding data rates.

    Args:
        sounds (list): A list of tuples, where each tuple contains sound data and
                       its associated sample rate.

    Returns:
        tuple: A tuple containing two lists:
            - List of numpy arrays, each representing a one-period audio signal.
            - List of integers, each representing the data rate of the corresponding
              one-period audio signal.

    Examples:
        Given a list of sound data in WAV format and period bounds, one can extract
        one-period audio signals and data rates as follows:

        >>> sounds = [sound1, sound2, ...]  # List of sound data and rates
        >>> one_period_audio, data_rates = extract_periods_and_data_rates(sounds)

        The 'one_period_audio' list will contain the extracted one-period audio signals,
        and the 'data_rates' list will contain the corresponding data rates.
    """

    periods, data_rates = [], []

    for (data, data_rate), (period_start, period_end) in zip(
        sounds, pb.PERIOD_BOUNDS.values()
    ):
        sample_start = int(period_start * data_rate)
        sample_end = int(period_end * data_rate)

        period = data[sample_start:sample_end]
        periods.append(period)
        data_rates.append(data_rate)

    return periods, data_rates


def calculate_fourier_coefficients(one_period_signal, n_harmonics):
    """
    Calculate the Fourier series coefficients for a given periodic signal represented
    as a discrete set of data points. Return the coefficients (an, bn)
    for each harmonic up to the Nth, plus the average term a0.

    The Fourier series of a periodic function f(t) with period T is given by

    f(t) = a0 + ∑(an * cos(2 * pi * n * t / T) + bn * sin(2 * pi * n * t / T)),

    where a0 is the average value of f(t) over one period and an and bn are the coefficients
    for the cosine and sine terms, respectively.
    The coefficients an and bn are calculated using the following formulas:

    an = (2/T) * ∑(f(t) * cos(2 * pi * n * t / T))
    bn = (2/T) * ∑(f(t) * sin(2 * pi * n * t / T))

    Parameters:
        period (numpy.ndarray): One-period audio signal.
        n_harmonics (int): Number of harmonics to calculate for approximating input signal.

    Returns:
        fourier_coefficients (numpy.ndarray): Array of Fourier series coefficients up to
                                              the Nth harmonic.
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
    Calculate the relative power spectrum of harmonic components in a signal.

    This function takes a set of Fourier coefficients representing the harmonic components
    of a signal and calculates the relative power of each component. The relative
    power spectrum expresses the power of each harmonic as a fraction of the total signal
    power. The first harmonic is excluded from the calculation because it represents the
    average value of the signal.

    Args:
        fourier_coefficients (numpy.ndarray): A 2D array containing Fourier coefficients
                                              representing the harmonic components of a
                                              signal.

    Returns:
        numpy.ndarray: An array of relative harmonic powers, where each value represents
                       the relative power of a harmonic component in the signal.

    Example:
        Given Fourier coefficients, you can calculate the relative harmonic powers as follows:

        >>> fourier_coeffs = np.array([[a1, b1], [a2, b2], ...])  # Fourier coefficients
        >>> relative_powers = calculate_harmonic_power_spectrum(fourier_coeffs)
        >>> print(relative_powers)
        [0.1234, 0.5678, ...]  # Relative powers of harmonic components
    """

    absolute_harmonic_powers = np.sqrt(np.sum(fourier_coefficients**2, axis=1))
    total_signal_power = np.sum(absolute_harmonic_powers)
    relative_harmonic_powers = absolute_harmonic_powers / total_signal_power

    # rounding to 4 decimal places
    relative_harmonic_powers = np.round(relative_harmonic_powers, 4)

    return relative_harmonic_powers[1:]


def reconstruct_original_signal(one_period_signal, fourier_coefficients):
    """
    Reconstruct the original signal from its Fourier coefficients.

    This function takes a one-period signal and its corresponding Fourier coefficients
    and reconstructs the original signal using the coefficients. It calculates the
    inverse Fourier series of the signal.

    Args:
        one_period_signal (numpy.ndarray): A one-period signal as a 1D array.
        fourier_coefficients (numpy.ndarray): A 2D array containing Fourier coefficients
                                              representing the harmonic components of the
                                              signal.

    Returns:
        numpy.ndarray: A reconstructed signal obtained from the Fourier coefficients.

    Example:
        Given a one-period signal and its Fourier coefficients, you can reconstruct the
        original signal as follows:

        >>> one_period_signal = np.array([value1, value2, ...])  # One-period signal
        >>> fourier_coeffs = np.array([[a1, b1], [a2, b2], ...])  # Fourier coefficients
        >>> reconstructed = reconstruct_original_signal(one_period_signal, fourier_coeffs)
        >>> print(reconstructed)
        [reconstructed_value1, reconstructed_value2, ...]  # Reconstructed signal
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
    Generate the mathematical representation of a signal from its Fourier coefficients.

    This function takes Fourier coefficients representing the harmonic components of a signal
    and generates a mathematical representation of the signal in terms of cosine and sine terms.

    Args:
        fourier_coefficients (numpy.ndarray): A 2D array containing Fourier coefficients
            representing the harmonic components of the signal.
        T (float): The period of the signal in seconds. The function converts the period
                   to milliseconds.

    Returns:
        str: A string containing the mathematical representation of the signal.

    Example:
        Given Fourier coefficients and the period T in seconds, you can generate the mathematical
        representation of the signal, where T is expressed in milliseconds, as follows:

        >>> fourier_coeffs = np.array([[a1, b1], [a2, b2], ...])  # Fourier coefficients
        >>> period_T = 0.005  # Period in seconds
        >>> representation = get_mathematical_representation_of_signal(fourier_coeffs, period_T)
        >>> print(representation)
        "a0 + a1*cos(2*pi*t/period_T) + b1*sin(2*pi*t/period_T) + ..."
    """

    representation = ""
    T *= 1000  # convert period to milliseconds

    for n, (a, b) in enumerate(fourier_coefficients):
        if n == 0:
            representation += f"{a/2:.3f}\n"
        else:
            representation += f" + {a:.3f}*cos(2*pi*{n}*t/{T:.3f}) + {b:.3f}*sin(2*pi*{n}*t/{T:.3f})\n"

    # Polishing the formula
    representation = representation.replace(" + -", " - ")

    return representation
