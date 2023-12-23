"""
general_functions_and_classes_utils.py

This module contains general utility functions and classes used in the project.

Public functions:
- prepare_checkbox_grid: Create a grid of checkboxes based on provided names.
- toggle_all: Toggle all checkboxes on or off.
"""

import ipywidgets as widgets
import math


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

    checkboxes = [widgets.Checkbox(value=True, description=name) for name in names]
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

    def __init__(self, button_descriptions):
        """
        Initializes the ButtonPanel with the specified button descriptions.

        Args:
            button_descriptions (list of str): Descriptions for each button to be created.
        """

        self.buttons = [
            widgets.Button(description=desc) for desc in button_descriptions
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
