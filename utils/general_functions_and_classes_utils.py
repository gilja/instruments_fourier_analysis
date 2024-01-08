"""
general_functions_and_classes_utils.py

This module contains general utility functions and classes used in the project.

Public functions:
- prepare_checkbox_grid: Create a grid of checkboxes based on provided names.
- toggle_all: Toggle all checkboxes on or off.
- export_to_pdf: Export a Plotly figure to a PDF file.
"""

import ipywidgets as widgets
import math
import plotly.io as pio
from settings import config as cfg
import re


def prepare_checkbox_grid(names):
    """
    Create a grid of checkboxes based on plot names.

    The function creates a grid of checkboxes based on the provided plot names.
    In each column, there are two checkboxes. The number of columns is determined
    by the number of plot names.

    Args:
        names (list of str): A list of checkbox names.

    Returns:
        tuple: A tuple containing the list of checkboxes and the layout for the grid.
    """

    checkboxes = [widgets.Checkbox(value=False, description=name) for name in names]
    n_columns = math.ceil(len(checkboxes) / 2)

    checkbox_layout = widgets.Layout(
        grid_template_columns="repeat(%d, 300px)" % n_columns,
        grid_gap="1px",
        align_items="flex-start",
    )

    return checkboxes, checkbox_layout


def toggle_all(checkboxes, _):
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


class ButtonPanel:
    """
    Base class for creating a panel of buttons.

    This class creates a horizontal container (HBox) with a set of buttons.
    Subclasses are expected to specify the button descriptions they require.

    Methods:
        get_buttons: Returns a list of button widgets.
        get_container: Returns the HBox container holding the buttons.
    """

    def __init__(self, button_descriptions, button_width="auto"):
        """
        Initializes the ButtonPanel with the specified button descriptions.

        Args:
            button_descriptions (list of str): Descriptions for each button to be created.
            button_width (str, optional): The width of the buttons (CSS width value).
        """

        button_layout = widgets.Layout(width=button_width)
        self.buttons = [
            widgets.Button(description=desc, layout=button_layout)
            for desc in button_descriptions
        ]
        self.button_container = widgets.HBox(self.buttons)

    def get_buttons(self):
        """
        Returns the list of button widgets.

        Returns:
            list: A list of widgets.Button instances.
        """

        return self.buttons

    def get_container(self):
        """
        Returns the HBox container holding the button widgets.

        Returns:
            widgets.HBox: The container with the buttons.
        """

        return self.button_container


def export_to_pdf(fig, n_rows, pdf_path):
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


def get_names(files):
    """
    Extracts and cleans plot names from a list of file paths.

    Function expects that files are of the WAV format and that the file names
    contain .WAV extension. The function removes the extension and replaces
    underscores and dashes with spaces. The function also removes the "16 bit"
    string from the plot names.

    Args:
        files (list of str): A list of file paths.

    Returns:
        list of str: A list of cleaned plot names extracted from the file paths.
    """

    names = [
        name.split("/")[-1].replace("-", "_").replace("_16_bit.wav", "")
        for name in files
    ]

    return names


def get_individual_terms(mathematical_representation_of_signal):
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


def get_grouped_terms(terms):
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
