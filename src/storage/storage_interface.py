# src/storage/storage_interface.py
from abc import ABC, abstractmethod


class StorageInterface(ABC):
    """Abstract interface for tool storage systems"""

    @abstractmethod
    def load_library(self):
        """Load the entire library (tools and toolsets)

        Returns:
            tuple: (tools_dict, toolsets_dict)
        """
        pass

    @abstractmethod
    def save_library(self, tools_dict, toolsets_dict):
        """Save the entire library

        Args:
            tools_dict (dict): Dictionary of tool data
            toolsets_dict (dict): Dictionary of toolset data

        Returns:
            bool: Success or failure
        """
        pass

    @abstractmethod
    def export_tool(self, tool_data, filepath):
        """Export a tool to a file

        Args:
            tool_data (dict): Tool data
            filepath (str): Target file path

        Returns:
            bool: Success or failure
        """
        pass

    @abstractmethod
    def import_tool_from_file(self, filepath):
        """Import a tool from a file

        Args:
            filepath (str): Source file path

        Returns:
            str: The file content
        """
        pass