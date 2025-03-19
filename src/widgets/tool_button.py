# src/widgets/tool_button.py
import os

from PySide2.QtCore import QMimeData
from PySide2.QtGui import QIcon, Qt, QDrag
from PySide2.QtWidgets import QSizePolicy, QPushButton, QMenu, QApplication


class ToolButton(QPushButton):
    def __init__(self, tool, parent=None):
        super(ToolButton, self).__init__(parent)
        self.tool = tool

        # Set fixed size to prevent stretching
        self.setFixedSize(100, 60)

        # Set text with word wrapping for longer names
        self.setText(tool.name)

        # Get button color from tool
        button_color = getattr(tool, 'color', "#333333")

        # Style with fixed dimensions and custom color
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {button_color};
                color: #EFEFEF;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 2px;
                font-size: 10px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: #444444;
                border: 1px solid #666666;
            }}
            QPushButton:pressed {{
                background-color: #222222;
            }}
        """)

        # For text wrapping, break long text manually
        if len(tool.name) > 15:
            # Add line breaks to long text
            words = tool.name.split()
            if len(words) > 1:
                # Try to break at word boundaries
                half = len(words) // 2
                first_half = ' '.join(words[:half])
                second_half = ' '.join(words[half:])
                self.setText(f"{first_half}\n{second_half}")

        # Connect signals
        self.clicked.connect(self.execute_tool)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def lighten_color(self, color, amount=20):
        """Lighten a hex color by the given amount (0-255)"""
        if color.startswith("#"):
            color = color[1:]
        r = min(255, int(color[0:2], 16) + amount)
        g = min(255, int(color[2:4], 16) + amount)
        b = min(255, int(color[4:6], 16) + amount)
        return f"#{r:02x}{g:02x}{b:02x}"

    def darken_color(self, color, amount=30):
        """Darken a hex color by the given amount (0-255)"""
        if color.startswith("#"):
            color = color[1:]
        r = max(0, int(color[0:2], 16) - amount)
        g = max(0, int(color[2:4], 16) - amount)
        b = max(0, int(color[4:6], 16) - amount)
        return f"#{r:02x}{g:02x}{b:02x}"

    def execute_tool(self):
        self.tool.execute()

    def show_context_menu(self, pos):
        menu = QMenu(self)

        favorite_action = menu.addAction("Add to Favorites")
        if self.tool.is_favorite:
            favorite_action.setText("Remove from Favorites")

        edit_action = menu.addAction("Edit Tool")
        remove_action = menu.addAction("Remove from Toolset")
        delete_action = menu.addAction("Delete Tool")

        action = menu.exec_(self.mapToGlobal(pos))

        if action == edit_action:
            self.parent().edit_tool(self.tool)
        elif action == remove_action:
            self.parent().remove_tool_from_toolset(self.tool.id)
        elif action == delete_action:
            self.parent().delete_tool(self.tool.id)

        if action == favorite_action:
            if self.tool.is_favorite:
                self.tool.is_favorite = False
                self.parent().remove_from_favorites(self.tool.id)
            else:
                self.tool.is_favorite = True
                self.parent().add_to_favorites(self.tool.id)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
        # Use the correct form of super()
        super(ToolButton, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return

        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(f"tool:{self.tool.id}")
        drag.setMimeData(mime_data)

        drag.exec_(Qt.MoveAction)
