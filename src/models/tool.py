# src/models/tool.py


"""
Tool class for GTools
Represents a single tool with its associated script, action, and metadata.
"""

import uuid

from src.utils.logging_utils import get_logger
from src.utils.nuke_utils import get_nuke

# Get logger
logger = get_logger("GTools.Tool")
nuke = get_nuke()


class Tool:
    def __init__(self, name, action=None, script=None, icon=None, module_path=None, function_name=None, is_favorite=False, color=None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.action = action
        self.script = script
        self.icon = icon
        self.module_path = module_path
        self.function_name = function_name
        self.is_favorite = is_favorite
        self.color = color or "#333333"

        logger.debug(f"Created Tool: {name} (ID: {self.id}, module: {module_path}, function: {function_name})")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'script': self.script,
            'icon': self.icon,
            'module_path': self.module_path,
            'function_name': self.function_name,
            'is_favorite': self.is_favorite,
            'color': self.color
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Tool from a dictionary"""
        tool = cls(
            name=data['name'],
            script=data.get('script'),
            icon=data.get('icon'),
            module_path=data.get('module_path'),
            function_name=data.get('function_name'),
            is_favorite=data.get('is_favorite', False),
            color = data.get('color', "#333333")
        )
        # Set the ID after creating the object
        tool.id = data['id']
        return tool

    def execute(self):
        """Execute the tool's script or function"""
        logger.info(f"Executing Tool: {self.name} (ID: {self.id})")

        try:
            # Case 1: Using module_path and function_name
            if self.module_path and self.function_name:
                logger.debug(f"Importing module: {self.module_path}")

                # Dynamically import the module
                module = __import__(self.module_path, fromlist=['*'])

                # Get the function from the module
                if hasattr(module, self.function_name):
                    func = getattr(module, self.function_name)
                    logger.debug(f"Calling function: {self.function_name}")

                    # Call the function
                    func()
                    logger.info(f"Tool execution successful: {self.name}")
                    return True
                else:
                    logger.error(f"Function {self.function_name} not found in module {self.module_path}")
                    return False

            # Case 2: Using direct script
            elif self.script:
                logger.debug(f"Executing script: {self.script[:50]}...")
                exec(self.script)
                logger.info(f"Tool execution successful: {self.name}")
                return True

            # Case 3: No script or function
            else:
                logger.warning(f"Tool has no script or action: {self.name}")
                return False

        except Exception as e:
            error_msg = f"Error executing tool '{self.name}': {str(e)}"
            logger.error(error_msg)
            import nuke
            nuke.message(error_msg)
            return False

    def __str__(self):
        """String representation of the tool"""
        return f"Tool({self.name})"

    def __repr__(self):
        """Detailed representation of the tool"""
        return f"Tool(name='{self.name}', id='{self.id}', icon='{self.icon}')"


# Example of creating a tool
def create_example_tool():
    """Create an example tool for testing"""
    script = """
# Example tool script
import nuke
nuke.message('Hello from GTools!')
print('Example tool executed')
"""
    return Tool(
        name="Example Tool",
        script=script,
        icon="python.png"
    )


if __name__ == "__main__":
    # Test tool creation and serialization
    tool = create_example_tool()
    print(f"Created tool: {tool}")

    # Test serialization
    data = tool.to_dict()
    print(f"Serialized: {data}")

    # Test deserialization
    tool2 = Tool.from_dict(data)
    print(f"Deserialized: {tool2}")

    # Check equality
    print(f"Same ID: {tool.id == tool2.id}")
    print(f"Same name: {tool.name == tool2.name}")