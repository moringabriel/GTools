# src/panels/gtools_shelf.py
import sys
from pathlib import Path

import nuke
import os

import traceback
from PySide2.QtGui import QCursor, Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QFrame, QScrollArea, \
    QMenu, QInputDialog, QLineEdit, QMessageBox, QDialog, QListWidget, QListWidgetItem, QFileDialog, QSizePolicy, \
    QStackedWidget, QTabWidget, QAction

from src.models.tool import Tool
from src.models.tool_library import ToolLibrary
from src.widgets.flow_layout import FlowLayout
from src.widgets.tool_button import ToolButton
from src.widgets.tool_edit_dialog import ToolEditDialog
from src.widgets.toolset_widget import ToolsetWidget


class GToolsShelf(QWidget):
    def __init__(self, tool_library=None, parent=None):
        super(GToolsShelf, self).__init__(parent)

        # Use provided tool_library or create a new one
        if tool_library is None:
            from src.models.tool_library import ToolLibrary
            self.tool_library = ToolLibrary()
        else:
            self.tool_library = tool_library

        self.setAcceptDrops(True)
        self.setup_ui()

        # Initialize with default or first toolset
        self.load_initial_toolset()


    def setup_ui(self):
        """Set up the GTools Shelf UI"""
        main_layout = QVBoxLayout(self)
        self.main_layout = main_layout
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(4)

        self.compact_button = QPushButton("≡")  # Hamburger menu icon
        self.compact_button.setCheckable(True)
        self.compact_button.setToolTip("Toggle Compact Mode")
        self.compact_button.clicked.connect(self.toggle_compact_mode)
        self.compact_button.setCheckable(True)
        self.compact_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #EFEFEF;
                padding: 0;
            }
            QPushButton:checked {
                color: #AAAAAA;
            }
            QPushButton:hover {
                color: #CCCCCC;
            }
        """)
        self.compact_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Add debug print to verify connection
        def on_compact_button_clicked():
            print("Compact button clicked!")
            self.toggle_compact_mode()

        self.compact_button.clicked.connect(on_compact_button_clicked)

        # Create a wrapper widget for centering the button
        compact_button_wrapper = QWidget()
        compact_button_layout = QHBoxLayout(compact_button_wrapper)
        compact_button_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        compact_button_layout.setContentsMargins(0, 0, 0, 0)
        compact_button_layout.addWidget(self.compact_button)

        main_layout.addWidget(compact_button_wrapper)

        # Toolset selection toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(5)
        self.toolbar_layout = toolbar_layout  # Store reference for toggle function

        toolset_label = QLabel("Toolset:")

        # Toolset label and combo
        toolbar_layout.addWidget(toolset_label)

        self.toolset_combo = QComboBox()
        self.toolset_combo.setMinimumWidth(150)
        self.toolset_combo.currentIndexChanged.connect(self.on_toolset_changed)
        toolbar_layout.addWidget(self.toolset_combo, 1)  # 1 = stretch factor

        # Toolset management buttons
        new_toolset_btn = QPushButton("+")
        new_toolset_btn.setToolTip("Create New Toolset")
        new_toolset_btn.setFixedSize(24, 24)
        new_toolset_btn.clicked.connect(self.create_new_toolset)
        toolbar_layout.addWidget(new_toolset_btn)

        rename_toolset_btn = QPushButton("...")
        rename_toolset_btn.setToolTip("Manage Toolset")
        rename_toolset_btn.setFixedSize(24, 24)
        rename_toolset_btn.clicked.connect(self.show_toolset_menu)
        toolbar_layout.addWidget(rename_toolset_btn)

        # Add toolbar to main layout
        main_layout.addLayout(toolbar_layout)

        # Add separator
        separator = QFrame()
        #separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.separator = separator  # Store reference for toggle function
        main_layout.addWidget(separator)

        # Tool management buttons and view selector in a container widget
        self.bottom_buttons_widget = QWidget()
        tool_management_layout = QHBoxLayout(self.bottom_buttons_widget)
        tool_management_layout.setContentsMargins(0, 0, 0, 0)

        # Add the buttons
        add_tool_btn = QPushButton("Add Tool")
        add_tool_btn.clicked.connect(self.show_add_tool_dialog)
        tool_management_layout.addWidget(add_tool_btn)

        capture_setup_btn = QPushButton("Capture Node Setup")
        capture_setup_btn.clicked.connect(self.capture_node_setup)
        tool_management_layout.addWidget(capture_setup_btn)

        import_btn = QPushButton("Import Tool")
        import_btn.clicked.connect(self.import_tool)
        tool_management_layout.addWidget(import_btn)

        # Add a spacer to push the view selector to the right
        tool_management_layout.addStretch()

        # Add view selector next to the buttons
        tool_management_layout.addWidget(QLabel("View:"))
        self.view_combo = QComboBox()
        self.view_combo.addItems(["All", "By Category", "Favorites"])
        self.view_combo.currentIndexChanged.connect(self.change_view)
        tool_management_layout.addWidget(self.view_combo)

        main_layout.addWidget(self.bottom_buttons_widget)

        # Create a stack widget to hold different views
        self.views_stack = QStackedWidget()
        main_layout.addWidget(self.views_stack, 1)  # 1 = stretch factor (this will expand)

        # Setup each view in the stack widget

        # 1. All tools view - using the existing ToolsetWidget
        self.toolset_widget = ToolsetWidget(self)
        self.toolset_widget.tool_removed.connect(self.remove_tool_from_toolset)
        self.tools_scroll = QScrollArea()
        self.tools_scroll.setWidgetResizable(True)
        self.tools_scroll.setFrameShape(QFrame.NoFrame)
        self.tools_scroll.setWidget(self.toolset_widget)
        self.views_stack.addWidget(self.tools_scroll)

        # 2. Category view
        self.category_widget = QTabWidget()
        self.views_stack.addWidget(self.category_widget)

        # 3. Favorites view
        self.favorites_scroll = QScrollArea()
        self.favorites_scroll.setWidgetResizable(True)
        self.favorites_scroll.setFrameShape(QFrame.NoFrame)
        self.favorites_widget = QWidget()
        self.favorites_layout = FlowLayout(self.favorites_widget)
        self.favorites_scroll.setWidget(self.favorites_widget)
        self.views_stack.addWidget(self.favorites_scroll)

        # Add search field
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Type to search tools...")
        self.search_edit.textChanged.connect(self.filter_tools)
        search_layout.addWidget(self.search_edit)

        main_layout.addLayout(search_layout)

        # Set overall styling
        self.setStyleSheet("""
            QWidget {
                background-color: #333333;
                color: #EFEFEF;
            }
            QComboBox, QLineEdit, QTextEdit {
                background-color: #444444;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 3px;
                color: #EFEFEF;
            }
            QPushButton {
                background-color: #3A3A3A;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                color: #EFEFEF;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
                border: 1px solid #777777;
            }
            QPushButton:pressed {
                background-color: #2A2A2A;
            }
            QScrollArea {
                border: 1px solid #555555;
                background-color: #2A2A2A;
                padding: 5px;
            }
            QLabel {
                color: #EFEFEF;
            }
        """)

        # Default size
        self.resize(400, 600)

    def refresh_favorites_view(self):
        print("DEBUG: Refreshing favorites view")

        # Clear existing items
        while self.favorites_layout.count():
            item = self.favorites_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get all tools
        all_tools = self.tool_library.get_all_tools()
        print(f"DEBUG: Found {len(all_tools)} total tools")

        # Filter to only show favorites
        favorite_tools = [tool for tool in all_tools if hasattr(tool, 'is_favorite') and tool.is_favorite]
        print(f"DEBUG: Found {len(favorite_tools)} favorite tools")

        if not favorite_tools:
            # Add a label if no favorites exist
            label = QLabel("No favorite tools. Mark tools as favorites to see them here.")
            label.setAlignment(Qt.AlignCenter)
            self.favorites_layout.addWidget(label)
        else:
            # Add all favorite tools to the view
            for tool in favorite_tools:
                print(f"DEBUG: Adding favorite tool to view: {tool.name}")
                tool_button = self.create_tool_button(tool)
                self.favorites_layout.addWidget(tool_button)

    def refresh_all_tools_view(self):
        # Clear existing items
        while self.all_tools_layout.count():
            item = self.all_tools_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get all tools
        all_tools = self.tool_library.get_all_tools()

        # Add all tools to the view
        for tool in all_tools:
            tool_button = self.create_tool_button(tool)
            self.all_tools_layout.addWidget(tool_button)

    def refresh_category_view(self):
        # Clear existing tabs
        while self.category_widget.count():
            self.category_widget.removeTab(0)

        # Group tools by toolset
        for toolset_id in self.tool_library.toolsets:
            toolset = self.tool_library.get_toolset(toolset_id)
            toolset_name = toolset.get('name', 'Unknown')

            # Create a widget for this toolset
            toolset_widget = QWidget()
            toolset_layout = FlowLayout(toolset_widget)

            # Add tools for this toolset
            toolset_tools = self.tool_library.get_toolset_tools(toolset_id)
            for tool in toolset_tools:
                tool_button = self.create_tool_button(tool)
                toolset_layout.addWidget(tool_button)

            # Add the tab
            self.category_widget.addTab(toolset_widget, toolset_name)

    def create_tool_button(self, tool):
        button = ToolButton(tool)
        button.clicked.connect(lambda: self.run_tool(tool))

        # Add context menu for additional actions
        button.setContextMenuPolicy(Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(lambda pos, t=tool, b=button: self.show_tool_context_menu(pos, t, b))

        return button

    def show_tool_context_menu(self, pos, tool, button):
        menu = QMenu()

        # Toggle favorite action
        favorite_action = QAction("Remove from Favorites" if tool.is_favorite else "Add to Favorites", self)
        favorite_action.triggered.connect(lambda: self.toggle_favorite(tool, button))
        menu.addAction(favorite_action)

        # Additional actions (edit, delete, etc.)
        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(lambda: self.edit_tool(tool))
        menu.addAction(edit_action)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_tool(tool))
        menu.addAction(delete_action)

        menu.exec_(button.mapToGlobal(pos))

    def toggle_favorite(self, tool, button):
        # Toggle the favorite status
        tool.is_favorite = not tool.is_favorite

        print(f"DEBUG: Toggled favorite status for {tool.name} to {tool.is_favorite}")

        # Save changes to the tool library
        self.tool_library.save_library()

        # Refresh the favorites view if it's currently displayed
        if self.views_stack.currentIndex() == 2:
            self.refresh_favorites_view()

        # Also refresh other views to update visual indicators
        current_index = self.views_stack.currentIndex()
        if current_index == 0:
            self.refresh_all_tools_view()
        elif current_index == 1:
            self.refresh_category_view()

    def filter_tools(self, text):
        text = text.lower()
        for button in self.findChildren(ToolButton):
            show = text in button.tool.name.lower()
            button.setVisible(show)

    def change_view(self, index):
        print(f"DEBUG: Changing view to index: {index}")
        self.views_stack.setCurrentIndex(index)

        if index == 0:  # All view
            self.refresh_all_tools_view()
        elif index == 1:  # By Category
            self.refresh_category_view()
        elif index == 2:  # Favorites
            self.refresh_favorites_view()

    def refresh_current_view(self):
        current_index = self.views_stack.currentIndex()
        if current_index == 0:
            self.refresh_all_tools_view()
        elif current_index == 1:
            self.refresh_category_view()
        elif current_index == 2:
            self.refresh_favorites_view()

    def toggle_compact_mode(self):
        """
        Toggle between compact and regular mode of the UI.
        """
        is_compact = self.compact_button.isChecked()

        # Widgets and layouts to hide in compact mode
        widgets_to_hide = [
            "toolbar_layout",
            "toolset_combo",
            "separator",
            "bottom_buttons_widget",
            "views_stack"
        ]

        # Hide/show specified widgets
        for widget_name in widgets_to_hide:
            try:
                widget = getattr(self, widget_name, None)

                if widget is not None:
                    if hasattr(widget, 'count'):  # Layout
                        for i in range(widget.count()):
                            item = widget.itemAt(i)
                            if item and item.widget():
                                item.widget().setVisible(not is_compact)
                    else:  # Widget
                        widget.setVisible(not is_compact)
            except Exception as widget_error:
                print(f"Error toggling widget {widget_name}: {widget_error}")

        # Modify QScrollArea appearance in compact mode
        if hasattr(self, 'views_stack'):
            if is_compact:
                # Remove border and background in compact mode
                self.views_stack.setStyleSheet("""
                    QScrollArea {
                        border: none;
                        background-color: transparent;
                        padding: 0px;
                    }
                """)
            else:
                # Restore original QScrollArea styling
                self.views_stack.setStyleSheet("""
                    QScrollArea {
                        border: 1px solid #555555;
                        background-color: #2A2A2A;
                        padding: 5px;
                    }
                """)

        # If you have a separator, modify its appearance
        if hasattr(self, 'separator'):
            if is_compact:
                # Remove border and background
                self.separator.setStyleSheet("""
                    QFrame {
                        background-color: transparent;
                        border: none;
                    }
                """)
            else:
                # Restore original separator styling
                self.separator.setStyleSheet("""
                    QFrame {
                        background-color: #4A4A4A;
                        border: 1px solid #777777;
                    }
                """)

        # Adjust layout margins based on compact mode
        margin_size = 2 if is_compact else 5
        try:
            self.main_layout.setContentsMargins(margin_size, margin_size, margin_size, margin_size)
        except Exception as margin_error:
            print(f"Error adjusting margins: {margin_error}")

        # Ensure layout updates
        try:
            self.updateGeometry()
            if hasattr(self, 'adjustSize'):
                self.adjustSize()
            if hasattr(self, 'update'):
                self.update()
        except Exception as update_error:
            print(f"Error updating geometry: {update_error}")

    def populate_toolset_combo(self):
        """Populate the toolset combo box"""
        print("DEBUG: Populating toolset combo")

        # Clear existing items
        self.toolset_combo.clear()

        # Get toolsets from library
        toolsets = self.tool_library.get_toolsets()
        print(f"DEBUG: Number of toolsets found: {len(toolsets)}")

        for toolset in toolsets:
            toolset_name = toolset.get('name', 'Unnamed')
            print(f"DEBUG: Adding toolset to combo: {toolset_name}")
            print(f"DEBUG: Toolset tools: {toolset.get('tools', [])}")

            # Set the entire toolset dictionary as item data
            self.toolset_combo.addItem(toolset_name, userData=toolset)

    def load_initial_toolset(self):
        """Load the first available toolset or create a default one"""
        print("DEBUG: Starting load_initial_toolset")

        # Populate toolset combo
        self.populate_toolset_combo()
        print(f"DEBUG: Toolset combo count after populate: {self.toolset_combo.count()}")

        # If no toolsets exist, create a default one
        if self.toolset_combo.count() == 0:
            print("DEBUG: No toolsets found, creating default toolset")
            default_id = self.tool_library.create_toolset("Default")
            print(f"DEBUG: Created default toolset with ID: {default_id}")
            self.populate_toolset_combo()

        # Select the first toolset
        if self.toolset_combo.count() > 0:
            print("DEBUG: Setting current index to 0")
            self.toolset_combo.setCurrentIndex(0)
            print("DEBUG: Calling refresh_tools()")
            self.refresh_tools()
        else:
            print("DEBUG: Still no toolsets after attempted creation")

    def on_toolset_changed(self, index):
        if index >= 0:
            self.refresh_tools()

    def show_toolset_menu(self):
        current_toolset_id = self.get_current_toolset_id()
        if not current_toolset_id:
            return

        menu = QMenu(self)
        rename_action = menu.addAction("Rename Toolset")
        delete_action = menu.addAction("Delete Toolset")

        action = menu.exec_(QCursor.pos())

        if action == rename_action:
            self.rename_current_toolset()
        elif action == delete_action:
            self.delete_current_toolset()

    def rename_current_toolset(self):
        current_toolset_id = self.get_current_toolset_id()
        if not current_toolset_id:
            return

        current_name = self.tool_library.toolsets[current_toolset_id]['name']
        new_name, ok = QInputDialog.getText(
            self, "Rename Toolset", "Enter new toolset name:",
            QLineEdit.Normal, current_name)

        if ok and new_name:
            self.tool_library.rename_toolset(current_toolset_id, new_name)
            # Update combo box
            current_index = self.toolset_combo.currentIndex()
            self.populate_toolset_combo()
            self.toolset_combo.setCurrentIndex(current_index)

    def delete_current_toolset(self):
        current_toolset_id = self.get_current_toolset_id()
        if not current_toolset_id:
            return

        reply = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this toolset?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.tool_library.remove_toolset(current_toolset_id)
            self.populate_toolset_combo()

            # Create a default toolset if none left
            if self.toolset_combo.count() == 0:
                default_id = self.tool_library.create_toolset("Default")
                self.populate_toolset_combo()

    def create_new_toolset(self):
        name, ok = QInputDialog.getText(self, "New Toolset", "Enter toolset name:")
        if ok and name:
            toolset_id = self.tool_library.create_toolset(name)
            self.populate_toolset_combo()

            # Switch to the new toolset
            index = self.toolset_combo.findData(toolset_id)
            if index >= 0:
                self.toolset_combo.setCurrentIndex(index)

    def get_current_toolset_id(self):
        """Get the current toolset ID or None"""
        current_index = self.toolset_combo.currentIndex()
        print(f"DEBUG: Current toolset combo index: {current_index}")

        if current_index >= 0:
            toolset = self.toolset_combo.itemData(current_index)
            print(f"DEBUG: Current toolset retrieved: {toolset}")
            return toolset.id if hasattr(toolset, 'id') else toolset

        print("DEBUG: No current toolset found")
        return None

    def show_add_tool_dialog(self):
        """Show dialog to add an existing tool or create a new one"""
        current_toolset_id = self.get_current_toolset_id()
        if not current_toolset_id:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Add Tool")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        # Create new tool button
        create_new_btn = QPushButton("Create New Tool")
        create_new_btn.clicked.connect(lambda: self.create_new_tool(dialog))
        layout.addWidget(create_new_btn)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Add a search box for filtering tools
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter tools...")
        self.search_edit.textChanged.connect(self.filter_tools_list)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)

        layout.addWidget(QLabel("Or add existing tool:"))

        # Available tools list
        self.available_tools_list = QListWidget()
        # Add all tools that aren't already in the current toolset
        toolset = self.tool_library.toolsets[current_toolset_id]

        for tool_id, tool in self.tool_library.available_tools.items():
            if tool_id not in toolset['tools']:
                item = QListWidgetItem(tool.name)
                item.setData(Qt.UserRole, tool_id)
                self.available_tools_list.addItem(item)

        layout.addWidget(self.available_tools_list)

        add_btn = QPushButton("Add to Current Toolset")
        add_btn.clicked.connect(lambda: self.add_selected_tool(dialog))
        layout.addWidget(add_btn)

        dialog.exec_()

    def create_new_tool(self, parent_dialog=None):
        """Open dialog to create a new tool"""
        dialog = ToolEditDialog(parent=self)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            data = dialog.get_tool_data()
            if data:
                # Create the tool
                tool = Tool(
                    name=data['name'],
                    script=data['script'],
                    icon=data['icon']
                )

                # Add to library
                tool_id = self.tool_library.add_tool(tool)

                # Add to current toolset
                current_toolset_id = self.get_current_toolset_id()
                if current_toolset_id:
                    toolset = self.tool_library.toolsets[current_toolset_id]
                    toolset['tools'].append(tool_id)
                    self.tool_library.save_library()

                # Refresh the display
                self.refresh_tools()

                # Close the parent dialog if provided
                if parent_dialog:
                    parent_dialog.accept()

    def filter_tools_list(self, text):
        """Filter the tools list based on search text"""
        for i in range(self.available_tools_list.count()):
            item = self.available_tools_list.item(i)
            if text.lower() in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def add_selected_tool(self, dialog):
        """Add the selected tool to the current toolset"""
        selected_items = self.available_tools_list.selectedItems()
        if not selected_items:
            return

        current_toolset_id = self.get_current_toolset_id()
        if not current_toolset_id:
            return

        for item in selected_items:
            tool_id = item.data(Qt.UserRole)
            self.tool_library.toolsets[current_toolset_id]['tools'].append(tool_id)

        self.tool_library.save_library()
        self.refresh_tools()
        dialog.accept()

    def remove_tool_from_toolset(self, tool_id):
        """Remove a tool from the current toolset"""
        current_toolset_id = self.get_current_toolset_id()
        if not current_toolset_id:
            return

        toolset = self.tool_library.toolsets[current_toolset_id]
        if tool_id in toolset['tools']:
            toolset['tools'].remove(tool_id)
            self.tool_library.save_library()
            self.refresh_tools()

    def delete_tool(self, tool_id):
        """Delete a tool from the library and all toolsets"""
        if self.tool_library.remove_tool(tool_id):
            self.refresh_tools()

    def update_tool1(self, tool_id, data):
        """Update an existing tool"""
        if self.tool_library.update_tool(
                tool_id,
                name=data['name'],
                script=data['script'],
                icon=data['icon']
        ):
            self.refresh_tools()

    def update_tool(self, tool_id, data):
        """Update a tool with new data"""
        print(f"Updating tool {tool_id} with data: {data}")
        tool = self.tool_library.get_tool(tool_id)
        if not tool:
            return False

        if 'name' in data:
            tool.name = data['name']
        if 'script' in data:
            tool.script = data['script']
        if 'icon' in data:
            tool.icon = data['icon']
        if 'color' in data:
            tool.color = data['color']

        # Save the changes to the library
        self.tool_library.save_library()

        # Refresh the view to show the changes
        self.refresh_current_view()

        return True

    import traceback

    def refresh_tools(self):
        """Refresh the tools display for the current toolset"""
        print("DEBUG: Starting refresh_tools")

        # Clear existing tools
        self.toolset_widget.clear()
        print("DEBUG: Cleared existing tools")

        # Get current toolset ID
        current_toolset_id = self.get_current_toolset_id()
        print(f"DEBUG: Current toolset ID: {current_toolset_id}, type: {type(current_toolset_id)}")

        if not current_toolset_id:
            print("DEBUG: No current toolset ID found")
            return

        # Get tools for this toolset
        tools = self.tool_library.get_toolset_tools(current_toolset_id)
        print(f"DEBUG: Number of tools to add: {len(tools)}")

        # Add each tool to the widget
        for tool in tools:
            try:
                print(f"DEBUG: Adding tool button for {tool.name}, tool: {tool}")
                self.toolset_widget.add_tool_button(tool)
                print(f"DEBUG: Added tool button for {tool.name}")
            except Exception as e:
                print(f"ERROR adding tool button for {tool.name}: {e}, traceback: {traceback.format_exc()}")

    def capture_node_setup(self):
        """Capture selected nodes as a node setup tool, preserving connections"""
        nodes = nuke.selectedNodes()
        if not nodes:
            nuke.message("Select nodes to capture")
            return

        # Find the bounding box of selected nodes
        min_x = min(node.xpos() for node in nodes)
        min_y = min(node.ypos() for node in nodes)

        # Create a very simple script
        setup_script = "# Captured Node Setup\n"
        setup_script += "import nuke\n\n"
        setup_script += "# Get click position\n"
        setup_script += "temp = nuke.createNode('NoOp', '', False)\n"
        setup_script += "click_x, click_y = temp.xpos(), temp.ypos()\n"
        setup_script += "nuke.delete(temp)\n\n"
        setup_script += "# Dictionary to store created nodes\n"
        setup_script += "created_nodes = {}\n\n"

        # Create all nodes first
        for node in nodes:
            node_type = node.Class()
            node_name = node.name()
            rel_x = node.xpos() - min_x
            rel_y = node.ypos() - min_y

            setup_script += f"# Create {node_name}\n"
            setup_script += f"node = nuke.createNode('{node_type}', '', False)\n"
            setup_script += f"node.setXYpos(click_x + {rel_x}, click_y + {rel_y})\n"
            setup_script += f"created_nodes['{node_name}'] = node\n\n"

        # Create connections
        setup_script += "# Create connections\n"
        for node in nodes:
            node_name = node.name()
            for i in range(node.inputs()):
                input_node = node.input(i)
                if input_node and input_node in nodes:
                    input_name = input_node.name()
                    setup_script += f"created_nodes['{node_name}'].setInput({i}, created_nodes['{input_name}'])\n"

        # Ask for tool name
        tool_name, ok = QInputDialog.getText(self, "Capture Setup", "Enter tool name:")
        if ok and tool_name:
            # Create the tool
            tool = Tool(name=tool_name, script=setup_script)

            # Add to library
            tool_id = self.tool_library.add_tool(tool)

            # Add to current toolset
            current_toolset_id = self.get_current_toolset_id()
            if current_toolset_id:
                self.tool_library.add_tool_to_toolset(tool_id, current_toolset_id)
                self.refresh_tools()

    def import_tool(self):
        """Import a tool from a Python file"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Import Tool", str(Path.home()), "Python Files (*.py)")

        if not filepath:
            return

        try:
            with open(filepath, 'r') as f:
                script_content = f.read()

            # Get the tool name from the filename
            tool_name = os.path.splitext(os.path.basename(filepath))[0]

            # Show tool editor to allow editing before import
            dialog = ToolEditDialog(parent=self)
            dialog.name_edit.setText(tool_name)
            dialog.script_edit.setText(script_content)

            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_tool_data()
                if data:
                    # Create and add the tool
                    tool = Tool(
                        name=data['name'],
                        script=data['script'],
                        icon=data['icon']
                    )

                    tool_id = self.tool_library.add_tool(tool)

                    # Add to current toolset
                    current_toolset_id = self.get_current_toolset_id()
                    if current_toolset_id:
                        self.tool_library.toolsets[current_toolset_id]['tools'].append(tool_id)
                        self.tool_library.save_library()
                        self.refresh_tools()

        except Exception as e:
            QMessageBox.warning(self, "Import Error", f"Failed to import tool: {str(e)}")

    def export_tool(self, tool_id):
        """Export a tool to a Python file"""
        if tool_id not in self.tool_library.available_tools:
            return

        tool = self.tool_library.available_tools[tool_id]

        # Let user choose where to save the file
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Tool", str(Path.home() / f"{tool.name}.py"),
            "Python Files (*.py)")

        if not filepath:
            return

        try:
            with open(filepath, 'w') as f:
                f.write(tool.script or "")

            QMessageBox.information(
                self, "Export Successful",
                f"Tool '{tool.name}' exported successfully to {filepath}"
            )
        except Exception as e:
            QMessageBox.warning(
                self, "Export Error",
                f"Failed to export tool: {str(e)}"
            )

    def refresh_tools1(self):
        """Refresh the tools display for the current toolset"""
        self.toolset_widget.clear()

        current_toolset_id = self.get_current_toolset_id()
        if not current_toolset_id:
            return

        toolset = self.tool_library.toolsets.get(current_toolset_id, {})
        tools = []
        for tool_id in toolset.get('tools', []):
            tool = self.tool_library.available_tools.get(tool_id)
            if tool:
                tools.append(tool)

        for tool in tools:
            self.toolset_widget.add_tool_button(tool)

    def add_selected_tool1(self, dialog):
        """Add the selected tool to the current toolset"""
        selected_items = self.available_tools_list.selectedItems()
        if not selected_items:
            return

        current_toolset_id = self.get_current_toolset_id()
        if not current_toolset_id:
            return

        for item in selected_items:
            tool_id = item.data(Qt.UserRole)
            self.tool_library.add_tool_to_toolset(tool_id, current_toolset_id)

        self.tool_library.save_library()
        self.refresh_tools()
        dialog.accept()

    def remove_tool_from_toolset1(self, tool_id):
        """Remove a tool from the current toolset"""
        current_toolset_id = self.get_current_toolset_id()
        if not current_toolset_id:
            return

        self.tool_library.remove_tool_from_toolset(tool_id, current_toolset_id)
        self.refresh_tools()

    def refresh_current_view1(self):
        print('refresh_current_view')
        pass

    def debug_library_contents(self):
        """Print detailed information about the tool library"""
        print("DEBUG: Tool Library Contents")
        print("=" * 30)

        print("\nAvailable Tools:")
        for tool_id, tool in self.tool_library.available_tools.items():
            print(f"- ID: {tool_id}")
            print(f"  Name: {tool.name}")
            print(f"  Module: {tool.module}")
            print(f"  Function: {tool.function}")
            print("---")

        print("\nToolsets:")
        for toolset_id, toolset in self.tool_library.toolsets.items():
            print(f"- ID: {toolset_id}")
            print(f"  Name: {toolset.get('name', 'Unnamed')}")
            print(f"  Tools: {toolset.get('tools', [])}")
            print("---")