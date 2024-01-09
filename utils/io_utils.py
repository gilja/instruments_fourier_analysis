"""
io_utils:
=========

The module contains utility functions for loading, playing and exporting audio data.

Public functions:
-----------------

-   load_sound: Load and normalize a WAV audio file.
-   play_audio: Displays audio players for a list of audio files within a Jupyter notebook.
-   export_and_store_one_period_audio: Export audio as a WAV file and store audio data in an array.
-   save_harmonics_sounds: Save individual harmonics for each selected instrument as a WAV file.
-   create_directory_structure: Creates a directory structure for storing import data and results.

Private functions:
------------------

-   _get_sound_frequency: Returns the fundamental frequency for the selected audio file.
-   _get_coefficients: Extracts coefficients from a term of the Fourier series.
-   _get_max_amplitude: Calculates the amplitude of the dominant harmonic within the audio file.
-   _calc_scaling_factors: Calculates the scaling factors for the amplitude of each harmonic.

Classes:
--------

-   _PrepareButtonsSaveHarmonicSounds:
        *   A subclass of the ButtonPanel class defined in general_functions_and_classes_utils.
        *   Used in save_harmonics_sounds function.

For more information on the functions and classes, refer to their docstrings.

Notes:
------

Author: Duje Giljanović (giljanovic.duje@gmail.com)
License: MIT License

If you use this module in your research or any other publication, please acknowledge it by citing
as follows:

@software{instruments_fourier_analysis,
    title = {Fourier Analysis of Musical Instruments},
    author = {Duje Giljanović},
    year = {2024},
    url = {github.com/gilja/instruments_fourier_analysis},
}
"""

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
    Loads and normalizes a WAV audio file.

    The function reads a WAV file specified by the filename and normalizes
    the audio sample data to the range of [-1, 1]. If the audio file has
    multiple channels (stereo), only the first channel is returned.

    Args:
        filename (str):
            -   The path to the WAV audio file. Absolute paths are recommended
                as they are used throughout the tool.

    Returns:
        tuple of (np.ndarray, int):
            -   A tuple containing two elements:
                *   data (np.ndarray): The normalized audio sample data. If the
                    audio is stereo, only the first channel is returned.
                *   sample_rate (int): The sample rate of the audio file in samples
                    per second.

    Raises:
        ValueError: If the file is not found or cannot be read.
        TypeError: If the provided file is not in the WAV format.

    Notes:
        -   The audio file must be in the WAV format.
        -   Recommended file names are <instrument>-<note>_16_bit.wav
            all lowercase, e.g. cello-c3_16_bit.wav
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
    Displays audio players for a list of audio files within a Jupyter Notebook.

    The function arranges the audio players in a grid format with a specified
    number of columns. Each audio player is accompanied by a centred label
    derived from the file name. If the number of audio players exceeds the
    number of columns, they are wrapped to the next row.

    Parameters:
        files (list of str):
            -   A list of strings representing the file paths to the audio files.
                Absolute paths are recommended as they are used throughout the
                tool.

        n_columns (int, optional):
        -   The number of audio players to display per row. Defaults to 3.

    Returns:
        None

    Raises:
        ValueError: Raised if the 'files' list is empty.
    """

    rows = []
    row = []

    if len(files) == 0:
        raise ValueError("No files provided")

    file_names = gfcu.get_names(files)

    for idx, file in enumerate(files):
        file_name = file_names[idx]

        # Create a label for the file name, centered
        label = widgets.Label(
            value=file_name,
            layout=Layout(width="100%", display="flex", justify_content="center"),
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
    Exports audio as a WAV file and stores audio data in an array.

    The function takes a list of input filenames, one-period audio signals,
    and their corresponding sample rates. It exports and stores each
    original one-period audio signal as a WAV file, 1-second long in the
    'one_period_audio' directory within the results folder. It also returns
    the one-period audio signals as an array.

    Args:
        files (list):
            -   Input filenames. Full paths to the files are expected.

        one_period_signals (list):
            -   1-period audio signals stored as NumPy arrays.
                *   This list is created using extract_periods_and_data_rates()
                    function from fourier_math_utils module.

        sample_rates (list):
            -   Sample rates corresponding to the one-period signals.
                    *   This list is created using extract_periods_and_data_rates()
                        function from fourier_math_utils module.

    Returns:
        one_period_audios (list):
            -   1-period audio signals 1-second long.
    """

    one_period_audios = []
    output_directory = os.path.join(cfg.PATH_RESULTS, "original_one_period_audios/")

    audio_names = gfcu.get_names(files)

    for idx, (signal, sample_rate, period_bound) in enumerate(
        zip(one_period_signals, sample_rates, pb.PERIOD_BOUNDS.values())
    ):
        name = audio_names[idx]

        duration = period_bound[1] - period_bound[0]

        # extend the signal to 1 second long to be audible
        one_period_audio_data = np.tile(signal, int(1 / duration))

        one_period_audios.append(one_period_audio_data)

        # Save the WAV file
        audio_path = os.path.join(output_directory, f"{name}.wav")

        wavfile.write(
            audio_path,
            sample_rate,
            one_period_audio_data,
        )

        print(
            f"Exported audio to .{output_directory[len(cfg.PATH_BASE):]}"
        )  # print relative path

    return one_period_audios


class _PrepareButtonsSaveHarmonicSounds(gfcu.ButtonPanel):
    """
    A subclass of the ButtonPanel class used for creating a panel with "Toggle All"
    and "Save As Individual Audio files"  buttons. Used in save_harmonics_sounds
    function.
    """

    def __init__(self):
        """
        Initializes _PrepareButtonsSaveHarmonicSounds with predefined buttons.
        """
        super().__init__(
            [
                "Toggle All",
                "Save Harmonics As Individual Audio files",
            ]
        )


def _get_sound_frequency(idx):
    """
    Returns the fundamental frequency for the selected audio file.

    Args:
        idx (int):
            -   The index of the selected audio file.

    Returns:
        float: The fundamental frequency for the selected audio file.
    """

    # Calculate sound periods and frequencies for the fundamental frequency of each instrument
    sound_periods = [end - start for start, end in pb.PERIOD_BOUNDS.values()]
    sound_frequencies = [1 / period for period in sound_periods]

    # Get the fundamental frequency for the current instrument
    return sound_frequencies[idx]


def _get_coefficients(term):
    """
    Extracts the coefficients a and b from a single term of the Fourier series.
    The term corresponds to one harmonic of the signal.

    Args:
        term (list):
            -   List of strings representing a single term of the Fourier series.
                *   The first element of the list contains the average term, a term
                    with cos and a term with sin; therefore, it has a length of 3.
                *   All other elements of the list contain a term with cos and a term
                    with sin; therefore, they have a length of 2.
                *   Note: the function returns positive coefficients a and b only
                    (without the sign). This is because the coefficients are used to
                    calculate the amplitude of the signal which is obtained by square
                    root of a^2 + b^2.

    Returns:
        a (float): Coefficient a of the Fourier series standing in front of the cosine term.
        b (float): Coefficient b of the Fourier series standing in front of the sine term.
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
    Calculates the amplitude of the dominant harmonic within the audio file.

    Args:
        grouped_terms (list):
            -   All the harmonics in the sound.

    Returns:
        max_amplitude (float): The amplitude of the dominant harmonic.
    """
    max_amplitude = np.max(
        [
            np.sqrt(a * a + b * b)
            for a, b in [_get_coefficients(term) for term in grouped_terms]
        ]
    )

    return max_amplitude


def _calc_scaling_factors(relative_harmonic_powers, grouped_terms):
    """
    Calculates the scaling factors for the amplitude of each harmonic.

    Scaling factors are calculated using the relative harmonic powers and the
    maximum amplitude of the signal corresponding to the dominant harmonic.

    Args:
        relative_harmonic_powers (list):
            -   Relative harmonic powers. The relative harmonic power is
                calculated as a fraction of the total signal power.

        grouped_terms (list):
            -   All the harmonics in the sound.

    Returns:
        scaling_factors (list): Scaling factors for the amplitude of each harmonic.
    """
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
    Saves individual harmonics for each of the selected instruments as a WAV file.

    The function allows the user to select one or more instruments by clicking on the
    checkboxes. It separates the signal into individual harmonics (grouped terms) and
    calculates the relative harmonic powers and the total sound power for the selected
    instrument. Then, it calculates the scaling factors for each harmonic based on the
    relative harmonic powers and the maximum amplitude of the signal corresponding to
    the dominant harmonic. This is reflected in the loudness of each harmonic.
    Finally, the function allows the user to save each harmonic as a WAV file.

    Buttons:

    -   Toggle All: Toggles all checkboxes on/off. Off by default.
    -   Save Harmonics As Individual Audio files: Saves individual harmonics as the WAV
        files for each selected instrument.

    Args:
        files (list):
            - Input filenames. Full paths to the files are expected.

        mathematical_representation_of_signal_per_instrument (list):
            -   2D list of mathematical representations of the signal for each instrument.
                Each element of this list is another list that stores the mathematical
                representation of the signal for one instrument (recording). The structure
                of the inner list is as follows:
                * First element: average term, a term with cos, and a term with sin.
                * All other elements: a term with cos and a term with sin.

        relative_harmonic_powers_per_instrument (list):
            -   Relative harmonic powers for each instrument. The relative harmonic
                power is calculated as a fraction of the total signal power.

    Returns:
        None
    """

    audio_names = gfcu.get_names(files)

    checkboxes, checkbox_layout = gfcu.prepare_checkbox_grid(audio_names)
    checkbox_grid = widgets.GridBox(checkboxes, layout=checkbox_layout)

    # prepare buttons
    buttons_panel = _PrepareButtonsSaveHarmonicSounds()
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
                cfg.PATH_RESULTS, "harmonics_sounds", f"{audio_names[idx]}/"
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


def create_directory_structure():
    """
    Creates a directory structure for storing instrument samples and results.

    The function creates the following directories:

    -   ./data/instrument_samples: stores the instrument samples
    -   ./results/analysed: stores the results of the analysis
        *   ./results/analysed/harmonics_function_plots
        *   ./results/analysed/harmonics_sounds
        *   ./results/analysed/original_one_period_audios
        *   ./results/analysed/original_waveforms
        *   ./results/analysed/power_spectra
        *   ./results/analysed/reconstructed_one_period_audio
        *   ./results/analysed/waveform_reconstruction

    Args:
        None

    Returns:
        None
    """

    instrument_samples = os.path.join(cfg.PATH_INSTRUMENT_SAMPLES)
    results = os.path.join(cfg.PATH_RESULTS)
    original_waveforms = os.path.join(results, "original_waveforms")
    original_one_period_audios = os.path.join(results, "original_one_period_audios")
    reconstructed_one_period_audios = os.path.join(
        results, "reconstructed_one_period_audio"
    )
    power_spectra = os.path.join(results, "power_spectra")
    harmonics_function_plots = os.path.join(results, "harmonics_function_plots")

    os.makedirs(instrument_samples, exist_ok=True)
    os.makedirs(results, exist_ok=True)
    os.makedirs(original_waveforms, exist_ok=True)
    os.makedirs(original_one_period_audios, exist_ok=True)
    os.makedirs(reconstructed_one_period_audios, exist_ok=True)
    os.makedirs(power_spectra, exist_ok=True)
    os.makedirs(harmonics_function_plots, exist_ok=True)
