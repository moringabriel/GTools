# GTools.py


"""
GTools - Main entry point for the GTools package

This module serves as the main entry point for importing and using GTools in Nuke.
It handles initialization, imports, and version management for the GTools package.

Author: Guillaume Morin
"""

import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to allow relative imports
# This ensures GTools can be imported from anywhere
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import utility modules
from src.utils.logging_utils import setup_logging, get_logger
from src.utils.nuke_utils import setup_nuke_paths, get_nuke, is_running_in_nuke
# Import storage implementations
from src.storage.file_storage import FileStorage

# Create main logger
logger = setup_logging("GTools")
logger.info("Initializing GTools package")

# Set up paths and check environment
setup_nuke_paths()
nuke = get_nuke()

# Package information
__version__ = "0.1.0"
__author__ = "Guillaume Morin"

# Initialize inside Nuke if applicable
RUNNING_IN_NUKE = is_running_in_nuke()
logger.info(f"Running in Nuke: {RUNNING_IN_NUKE}")

# Root directory for the GTools package
GTOOLS_ROOT = Path(current_dir)
logger.info(f"GTools root directory: {GTOOLS_ROOT}")


# Import main components (lazy imports to avoid circular dependencies)
def get_tool_shelf():
    """Get the GToolsShelf class"""
    from src.panels.gtools_shelf import GToolsShelf
    return GToolsShelf


def create_shelf_panel():
    """Create a new instance of the GToolsShelf panel"""
    try:
        from src.panels.gtools_shelf import GToolsShelf
        from src.models.tool_library import ToolLibrary

        # Create storage
        storage = get_default_storage()

        # Create tool library with explicit storage
        tool_library = ToolLibrary(storage=storage)

        # Create panel with tool library
        panel = GToolsShelf(tool_library)

        logger.info("Created GToolsShelf panel instance")
        return panel
    except Exception as e:
        logger.error(f"Error creating shelf panel: {e}", exc_info=True)
        return None


def show_shelf():
    """Show the GTools shelf as a standalone window"""
    if RUNNING_IN_NUKE:
        logger.info("Creating GTools shelf panel in Nuke")
        panel = create_shelf_panel()
        return panel
    else:
        # For standalone usage
        logger.info("Creating standalone GTools shelf window")
        from PySide2.QtWidgets import QApplication

        app = None
        if not QApplication.instance():
            app = QApplication(sys.argv)

        shelf = create_shelf_panel()
        shelf.show()

        if app:
            sys.exit(app.exec_())

        return shelf


def get_default_storage():
    """Get the default storage implementation based on configuration"""
    # You could read this from an environment variable or config file
    storage_type = os.environ.get('GTOOLS_STORAGE', 'file')

    if storage_type.lower() == 'database':
        from src.storage.db_storage import DatabaseStorage
        return DatabaseStorage()
    else:
        from src.storage.file_storage import FileStorage
        return FileStorage()


class _LazyComponentImporter:
    """Utility class for lazy importing of GTools components"""

    @property
    def Tool(self):
        from src.models.tool import Tool
        return Tool

    @property
    def ToolLibrary(self):
        from src.models.tool_library import ToolLibrary
        return ToolLibrary

    @property
    def GToolsShelf(self):
        return get_tool_shelf()


# Create a lazy component importer
components = _LazyComponentImporter()

# Export main components
__all__ = [
    'show_shelf',
    'create_shelf_panel',
    'components',
    '__version__',
    '__author__',
    'GTOOLS_ROOT',
    'RUNNING_IN_NUKE'
]

if __name__ == "__main__":
    # If run directly, show the shelf
    logger.info("Running GTools.py directly")
    shelf = show_shelf()