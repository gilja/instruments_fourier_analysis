import ipywidgets as widgets
from IPython.display import Audio, display, clear_output
from ipywidgets import Layout
from functools import partial
import numpy as np
import os
from scipy.io import wavfile
import plotly.graph_objs as go
import re
import sympy
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


class _PrepareButtonsPowerSpectra(gfcu.ButtonPanel):
    """
    Subclass of a ButtonPanel class used for creating a panel with "Plot Joined",
    "Plot Individual", "Toggle All", "Save Joined" and "Save Individual" buttons.
    Used in draw_harmonics_power_spectra function.
    """

    def __init__(self):
        """
        Initializes _PrepareButtonsPowerSpectra with predefined buttons.
        """
        super().__init__(
            [
                "Plot Joined",
                "Plot Individual",
                "Toggle All",
                "Save Joined",
                "Save Individual",
            ]
        )


def _draw_joined_plotter_function(
    fig, selected_indices, relative_harmonic_powers_per_instrument, audio_file_names
):
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
            title={
                "text": "Harmonic Power Spectrum",
                "x": 0.5,  # Set to 0.5 for center alignment horizontally
            },
            xaxis_title="Order of harmonic",
            yaxis_title="Relative Power",
        )


def _daw_individual_plotter_function(
    idx, relative_harmonic_powers_per_instrument, audio_file_names
):
    relative_powers = relative_harmonic_powers_per_instrument[idx] * 100
    harmonic_order = list(range(1, len(relative_powers) + 1))

    # Create a new figure for each selected checkbox
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=harmonic_order,
            y=relative_powers,
            name=f"Harmonic power spectrum for {audio_file_names[idx]}",
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
    audio_file_names = _get_audiofile_names(files)
    checkboxes, checkbox_layout = gfcu.prepare_checkbox_grid(audio_file_names)
    checkbox_grid = widgets.GridBox(checkboxes, layout=checkbox_layout)

    # Prepare buttons
    buttons_panel = _PrepareButtonsPowerSpectra()
    (
        plot_joined_button,
        plot_individual_button,
        toggle_all_button,
        save_joined_button,
        save_individual_button,
    ) = buttons_panel.get_buttons()
    button_container = buttons_panel.get_container()

    display(checkbox_grid, button_container)

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

    toggle_all_button.on_click(partial(gfcu.toggle_all, checkboxes))

    def _save_joined(_):
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

        pdf_path = os.path.join(cfg.PATH_RESULTS, "power_spectra/")
        gfcu.export_to_pdf(
            fig, n_rows=2, pdf_path=pdf_path + name + ".pdf"
        )  # n_rows=2 to modify plot size

        print(
            f"Saved joined plot to .{pdf_path[len(cfg.PATH_BASE):]}"
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
            pdf_path = os.path.join(cfg.PATH_RESULTS, "power_spectra/")
            gfcu.export_to_pdf(
                fig, n_rows=2, pdf_path=pdf_path + name + ".pdf"
            )  # n_rows=2 to modify plot size

            print(
                f"Saved individual plot to .{pdf_path[len(cfg.PATH_BASE):]}"
            )  # print relative path

    save_individual_button.on_click(_save_individual)


class _PrepareButtonsDrawIndividualHarmonics(gfcu.ButtonPanel):
    """
    Subclass of a ButtonPanel class used for creating a panel with "Toggle All" and
    "Plot harmonics" buttos. Used in plot_individual_harmonics function.
    """

    def __init__(self):
        """
        Initializes _PrepareButtonsDrawIndividualHarmonics with predefined buttons.
        """
        super().__init__(
            [
                "Toggle All",
                "Plot Harmonics",
            ]
        )


def _get_individual_terms(mathematical_representation_of_signal):
    """
    Extract individual terms from a mathematical function representing the signal.

    Args:
        mathematical_representation_of_signal (str): A mathematical representation
            of a signal.

    Returns:
        terms (list): A list of individual terms.
    """

    terms = re.findall(
        r"[\+\-]?\s*\d+\.?\d*\*?[^+\-]+",
        mathematical_representation_of_signal,
    )
    terms = [t.rstrip() for t in terms]

    return terms


def _get_grouped_terms(terms):
    """
    Group terms by their harmonic order.

    Function groups the terms in the following way:

    1. The first term in the list is the constant term and
       is combined with the 2nd and the 3rd terms representing
       the first harmonic.
    2. The 4th and the 5th terms represent the second harmonic and
       are combined together.
    3. The 6th and the 7th terms represent the third harmonic and
       are combined together.

    The process is continued until all terms are grouped. The function
    returns a list of grouped terms. The grouped_terms list will contain
    three terms as the first element (constant and the first harmonic),
    two terms as the second element (second harmonic), two terms as the
    third element (third harmonic), etc.

    Args:
        terms (list): A list of individual terms.

    Returns:
        grouped_terms (list): A list of grouped terms.
    """

    grouped_terms = [terms[:3]]
    grouped_terms.extend(
        [terms[i : i + 2] for i in range(3, len(terms), 2)]  # noqa: E203
    )

    return grouped_terms


def _get_null_points(grouped_terms):
    """
    Find null points of a function.

    Function finds the null points of a sympy function. The null-points are
    used to define the range of t values for which the function is plotted.
    Only the null points of the first harmonic are used to define the range
    since the first harmonic has the largest period by definition. By finding
    the proper range for the first harmonic, the proper range for all other
    harmonics is also defined.

    Args:
        grouped_terms (list): A list functions representing individual harmonics.
                      Each element of the list is a string is a list of
                      strings representing individual terms.

    Returns:
        null_points (list): A list of null points.
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
    Function converts given term to numerical values for plotting. It returns a list
    of numerical values for t and y axes. The function is used in plot_individual_harmonics.

    Args:
        term (list): A list of strings representing individual harmonics. If the term
                     represents the first harmonic, the list will contain three strings
                     (constant, sine term, and cosine term). If the term represents any other
                     harmonic, the list will contain two strings (sine term and cosine term).
        t_min (float): The minimum value of t for which the function is plotted.
        t_max (float): The maximum value of t for which the function is plotted.


    Returns:
        t_values (list): A list of numerical values representing time coordinates.
        y_values (list): A list of numerical values representing values of the function for
                         each time coordinate.
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


def plot_individual_harmonics(
    files, mathematical_representation_of_signal_per_instrument
):
    audio_file_names = _get_audiofile_names(files)
    checkboxes, checkbox_layout = gfcu.prepare_checkbox_grid(audio_file_names)
    checkbox_grid = widgets.GridBox(checkboxes, layout=checkbox_layout)

    # Prepare buttons
    buttons_panel = _PrepareButtonsDrawIndividualHarmonics()
    (
        toggle_all_button,
        plot_harmonics_button,
    ) = buttons_panel.get_buttons()
    button_container = buttons_panel.get_container()

    display(checkbox_grid, button_container)

    def _plot_harmonics(_):
        clear_output(wait=True)  # unique output
        display(checkbox_grid, button_container)  # unique output

        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        for idx in selected_indices:
            fig = go.Figure()
            terms = _get_individual_terms(
                mathematical_representation_of_signal_per_instrument[idx]
            )

            grouped_terms = _get_grouped_terms(terms)

            null_points = _get_null_points(grouped_terms)
            # defining the range of the x-axis
            t_min = null_points[0]
            t_max = t_min + 2 * (null_points[1] - null_points[0])  # get 1 period

            for n, term in enumerate(grouped_terms):
                t_values, y_values = _get_numerical_values_from_term(term, t_min, t_max)

                if n == 0:
                    name = "Constant + 1st harmonic"
                else:
                    name = f"{n+1}th harmonic"
                fig.add_trace(
                    go.Scatter(
                        x=t_values,
                        y=y_values,
                        mode="lines",  # Use "lines" mode for curves
                        name=name,
                        showlegend=True,  # To display the legend
                    )
                )

            fig.update_layout(
                title={
                    "text": f"Harmonic content for {audio_file_names[idx]}",
                    "x": 0.5,  # Set to 0.5 for center alignment horizontally
                },
                xaxis_title="t",
                yaxis_title="y",
                showlegend=True,  # To display the legend
            )

            fig.show()

    plot_harmonics_button.on_click(_plot_harmonics)

    toggle_all_button.on_click(partial(gfcu.toggle_all, checkboxes))
