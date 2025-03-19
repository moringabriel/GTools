# src/panels/gtools_panel.py
"""
GTools Panel Registration Module
Handles registration of the GTools shelf panel in Nuke.
"""

import nuke
import nukescripts
from PySide2 import QtWidgets

from ..utils.logging_utils import get_logger
from .gtools_shelf import GToolsShelf

# Get logger
logger = get_logger("GTools.Panel")


class NukeGToolsPanel(QtWidgets.QWidget):
    """
    Container widget for the GTools shelf.
    This is the widget that gets registered with Nuke's panel system.
    """

    def __init__(self, parent=None):
        logger.debug("Initializing NukeGToolsPanel")
        QtWidgets.QWidget.__init__(self, parent)

        # Set up the layout
        self.setLayout(QtWidgets.QHBoxLayout())
        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        # Create the shelf widget
        try:
            self.shelf = GToolsShelf()
            self.layout().addWidget(self.shelf)

            # Set size policy to expand
            self.setSizePolicy(QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding
            ))

            logger.debug("NukeGToolsPanel initialized successfully")
        except Exception as e:
            logger.error(f"Error creating GToolsShelf: {e}", exc_info=True)
            error_label = QtWidgets.QLabel(f"Error loading GTools Shelf:\n{str(e)}")
            error_label.setStyleSheet("color: red; padding: 20px;")
            self.layout().addWidget(error_label)


# Panel ID - used for registration and restoration
PANEL_ID = 'com.gmorin.gtools.shelf'


def create_gtools_panel():
    """
    Create a new instance of the GTools panel.
    This function is called by Nuke when the panel is needed.
    """
    try:
        logger.debug("Creating GTools panel")
        return NukeGToolsPanel()
    except Exception as e:
        logger.error(f"Failed to create GTools panel: {e}", exc_info=True)
        # Return a minimal widget with error message
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        label = QtWidgets.QLabel(f"Error creating GTools panel: {e}")
        label.setStyleSheet("color: red;")
        layout.addWidget(label)
        return widget


# Register the panel with Nuke
def register_panel():
    """
    Register the GTools panel with Nuke.
    This should be called during Nuke startup.
    """
    try:
        logger.info(f"Registering GTools panel with ID: {PANEL_ID}")
        nukescripts.panels.registerWidgetAsPanel(
            'create_gtools_panel',  # Function name as string
            'GTools Shelf',  # Panel title
            PANEL_ID,  # Panel ID
            True  # Create panel on demand
        )
        logger.info("GTools panel registered successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to register GTools panel: {e}", exc_info=True)
        return False


# Initial registration on module import
if __name__ != "__main__":
    register_panel()