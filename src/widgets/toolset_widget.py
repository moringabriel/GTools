# src/widgets/toolset_widget.py
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget, QGridLayout, QDialog, QMessageBox, QHBoxLayout, QScrollArea

from src.widgets.flow_layout import FlowLayout
from src.widgets.tool_button import ToolButton
from src.widgets.tool_edit_dialog import ToolEditDialog


class ToolsetWidget(QWidget):
    """Container for tool buttons that supports drag and drop"""

    tool_removed = Signal(str)  # Tool ID

    def __init__(self, parent=None):
        super(ToolsetWidget, self).__init__(parent)
        self.setAcceptDrops(True)

        # Use a flow layout which adapts to available space
        self.layout = FlowLayout(self)
        self.layout.setSpacing(6)  # Consistent spacing
        self.layout.setContentsMargins(6, 6, 6, 6)

        self.tool_buttons = []

        # Set styling
        self.setStyleSheet("""
            QWidget {
                background-color: #2A2A2A;
                border-radius: 3px;
            }
        """)

    def edit_tool(self, tool):
        dialog = ToolEditDialog(tool, self)
        if dialog.exec_() == QDialog.Accepted:
            tool_data = dialog.get_tool_data()
            if tool_data:
                # Update tool attributes
                tool.color = tool_data['color']

                # Update button appearance
                self.update_tool_button(tool)

    def update_tool_button(self, tool):
        """Update a specific tool button's appearance"""
        print(f"DEBUG: Updating tool button for tool: {tool.name}")

        # Ensure tool_buttons exists
        if not hasattr(self, 'tool_buttons'):
            print("DEBUG: tool_buttons list does not exist")
            return

        for button in self.tool_buttons:
            if hasattr(button, 'tool') and button.tool == tool:
                print(f"DEBUG: Found button for tool {tool.name}")
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {tool.color};
                        border: 1px solid #555555;
                        border-radius: 3px;
                        padding: 5px;
                        color: #EFEFEF;
                    }}
                """)
                button.repaint()
                return

        print(f"DEBUG: No button found for tool {tool.name}")

    def add_tool_button(self, tool):
        # When creating a tool button, add it to tool_buttons
        button = ToolButton(tool)  # Assuming this is how you create tool buttons
        self.tool_buttons.append(button)
        # Rest of your existing add_tool_button logic
        return button

    def _get_next_position(self):
        """Find the next available position in the grid"""
        count = self.layout.count()
        row = count // self.columns
        col = count % self.columns
        return row, col

    def clear(self):
        """Remove all tool buttons"""
        print("DEBUG: Clearing tool buttons")

        # Track number of widgets to be removed
        widget_count = self.layout.count()
        print(f"DEBUG: Number of widgets to remove: {widget_count}")

        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                widget = item.widget()
                print(f"DEBUG: Removing widget: {widget}")
                widget.deleteLater()

        # Reset tool buttons list if it exists
        if hasattr(self, 'tool_buttons'):
            self.tool_buttons.clear()
            print("DEBUG: Cleared tool_buttons list")

    def remove_tool_from_toolset(self, tool_id):
        self.tool_removed.emit(tool_id)

    def delete_tool(self, tool_id):
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this tool?\nThis will remove it from all toolsets.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.parent().delete_tool(tool_id)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text().startswith('tool:'):
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            text = event.mimeData().text()
            if text.startswith('tool:'):
                tool_id = text.split(':', 1)[1]
                # Handle dropping tool at specific position (TBD)
                event.acceptProposedAction()

    def add_to_favorites(self, tool_id):
        print(f'add_to_favorites: {tool_id}')
        tool = self.parent().tool_library.get_tool(tool_id)
        if tool:
            tool.is_favorite = True
            self.parent().tool_library.save_library()
            # Refresh favorites view if it's currently displayed
            if self.parent().view_combo.currentIndex() == 2:
                self.parent().refresh_favorites_view()

    def remove_from_favorites(self, tool_id):
        print(f'remove_from_favorites: {tool_id}')
        tool = self.parent().tool_library.get_tool(tool_id)
        if tool:
            tool.is_favorite = False
            self.parent().tool_library.save_library()
            # Refresh favorites view if it's currently displayed
            if self.parent().view_combo.currentIndex() == 2:
                self.parent().refresh_favorites_view()

