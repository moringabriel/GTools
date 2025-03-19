# src/widgets/tool_edit_dialog.py

import os
from pathlib import Path

from PySide2.QtGui import QFont, QColor
from PySide2.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                               QTextEdit, QPushButton, QFileDialog, QMessageBox, QColorDialog)

from src.models.tool import Tool


class ToolEditDialog(QDialog):
    """Dialog for creating or editing tools"""

    def __init__(self, tool=None, parent=None):
        super(ToolEditDialog, self).__init__(parent)
        self.tool = tool
        print(f"Initial tool color: {getattr(tool, 'color', 'No color')}")
        self.current_color = getattr(tool, 'color', "#333333")
        print(f"Initial current_color: {self.current_color}")

        self.setup_ui()

    def get_tool_data(self):
        name = self.name_edit.text().strip()
        script = self.script_edit.toPlainText()
        icon = self.icon_edit.text().strip()

        if not name:
            QMessageBox.warning(self, "Validation Error", "Tool name is required.")
            return None

        print(f"Saving color: {self.current_color}")

        # If tool exists, update its attributes
        if self.tool:
            self.tool.color = self.current_color
            print(f"Updated tool color: {self.tool.color}")

        return {
            'name': name,
            'script': script,
            'icon': icon if icon else None,
            'color': self.current_color
        }

    def accept(self):
        """Override accept method to print debug info"""
        print("Dialog accepted")
        super().accept()

    def choose_color(self):
        """Open a color dialog to choose a button color"""
        color = QColorDialog.getColor(QColor(self.current_color), self, "Choose Button Color")
        if color.isValid():
            self.current_color = color.name()
            print(f"Selected color: {self.current_color}")
            self.update_color_button()

    def setup_ui(self):
        self.setWindowTitle("Tool Editor")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Tool name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Tool Name:"))
        self.name_edit = QLineEdit()
        if self.tool:
            self.name_edit.setText(self.tool.name)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Script editor
        layout.addWidget(QLabel("Script:"))
        self.script_edit = QTextEdit()
        self.script_edit.setMinimumHeight(300)
        self.script_edit.setFont(QFont("Consolas", 10))
        if self.tool and self.tool.script:
            self.script_edit.setText(self.tool.script)
        layout.addWidget(self.script_edit)

        # Icon selection (simplified for now)
        icon_layout = QHBoxLayout()
        icon_layout.addWidget(QLabel("Icon:"))
        self.icon_edit = QLineEdit()
        if self.tool and self.tool.icon:
            self.icon_edit.setText(self.tool.icon)
        icon_layout.addWidget(self.icon_edit)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_icon)
        icon_layout.addWidget(browse_btn)
        layout.addLayout(icon_layout)

        # Button color selection
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Button Color:"))

        self.color_button = QPushButton()
        self.color_button.setFixedSize(30, 20)
        self.update_color_button()
        self.color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_button)

        layout.addLayout(color_layout)

        # Buttons
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def update_color_button(self):
        """Update the color button to show the selected color"""
        self.color_button.setStyleSheet(f"background-color: {self.current_color}; border: 1px solid #555555;")

    def browse_icon(self):
        # This would need to be adapted to your icon directory structure
        icon_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'icons')
        if not os.path.exists(icon_dir):
            icon_dir = str(Path.home())

        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Icon", icon_dir, "Image Files (*.png *.jpg *.ico)")

        if filename:
            # Extract just the filename for storage
            self.icon_edit.setText(os.path.basename(filename))



