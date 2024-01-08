import os
from scipy.io import wavfile
import ipywidgets as widgets
from IPython.display import Audio, display, clear_output
from ipywidgets import Layout
import numpy as np
from functools import partial
from settings import period_bounds as pb
from settings import config as cfg
from utils import general_functions_and_classes_utils as gfcu


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


class _PrepareButtonsPlayIndividualHarmonics(gfcu.ButtonPanel):
    """
    Subclass of a ButtonPanel class used for creating a panel with "Toggle All" and
    "Save As Individual Audio files"  buttons. Used in save_harmonics_sounds
    function.
    """

    def __init__(self):
        """
        Initializes _PrepareButtonsPlayIndividualHarmonics with predefined buttons.
        """
        super().__init__(
            [
                "Toggle All",
                "Save As Individual Audio files",
            ]
        )


def _get_sound_frequency(idx):
    # Calculate sound periods and frequencies for the fundamental frequency of each instrument
    sound_periods = [end - start for start, end in pb.PERIOD_BOUNDS.values()]
    sound_frequencies = [1 / period for period in sound_periods]

    # Get the fundamental frequency for the current instrument
    return sound_frequencies[idx]


def _get_coefficients(term):
    """
    Function extracts coefficients a and b from a term of the Fourier series. The term
    correspnds to one harmonic of the signal.

    Args:
        term (list): List containing average term, a term with cos, and a term with sin.
                    The first element of the list contains the strings: the average term,
                    a term with cos, and a term with sin. All other elements of the list
                    contain two strings: a term with cos and a term with sin.
                    Note: the function returns positive coefficients a and b only (without
                    the sign). This is because the coefficients are used to calculate the
                    amplitude of the signal which is obtained by square root of a^2 + b^2.

    Returns:
        a (float): Coefficient a of the Fourier series standing in front of cosine term.
        b (float): Coefficient b of the Fourier series standing in front of sine term.
    """
    if len(term) == 3:
        term = term[1:]  # remove the average term

    a = term[0].split("*cos")[0]
    b = term[1].split("*sin")[0]

    if a.startswith(("+ ", "- ")):
        a = float(a[2:])
    if b.startswith(("+ ", "- ")):
        b = float(b[2:])

    return a, b


def _get_max_amplitude(grouped_terms):
    """
    Function calculates the maximum amplitude of the signal corresponding to the dominant harmonic.

    Args:
        grouped_terms (list): List of grouped terms for the dominant harmonic.

    Returns:
        max_amplitude (float): Maximum amplitude of the signal corresponding to the dominant harmonic.
    """
    max_amplitude = np.max(
        [
            np.sqrt(a * a + b * b)
            for a, b in [_get_coefficients(term) for term in grouped_terms]
        ]
    )

    return max_amplitude


def _calc_scaling_factors(relative_harmonic_powers, grouped_terms):
    scaling_factors = [
        np.sqrt(relative_harmonic_powers[n]) for n in range(len(grouped_terms))
    ]

    return scaling_factors


def save_harmonics_sounds(
    files,
    mathematical_representation_of_signal_per_instrument,
    relative_harmonic_powers_per_instrument,
):
    """
    Save individual harmonics for each selected instrument as a WAV file.

    Allows to select one ore more instruments by clicking on the checkboxes. The function
    separates the signal into individual harmonics (grouped terms) and calculates the
    relative harmonic powers and a total sound power for the selected instrument. Then,
    it calculates the scaling factors for each harmonic based on the relative harmonic
    powers and the maximum amplitude of the signal corresponding to the dominant harmonic.
    Finally, it saves each harmonic as a WAV file.

    Args:
        files (list):
            - List of input filenames. Full paths to the files are expected.

        mathematical_representation_of_signal_per_instrument (list):
            -   2D list of mathematical representations of the signal for each instrument.
                Each element of this list is another list that stores the mathematical
                representation of the signal for one instrument (recording). The structure
                of the inner list is as follows:
                * First element: average term, a term with cos, and a term with sin.
                * All other elements: a term with cos and a term with sin.

        relative_harmonic_powers_per_instrument (list):
            -   List of relative harmonic powers for each instrument. The relative harmonic
                power is calculated as a fraction of the total signal power.

    Returns:
        None
    """
    audio_names = gfcu.get_names(files)

    checkboxes, checkbox_layout = gfcu.prepare_checkbox_grid(audio_names)
    checkbox_grid = widgets.GridBox(checkboxes, layout=checkbox_layout)

    # prepare buttons
    buttons_panel = _PrepareButtonsPlayIndividualHarmonics()
    (
        toggle_all_button,
        save_individual_audios_button,
    ) = buttons_panel.get_buttons()
    button_container = buttons_panel.get_container()

    display(checkbox_grid, button_container)

    toggle_all_button.on_click(partial(gfcu.toggle_all, checkboxes))

    def _save_individual_audios(_):
        clear_output(wait=True)  # unique output
        display(checkbox_grid, button_container)  # unique output

        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        for idx in selected_indices:
            # get individual harmonics (grouped terms) for the selected instrument
            terms = gfcu.get_individual_terms(
                mathematical_representation_of_signal_per_instrument[idx]
            )
            grouped_terms = gfcu.get_grouped_terms(terms)

            # get relative harmonic powers and a total sound power for the selected instrument
            relative_harmonic_powers = relative_harmonic_powers_per_instrument[idx]

            # get the fundamental frequency for the selected instrument
            fundamental_frequency = _get_sound_frequency(idx)

            t = np.linspace(
                0, cfg.AUDIO_DURATION, int(cfg.AUDIO_DURATION * cfg.SAMPLE_RATE)
            )

            max_amplitude = _get_max_amplitude(grouped_terms)
            scaling_factors = _calc_scaling_factors(
                relative_harmonic_powers, grouped_terms
            )

            output_directory = os.path.join(
                cfg.PATH_RESULTS, "harmonics_sounds", audio_names[idx]
            )

            for n, term in enumerate(grouped_terms):
                t = np.linspace(
                    0, cfg.AUDIO_DURATION, int(cfg.AUDIO_DURATION * cfg.SAMPLE_RATE)
                )

                a, b = _get_coefficients(term)
                f = fundamental_frequency * (n + 1)

                amplitude = np.sqrt(a * a + b * b)

                # Calculate the scaling factor based on the relative power
                scaling_factor = (
                    10000 * scaling_factors[n] / max_amplitude
                )  # multiply by 10000 to make the sound louder

                harmonic_sound = np.int16(
                    scaling_factor * amplitude * np.sin(2 * np.pi * f * t)
                )

                # Save the WAV file
                filename = os.path.join(
                    output_directory, f"{audio_names[idx]}_harmonic_{n + 1}.wav"
                )
                wavfile.write(filename, cfg.SAMPLE_RATE, harmonic_sound)

                # print relative path to the saved file
                print(f"Saved joined plot to .{output_directory[len(cfg.PATH_BASE):]}")

    save_individual_audios_button.on_click(_save_individual_audios)
