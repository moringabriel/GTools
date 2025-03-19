# src/widgets/flow_layout.py
from PySide2.QtCore import Qt, QRect, QSize, QPoint
from PySide2.QtWidgets import QLayout, QSizePolicy


class FlowLayout(QLayout):
    """Custom flow layout for tool buttons that wraps properly"""

    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self._items = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())

        margin = self.contentsMargins().left()
        size += QSize(2 * margin, 2 * margin)
        return size

    def _doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        spacing = 8  # Fixed spacing value for consistency (changed from self.spacing())

        for item in self._items:  # Fixed from self.*items
            # Use fixed spacing instead of dynamic spacing
            spacingX = spacing
            spacingY = spacing

            nextX = x + item.sizeHint().width() + spacingX
            if nextX - spacingX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spacingY
                nextX = x + item.sizeHint().width() + spacingX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()