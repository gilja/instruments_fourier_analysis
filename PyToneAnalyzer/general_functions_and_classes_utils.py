"""
general_functions_and_classes_utils:
====================================

The module contains general utility functions and classes used throughout the project.

Public functions:
-----------------
-   prepare_checkbox_grid: Creates a grid of checkboxes based on audio names.
-   toggle_all: Toggles all checkboxes on or off. Off by default.
-   export_to_pdf: Exports a Plotly figure to a PDF file.
-   get_names: Extracts and cleans names from a list of file paths.
-   get_individual_terms: Extracts individual terms from a mathematical function
    representing the reconstructed signal.
-   get_grouped_terms: Groups terms by their harmonic order.

Classes:
--------
-   ButtonPanel: The base class for creating a panel with buttons.

For more information on the functions and classes, refer to their docstrings.

Notes:
------

Author: Duje Giljanović (giljanovic.duje@gmail.com)
License: MIT License

If you use PyToneAnalyzer in your research or any other publication, please acknowledge it by
citing as follows:

@software{PyToneAnalyzer,
    title = {PyToneAnalyzer: Fourier Analysis of Musical Instruments},
    author = {Duje Giljanović},
    year = {2024},
    url = {github.com/gilja/instruments_fourier_analysis},
}
"""

import re
import math
import ipywidgets as widgets
import plotly.io as pio
from .config_manager import ConfigManager


def prepare_checkbox_grid(names):
    """
    Creates a grid of checkboxes based on audio names.

    The function creates a grid of checkboxes based on the provided audio names.
    In each column, there are two checkboxes. The number of columns is determined
    by the number of plot names.

    Args:
        names (list of str):
            -   Checkbox names.

    Returns:
        tuple: List of checkboxes and the layout for the grid.
    """

    checkboxes = [widgets.Checkbox(value=False, description=name) for name in names]
    n_columns = math.ceil(len(checkboxes) / 2)

    checkbox_layout = widgets.Layout(
        grid_template_columns=f"repeat({n_columns}, 300px)",
        grid_gap="1px",
        align_items="flex-start",
    )

    return checkboxes, checkbox_layout


def toggle_all(checkboxes, _):
    """
    Toggles all checkboxes on or off. Off by default.

    Args:
        checkboxes (list):
            -   Checkbox widgets.
        _ (object):
            -   A placeholder argument (ignored). Needed to make the function
                compatible with the on_click event handler.

    Returns:
        None
    """

    new_value = not checkboxes[0].value
    for cb in checkboxes:
        cb.value = new_value


class ButtonPanel:
    """
    The base class for creating a panel with buttons.

    The class creates a horizontal container (HBox) with a set of buttons.
    Subclasses that inherit this class are expected to specify the button
    descriptions they require.

    Methods:
        get_buttons: Returns a list of button widgets.
        get_container: Returns the HBox container holding the buttons.
    """

    def __init__(self, button_descriptions, button_width="auto"):
        """
        Initializes the ButtonPanel with the specified button descriptions.

        Args:
            self (ButtonPanel):
                -   The ButtonPanel instance to be initialized.

            button_descriptions (list of str):
                -   Descriptions for each button to be created.

            button_width (str, optional):
                -   The width of the buttons (CSS width value).
        """

        button_layout = widgets.Layout(width=button_width)
        self.buttons = [
            widgets.Button(description=desc, layout=button_layout)
            for desc in button_descriptions
        ]
        self.button_container = widgets.HBox(self.buttons)

    def get_buttons(self):
        """
        Returns:
            A list of widgets.Button instances.
        """

        return self.buttons

    def get_container(self):
        """
        Returns:
            widgets.HBox: The container with the buttons.
        """

        return self.button_container


def export_to_pdf(fig, n_rows, pdf_path):
    """
    Exports a Plotly figure to a PDF file.

    The function exports the specified Plotly figure to a PDF file at the specified
    path. It customizes the height of the exported PDF based on the number of rows
    for waveform plots. Both the height and the width of the exported PDF are defined
    in the config file.

    Args:
        fig (plotly.graph_objs.Figure):
            -   The Plotly figure to export.
        n_rows (int):
            -   The number of rows for waveform plots.
        pdf_path (str):
            -   The file path where the PDF will be saved.

    Returns:
        None
    """

    cfg = ConfigManager.get_instance().config

    pio.write_image(
        fig,
        pdf_path,
        format="pdf",
        height=cfg.FIGURE_HEIGHT_PER_PLOT * n_rows,
        width=cfg.FIGURE_WIDTH,
    )


def get_names(files):
    """
    Extracts and cleans plot names from a list of file paths.

    The function expects that files are of the WAV format and that the file names
    contain a .wav extension. The function removes the extension and replaces
    underscores and dashes with spaces. The function also removes the "16_bit"
    string from the plot names. The expected file name format is
    <instrument>-<note>_16_bit.wav all lowercase, e.g. cello-c3_16_bit.wav.


    Args:
        files (list of str):
            -   The path to the WAV audio file. Absolute paths are recommended as
                they are used throughout the tool.

    Returns:
        list of str:
            -   A list of cleaned plot names extracted from the file paths.
    """

    names = [
        name.split("/")[-1].replace("-", "_").replace("_16_bit.wav", "")
        for name in files
    ]

    return names


def get_individual_terms(mathematical_representation_of_signal):
    """
    Extracts individual terms from a mathematical function representing the
    reconstructed signal.

    The individual term is either a string representing a constant term, a
    string representing a term with a cosine, or a string representing a term with
    a sine. In the case of a term including a cosine or a sine function, the amplitude
    and the argument of the trigonometric function are included in the term.
    The sign of the term is included in all cases.

    Args:
        mathematical_representation_of_signal (str):
            -   A list that stores the mathematical representation of the signal for
                one instrument (recording). The structure is as follows:
                * First element: average term, a term with cos, and a term with sin.
                * All other elements: a term with cos and a term with sin.

    Returns:
        terms (list): Individual terms.
    """

    terms = re.findall(
        r"[\+\-]?\s*\d+\.?\d*\*?[^+\-]+",
        mathematical_representation_of_signal,
    )
    terms = [t.rstrip() for t in terms]

    return terms


def get_grouped_terms(terms):
    """
    Groups terms by their harmonic order.

    The function groups the terms in the following way:

    1.  The first term in the list is the constant term and
        is combined with the 2nd and the 3rd terms representing
        the first harmonic.
    2.  The 4th and the 5th terms represent the second harmonic and
        are combined.
    3.  The 6th and the 7th terms represent the third harmonic and
        are combined.

    The process is continued until all terms are grouped. The function
    returns a list of grouped terms. The grouped_terms list will contain
    three terms as the first element (constant and the first harmonic),
    two terms as the second element (second harmonic), two terms as the
    third element (third harmonic), etc.

    Args:
        terms (list):
            -   Individual terms.

    Returns:
        grouped_terms (list): Grouped terms.
    """

    grouped_terms = [terms[:3]]
    grouped_terms.extend(
        [terms[i : i + 2] for i in range(3, len(terms), 2)]  # noqa: E203
    )

    return grouped_terms
