# src/storage/file_storage.py
import os
import json
from pathlib import Path
from .storage_interface import StorageInterface
from ..utils.logging_utils import get_logger, log_exception

logger = get_logger("GTools.FileStorage")


class FileStorage(StorageInterface):
    """File-based implementation of tool storage"""

    def __init__(self, user_dir=None):
        """Initialize file storage"""
        # Set up storage paths
        if user_dir is None:
            self.user_dir = Path.home() / '.nuke' / 'GTools'
        else:
            self.user_dir = Path(user_dir)

        self.library_path = self.user_dir / 'tool_library.json'
        logger.debug(f"Tool library path: {self.library_path}")

        # Create directory if it doesn't exist
        try:
            self.library_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {self.library_path.parent}")
        except Exception as e:
            logger.error(f"Failed to create directory: {e}")

    def load_library(self):
        """Load library from file"""
        tools_dict = {}
        toolsets_dict = {}

        if not self.library_path.exists():
            logger.info(f"Tool library file not found: {self.library_path}")
            return tools_dict, toolsets_dict

        try:
            logger.debug(f"Loading tool library from: {self.library_path}")
            with open(self.library_path, 'r') as f:
                library_data = json.load(f)
                tools_dict = library_data.get('available_tools', {})
                toolsets_dict = library_data.get('toolsets', {})

            logger.info(f"Loaded {len(tools_dict)} tools and {len(toolsets_dict)} toolsets")
            return tools_dict, toolsets_dict

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding tool library: {e}")
        except Exception as e:
            logger.error(f"Error loading tool library: {e}")
            log_exception(logger, "Error loading tool library")

        return tools_dict, toolsets_dict

    def save_library(self, tools_dict, toolsets_dict):
        """Save library to file"""
        logger.debug("Saving tool library")
        try:
            library_data = {
                'available_tools': tools_dict,
                'toolsets': toolsets_dict
            }

            with open(self.library_path, 'w') as f:
                json.dump(library_data, f, indent=4)

            logger.debug(f"Tool library saved to: {self.library_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save tool library: {e}")
            log_exception(logger, "Error saving tool library")
            return False

    def export_tool(self, tool_data, filepath):
        """Export a tool to a file"""
        try:
            with open(filepath, 'w') as f:
                if tool_data.get('script'):
                    f.write(tool_data['script'])
                else:
                    f.write(f"# Tool: {tool_data['name']}\n# No script available")

            logger.info(f"Tool '{tool_data['name']}' exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export tool: {e}")
            log_exception(logger, "Error exporting tool")
            return False

    def import_tool_from_file(self, filepath):
        """Import a tool from a file"""
        try:
            with open(filepath, 'r') as f:
                script_content = f.read()
            return script_content
        except Exception as e:
            logger.error(f"Failed to import tool: {e}")
            log_exception(logger, "Error importing tool")
            return None