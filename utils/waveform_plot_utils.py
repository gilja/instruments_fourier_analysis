"""
waveform_plot_utils.py

This module provides utility functions for working with waveform plots. It includes functions for
plotting, saving, and interacting with waveform data.

Public Functions:
- plot_waveform: Create an interactive visualization interface to display and save waveform plots.

Private Functions:
- _get_plot_names: Extracts and cleans plot names from a list of file paths.
- _prepare_checkbox_grid: Create a grid of checkboxes based on plot names.
- _prepare_buttons: Prepare a set of buttons and a button container.
- _toggle_all: Toggle all checkboxes on or off.
- _prepare_subplots: Prepare two subplots for waveform plots.
- _draw_unzoomed_waveforms: Draw zoomed-out waveform on the left subplot of a figure.
- _draw_zoomed_waveforms: Draw zoomed-in waveform on the right subplot of a figure.
- _update_plot: Update the layout of a Plotly figure for waveform plots.
- _export_to_pdf: Export a Plotly figure to a PDF file.
- _get_save_filenames: Generate PDF filenames for saving waveform plots using the name of subplots.
"""

import ipywidgets as widgets
import math
from IPython.display import display, clear_output
from plotly.subplots import make_subplots
import numpy as np
import plotly.graph_objs as go
import plotly.io as pio
from settings import config as cfg
import os
from functools import partial


def _get_plot_names(files):
    """
    Extracts and cleans plot names from a list of file paths.

    Function expects that files are of the WAC format and that the file names
    contain .WAV extension. The function removes the extension and replaces
    underscores and dashes with spaces. The function also removes the "16 bit"
    string from the plot names.

    Args:
        files (list of str): A list of file paths.

    Returns:
        list of str: A list of cleaned plot names extracted from the file paths.
    """

    plot_names = [
        name.split("/")[-1]
        .replace(".WAV", "")
        .replace("_", " ")
        .replace("-", " ")
        .replace("16 bit", "")
        .lower()
        for name in files
    ]

    return plot_names


def _prepare_checkbox_grid(plot_names):
    """
    Create a grid of checkboxes based on plot names.

    The function creates a grid of checkboxes based on the provided plot names.
    In each column, there are two checkboxes. The number of columns is determined
    by the number of plot names.

    Args:
        plot_names (list of str): A list of plot names.

    Returns:
        tuple: A tuple containing the list of checkboxes and the layout for the grid.
    """

    checkboxes = [widgets.Checkbox(value=True, description=name) for name in plot_names]
    n_columns = math.ceil(len(checkboxes) / 2)

    checkbox_layout = widgets.Layout(
        grid_template_columns="repeat(%d, 300px)" % n_columns,
        grid_gap="1px",
        align_items="flex-start",
    )

    return checkboxes, checkbox_layout


def _prepare_buttons():
    """
    Prepare a set of buttons and a button container.

    The function creates "draw", "Toggle All", "Save All", and "Save Individual"
    buttons. The buttons are then placed in a horizontal container at the bottom
    of the window.

    Returns:
        tuple: A tuple containing the individual buttons and a container holding them.
    """

    draw_button = widgets.Button(description="Draw")
    toggle_all_button = widgets.Button(description="Toggle All")
    save_all_button = widgets.Button(description="Save All")
    save_individual_button = widgets.Button(description="Save Individual")
    button_container = widgets.HBox(
        [
            draw_button,
            toggle_all_button,
            save_all_button,
            save_individual_button,
        ]
    )

    return (
        draw_button,
        toggle_all_button,
        save_all_button,
        save_individual_button,
        button_container,
    )


def _toggle_all(checkboxes, _):
    """
    Toggle all checkboxes on or off.

    Args:
        checkboxes (list): A list of Checkbox widgets.
        _ (object): A placeholder argument (ignored).

    Note:
        This function updates the state of all checkboxes to match the state of the first checkbox.

    """

    new_value = not checkboxes[0].value
    for cb in checkboxes:
        cb.value = new_value


def _prepare_subplots(plot_names, selected_indices, n_rows, name=None):
    """
    Prepare two subplots for waveform plots.

    The function prepares two subplots for each loaded sound. The left subplot
    contains the entire waveform, while the right subplot contains a zoomed-in
    portion of the waveform. Depending on the 'name' argument, the function will
    prepare either a single two-column figure with all plots together or a single
    two-column figure for a single sound.

    Args:
        plot_names (list): List of plot names.
        selected_indices (list): List of selected indices.
        n_rows (int): Number of rows for subplots.
        name (str, optional): The name for individual plot titles (default is None).
                              If the name is not provided, the function creates the
                              single figure with all plots together. If the name is
                              provided, the function creates a figure with only one
                              current plot.

    Returns:
        plotly.graph_objs.Figure: A Plotly figure object.

    Note: Vertical spacing between subplots has to be adjusted based on the number of
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
    Draw zoomed-out waveform on the left subplot of a figure.

    This function adds the full waveform plot to the specified row of a left subplot.
    It extracts the sound data and sample rate from the `sounds` list, generates time
    data for the x-axis in milliseconds, and plots the waveform.

    Args:
        fig (plotly.graph_objs.Figure): The Plotly figure to draw on.
        sounds (list): List of sound data and sample rates.
        row (int): The row number of the subplot to draw on.
        idx (int): The index of the selected sound in the `sounds` list.

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


def _draw_zoomed_waveforms(fig, sounds, zoom_percentages, row, idx):
    """
    Draw zoomed-in waveform on the right subplot of a figure.

    This function adds a zoomed-in waveform plot to the specified row of a right subplot.
    It extracts the sound data and sample rate from the `sounds` list, generates time
    data for the x-axis in milliseconds, calculates the zoomed portion indices, and plots
    the zoomed waveform.

    Args:
        fig (plotly.graph_objs.Figure): The Plotly figure to draw on.
        sounds (list): List of sound data and sample rates.
        zoom_percentages (list): List of zoom percentages for the sounds.
        row (int): The row number of the subplot to draw on.
        idx (int): The index of the selected sound in the `sounds` list.

    Returns:
        None
    """

    wav, rate = sounds[idx]
    zoom_percentage = zoom_percentages[idx]

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


def _update_plot(fig, n_rows):
    """
    Update the layout of a Plotly figure for waveform plots.

    This function updates the layout of the specified Plotly figure by adjusting the
    height, width, title, and title position to accommodate the given number of rows
    for waveform plots.

    Args:
        fig (plotly.graph_objs.Figure): The Plotly figure to update.
        n_rows (int): The number of rows for waveform plots.

    Returns:
        None
    """

    fig.update_layout(
        height=cfg.FIGURE_HEIGHT_PER_PLOT * n_rows,
        width=cfg.FIGURE_WIDTH,
        title_text="Waveform Plots",
        title_x=0.5,
    )


def _export_to_pdf(fig, n_rows, pdf_path):
    """
    Export a Plotly figure to a PDF file.

    This function exports the specified Plotly figure to a PDF file at the specified
    path. It customizes the height of the exported PDF based on the number of rows
    for waveform plots. Both the height and the width of the exported PDF are defined
    in the config file.

    Args:
        fig (plotly.graph_objs.Figure): The Plotly figure to export.
        n_rows (int): The number of rows for waveform plots.
        pdf_path (str): The file path where the PDF will be saved.

    Returns:
        None
    """

    pio.write_image(
        fig,
        pdf_path,
        format="pdf",
        height=cfg.FIGURE_HEIGHT_PER_PLOT * n_rows,
        width=cfg.FIGURE_WIDTH,
    )


def _get_save_filenames(files):
    """
    Generate PDF filenames for saving waveform plots using the name of subplots.

    This function generates filenames for saving waveform plots as PDF files. It
    takes a list of plot names, cleans them by replacing spaces with underscores,
    and appends the ".pdf" file extension to each filename.

    Args:
        files (list): List of input filenames.

    Returns:
        list: List of generated PDF filenames.
    """

    filenames = [
        name.strip().replace(" ", "_") + ".pdf" for name in _get_plot_names(files)
    ]

    return filenames


def plot_waveform(sounds, zoom_percentages, files):
    """
    Draw and save waveform plots based on user selections.

    This function creates an interactive visualization interface to display and
    save waveform plots. It takes a list of input filenames, sound data, and zoom
    percentages. Users can select which waveforms to visualize and save.

    Args:
        sounds (list): List of sound data and sample rates.
        zoom_percentages (list): List of zoom percentages for each waveform.
        files (list): List of input filenames.

    Returns:
        None
    """

    plot_names = _get_plot_names(files)

    checkboxes, checkbox_layout = _prepare_checkbox_grid(plot_names)
    checkbox_grid = widgets.GridBox(checkboxes, layout=checkbox_layout)

    (
        draw_button,
        toggle_all_button,
        save_all_button,
        save_individual_button,
        button_container,
    ) = _prepare_buttons()

    display(checkbox_grid, button_container)

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
            _draw_zoomed_waveforms(fig, sounds, zoom_percentages, row=i + 1, idx=idx)

        _update_plot(fig, n_rows=len(selected_indices))
        fig.show()

    draw_button.on_click(_draw_plot)

    toggle_all_button.on_click(partial(_toggle_all, checkboxes))

    def _save_all_plots(_):
        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        fig = _prepare_subplots(
            plot_names, selected_indices, n_rows=len(selected_indices)
        )

        for i, idx in enumerate(selected_indices):
            _draw_unzoomed_waveforms(fig, sounds, row=i + 1, idx=idx)
            _draw_zoomed_waveforms(fig, sounds, zoom_percentages, row=i + 1, idx=idx)

        _update_plot(fig, n_rows=len(selected_indices))

        # Save the plot to PDF
        pdf_path = os.path.join(cfg.PATH_RESULTS, "waveforms_all.pdf")
        _export_to_pdf(fig, selected_indices, pdf_path)
        print(f"Saved all plots to {pdf_path}")

    save_all_button.on_click(_save_all_plots)

    def _save_individual_plots(_):
        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        # Format the file name correctly
        filenames = _get_save_filenames(files)

        for idx in selected_indices:
            fig = _prepare_subplots(
                plot_names, selected_indices, n_rows=1, name=plot_names[idx]
            )
            _draw_unzoomed_waveforms(fig, sounds, row=1, idx=idx)
            _draw_zoomed_waveforms(fig, sounds, zoom_percentages, row=1, idx=idx)
            _update_plot(fig, n_rows=1)

            # Save the plot to PDF
            pdf_path = os.path.join(cfg.PATH_RESULTS, f"waveform_{filenames[idx]}")
            _export_to_pdf(fig, n_rows=1, pdf_path=pdf_path)
            print(f"Saved individual plot to {pdf_path}")

    save_individual_button.on_click(_save_individual_plots)
