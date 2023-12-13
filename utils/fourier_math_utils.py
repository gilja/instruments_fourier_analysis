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
