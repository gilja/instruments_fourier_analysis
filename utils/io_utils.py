from scipy.io import wavfile
import ipywidgets as widgets
from IPython.display import Audio, display
from ipywidgets import Layout
import numpy as np
import os
from settings import period_bounds as pb
from settings import config as cfg


def load_sound(filename):
    """
    Load and normalize a WAV audio file.

    Reads a WAV file specified by the filename and normalizes the audio sample
    data to the range of [-1, 1]. If the audio file has multiple channels
    (stereo), only the first channel is returned.

    Parameters:
        filename (str): The path to the WAV audio file. The path can be either
                        relative or absolute.

    Returns:
        tuple of (np.ndarray, int): A tuple containing two elements:
            - data (np.ndarray): The normalized audio sample data. If the
              audio is stereo, only the first channel is returned.
            - sample_rate (int): The sample rate of the audio file in samples
              per second.

    Raises:
        ValueError: If the file is not found or cannot be read.
        TypeError: If the provided file is not in the WAV format.

    Notes:
        - The function requires the 'scipy.io.wavfile' module to be imported as
          'wavfile' before calling.
        - The audio file must be in the WAV format.
    """

    if not filename:
        raise ValueError("No file was provided.")

    if ".wav" not in filename.lower():
        raise TypeError("The provided file is not in the WAV format.")

    sample_rate, data = wavfile.read(filename)
    data = data * 1.0 / (abs(data).max())

    if len(data.shape) > 1:  # for stereo data, use only first channel
        data = data[:, 0]

    return data, sample_rate


def play_audio(files, n_columns=3):
    """
    Display audio players for a list of audio files within a Jupyter notebook.

    The function arranges the audio players in a grid format with a specified
    number of columns. Each audio player is accompanied by a centered label
    derived from the file name. If the number of audio players exceeds the
    number of columns, they are wrapped to the next row.

    Parameters:
        files (list of str): A list of strings representing the file paths to
                             the audio files. Each path should be a valid
                             system path.

        n_columns (int, optional): The number of audio players to display per
                                   row. Defaults to 3.

    Returns:
        None

    Raises:
        ValueError: Raised if the 'files' list is empty.

    Notes:
        - The function requires the 'ipywidgets' module to be imported as
          widgets

    Examples:
        >>> playAudio(['/path/to/audio1.wav', '/path/to/audio2.wav'],
                        n_columns=2)
    """
    rows = []
    row = []

    if len(files) == 0:
        raise ValueError("No files provided")

    for file in files:
        # Extract the file name for display
        name = file.split("/")[-1]

        # Create a label for the file name, centered
        label = widgets.Label(
            value=name.replace(".WAV", "")
            .replace("_", " ")
            .replace("-", " ")
            .replace(" 16 bit", ""),
            layout=Layout(
                width="100%", display="flex", justify_content="center"
            ),  # note: type: ignore
        )

        # Create an Output widget for the audio player
        audio_player = Audio(file)
        output_widget = widgets.Output()

        with output_widget:
            display(audio_player)

        # Combine the label and the audio player in a vertical layout
        combined_widget = widgets.VBox([label, output_widget])

        # Add the combined widget to the current row
        row.append(combined_widget)

        if (
            len(row) == n_columns
        ):  # If a row has n_columns widgets, add to rows and start a new row
            rows.append(widgets.HBox(row))
            row = []

    if row:  # Add any remaining widgets as the last row
        rows.append(widgets.HBox(row))

    # Arrange all rows vertically
    vbox = widgets.VBox(rows)
    display(vbox)


def export_and_store_one_period_audio(files, one_period_signals, sample_rates):
    """
    Export audio as WAV file and store in an array one-period audio signals.

    This function takes a list of input filenames, one-period audio signals,
    and their corresponding sample rates. It exports and stores each
    one-period audio signal as a WAV file, 1-second long in the
    'one_period_audio' directory within the results folder. It also returns
    the one-period audio signals as an array.

    Args:
        files (list): List of input filenames. Full paths to the files are expected.
        one_period_signals (list): List of one-period audio signals stored as NumPy arrays.
                                   This list is created using extract_periods_and_data_rates()
                                   function from utils/fourier_math_utils.py.
        sample_rates (list): List of sample rates corresponding to the one-period signals.
                             This list is created using extract_periods_and_data_rates()
                             function from utils/fourier_math_utils.py.

    Returns:
        one_period_audios (list): List of one-period audio signals 1-second long.
    """

    one_period_audios = []
    output_directory = os.path.join(cfg.PATH_RESULTS, "one_period_audio")

    for file, signal, sample_rate, period_bound in zip(
        files, one_period_signals, sample_rates, pb.PERIOD_BOUNDS.values()
    ):
        name = (
            file.split("/")[-1]
            .replace(".WAV", "")
            .replace("-", "_")
            .replace("_16_bit", "")
        )

        duration = period_bound[1] - period_bound[0]
        # extend the signal to 1 second long to be audible
        one_period_audio_data = np.tile(signal, int(1 / duration))

        one_period_audios.append(one_period_audio_data)
        wavfile.write(
            f"{output_directory}/{name}",
            sample_rate,
            one_period_audio_data,
        )

    return one_period_audios


def play_individual_harmonics():
    pass
