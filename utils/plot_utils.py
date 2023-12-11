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


def get_plot_names(files):
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


def prepare_checkbox_grid(plot_names):
    checkboxes = [widgets.Checkbox(value=True, description=name) for name in plot_names]
    n_columns = math.ceil(len(checkboxes) / 2)

    checkbox_layout = widgets.Layout(
        grid_template_columns="repeat(%d, 300px)" % n_columns,
        grid_gap="1px",
        align_items="flex-start",
    )

    return checkboxes, checkbox_layout


def prepare_buttons():
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


def toggle_all(checkboxes, _):
    new_value = not checkboxes[0].value
    for cb in checkboxes:
        cb.value = new_value


def prepare_subplots(plot_names, selected_indices, n_rows, name=None):
    if not name:  # scenario: all plots together
        subplot_titles = [
            f"{plot_names[i]} waveform" for i in selected_indices for _ in (0, 1)
        ]
        fig = make_subplots(
            rows=n_rows,
            cols=2,
            subplot_titles=subplot_titles,
            horizontal_spacing=cfg.HSPACING,
            vertical_spacing=cfg.VSPACING,
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


def draw_unzoomed_waveforms(fig, sounds, row, idx):
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


def draw_zoomed_waveforms(fig, sounds, zoom_percentages, row, idx):
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


def update_plot(fig, n_rows):
    fig.update_layout(
        height=cfg.FIGURE_HEIGHT_PER_PLOT * n_rows,
        width=cfg.FIGURE_WIDTH,
        title_text="Waveform Plots",
        title_x=0.5,
    )


def export_to_pdf(fig, n_rows, pdf_path):
    pio.write_image(
        fig,
        pdf_path,
        format="pdf",
        height=cfg.FIGURE_HEIGHT_PER_PLOT * n_rows,
        width=cfg.FIGURE_WIDTH,
    )


def get_save_filenames(files):
    filenames = [
        name.strip().replace(" ", "_") + ".pdf" for name in get_plot_names(files)
    ]

    return filenames


def plot_waveform(sounds, zoom_percentages, files):
    plot_names = get_plot_names(files)

    checkboxes, checkbox_layout = prepare_checkbox_grid(plot_names)
    checkbox_grid = widgets.GridBox(checkboxes, layout=checkbox_layout)

    (
        draw_button,
        toggle_all_button,
        save_all_button,
        save_individual_button,
        button_container,
    ) = prepare_buttons()

    display(checkbox_grid, button_container)

    def draw_plot(_):
        clear_output(wait=True)  # unique output
        display(checkbox_grid, button_container)  # unique output

        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        fig = prepare_subplots(
            plot_names, selected_indices, n_rows=len(selected_indices)
        )

        for i, idx in enumerate(selected_indices):
            draw_unzoomed_waveforms(fig, sounds, row=i + 1, idx=idx)
            draw_zoomed_waveforms(fig, sounds, zoom_percentages, row=i + 1, idx=idx)

        update_plot(fig, n_rows=len(selected_indices))
        fig.show()

    draw_button.on_click(draw_plot)

    toggle_all_button.on_click(partial(toggle_all, checkboxes))

    def save_all_plots(_):
        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        fig = prepare_subplots(
            plot_names, selected_indices, n_rows=len(selected_indices)
        )

        for i, idx in enumerate(selected_indices):
            draw_unzoomed_waveforms(fig, sounds, row=i + 1, idx=idx)
            draw_zoomed_waveforms(fig, sounds, zoom_percentages, row=i + 1, idx=idx)

        update_plot(fig, n_rows=len(selected_indices))

        # Save the plot to PDF
        pdf_path = os.path.join(cfg.PATH_RESULTS, "waveforms_all.pdf")
        export_to_pdf(fig, selected_indices, pdf_path)
        print(f"Saved all plots to {pdf_path}")

    save_all_button.on_click(save_all_plots)

    def save_individual_plots(_):
        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.value]
        if not selected_indices:
            return

        # Format the file name correctly
        filenames = get_save_filenames(files)

        for idx in selected_indices:
            fig = prepare_subplots(
                plot_names, selected_indices, n_rows=1, name=plot_names[idx]
            )
            draw_unzoomed_waveforms(fig, sounds, row=1, idx=idx)
            draw_zoomed_waveforms(fig, sounds, zoom_percentages, row=1, idx=idx)
            update_plot(fig, n_rows=1)

            # Save the plot to PDF
            pdf_path = os.path.join(cfg.PATH_RESULTS, f"waveform_{filenames[idx]}")
            export_to_pdf(fig, n_rows=1, pdf_path=pdf_path)
            print(f"Saved individual plot to {pdf_path}")

    save_individual_button.on_click(save_individual_plots)
