import ipywidgets as widgets
from IPython.display import display, clear_output
from functools import partial
from utils import general_functions_utils as gfu
from settings import period_bounds as pb


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


def _prepare_buttons():
    """
    Prepare a set of buttons and a button container.

    The function creates "Print function" and "Toggle All" buttons The buttons are
    then placed in a horizontal container at the bottom of the window.

    Returns:
        tuple: A tuple containing the individual buttons and a container holding them.
    """

    display_function_button = widgets.Button(description="Display Function")
    toggle_all_button = widgets.Button(description="Toggle All")
    button_container = widgets.HBox(
        [
            display_function_button,
            toggle_all_button,
        ]
    )

    return (
        display_function_button,
        toggle_all_button,
        button_container,
    )


def print_mathematical_representation_of_signal(
    files, mathematical_representation_of_signal_per_instrument
):
    audio_file_names = _get_audiofile_names(files)
    checkboxes, checkbox_layout = gfu.prepare_checkbox_grid(audio_file_names)
    checkbox_grid = widgets.GridBox(checkboxes, layout=checkbox_layout)

    (
        display_function_button,
        toggle_all_button,
        button_container,
    ) = _prepare_buttons()

    display(checkbox_grid, button_container)

    def _display_function(_):
        clear_output(wait=True)  # unique output
        display(checkbox_grid, button_container)  # unique output

        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        sound_periods = [end - start for start, end in pb.PERIOD_BOUNDS.values()]
        sound_frequencies = [1 / period for period in sound_periods]

        for i, idx in enumerate(selected_indices):
            print(
                f"Instrument: {audio_file_names[idx]} ({sound_frequencies[idx]:.2f} Hz)"
            )
            print(mathematical_representation_of_signal_per_instrument[idx])

    display_function_button.on_click(_display_function)

    toggle_all_button.on_click(partial(gfu.toggle_all, checkboxes))
