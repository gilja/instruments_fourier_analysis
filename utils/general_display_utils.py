import ipywidgets as widgets
from IPython.display import Audio, display, clear_output
from ipywidgets import Layout
from functools import partial
import numpy as np
import os
from scipy.io import wavfile
from utils import general_functions_and_classes_utils as gfcu
from settings import period_bounds as pb
from settings import config as cfg


def _get_audiofile_names(files):
    """
    Extracts and cleans audio file names from a list of file paths.

    Function expects that files are of the WAV format and that the file names
    contain .WAV extension. The function removes the extension and replaces
    underscores and dashes with spaces. The function also removes the "16 bit"
    string from the plot names.

    Args:
        files (list of str): A list of file paths.

    Returns:
        audio_file_names (list of str): A list of cleaned audio file names
                                        extracted from the file paths.
    """

    audio_file_names = [
        name.split("/")[-1].replace("-", "_").replace("_16_bit.wav", "")
        for name in files
    ]

    return audio_file_names


class _PrepareButtonsMathematicalRepresentation(gfcu.ButtonPanel):
    """
    Subclass of a ButtonPanel class used for creating a panel with "Display Function"
    and "Toggle All" buttons. Used for displaying mathematical representations of
    signals through Fourier series.
    """

    def __init__(self):
        """
        Initializes _PrepareButtonsMathematicalRepresentation with predefined buttons.
        """
        super().__init__(["Display Function", "Toggle All"])


def print_mathematical_representation_of_signal(
    files, mathematical_representation_of_signal_per_instrument
):
    """
    Display mathematical representations of the reconstructed audio signals for
    selected audio files.

    Function generates a graphical user interface (GUI) that allows the user
    to select files and view the mathematical representations of reconstructed
    signal. It displays checkboxes for each audio file, buttons to control the
    display, and prints the mathematical representation of the selected audio files.

    Args:
        files (list): A list of audio file paths.
        mathematical_representation_of_signal_per_instrument (list): A list of
            mathematical representations for each audio file.

    Returns:
        None
    """

    audio_file_names = _get_audiofile_names(files)
    checkboxes, checkbox_layout = gfcu.prepare_checkbox_grid(audio_file_names)
    checkbox_grid = widgets.GridBox(checkboxes, layout=checkbox_layout)

    # Prepare buttons
    buttons_panel = _PrepareButtonsMathematicalRepresentation()
    display_function_button, toggle_all_button = buttons_panel.get_buttons()
    button_container = buttons_panel.get_container()

    display(checkbox_grid, button_container)

    def _display_function(_):
        clear_output(wait=True)  # unique output
        display(checkbox_grid, button_container)  # unique output

        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        sound_periods = [end - start for start, end in pb.PERIOD_BOUNDS.values()]
        sound_frequencies = [1 / period for period in sound_periods]

        for idx in selected_indices:
            print(
                f"Instrument: {audio_file_names[idx]} ({sound_frequencies[idx]:.2f} Hz)"
            )
            print(mathematical_representation_of_signal_per_instrument[idx])

    display_function_button.on_click(_display_function)

    toggle_all_button.on_click(partial(gfcu.toggle_all, checkboxes))


class _PrepareButtonsDisplayAudio(gfcu.ButtonPanel):
    """
    Subclass of a ButtonPanel class used for creating a panel with "Display Audio",
    "Toggle All" and "Save Selected Reconstructed" buttons. Used in
    display_reconstructed_and_original_audio function.
    """

    def __init__(self):
        """
        Initializes _PrepareButtonsDisplayAudio with predefined buttons.
        """
        super().__init__(
            [
                "Display",
                "Toggle All",
                "Save Selected",
            ]
        )


def _draw_play_audio_buttons(
    idx,
    audio_file_names,
    period_bounds,
    sample_rates,
    one_period_signals,
    reconstructed_signals,
    rows,
):
    """
    Draw play audio buttons for original and reconstructed audio.

    This function generates widgets to play the original and reconstructed audio
    for a selected audio file. It creates Audio widgets for both audio signals
    and adds labels to identify them. These widgets are then combined into a
    horizontal layout and added to the `rows` list. Depending on the number of
    checked checkboxes, the function may add multiple rows to the `rows` list.
    The function is used in display_reconstructed_and_original_audio function.

    Args:
        idx (int): Index of the selected audio file.
        audio_file_names (list): List of audio file names.
        period_bounds (list): List of period bounds for audio files.
        sample_rates (list): List of sample rates for audio files.
        one_period_signals (list): List of one-period audio signals.
        reconstructed_signals (list): List of reconstructed audio signals.
        rows (list): List of rows to which the widgets are added.

    Returns:
        None
    """

    title = audio_file_names[idx]
    duration = period_bounds[idx][1] - period_bounds[idx][0]
    sample_rate = sample_rates[idx]

    one_period_audio_data_original = np.tile(one_period_signals[idx], int(1 / duration))
    one_period_audio_data_reconstructed = np.tile(
        reconstructed_signals[idx], int(1 / duration)
    )

    label_original = widgets.Label(
        value=f"{title} (original)",
        layout=Layout(width="100%", display="flex", justify_content="center"),
    )

    audio_player_original = Audio(one_period_audio_data_original, rate=sample_rate)
    output_widget_original = widgets.Output()

    with output_widget_original:
        display(audio_player_original)

    combined_widget_original = widgets.VBox([label_original, output_widget_original])

    label_reconstructed = widgets.Label(
        value=f"{title} (reconstructed)",
        layout=Layout(width="100%", display="flex", justify_content="center"),
    )

    audio_player_reconstructed = Audio(
        one_period_audio_data_reconstructed, rate=sample_rate
    )
    output_widget_reconstructed = widgets.Output()

    with output_widget_reconstructed:
        display(audio_player_reconstructed)

    combined_widget_reconstructed = widgets.VBox(
        [label_reconstructed, output_widget_reconstructed]
    )

    row = widgets.HBox([combined_widget_original, combined_widget_reconstructed])
    rows.append(row)


def display_reconstructed_and_original_audio(
    files, reconstructed_signals, one_period_signals, sample_rates
):
    """
    Display widgets for playing original and reconstructed audio.

    Function generates a graphical user interface (GUI) that allows the user
    to select files and play their original and reconstructed audio. The GUI
    also allows the user to export reconstructed audio to a predefined directory.

    Args:
        files (list): List of audio file paths.
        reconstructed_signals (list): List of reconstructed audio signals.
        one_period_signals (list): List of one-period audio signals.
        sample_rates (list): List of sample rates for audio files.

    Returns:
        None
    """

    audio_file_names = _get_audiofile_names(files)
    checkboxes, checkbox_layout = gfcu.prepare_checkbox_grid(audio_file_names)
    checkbox_grid = widgets.GridBox(checkboxes, layout=checkbox_layout)

    # Prepare buttons
    buttons_panel = _PrepareButtonsDisplayAudio()
    (
        display_audio_button,
        toggle_all_button,
        save_selected_button,
    ) = buttons_panel.get_buttons()
    button_container = buttons_panel.get_container()

    display(checkbox_grid, button_container)

    def _display_audio(_):
        clear_output(wait=True)  # unique output
        display(checkbox_grid, button_container)  # unique output

        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        period_bounds = list(pb.PERIOD_BOUNDS.values())
        rows = []
        for idx in selected_indices:
            _draw_play_audio_buttons(
                idx,
                audio_file_names,
                period_bounds,
                sample_rates,
                one_period_signals,
                reconstructed_signals,
                rows,
            )

        display(widgets.VBox(rows))

    display_audio_button.on_click(_display_audio)

    toggle_all_button.on_click(partial(gfcu.toggle_all, checkboxes))

    def _save_selected_button(_):
        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        period_bounds = list(pb.PERIOD_BOUNDS.values())
        output_directory = os.path.join(
            cfg.PATH_RESULTS, "one_period_reconstructed_audio"
        )

        print(
            f'Exporting reconstructed audio to ".{output_directory[len(cfg.PATH_BASE):]}'
        )
        for idx in selected_indices:
            name = audio_file_names[idx]
            duration = period_bounds[idx][1] - period_bounds[idx][0]
            sample_rate = sample_rates[idx]

            one_period_audio_data_reconstructed = np.tile(
                reconstructed_signals[idx], int(1 / duration)
            )

            wavfile.write(
                f"{output_directory}/{name}_reconstructed.wav",
                sample_rate,
                one_period_audio_data_reconstructed,
            )

    save_selected_button.on_click(_save_selected_button)
