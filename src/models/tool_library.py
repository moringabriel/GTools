# src/models/tool_library.py
import os
import uuid
from datetime import datetime

from src.models.tool import Tool
from src.storage.file_storage import FileStorage
from src.utils.logging_utils import get_logger

logger = get_logger("GTools.ToolLibrary")


class ToolLibrary:
    """
    Manages a collection of tools and toolsets with persistence

    The ToolLibrary is responsible for:
    - Loading and saving tools from/to storage
    - Managing toolsets (groups of tools)
    - Providing access to tools and toolsets
    """

    def __init__(self, storage=None):
        # Initialize storage
        self.storage = storage or FileStorage()

        # Load existing library
        self.available_tools = {}
        self.toolsets = {}
        # Load library first
        self.load_library()

        logger.info(f"Library loaded with {len(self.available_tools)} tools and {len(self.toolsets)} toolsets")

        # Only populate if truly empty
        if not self.available_tools:
            logger.warning("No tools found in library - will populate with defaults")
            self._populate_default_tools()

    def _populate_default_tools(self):
        """Add default tools to the empty library using organized function modules"""
        try:
            # Check if tools already exist to prevent re-population
            if self.available_tools:
                logger.warning("Tools already exist. Skipping default tool population.")
                return

            logger.warning("POPULATING DEFAULT TOOLS - LIBRARY WAS EMPTY")

            # Create toolsets for different categories
            default_toolset_id = self.create_toolset("Default")
            file_toolset_id = self.create_toolset("File")
            node_toolset_id = self.create_toolset("Node")

            # Map categories to toolset IDs
            toolsets = {
                "Default": default_toolset_id,
                "File": file_toolset_id,
                "Node": node_toolset_id
            }

            logger.info(f"Created default toolsets: {toolsets}")

            # Define default tools based on your organized modules
            default_tools = [
                # File Operations
                {
                    "name": "Open Script Directory",
                    "module_path": "src.functions.file_ops",
                    "function_name": "open_current_nuke_script_dir",
                    "category": "File"
                },

                # Node Arrangement
                {
                    "name": "Align X",
                    "module_path": "src.functions.node_arrangement",
                    "function_name": "align_x_pos",
                    "category": "Default"
                },
                {
                    "name": "Align Y",
                    "module_path": "src.functions.node_arrangement",
                    "function_name": "align_y_pos",
                    "category": "Default"
                },

                # Node Management
                {
                    "name": "Enable Postage Stamp",
                    "module_path": "src.functions.node_arrangement",
                    "function_name": "enable_postage_stamp",
                    "category": "Default"
                },
                {
                    "name": "Disable Postage Stamp",
                    "module_path": "src.functions.node_arrangement",
                    "function_name": "disable_postage_stamp",
                    "category": "Default"
                },

                # Channel Utilities - Frequency Split
                {
                    "name": "Split Frequencies",
                    "module_path": "src.functions.channel_utils",
                    "function_name": "split_frequencies_from_selected_node",
                    "category": "Default"
                },

                # Channel Utilities - Constant Nodes
                {
                    "name": "Red Constant",
                    "module_path": "src.functions.channel_utils",
                    "function_name": "red_constant",
                    "category": "Node"
                },
                {
                    "name": "Green Constant",
                    "module_path": "src.functions.channel_utils",
                    "function_name": "green_constant",
                    "category": "Node"
                },
                {
                    "name": "Blue Constant",
                    "module_path": "src.functions.channel_utils",
                    "function_name": "blue_constant",
                    "category": "Node"
                },
                {
                    "name": "Grey Constant",
                    "module_path": "src.functions.channel_utils",
                    "function_name": "grey_constant",
                    "category": "Node"
                },
                {
                    "name": "Alpha Constant",
                    "module_path": "src.functions.channel_utils",
                    "function_name": "alpha_constant",
                    "category": "Node"
                },

                # Channel Utilities - Generator
                {
                    "name": "Checkerboard",
                    "module_path": "src.functions.channel_utils",
                    "function_name": "create_checkerboard",
                    "category": "Node"
                },

                # Effects
                {
                    "name": "Random Constant",
                    "module_path": "src.functions.effects",
                    "function_name": "random_primary_color",
                    "category": "Node"
                }
            ]

            # Track unique tool names to prevent duplicates
            added_tool_names = set()

            # Add each tool to the library and appropriate toolset
            for tool_info in default_tools:
                tool_name = tool_info["name"]

                # Skip if tool name already added
                if tool_name in added_tool_names:
                    logger.debug(f"Skipping duplicate tool: {tool_name}")
                    continue

                try:
                    tool = Tool(
                        name=tool_name,
                        module_path=tool_info["module_path"],
                        function_name=tool_info["function_name"],
                        color=tool_info.get("color", "#333333")
                    )

                    tool_id = self.add_tool(tool)
                    category = tool_info.get("category", "Default")

                    # Add tool to appropriate toolset
                    self.add_tool_to_toolset(tool_id, toolsets[category])

                    # Mark tool name as added
                    added_tool_names.add(tool_name)

                except Exception as e:
                    logger.error(f"Error adding tool {tool_name}: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())

            logger.info(f"Successfully added {len(added_tool_names)} default tools")

        except Exception as e:
            logger.error(f"Error in _populate_default_tools: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

    def add_tool(self, tool):
        """
        Add a tool to the library

        Args:
            tool (Tool): The tool to add

        Returns:
            str: The tool ID
        """
        logger.info(f"Adding tool to library: {tool.name} (ID: {tool.id})")
        self.available_tools[tool.id] = tool
        self.save_library()
        return tool.id

    def get_tool(self, tool_id):
        """
        Get a tool by ID

        Args:
            tool_id (str): The tool ID

        Returns:
            Tool: The tool, or None if not found
        """
        return self.available_tools.get(tool_id)

    def update_tool(self, tool_id, name=None, script=None, icon=None):
        """
        Update an existing tool

        Args:
            tool_id (str): The tool ID
            name (str, optional): New name
            script (str, optional): New script
            icon (str, optional): New icon

        Returns:
            bool: True if successful, False otherwise
        """
        if tool_id not in self.available_tools:
            logger.warning(f"Tool not found for update: {tool_id}")
            return False

        logger.info(f"Updating tool: {tool_id}")
        tool = self.available_tools[tool_id]

        if name:
            logger.debug(f"Updating tool name: {tool.name} -> {name}")
            tool.name = name
        if script is not None:
            logger.debug(f"Updating tool script for: {tool.name}")
            tool.script = script
        if icon is not None:
            logger.debug(f"Updating tool icon: {tool.icon} -> {icon}")
            tool.icon = icon

        self.save_library()
        return True

    def remove_tool(self, tool_id):
        """
        Remove a tool from the library

        Args:
            tool_id (str): The tool ID

        Returns:
            bool: True if successful, False otherwise
        """
        if tool_id in self.available_tools:
            tool_name = self.available_tools[tool_id].name
            logger.info(f"Removing tool: {tool_name} (ID: {tool_id})")
            del self.available_tools[tool_id]

            # Remove from all toolsets
            for toolset_id, toolset in self.toolsets.items():
                if tool_id in toolset['tools']:
                    logger.debug(f"Removing tool {tool_id} from toolset {toolset['name']}")
                    toolset['tools'].remove(tool_id)

            self.save_library()
            return True

        logger.warning(f"Tool not found for removal: {tool_id}")
        return False

    def create_toolset(self, name):
        """
        Create a new toolset

        Args:
            name (str): The toolset name

        Returns:
            str: The toolset ID
        """
        toolset_id = str(uuid.uuid4())
        logger.info(f"Creating toolset: {name} (ID: {toolset_id})")
        self.toolsets[toolset_id] = {
            'name': name,
            'tools': [],
            'created_at': datetime.now().isoformat()
        }
        self.save_library()
        return toolset_id

    def get_toolset(self, toolset_id):
        """
        Get a toolset by ID

        Args:
            toolset_id (str): The toolset ID

        Returns:
            dict: The toolset, or None if not found
        """
        return self.toolsets.get(toolset_id)

    def get_toolsets(self):
        """
        Get all toolsets

        Returns:
            list: A list of toolset dictionaries
        """
        logger.debug(f"Retrieving toolsets. Total count: {len(self.toolsets)}")

        for toolset_id, toolset in self.toolsets.items():
            logger.debug(f"Toolset ID: {toolset_id}")
            logger.debug(f"Toolset Name: {toolset.get('name', 'Unnamed')}")
            logger.debug(f"Tools in toolset: {toolset.get('tools', [])}")

        return list(self.toolsets.values())

    def get_toolset_tools(self, toolset_id):
        """
        Get all tools in a toolset

        Args:
            toolset_id (str): The toolset ID

        Returns:
            list: List of Tool objects
        """
        print(f"DEBUG: Received toolset_id of type {type(toolset_id)} with value: {toolset_id}")

        # If toolset_id is a dictionary, extract its ID
        if isinstance(toolset_id, dict):
            possible_keys = ["id", "toolset_id", "uuid"]  # Add more if needed
            for key in possible_keys:
                if key in toolset_id:
                    toolset_id = toolset_id[key]
                    break
            else:
                print("ERROR: toolset_id dictionary does not contain a valid ID key")
                return []

        if not isinstance(toolset_id, str):
            print(f"ERROR: toolset_id is not a string after processing. Value: {toolset_id}")
            return []

        print(f"DEBUG: Looking up toolset {toolset_id} in available toolsets")

        if toolset_id not in self.toolsets:
            print(f"DEBUG: Toolset {toolset_id} not found in toolsets")
            return []

        toolset = self.toolsets[toolset_id]
        tool_ids = toolset.get('tools', [])
        print(f"DEBUG: Toolset tool IDs: {tool_ids}")

        resolved_tools = []
        for tool_id in tool_ids:
            tool = self.available_tools.get(tool_id)
            if tool:
                print(f"DEBUG: Found tool: {tool.name} (ID: {tool_id})")
                resolved_tools.append(tool)
            else:
                print(f"DEBUG: Tool ID {tool_id} not found in available_tools")

        print(f"DEBUG: Resolved {len(resolved_tools)} tools")
        return resolved_tools

    def add_tool_to_toolset(self, tool_id, toolset_id):
        """Add a tool to a toolset"""
        try:
            logger.info(f"Adding tool {tool_id} to toolset {toolset_id}")

            if tool_id not in self.available_tools:
                logger.warning(f"Tool not found: {tool_id}")
                return False

            if toolset_id not in self.toolsets:
                logger.warning(f"Toolset not found: {toolset_id}")
                return False

            toolset = self.toolsets[toolset_id]
            if tool_id not in toolset['tools']:
                toolset['tools'].append(tool_id)
                logger.info(f"Added tool {tool_id} to toolset {toolset['name']}")
                self.save_library()

            return True
        except Exception as e:
            logger.error(f"Error in add_tool_to_toolset: {e}", exc_info=True)
            return False

    def remove_tool_from_toolset(self, tool_id, toolset_id):
        """
        Remove a tool from a toolset

        Args:
            tool_id (str): The tool ID
            toolset_id (str): The toolset ID

        Returns:
            bool: True if successful, False otherwise
        """
        if toolset_id not in self.toolsets:
            logger.warning(f"Toolset not found: {toolset_id}")
            return False

        toolset = self.toolsets[toolset_id]
        if tool_id in toolset['tools']:
            toolset['tools'].remove(tool_id)
            logger.debug(f"Removed tool {tool_id} from toolset {toolset['name']}")
            self.save_library()
            return True

        return False

    def rename_toolset(self, toolset_id, new_name):
        """
        Rename a toolset

        Args:
            toolset_id (str): The toolset ID
            new_name (str): The new name

        Returns:
            bool: True if successful, False otherwise
        """
        if toolset_id in self.toolsets:
            old_name = self.toolsets[toolset_id]['name']
            logger.info(f"Renaming toolset: {old_name} -> {new_name}")
            self.toolsets[toolset_id]['name'] = new_name
            self.save_library()
            return True

        logger.warning(f"Toolset not found for rename: {toolset_id}")
        return False

    def remove_toolset(self, toolset_id):
        """
        Remove a toolset

        Args:
            toolset_id (str): The toolset ID

        Returns:
            bool: True if successful, False otherwise
        """
        if toolset_id in self.toolsets:
            toolset_name = self.toolsets[toolset_id]['name']
            logger.info(f"Removing toolset: {toolset_name} (ID: {toolset_id})")
            del self.toolsets[toolset_id]
            self.save_library()
            return True

        logger.warning(f"Toolset not found for removal: {toolset_id}")
        return False

    def save_library(self):
        """
        Save the tool library using the storage implementation

        Returns:
            bool: True if successful, False otherwise
        """
        # Convert tools to dictionaries for storage
        tools_dict = {
            tool_id: tool.to_dict()
            for tool_id, tool in self.available_tools.items()
        }

        # Use the storage implementation to save
        return self.storage.save_library(tools_dict, self.toolsets)

    def load_library(self):
        """
        Load the tool library using the storage implementation

        Returns:
            bool: True if successful, False otherwise
        """
        # Use the storage implementation to load
        tools_dict, toolsets_dict = self.storage.load_library()

        # Convert tool dictionaries to Tool objects
        self.available_tools = {
            tool_id: Tool.from_dict(tool_info)
            for tool_id, tool_info in tools_dict.items()
        }

        self.toolsets = toolsets_dict

        return len(self.available_tools) > 0 or len(self.toolsets) > 0

    def export_tool(self, tool_id, filepath):
        """
        Export a tool to a Python file

        Args:
            tool_id (str): The tool ID
            filepath (str): The file path

        Returns:
            bool: True if successful, False otherwise
        """
        if tool_id not in self.available_tools:
            logger.warning(f"Tool not found for export: {tool_id}")
            return False

        tool = self.available_tools[tool_id]

        # Use the storage implementation to export
        return self.storage.export_tool(tool.to_dict(), filepath)

    def import_tool_from_file(self, filepath, name=None):
        """
        Import a tool from a Python file

        Args:
            filepath (str): The file path
            name (str, optional): Tool name (default: filename)

        Returns:
            str: The tool ID if successful, None otherwise
        """
        # Use the storage implementation to import
        script_content = self.storage.import_tool_from_file(filepath)

        if script_content is None:
            return None

        # Get the tool name from the filename if not provided
        if not name:
            name = os.path.splitext(os.path.basename(filepath))[0]

        # Create the tool
        tool = Tool(
            name=name,
            script=script_content
        )

        # Add to library
        self.add_tool(tool)
        logger.info(f"Imported tool '{name}' from {filepath}")
        return tool.id

    def get_all_tools(self):
        """Return all tools as a list"""
        # Collect all tools from available_tools dictionary
        all_tools = list(self.available_tools.values())
        return all_tools

    def debug_library_contents(self):
        """
        Comprehensive debugging of tool library contents
        """
        print("=" * 50)
        print("TOOL LIBRARY DEBUG INFORMATION")
        print("=" * 50)

        # Available Tools
        print("\nAVAILABLE TOOLS:")
        print(f"Total tools: {len(self.available_tools)}")
        for tool_id, tool in self.available_tools.items():
            print(f"- Tool ID: {tool_id}")
            print(f"  Name: {tool.name}")
            print(f"  Module: {getattr(tool, 'module', 'N/A')}")
            print(f"  Function: {getattr(tool, 'function', 'N/A')}")
            print("---")

        # Toolsets
        print("\nTOOLSETS:")
        print(f"Total toolsets: {len(self.toolsets)}")
        for toolset_id, toolset in self.toolsets.items():
            print(f"- Toolset ID: {toolset_id}")
            print(f"  Name: {toolset.get('name', 'Unnamed')}")
            print(f"  Tools in toolset: {toolset.get('tools', [])}")

            # Verify tools in this toolset
            try:
                toolset_tools = self.get_toolset_tools(toolset_id)
                print(f"  Resolved tools: {[tool.name for tool in toolset_tools]}")
            except Exception as e:
                print(f"  Error retrieving toolset tools: {e}")
            print("---")

        print("=" * 50)