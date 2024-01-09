"""
waveform_plot_utils:
====================

The module contains utility functions for plotting and saving audio waveforms. It provides a simple
GUI that allows one to select an audio file(s) to analyze.

Public Functions:
-----------------

-   plot_waveform: Draws and saves waveform plots based on user selections.
-   draw_waveform_reconstruction_timeline: Draws the evolution of the waveform reconstruction for
    the selected audio file.

Private Functions:
------------------

-   _prepare_subplots: Prepares the subplots for plotting audio waveforms. Used in plot_waveform.
-   _draw_unzoomed_waveforms: Draws a full audio waveform on the left subplot of a figure. Used in
    plot_waveform.
-   _draw_zoomed_waveforms: Draws a zoomed-in waveform on the right subplot of a figure. Used in
    plot_waveform.
-   _update_plot: Updates the layout of a Plotly figure. Used in plot_waveform.
-   _add_harmonic_to_plot: Adds a single harmonic to the plot. Used in
    draw_waveform_reconstruction_timeline.

Classes:
--------
-   _PrepareButtonsWaveformsPlot:
        *   A subclass of the ButtonPanel class defined in general_functions_and_classes_utils.
        *   Used in plot_waveform function.
-   _PrepareButtonsReconstructionTimeline:
        *   A subclass of the ButtonPanel class defined in general_functions_and_classes_utils.
        *   Used in draw_waveform_reconstruction_timeline function.

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

import ipywidgets as widgets
from IPython.display import display, clear_output
from plotly.subplots import make_subplots
import numpy as np
import plotly.graph_objs as go
import os
from functools import partial
from settings import period_bounds as pb
from settings import config as cfg
from utils import general_functions_and_classes_utils as gfcu
from utils import fourier_math_utils as fmu


class _PrepareButtonsWaveformsPlot(gfcu.ButtonPanel):
    """
    A subclass of the ButtonPanel class used for creating a panel with "Toggle All",
    "Draw", "Save All", and "Save Individual" buttons. Used in plot_waveform function.
    """

    def __init__(self):
        """
        Initializes _PrepareButtonsWaveformsPlot with predefined buttons.
        """
        super().__init__(
            [
                "Toggle All",
                "Plot Waveforms",
                "Save Selected Together",
                "Save Selected Individually",
            ]
        )


def _prepare_subplots(plot_names, selected_indices, n_rows, name=None):
    """
    Prepares the subplots for plotting audio waveforms.

    The function prepares two subplots for each loaded sound. The left subplot
    contains the entire waveform, while the right subplot contains a zoomed-in
    portion of the waveform. Depending on the 'name' argument, the function will
    prepare either a single two-column figure with all plots together or a single
    two-column figure for a single sound.

    Args:
        plot_names (list):
            -   Plot names.

        selected_indices (list):
            -   Selected indices.

        n_rows (int):
            -   Number of rows for subplots.

        name (str, optional):
            -   The name for individual plot titles (default is None). If the
                name is not provided, the function creates a single figure
                with all plots together. If the name is provided, the function
                creates a figure with only one current plot.

    Returns: plotly.graph_objs.Figure: A Plotly figure object.

    Note:
        Vertical spacing between subplots has to be adjusted based on the number of
        rows. Otherwise, the spacing will diverge as the number of rows increases.
    """

    if not name:  # scenario: all plots together
        subplot_titles = [
            f"{plot_names[i]} waveform" for i in selected_indices for _ in (0, 1)
        ]
        fig = make_subplots(
            rows=n_rows,
            cols=2,
            subplot_titles=subplot_titles,
            horizontal_spacing=cfg.HSPACING,
            vertical_spacing=cfg.VSPACING / n_rows,
        )
    else:  # scenario: plots individually
        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=[
                f"{name} waveform",
                f"{name} waveform (zoomed)",
            ],
        )

    return fig


def _draw_unzoomed_waveforms(fig, sounds, row, idx):
    """
    Draws a full audio waveform on the left subplot of a figure.

    The function adds the full waveform plot to the specified row of a left subplot.
    It extracts the sound data and sample rate from the `sounds` list, generates time
    data for the x-axis in milliseconds, and plots the waveform.

    Args:
        fig (plotly.graph_objs.Figure):
            -   The Plotly figure to draw on.

        sounds (list):
            -   Sound data and sample rates.

        row (int):
            -   The row number of the subplot to draw on.

        idx (int):
            -   The index of the selected sound in the `sounds` list.

    Returns:
        None
    """

    wav, rate = sounds[idx]

    # Generate time data for the x-axis in milliseconds
    time_in_seconds = np.arange(0, len(wav)) / rate
    time_in_milliseconds = time_in_seconds * 1000

    fig.add_trace(
        go.Scatter(
            x=time_in_milliseconds,
            y=wav,
            mode="lines",
            showlegend=False,
        ),
        row=row,
        col=1,
    )

    # update x-axis labels
    fig.update_xaxes(title_text="t [ms]", row=row, col=1)


def _draw_zoomed_waveforms(fig, sounds, row, idx, mark_one_period=False):
    """
    Draws a zoomed-in waveform on the right subplot of a figure. Optionally, draws two
    vertical lines for marking the start and the end of one period.

    This function adds a zoomed-in waveform plot to the specified row of a right subplot.
    It extracts the sound data and sample rate from the `sounds` list, generates time
    data for the x-axis in milliseconds, calculates the zoomed portion indices, and plots
    the zoomed waveform. If the `mark_one_period` list is set to True, the function also
    draws two vertical lines for marking the start and end of one period.

    Args:
        fig (plotly.graph_objs.Figure):
            -   The Plotly figure to draw on.

        sounds (list):
            -   Sound data and sample rates.

        row (int):
            -   The row number of the subplot to draw on.

        idx (int):
            -   The index of the selected sound in the `sounds` list.

        mark_one_period (bool, optional):
            -   Whether to mark one period on the zoomed-in waveform
                plots (default is False).

    Returns:
        None
    """

    wav, rate = sounds[idx]
    zoom_percentage = cfg.WAVEFORM_ZOOM_PERCENTAGES[idx]

    # Generate time data for the x-axis in milliseconds
    time_in_seconds = np.arange(0, len(wav)) / rate
    time_in_milliseconds = time_in_seconds * 1000

    # Calculate the zoomed portion indices
    length = zoom_percentage * len(wav)
    start_index = int((0.5 - (zoom_percentage / 2)) * len(wav))
    end_index = int(start_index + length)

    fig.add_trace(
        go.Scatter(
            x=time_in_milliseconds[start_index:end_index],
            y=wav[start_index:end_index],
            mode="lines",
            showlegend=False,
        ),
        row=row,
        col=2,
    )

    # update x-axis labels
    fig.update_xaxes(title_text="t [ms]", row=row, col=2)

    # adding vertical lines for marking the start and end of the period
    if mark_one_period is True:
        bounds_list = list(pb.PERIOD_BOUNDS.values())
        x1, x2 = bounds_list[idx]  # bounds are in seconds, converted to ms below

        plot_x_min = time_in_milliseconds[start_index]
        plot_x_max = time_in_milliseconds[end_index]

        if plot_x_max - plot_x_min < (x2 - x1) * 1000:
            raise ValueError(
                f"Plot not showing entire period. Change zoom percentage for index {idx}."
            )

        if x2 * 1000 > plot_x_max or x1 * 1000 < plot_x_min:
            period = x2 - x1

            while x2 * 1000 > plot_x_max or x1 * 1000 < plot_x_min:
                x1 -= period
                x2 -= period

        fig.add_vline(
            x=x1 * 1000,
            row=row,
            col=2,
            line_color="black",
            line_dash="dash",
            line_width=2,
        )
        fig.add_vline(
            x=x2 * 1000,
            row=row,
            col=2,
            line_color="black",
            line_dash="dash",
            line_width=2,
        )


def _update_plot(fig, title, n_rows, legend=False):
    """
    Updates the layout of a Plotly figure.

    This function updates the layout of the specified Plotly figure by adjusting the
    height, width, title, and title position to accommodate the given number of rows
    for waveform plots.

    Args:
        fig (plotly.graph_objs.Figure):
            -   The Plotly figure to update.

        title (str):
            -   The title of the figure.

        n_rows (int):
            -   The number of rows for waveform plots.

        legend (bool, optional):
            -   Whether to show the legend (default is False).

    Returns:
        None
    """

    fig.update_layout(
        height=cfg.FIGURE_HEIGHT_PER_PLOT * n_rows,
        title_text=title,
        title_x=0.5,
        showlegend=legend,
    )


def plot_waveform(sounds, files, mark_one_period=False):
    """
    Draws and saves waveform plots based on user selections.

    The function creates an interactive visualization interface to display and
    save waveform plots. It takes a list of sound data and file names. Optionally,
    the user can provide a mark_one_period parameter to mark one period on the
    zoomed-in waveform plots.

    Buttons:

    -   Toggle All: Toggles all checkboxes.
    -   Plot Waveforms: Draws the selected waveforms. The left subplot contains the full
        waveform, while the right subplot contains a zoomed-in portion of the waveform.
    -   Save Selected Together: Saves the selected waveforms together in a single PDF file.
    -   Save Selected Individually: Saves the selected waveforms as separate PDF files.

    Args:
        sounds (list):
            -   Sound data and sample rates.

        zoom_percentages (list):
            -   Zoom percentages for each waveform.
                    *   This is defined in the config file.

        files (list):
            -   Input filenames.

        mark_one_period (bool, optional):
            -   Whether to mark one period on the zoomed-in waveform plots
                (default is False).

    Returns:
        None
    """

    plot_names = gfcu.get_names(files)

    checkboxes, checkbox_layout = gfcu.prepare_checkbox_grid(plot_names)
    checkbox_grid = widgets.GridBox(checkboxes, layout=checkbox_layout)

    # prepare buttons
    buttons_panel = _PrepareButtonsWaveformsPlot()
    (
        toggle_all_button,
        draw_button,
        save_all_button,
        save_individual_button,
    ) = buttons_panel.get_buttons()
    button_container = buttons_panel.get_container()

    display(checkbox_grid, button_container)

    toggle_all_button.on_click(partial(gfcu.toggle_all, checkboxes))

    def _draw_plot(_):
        clear_output(wait=True)  # unique output
        display(checkbox_grid, button_container)  # unique output

        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        fig = _prepare_subplots(
            plot_names, selected_indices, n_rows=len(selected_indices)
        )

        for i, idx in enumerate(selected_indices):
            _draw_unzoomed_waveforms(fig, sounds, row=i + 1, idx=idx)
            if mark_one_period is True:
                _draw_zoomed_waveforms(
                    fig,
                    sounds,
                    row=i + 1,
                    idx=idx,
                    mark_one_period=mark_one_period,
                )
            else:
                _draw_zoomed_waveforms(fig, sounds, row=i + 1, idx=idx)

        _update_plot(fig, title="Waveform Plots", n_rows=len(selected_indices))
        fig.show()

    draw_button.on_click(_draw_plot)

    def _save_together_plots(_):
        clear_output(wait=True)  # unique output
        display(checkbox_grid, button_container)  # unique output

        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        fig = _prepare_subplots(
            plot_names, selected_indices, n_rows=len(selected_indices)
        )

        for i, idx in enumerate(selected_indices):
            _draw_unzoomed_waveforms(fig, sounds, row=i + 1, idx=idx)
            if mark_one_period is True:
                _draw_zoomed_waveforms(
                    fig,
                    sounds,
                    row=i + 1,
                    idx=idx,
                    mark_one_period=mark_one_period,
                )
            else:
                _draw_zoomed_waveforms(fig, sounds, row=i + 1, idx=idx)

        _update_plot(fig, title="Waveform Plots", n_rows=len(selected_indices))

        # Save the plot to PDF
        save_path = os.path.join(cfg.PATH_RESULTS, "original_waveforms/")
        pdf_path = os.path.join(save_path, "waveforms_all.pdf")
        gfcu.export_to_pdf(
            fig,
            n_rows=len(selected_indices),
            pdf_path=pdf_path,
        )

        print(
            f"Saved joined plot to .{save_path[len(cfg.PATH_BASE):]}"
        )  # print relative path

    save_all_button.on_click(_save_together_plots)

    def _save_individual_plots(_):
        clear_output(wait=True)  # unique output
        display(checkbox_grid, button_container)  # unique output

        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        for idx in selected_indices:
            fig = _prepare_subplots(
                plot_names, selected_indices, n_rows=1, name=plot_names[idx]
            )
            _draw_unzoomed_waveforms(fig, sounds, row=1, idx=idx)
            if mark_one_period is True:
                _draw_zoomed_waveforms(
                    fig,
                    sounds,
                    row=1,
                    idx=idx,
                    mark_one_period=mark_one_period,
                )
            else:
                _draw_zoomed_waveforms(fig, sounds, row=1, idx=idx)
            _update_plot(fig, title="Waveform Plots", n_rows=1)

            # Save the plot to PDF
            save_path = os.path.join(cfg.PATH_RESULTS, "original_waveforms/")
            pdf_path = os.path.join(save_path, f"waveform_{plot_names[idx]}.pdf")
            gfcu.export_to_pdf(
                fig,
                n_rows=1,
                pdf_path=pdf_path,
            )  # 2 just to modify the plot size

            print(
                f"Saved joined plot to .{save_path[len(cfg.PATH_BASE):]}"
            )  # print relative path

    save_individual_button.on_click(_save_individual_plots)


class _PrepareButtonsReconstructionTimeline(gfcu.ButtonPanel):
    """
    A subclass of the ButtonPanel class used for creating a panel with "Toggle All",
    "Reconstruct Waveform" and "Save Individual Plots" buttons. Used in
    draw_waveform_reconstruction_timeline function.
    """

    def __init__(self):
        """
        Initializes _PrepareButtonsReconstructionTimeline with predefined buttons.
        """
        super().__init__(
            [
                "Toggle All",
                "Show Reconstruction Timeline",
                "Save Individual Steps",
            ]
        )


def _add_harmonic_to_plot(
    fig,
    one_period_signal,
    sample_rates,
    n,
    idx,
    saving_individual=False,
):
    """
    Adds a single harmonic to the plot.

    This function calculates the Fourier coefficients for the specified harmonic
    and reconstructs the original signal using the coefficients. It then adds the
    original and reconstructed signals to the specified Plotly figure.

    Args:
        fig (plotly.graph_objs.Figure):
            -   The Plotly figure to draw on.

        one_period_signal (numpy.ndarray):
            -   A one-period audio signal.

        sample_rates (list):
            -   Sample rates corresponding to each audio signal.

        n (int):
            -   The order of the harmonic.

        idx (int):
            -   The index of the selected instrument in the `sounds` list.

        saving_individual (bool, optional):
            -   Whether to save the individual plots (default is False).

    Returns:
        None
    """
    fourier_coefficients = fmu.calculate_fourier_coefficients(one_period_signal, n)
    reconstructed_signal = fmu.reconstruct_original_signal(
        one_period_signal, fourier_coefficients
    )

    # Generate time data for the x-axis in milliseconds
    time_in_seconds = np.arange(0, len(one_period_signal)) / sample_rates[idx]
    time_in_milliseconds = time_in_seconds * 1000

    # Determine the row and column for the current plot
    if saving_individual:
        row = 1
        col = 1
    else:
        row = (n // 2) + 1
        col = 1 if n % 2 == 0 else 2

    fig.add_trace(
        go.Scatter(
            x=time_in_milliseconds,
            y=one_period_signal,
            mode="lines",
            name="Original Signal",
            line=dict(color="red"),
        ),
        row=row,
        col=col,
    )

    fig.add_trace(
        go.Scatter(
            x=time_in_milliseconds,
            y=reconstructed_signal,
            mode="lines",
            name="Reconstructed Signal",
            line=dict(color="blue"),
        ),
        row=row,
        col=col,
    )

    # Set x-axis title for each subplot
    fig.update_xaxes(title_text="t [ms]", row=row, col=col)


def draw_waveform_reconstruction_timeline(files, one_period_signals, sample_rates):
    """
    Draws the evolution of the waveform reconstruction for a selected instrument.

    The function allows the user to select one instrument at a time and generates
    a grid of plots showing how the reconstructed waveform approaches the original
    waveform as more harmonics are added. The instrument selection is done using
    checkboxes. The function also enables the user to save individual each step of the
    reconstruction.

    Buttons:

    -   Toggle All: Toggles all checkboxes.
    -   Show Reconstruction Timeline: Draws the evolution of the waveform reconstruction
        for the selected instrument.
    -   Save Individual Steps: Saves the individual steps of the waveform reconstruction
        for the selected instrument as separate PDF files.

    Args:
        files (list):
            -   File names.

        one_period_signals (list):
            -   1-period audio signals.

        sample_rates (list):
            -   Sample rates corresponding to each audio signal.

    Returns:
        None
    """

    plot_names = gfcu.get_names(files)

    checkboxes, checkbox_layout = gfcu.prepare_checkbox_grid(plot_names)
    checkbox_grid = widgets.GridBox(checkboxes, layout=checkbox_layout)

    # prepare buttons
    buttons_panel = _PrepareButtonsReconstructionTimeline()
    (
        toggle_all_button,
        reconstruct_waveform_button,
        save_individual_plots_button,
    ) = buttons_panel.get_buttons()
    button_container = buttons_panel.get_container()

    display(checkbox_grid, button_container)

    toggle_all_button.on_click(partial(gfcu.toggle_all, checkboxes))

    def _reconstruct_waveform(_):
        clear_output(wait=True)  # unique output
        display(checkbox_grid, button_container)  # unique output

        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        if len(selected_indices) > 1:
            print("Please select only one instrument.")
            return

        # Get the index of the selected instrument
        idx = selected_indices[0]

        # Get the one-period audio signal for the selected instrument
        one_period_signal = one_period_signals[idx]
        n_harmonics = cfg.N_HARMONICS_PER_INSTRUMENT[idx]

        # Calculate the number of rows needed for the subplot
        rows = (n_harmonics + 1) // 2 if n_harmonics % 2 == 1 else n_harmonics // 2

        # Generate subplot titles
        subplot_titles = [f"All prior + {n}. harmonic" for n in range(n_harmonics)]
        subplot_titles[0] = "Average term"
        subplot_titles[1] = "Average term + 1. harmonic"

        # Create subplot figure with 2 columns and the calculated number of rows
        fig = make_subplots(rows=rows, cols=2, subplot_titles=subplot_titles)

        for n in range(n_harmonics):
            _add_harmonic_to_plot(fig, one_period_signal, sample_rates, n, idx)

        title = f"Reconstruction evolution for {plot_names[idx]}"
        _update_plot(fig, title, n_rows=rows, legend=False)
        fig.show()

    reconstruct_waveform_button.on_click(_reconstruct_waveform)

    def _save_individual_plots(_):
        clear_output(wait=True)  # unique output
        display(checkbox_grid, button_container)  # unique output

        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        for idx in selected_indices:
            # Get the one-period audio signal for the selected instrument
            one_period_signal = one_period_signals[idx]
            n_harmonics = cfg.N_HARMONICS_PER_INSTRUMENT[idx]

            # Generate subplot titles
            subplot_titles = [f"All prior + {n}. harmonic" for n in range(n_harmonics)]
            subplot_titles[0] = "Average term"
            subplot_titles[1] = "Average term + 1. harmonic"

            for n in range(n_harmonics):
                # create a figure with one row and one column (one plot)
                fig = make_subplots(
                    rows=1, cols=1, subplot_titles=""
                )  # only one row. subplot used for consistency instead of go.Figure()

                _add_harmonic_to_plot(
                    fig, one_period_signal, sample_rates, n, idx, saving_individual=True
                )

                title = f"{subplot_titles[n]} for {plot_names[idx]}"
                _update_plot(fig, title=title, n_rows=1, legend=True)

                # Save the plot to PDF
                name = plot_names[idx]

                pdf_path = os.path.join(cfg.PATH_RESULTS, "waveform_reconstruction/")
                gfcu.export_to_pdf(
                    fig,
                    n_rows=2,
                    pdf_path=pdf_path + name + f"_step_{n+1}.pdf",
                )  # n_rows=2 only here to modify plot size

                print(
                    f"Saved joined plot to .{pdf_path[len(cfg.PATH_BASE):]}"
                )  # print relative path

    save_individual_plots_button.on_click(_save_individual_plots)
