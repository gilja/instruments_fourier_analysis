"""
general_display_utils:
======================

A module containing general display utility functions and classes used in the project.
It provides a simple GUI that allows the user to select an audio file(s) and obtain insights
such as a mathematical representation of the reconstructed signal, reconstructed audio,
and the power spectra of harmonics present in the signal.

Public functions:
-----------------

-   print_mathematical_representation_of_signal: Displays a mathematical representation
    of the reconstructed audio signals for selected audio files.
-   display_reconstructed_and_original_audio: Displays widgets for playing original and
    reconstructed 1-period audios.
-   draw_harmonics_power_spectra: Displays power spectra for the selected audio file(s)
    and exports them to a PDF.
-   plot_individual_harmonics: Plots individual harmonics for selected audio file(s) and
    export them to a PDF.

Private functions:
------------------

-   _draw_play_audio_buttons: Draws widgets for playing the original and the reconstructed
    audio. Used in display_reconstructed_and_original_audio.
-   _draw_joined_plotter_function: Generates a Plotly figure with joined power spectra for
    selected audio files. Used in draw_harmonics_power_spectra.
-   _daw_individual_plotter_function: Generates a Plotly figure with individual power spectra
    for selected audio files. Used in draw_harmonics_power_spectra.
-   _get_null_points: Finds null points of a function. Used in plot_individual_harmonics.
-   _get_numerical_values_from_term: Uses a sympy library to convert a given term to numerical
    values for plotting. Used in plot_individual_harmonics.
-   _add_harmonic_to_plot: Adds a single harmonic to a Plotly figure. Used in
    plot_individual_harmonics.
-   _update_plot_layout: Updates the layout of a Plotly figure. Used in plot_individual_harmonics.
-   _get_y_axis_range: Calculates the Y-axis range for all harmonics. Used in
    plot_individual_harmonics.

Classes:
--------
-   _PrepareButtonsMathematicalRepresentation:
        *   A subclass of the ButtonPanel class defined in general_functions_and_classes_utils.
        *   Used in print_mathematical_representation_of_signal function.
-   _PrepareButtonsDisplayAudio:
        *   A subclass of the ButtonPanel class defined in general_functions_and_classes_utils.
        *   Used in display_reconstructed_and_original_audio function.
-   _PrepareButtonsPowerSpectra:
        *   A subclass of the ButtonPanel class defined in general_functions_and_classes_utils.
        *   Used in draw_harmonics_power_spectra function.

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
from functools import partial
import ipywidgets as widgets
from IPython.display import Audio, display, clear_output
from ipywidgets import Layout
import numpy as np
from scipy.io import wavfile
import plotly.graph_objs as go
import sympy
from utils import general_functions_and_classes_utils as gfcu
from settings import period_bounds as pb
from settings import config as cfg


class _PrepareButtonsMathematicalRepresentation(gfcu.ButtonPanel):
    """
    A subclass of the ButtonPanel class used for creating a panel with "Toggle All"
    and "Display Function" buttons. Used in print_mathematical_representation_of_signal
    function.
    """

    def __init__(self):
        """
        Initializes _PrepareButtonsMathematicalRepresentation with predefined buttons.
        """
        super().__init__(["Toggle All", "Display Function"])


def print_mathematical_representation_of_signal(
    files, mathematical_representation_of_signal_per_instrument
):
    """
    Displays a mathematical representation of the reconstructed audio signals
    for selected audio files.

    The function generates a graphical user interface (GUI) that allows a user
    to select audio files and view the mathematical representations of reconstructed
    signal for selected audio files.

    Buttons:

    -   Toggle All: Toggles all checkboxes on or off. Off by default.
    -   Display Function: Displays the mathematical representation of the
        reconstructed signal for the selected audio file(s).

    Args:
        files (list):
            -   A list of audio file paths.

        mathematical_representation_of_signal_per_instrument (list):
            -   A list of mathematical representations for each audio file.

    Returns:
        None
    """

    audio_file_names = gfcu.get_names(files)
    checkboxes, checkbox_layout = gfcu.prepare_checkbox_grid(audio_file_names)
    checkbox_grid = widgets.GridBox(checkboxes, layout=checkbox_layout)

    # Prepare buttons
    buttons_panel = _PrepareButtonsMathematicalRepresentation()
    toggle_all_button, display_function_button = buttons_panel.get_buttons()
    button_container = buttons_panel.get_container()

    display(checkbox_grid, button_container)

    toggle_all_button.on_click(partial(gfcu.toggle_all, checkboxes))

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


class _PrepareButtonsDisplayAudio(gfcu.ButtonPanel):
    """
    A subclass of the ButtonPanel class used for creating a panel with "Toggle All",
    "Display Audio" and "Save Selected Reconstructed" buttons. Used in
    display_reconstructed_and_original_audio function.
    """

    def __init__(self):
        """
        Initializes _PrepareButtonsDisplayAudio with predefined buttons.
        """
        super().__init__(
            [
                "Toggle All",
                "Display Audio Widgets",
                "Save Selected Reconstructed",
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
    Draws widgets for playing the original and the reconstructed audio.

    The function generates widgets to play the original and reconstructed audio
    for a selected audio file(s). It creates Audio widgets for both audio signals
    and adds labels to identify them. These widgets are then combined into a
    horizontal layout. Depending on the number of the selected audio files, the
    function may add multiple rows of widgets. The function is used in the
    display_reconstructed_and_original_audio function.

    Args:
        idx (int):
            -   The index of the selected audio file.

        audio_file_names (list):
            -   Audio file names.

        period_bounds (list):
            -   Period bounds for audio files.

        sample_rates (list):
            -   Sample rates for audio files.

        one_period_signals (list):
            -   1-period audio signals.

        reconstructed_signals (list):
            -   Reconstructed audio signals.

        rows (list):
            -   Rows to which the widgets are added.

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
    Displays widgets for playing original and reconstructed 1-period audios.

    The function generates a graphical user interface (GUI) that allows the user
    to select files and play their original and reconstructed audio. The GUI
    also allows the user to export reconstructed audio files in WAV format.

    Buttons:

    -   Toggle All: Toggles all checkboxes on or off. Off by default.
    -   Display Audio Widgets: Displays widgets for playing the original and the
        reconstructed audio for the selected audio file(s).
    -   Save Selected Reconstructed: Saves the reconstructed audio for the selected
        audio file(s) in WAV format.

    Args:
        files (list):
            -   Audio file paths. Full paths to the files are expected.

        reconstructed_signals (list):
            -   Reconstructed audio signals.

        one_period_signals (list):
            -   1-period audio signals.

        sample_rates (list):
            -   Sample rates for audio files.

    Returns:
        None
    """

    audio_file_names = gfcu.get_names(files)
    checkboxes, checkbox_layout = gfcu.prepare_checkbox_grid(audio_file_names)
    checkbox_grid = widgets.GridBox(checkboxes, layout=checkbox_layout)

    # Prepare buttons
    buttons_panel = _PrepareButtonsDisplayAudio()
    (
        toggle_all_button,
        display_audio_button,
        save_selected_button,
    ) = buttons_panel.get_buttons()
    button_container = buttons_panel.get_container()

    display(checkbox_grid, button_container)

    toggle_all_button.on_click(partial(gfcu.toggle_all, checkboxes))

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

    def _save_selected_button(_):
        clear_output(wait=True)  # unique output
        display(checkbox_grid, button_container)  # unique output

        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        period_bounds = list(pb.PERIOD_BOUNDS.values())
        output_directory = os.path.join(
            cfg.PATH_RESULTS, "reconstructed_one_period_audio/"
        )

        for idx in selected_indices:
            name = audio_file_names[idx]
            duration = period_bounds[idx][1] - period_bounds[idx][0]
            sample_rate = sample_rates[idx]

            one_period_audio_data_reconstructed = np.tile(
                reconstructed_signals[idx], int(1 / duration)
            )

            # Save the WAV file
            audio_path = os.path.join(output_directory, f"{name}.wav")

            wavfile.write(
                audio_path,
                sample_rate,
                one_period_audio_data_reconstructed,
            )

        print(
            f'Exported reconstructed audio to ".{output_directory[len(cfg.PATH_BASE):]}'
        )

    save_selected_button.on_click(_save_selected_button)


class _PrepareButtonsPowerSpectra(gfcu.ButtonPanel):
    """
    A subclass of the ButtonPanel class used for creating a panel with "Toggle All",
    "Plot Joined", "Plot Individual", "Save Joined" and "Save Individual" buttons.
    Used in draw_harmonics_power_spectra function.
    """

    def __init__(self):
        """
        Initializes _PrepareButtonsPowerSpectra with predefined buttons.
        """
        super().__init__(
            [
                "Toggle All",
                "Plot Selected Grouped",
                "Plot Selected Individually",
                "Save Selected Grouped",
                "Save Selected Individually",
            ]
        )


def _draw_joined_plotter_function(
    fig, selected_indices, relative_harmonic_powers_per_instrument, audio_file_names
):
    """
    Generates a Plotly figure with joined power spectra for selected
    audio files. The function is used in the draw_harmonics_power_spectra function.

    Args:
        fig (plotly.graph_objs.Figure):
            -   The Plotly figure to export.ž

        selected_indices (list):
            -   Indices of selected audio files.

        relative_harmonic_powers_per_instrument (list):
            -   Relative harmonic powers for each audio file.

        audio_file_names (list):
            -   Audio file names.

    Returns:
        None
    """

    for idx in selected_indices:
        relative_powers = relative_harmonic_powers_per_instrument[idx] * 100
        harmonic_order = list(range(1, len(relative_powers) + 1))

        fig.add_trace(
            go.Bar(
                x=harmonic_order,
                y=relative_powers,
                name=f"{audio_file_names[idx]}",
            )
        )
        fig.update_layout(
            title_text="Harmonic Power Spectrum",
            title_x=0.5,
            xaxis_title="Order of harmonic",
            yaxis_title="Relative Power",
        )


def _find_closest_note_name(frequency):
    """
    Finds the closest note name for a given frequency.

    The function uses the NOTE_FREQUENCIES dictionary from the config file to
    map the frequency to the closest note name.

    Args:
        frequency (float):
            -   The frequency for which the closest note name is found.

    Returns:
        -   str: The closest note name.
    """

    closest_note = min(cfg.NOTE_FREQUENCIES, key=lambda note: abs(note - frequency))
    return cfg.NOTE_FREQUENCIES[closest_note]


def _daw_individual_plotter_function(
    idx, relative_harmonic_powers_per_instrument, audio_file_names
):
    """
    Generates a Plotly figure with individual power spectra for selected
    audio files.

    The function calculates the relative power of each harmonic (expressed
    in %) and finds the fundamental frequency for the selected audio file
    using the period bounds from the config file.
    It then calculates the frequencies of each harmonic and finds the
    closest note name for each harmonic. The function uses the calculated
    frequencies and note names to create a custom label for each bar in the
    plot.
    The function is used in the draw_harmonics_power_spectra function.

    Args:
        idx (int):
            -   The index of the selected audio file.

        relative_harmonic_powers_per_instrument (list):
            -   Relative harmonic powers for each audio file.

        audio_file_names (list):
            -   Audio file names.

    Returns:
        None
    """

    relative_powers = relative_harmonic_powers_per_instrument[idx] * 100
    harmonic_order = list(range(1, len(relative_powers) + 1))

    # Calculate sound periods and frequencies for the fundamental frequency of each instrument
    sound_periods = [end - start for start, end in pb.PERIOD_BOUNDS.values()]
    sound_frequencies = [1 / period for period in sound_periods]

    # Get the fundamental frequency for the current instrument
    fundamental_frequency = sound_frequencies[idx]

    # Calculate frequencies of each harmonic for the current instrument
    frequencies = [fundamental_frequency * n for n in harmonic_order]
    # Find the closest note name for each frequency
    note_labels = [_find_closest_note_name(freq) for freq in frequencies]

    # Pair the frequency and note label for each bar
    custom_label = [
        {"frequency": f"{freq:.2f} Hz", "note": note}
        for freq, note in zip(frequencies, note_labels)
    ]

    # Create a new figure for each selected checkbox
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=harmonic_order,
            y=relative_powers,
            name=f"Harmonic power spectrum for {audio_file_names[idx]}",
            text=note_labels,
            customdata=custom_label,
            hovertemplate=(
                "Harmonic Order: %{x}<br>"
                "Relative Power: %{y:.2f}%<br>"
                "Frequency: %{customdata.frequency}<br>"
                "Note: %{customdata.note}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title={
            "text": f"Harmonic Power Spectrum for {audio_file_names[idx]}",
            "x": 0.5,  # Set to 0.5 for center alignment horizontally
        },
        xaxis_title="Order of harmonic",
        yaxis_title="Relative Power",
    )

    return fig


def draw_harmonics_power_spectra(files, relative_harmonic_powers_per_instrument):
    """
    Displays power spectra for the selected audio file(s) and exports them to a PDF.

    The function generates a GUI that allows the user to select files and view their
    power spectra. The GUI also allows the user to export the power spectra to PDF.
    This can be done for all selected files together, drawing them on the same figure
    as a grouped bar plot, or for each file individually, drawing them on separate
    figures. If plotted individually, the function also displays the fundamental
    frequency and the closest note name for each harmonic on hover as well as the note
    name on top of each bar.

    Buttons:

    -   Toggle All: Toggles all checkboxes on or off. Off by default.
    -   Plot Selected Grouped: Plots the power spectra for the selected audio files
        on the same figure as a grouped bar plot.
    -   Plot Selected Individually: Plots the power spectra for the selected audio file(s)
        on separate figures.
    -   Save Selected Grouped: Saves the power spectra for the selected audio files
        to a single PDF file as a grouped bar plot.
    -   Save Selected Individually: Saves the power spectra for the selected audio file(s)
        as separate PDF files.

    Args:
        files (list):
            -   A list of audio file paths. Full paths to the files are expected.

        relative_harmonic_powers_per_instrument (list):
            -   A list of relative harmonic powers for each audio file.

    Returns:
        None
    """

    audio_file_names = gfcu.get_names(files)
    checkboxes, checkbox_layout = gfcu.prepare_checkbox_grid(audio_file_names)
    checkbox_grid = widgets.GridBox(checkboxes, layout=checkbox_layout)

    # Prepare buttons
    buttons_panel = _PrepareButtonsPowerSpectra()
    (
        toggle_all_button,
        plot_joined_button,
        plot_individual_button,
        save_joined_button,
        save_individual_button,
    ) = buttons_panel.get_buttons()
    button_container = buttons_panel.get_container()

    display(checkbox_grid, button_container)

    toggle_all_button.on_click(partial(gfcu.toggle_all, checkboxes))

    def _draw_joined(_):
        clear_output(wait=True)  # unique output
        display(checkbox_grid, button_container)  # unique output

        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        fig = go.Figure()

        _draw_joined_plotter_function(
            fig,
            selected_indices,
            relative_harmonic_powers_per_instrument,
            audio_file_names,
        )

        fig.show()

    plot_joined_button.on_click(_draw_joined)

    def _draw_individual(_):
        clear_output(wait=True)  # unique output
        display(checkbox_grid, button_container)  # unique output

        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        for idx in selected_indices:
            fig = _daw_individual_plotter_function(
                idx,
                relative_harmonic_powers_per_instrument,
                audio_file_names,
            )

            fig.show()

    plot_individual_button.on_click(_draw_individual)

    def _save_joined(_):
        clear_output(wait=True)  # unique output
        display(checkbox_grid, button_container)  # unique output

        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        fig = go.Figure()

        _draw_joined_plotter_function(
            fig,
            selected_indices,
            relative_harmonic_powers_per_instrument,
            audio_file_names,
        )

        # Save the plot to PDF
        name = ""
        for idx in selected_indices:
            name += f"{audio_file_names[idx]}_"
        name = name[:-1]  # remove last underscore

        save_path = os.path.join(cfg.PATH_RESULTS, "power_spectra/")
        pdf_path = os.path.join(save_path, f"waveform_{name}.pdf")

        gfcu.export_to_pdf(
            fig, n_rows=2, pdf_path=pdf_path
        )  # n_rows=2 to modify plot size

        print(
            f"Saved joined plot to .{save_path[len(cfg.PATH_BASE):]}"
        )  # print relative path

    save_joined_button.on_click(_save_joined)

    def _save_individual(_):
        clear_output(wait=True)  # unique output
        display(checkbox_grid, button_container)  # unique output

        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        for idx in selected_indices:
            fig = _daw_individual_plotter_function(
                idx,
                relative_harmonic_powers_per_instrument,
                audio_file_names,
            )

            # Save the plot to PDF
            name = audio_file_names[idx]

            save_path = os.path.join(cfg.PATH_RESULTS, "power_spectra/")
            pdf_path = os.path.join(save_path, f"waveform_{name}.pdf")

            gfcu.export_to_pdf(
                fig, n_rows=2, pdf_path=pdf_path
            )  # n_rows=2 to modify plot size

            print(
                f"Saved individual plots to .{save_path[len(cfg.PATH_BASE):]}"
            )  # print relative path

    save_individual_button.on_click(_save_individual)


class _PrepareButtonsDrawIndividualHarmonics(gfcu.ButtonPanel):
    """
    A subclass of the ButtonPanel class used for creating a panel with "Toggle All",
    "Plot harmonics", "Save Joined" and "Save Individual" buttons.
    Used in plot_individual_harmonics function.
    """

    def __init__(self):
        """
        Initializes _PrepareButtonsDrawIndividualHarmonics with predefined buttons.
        """
        super().__init__(
            [
                "Toggle All",
                "Plot Harmonics",
                "Save Selected Plots",
                "Save Individual Harmonics Separately",
            ]
        )


def _get_null_points(grouped_terms):
    """
    Finds null points of a function.

    The function finds the null points of a function using sympy library.
    The null points are used to define the range of t values (x-axis) for
    which the function is plotted.
    Only the null points of the first harmonic are used to define the range
    since the first harmonic has the largest period by definition. By finding
    the proper range for the first harmonic, the proper range for all other
    harmonics is also defined.

    Args:
        grouped_terms (list):
            -   All the harmonics in the sound.

    Returns:
        null_points (list): Null points.
    """

    # Find the null points of the first harmonic. Other harmonics
    #
    term = "".join(grouped_terms[0])
    # parse the function string using sympy
    t = sympy.symbols("t")
    f = sympy.sympify(term)

    # Find the null points
    null_points = sympy.solve(f, t)

    # Convert null points to floats
    null_points = [float(point) for point in null_points]

    if len(null_points) < 2:
        print("Warning: Not enough null points found. Using default range ([0, 20]).")
        null_points = [0, 10]

    return null_points


def _get_numerical_values_from_term(term, t_min, t_max):
    """
    Uses a sympy library to convert a given term to numerical values for plotting.

    The function joins the term (list of strings) into a single string and parses
    the function string using sympy. It then creates a list of t values within the
    specified range and evaluates the function for each value of t.
    Used in plot_individual_harmonics function.

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

        t_min (float):
            -   The minimum value of t for which the function is plotted.

        t_max (float):
            -   The maximum value of t for which the function is plotted.


    Returns:
        tuple of (list, list)
        -   A tuple containing two elements:
            *   t_values (list): Numerical values representing time coordinates.
            *   y_values (list): Values of the function for each time coordinate.
    """

    # join the terms into a single string
    term = "".join(term)

    # parse the function string using sympy
    t = sympy.symbols("t")
    f = sympy.sympify(term)

    # create a list of t values within the specified range
    t_values = np.linspace(t_min, t_max, 1000)

    # evaluate the function for each value of t
    y_values = [float(f.evalf(subs={t: value})) for value in t_values]

    return t_values, y_values


def _add_harmonic_to_plot(fig, t_values, y_values, name):
    """
    Adds a single harmonic to a Plotly figure. Used in plot_individual_harmonics

    Args:
        fig (plotly.graph_objs.Figure):
            -   The Plotly figure to export.

        t_values (list):
            -   Numerical values representing time coordinates.

        y_values (list):
            -   Values of the function for each time coordinate.

        name (str):
            -   Name shown in the legend.

    Returns:
        None
    """

    fig.add_trace(
        go.Scatter(
            x=t_values,
            y=y_values,
            mode="lines",  # Use "lines" mode for curves
            name=name,
            showlegend=True,  # To display the legend
        )
    )


def _update_plot_layout(fig, title, legend=True, y_range=None):
    """
    Updates the layout of a Plotly figure.

    This function updates the layout of a Plotly figure by setting the title,
    x-axis title, legend, and y-axis range. It is used in plot_individual_harmonics

    Args:
        fig (plotly.graph_objs.Figure):
            -   The Plotly figure to export.

        title (str):
            -   The title of the figure.

        legend (bool, optional):
            -   To display the legend.

        y_range (list, optional):
            -   Y-axis range.

    Returns:
        None
    """

    layout = {
        "title": {"text": title, "x": 0.5},  # Title settings
        "xaxis_title": "t",  # X-axis title
        "showlegend": legend,  # To display the legend
    }

    if y_range is not None:
        layout["yaxis"] = {"range": y_range}  # Y-axis range

    fig.update_layout(layout)


def _get_y_axis_range(grouped_terms, t_min, t_max):
    """
    Calculates the Y-axis range for all harmonics.

    The function calculates the maximum value of a function for all harmonics and
    adds a margin to it. The margin is defined in the config file. It is used in
    plot_individual_harmonics to set the same y-axis range for all plots.

    Args:
        grouped_terms (list):
            -   All the harmonics in the sound.

        t_min (float):
            -   The minimum value of t for which the function is plotted.

        t_max (float):
            -   The maximum value of t for which the function is plotted.

    Returns:
        max_y_value (float): The maximum value of y for all harmonics plus a margin.
    """

    max_y_per_harmonic = []
    for term in grouped_terms:
        _, y_values = _get_numerical_values_from_term(term, t_min, t_max)
        max_y_per_harmonic.append(max(y_values))

    return max(max_y_per_harmonic) * cfg.Y_AXIS_MARGIN


def plot_individual_harmonics(
    files, mathematical_representation_of_signal_per_instrument
):
    """
    Plots individual harmonics for selected audio file(s) and export them to a PDF.

    The function generates a GUI that allows the user to select audio file(s) and
    plot individual harmonics. The GUI also allows a user to export the plots as a
    PDF. The user can choose to draw all harmonics for the selected audio file(s)
    in a single plot or to draw each harmonic in a separate plot.

    Buttons:

    -   Toggle All: Toggles all checkboxes on or off. Off by default.
    -   Plot Harmonics: Plots individual harmonics for the selected audio file(s).
        All harmonics are plotted on the same figure for each selected audio file.
    -   Save Selected Plots: Saves the plots for the selected audio file(s) to
        separate PDF files. Each PDF file contains a plot with all harmonics.
    -   Save Individual Harmonics Separately: Saves the individual harmonics for
        the selected audio file(s) as separate PDF files.

    Args:
        files (list of str):
            -   A list of strings representing the file paths to the audio files.
                Absolute paths are recommended as they are used throughout the
                tool.

        mathematical_representation_of_signal_per_instrument (list):
            -   2D list of mathematical representations of the signal for each instrument.
                Each element of this list is another list that stores the mathematical
                representation of the signal for one instrument (recording). The structure
                of the inner list is as follows:
                * First element: average term, a term with cos, and a term with sin.
                * All other elements: a term with cos and a term with sin.

    Returns:
        None
    """

    audio_file_names = gfcu.get_names(files)
    checkboxes, checkbox_layout = gfcu.prepare_checkbox_grid(audio_file_names)
    checkbox_grid = widgets.GridBox(checkboxes, layout=checkbox_layout)

    # Prepare buttons
    buttons_panel = _PrepareButtonsDrawIndividualHarmonics()
    (
        toggle_all_button,
        plot_harmonics_button,
        save_joined_button,
        save_individual_button,
    ) = buttons_panel.get_buttons()
    button_container = buttons_panel.get_container()

    display(checkbox_grid, button_container)

    toggle_all_button.on_click(partial(gfcu.toggle_all, checkboxes))

    def _plot_harmonics(_, save=False):
        clear_output(wait=True)  # unique output
        display(checkbox_grid, button_container)  # unique output

        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        for idx in selected_indices:
            print("Preparing the plot. Please wait...")

            fig = go.Figure()
            terms = gfcu.get_individual_terms(
                mathematical_representation_of_signal_per_instrument[idx]
            )

            grouped_terms = gfcu.get_grouped_terms(terms)

            # defining the range of the x-axis
            null_points = _get_null_points(grouped_terms)
            t_min = null_points[0]
            t_max = t_min + 2 * (null_points[1] - null_points[0])  # get 1 period

            for n, term in enumerate(grouped_terms):
                t_values, y_values = _get_numerical_values_from_term(term, t_min, t_max)

                if n == 0:
                    name = "Constant + 1st harmonic"
                else:
                    name = f"{n+1}th harmonic"

                _add_harmonic_to_plot(fig, t_values, y_values, name)

            title = f"Harmonic content for {audio_file_names[idx]}"
            _update_plot_layout(fig, title)

            if not save:
                fig.show()

            if save:
                # Save the plot to PDF
                name = audio_file_names[idx]

                save_path = os.path.join(cfg.PATH_RESULTS, "harmonics_function_plots/")
                pdf_path = os.path.join(save_path, f"harmonics_{name}.pdf")

                gfcu.export_to_pdf(
                    fig, n_rows=2, pdf_path=pdf_path
                )  # n_rows=2 to modify plot size

                print(
                    f"Saved joined plot to .{save_path[len(cfg.PATH_BASE):]}"
                )  # print relative path

    plot_harmonics_button.on_click(_plot_harmonics)

    save_joined_button.on_click(partial(_plot_harmonics, save=True))

    def _save_individual(_):
        clear_output(wait=True)  # unique output
        display(checkbox_grid, button_container)  # unique output

        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        for idx in selected_indices:
            print("Preparing plots. Please wait...")
            terms = gfcu.get_individual_terms(
                mathematical_representation_of_signal_per_instrument[idx]
            )

            grouped_terms = gfcu.get_grouped_terms(terms)

            null_points = _get_null_points(grouped_terms)
            # defining the range of the x-axis
            t_min = null_points[0]
            t_max = t_min + 2 * (null_points[1] - null_points[0])  # get 1 period

            # max y value for all plots
            max_y_value = _get_y_axis_range(grouped_terms, t_min, t_max)

            for n, term in enumerate(grouped_terms):
                fig = go.Figure()
                t_values, y_values = _get_numerical_values_from_term(term, t_min, t_max)

                if n == 0:
                    name = "Constant + 1st harmonic"
                else:
                    name = f"{n+1}th harmonic"

                _add_harmonic_to_plot(fig, t_values, y_values, name)

                title = f"{name} for {audio_file_names[idx]}"
                y_range = [-max_y_value, max_y_value]

                _update_plot_layout(fig, title, legend=False, y_range=y_range)

                # Save the plot to PDF
                name = f"{audio_file_names[idx]}_{str(n + 1)}th_harmonic"

                save_path = os.path.join(cfg.PATH_RESULTS, "harmonics_function_plots/")
                pdf_path = os.path.join(save_path, f"{name}.pdf")

                gfcu.export_to_pdf(
                    fig, n_rows=2, pdf_path=pdf_path
                )  # n_rows=2 to modify plot size

                print(
                    f"Saved individual plots to .{save_path[len(cfg.PATH_BASE):]}"
                )  # print relative path

    save_individual_button.on_click(_save_individual)
