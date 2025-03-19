# src/utils/nuke_utils.py


"""
Nuke utility functions and mock Nuke implementation for GTools
This module provides utility functions for working with Nuke, as well as
a mock implementation of the Nuke module for standalone testing.
"""

import os
import sys
import logging

# Get logger
logger = logging.getLogger('GToolsShelf.nuke_utils')


def setup_nuke_paths():
    """
    Add Nuke Python paths to sys.path if they exist
    Returns True if Nuke paths were added, False otherwise
    """
    nuke_paths = [
        r'C:\Program Files\Nuke15.1v5\pythonextensions\site-packages',
        r'C:\Program Files\Nuke15.1v5\lib\site-packages'
    ]

    added_paths = False
    for path in nuke_paths:
        if os.path.exists(path) and path not in sys.path:
            sys.path.append(path)
            logger.debug(f"Added Nuke path to sys.path: {path}")
            added_paths = True

    return added_paths


def is_running_in_nuke():
    """
    Check if the code is running inside Nuke
    Returns True if running in Nuke, False otherwise
    """
    return 'nuke' in sys.modules


def get_nuke_version():
    """
    Get the Nuke version if running in Nuke
    Returns a tuple (major, minor, release) or None if not in Nuke
    """
    if not is_running_in_nuke():
        return None

    import nuke
    version_string = nuke.NUKE_VERSION_STRING
    try:
        # Parse version like "15.1v5"
        version_parts = version_string.replace('v', '.').split('.')
        major = int(version_parts[0])
        minor = int(version_parts[1])
        release = int(version_parts[2]) if len(version_parts) > 2 else 0
        return (major, minor, release)
    except (IndexError, ValueError):
        logger.warning(f"Failed to parse Nuke version: {version_string}")
        return None


class MockNode:
    """
    Mock implementation of a Nuke node for standalone testing
    """

    def __init__(self, node_type, knobs=None):
        self.node_type = node_type
        self.knobs = knobs or {}
        self.inputs = []
        self.outputs = []

        logger.debug(f"Created MockNode of type: {node_type}")

    def Class(self):
        """Return the node class name"""
        return self.node_type

    def name(self):
        """Return the node name"""
        return f"{self.node_type}1"

    def setInput(self, index, node):
        """Set input at index to node"""
        while len(self.inputs) <= index:
            self.inputs.append(None)
        self.inputs[index] = node
        if node and self not in node.outputs:
            node.outputs.append(self)

    def input(self, index):
        """Get input at index"""
        if 0 <= index < len(self.inputs):
            return self.inputs[index]
        return None

    def knob(self, name):
        """Get knob by name"""
        return self.knobs.get(name)

    def writeKnobs(self, write_all=False):
        """Return knobs as a TCL script"""
        knob_script = ""
        for name, value in self.knobs.items():
            knob_script += f"{name} {{{value}}}\n"
        return knob_script

    def readKnobs(self, script):
        """Read knobs from TCL script"""
        logger.debug(f"MockNode.readKnobs: {script[:50]}...")

    def __str__(self):
        return f"MockNode({self.node_type})"


class MockNuke:
    """
    Mock implementation of the Nuke module for standalone testing
    """
    NUKE_VERSION_STRING = "15.1v5"

    def __init__(self):
        self.nodes = []
        logger.info("MockNuke initialized")

    def message(self, msg):
        """Display a message to the user"""
        logger.info(f"NUKE MESSAGE: {msg}")
        print(f"NUKE MESSAGE: {msg}")

    def selectedNodes(self):
        """Return a list of selected nodes"""
        logger.debug("MockNuke.selectedNodes() called")
        # Return a subset of nodes as "selected"
        return self.nodes[:min(len(self.nodes), 2)]

    def allNodes(self, filter=None):
        """Return all nodes, optionally filtered by class"""
        if filter:
            return [node for node in self.nodes if node.Class() == filter]
        return self.nodes

    def createNode(self, node_type, knobs=None):
        """Create a new node"""
        logger.debug(f"MockNuke.createNode({node_type}, {knobs}) called")
        print(f"Creating node: {node_type} with knobs: {knobs}")
        node = MockNode(node_type, knobs)
        self.nodes.append(node)
        return node

    def delete(self, node):
        """Delete a node"""
        if node in self.nodes:
            self.nodes.remove(node)
            logger.debug(f"Deleted node: {node}")

    def tprint(self, msg):
        """Print to script editor"""
        logger.debug(f"NUKE SCRIPT: {msg}")
        print(f"NUKE SCRIPT: {msg}")

    def scriptSave(self):
        """Save the current script"""
        logger.debug("MockNuke.scriptSave() called")
        return True

    def scriptOpen(self, filename):
        """Open a script"""
        logger.debug(f"MockNuke.scriptOpen({filename}) called")
        return True

    def tcl(self, cmd):
        """Execute a TCL command"""
        logger.debug(f"MockNuke.tcl({cmd}) called")
        return ""

    # Add other Nuke functions as needed


# Export the correct Nuke module or a mock
try:
    import nuke

    logger.debug("Using real Nuke module")
except ImportError:
    logger.info("Nuke not found, using MockNuke")
    nuke = MockNuke()


def get_nuke():
    """Return the Nuke module (real or mock)"""
    return nuke