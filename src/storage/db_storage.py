# src/storage/db_storage.py
import os
import json
from pathlib import Path
import sqlite3  # Or another database library
from .storage_interface import StorageInterface
from ..utils.logging_utils import get_logger, log_exception

logger = get_logger("GTools.DBStorage")


class DatabaseStorage(StorageInterface):
    """Database implementation of tool storage"""

    def __init__(self, db_path=None):
        """Initialize database storage"""
        # Set default database path if not provided
        if db_path is None:
            self.user_dir = Path.home() / '.nuke' / 'GTools'
            self.db_path = self.user_dir / 'gtools.db'
        else:
            self.db_path = Path(db_path)

        # Create directory if it doesn't exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self.conn = self._create_connection()
        self._create_tables()

    def _create_connection(self):
        """Create a database connection"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            return conn
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            return None

    def _create_tables(self):
        """Create the necessary tables if they don't exist"""
        if not self.conn:
            return

        try:
            cursor = self.conn.cursor()

            # Create tools table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS tools (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                script TEXT,
                icon TEXT,
                function_name TEXT,
                module_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # Create toolsets table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS toolsets (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # Create toolset_tools junction table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS toolset_tools (
                toolset_id TEXT,
                tool_id TEXT,
                position INTEGER,
                PRIMARY KEY (toolset_id, tool_id),
                FOREIGN KEY (toolset_id) REFERENCES toolsets(id),
                FOREIGN KEY (tool_id) REFERENCES tools(id)
            )
            ''')

            self.conn.commit()
            logger.debug("Database tables created")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")

    def load_library(self):
        """Load library from database"""
        tools_dict = {}
        toolsets_dict = {}

        if not self.conn:
            return tools_dict, toolsets_dict

        try:
            # Load tools
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name, script, icon, function_name, module_path FROM tools")

            for row in cursor.fetchall():
                tool_id, name, script, icon, function_name, module_path = row
                tools_dict[tool_id] = {
                    'id': tool_id,
                    'name': name,
                    'script': script,
                    'icon': icon,
                    'function_name': function_name,
                    'module_path': module_path
                }

            # Load toolsets
            cursor.execute("SELECT id, name, created_at FROM toolsets")

            for row in cursor.fetchall():
                toolset_id, name, created_at = row
                toolsets_dict[toolset_id] = {
                    'name': name,
                    'tools': [],
                    'created_at': created_at
                }

            # Load toolset tools
            cursor.execute("SELECT toolset_id, tool_id FROM toolset_tools ORDER BY position")

            for row in cursor.fetchall():
                toolset_id, tool_id = row
                if toolset_id in toolsets_dict and tool_id in tools_dict:
                    toolsets_dict[toolset_id]['tools'].append(tool_id)

            logger.info(f"Loaded {len(tools_dict)} tools and {len(toolsets_dict)} toolsets from database")

        except Exception as e:
            logger.error(f"Error loading from database: {e}")
            log_exception(logger, "Database load error")

        return tools_dict, toolsets_dict

    def save_library(self, tools_dict, toolsets_dict):
        """Save library to database"""
        if not self.conn:
            return False

        try:
            cursor = self.conn.cursor()

            # Begin transaction
            self.conn.execute("BEGIN TRANSACTION")

            # Save tools (update or insert)
            for tool_id, tool_data in tools_dict.items():
                cursor.execute(
                    "SELECT COUNT(*) FROM tools WHERE id = ?",
                    (tool_id,)
                )

                if cursor.fetchone()[0] > 0:
                    # Update existing tool
                    cursor.execute(
                        "UPDATE tools SET name = ?, script = ?, icon = ?, function_name = ?, module_path = ? WHERE id = ?",
                        (
                            tool_data['name'],
                            tool_data.get('script'),
                            tool_data.get('icon'),
                            tool_data.get('function_name'),
                            tool_data.get('module_path'),
                            tool_id
                        )
                    )
                else:
                    # Insert new tool
                    cursor.execute(
                        "INSERT INTO tools (id, name, script, icon, function_name, module_path) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            tool_id,
                            tool_data['name'],
                            tool_data.get('script'),
                            tool_data.get('icon'),
                            tool_data.get('function_name'),
                            tool_data.get('module_path')
                        )
                    )

            # Save toolsets (update or insert)
            for toolset_id, toolset_data in toolsets_dict.items():
                cursor.execute(
                    "SELECT COUNT(*) FROM toolsets WHERE id = ?",
                    (toolset_id,)
                )

                if cursor.fetchone()[0] > 0:
                    # Update existing toolset
                    cursor.execute(
                        "UPDATE toolsets SET name = ? WHERE id = ?",
                        (toolset_data['name'], toolset_id)
                    )
                else:
                    # Insert new toolset
                    cursor.execute(
                        "INSERT INTO toolsets (id, name, created_at) VALUES (?, ?, ?)",
                        (toolset_id, toolset_data['name'], toolset_data.get('created_at'))
                    )

                # Delete old toolset_tools entries
                cursor.execute(
                    "DELETE FROM toolset_tools WHERE toolset_id = ?",
                    (toolset_id,)
                )

                # Insert new toolset_tools entries
                for position, tool_id in enumerate(toolset_data.get('tools', [])):
                    cursor.execute(
                        "INSERT INTO toolset_tools (toolset_id, tool_id, position) VALUES (?, ?, ?)",
                        (toolset_id, tool_id, position)
                    )

            # Commit transaction
            self.conn.commit()
            logger.debug("Library saved to database")
            return True

        except Exception as e:
            # Rollback on error
            self.conn.rollback()
            logger.error(f"Error saving to database: {e}")
            log_exception(logger, "Database save error")
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