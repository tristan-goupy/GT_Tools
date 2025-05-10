from PySide2.QtCore import Qt, QSize
from PySide2.QtWidgets import QScrollArea, QToolButton, QGridLayout, QLabel, QSizePolicy, QWidget
from PySide2.QtGui import QIcon
import hou
from ui.ui_utils import getIconPath

class Section(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent)

        self.downArrowIcon = QIcon(getIconPath("downArrow.svg"))
        self.rightArrowIcon = QIcon(getIconPath("rightArrow.svg"))

        self.toggleButton = QToolButton(self)
        self.headerLine = hou.qt.Separator()
        self.contentArea = QScrollArea(self)
        self.mainLyt = QGridLayout(self)

        self.toggleButton.setStyleSheet("QToolButton { margin:1px; border: none; background: none}")
        self.toggleButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggleButton.setFixedSize(20, 20)
        self.toggleButton.setIcon(self.rightArrowIcon)
        self.toggleButton.setIconSize(QSize(20, 20))
        self.toggleButton.setText(title)
        self.toggleButton.setCheckable(True)
        self.toggleButton.setChecked(False)

        self.toggleLabel = QLabel(title)

        self.contentArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.contentArea.setStyleSheet("QScrollArea { border: none }")
        self.contentArea.setVisible(False)

        self.mainLyt.setVerticalSpacing(0)
        self.mainLyt.setContentsMargins(0, 0, 0, 0)

        row = 0
        self.mainLyt.addWidget(self.toggleButton, row, 0, 1, 1)
        self.mainLyt.addWidget(self.toggleLabel, row, 1, 1, 1, Qt.AlignLeft)
        self.mainLyt.addWidget(self.headerLine, row, 2, 1, 1)
        self.mainLyt.addWidget(self.contentArea, row + 1, 0, 1, 3)
        self.mainLyt.setColumnStretch(0, 1)
        self.mainLyt.setColumnStretch(1, 0)
        self.mainLyt.setColumnStretch(2, 5)
        self.mainLyt.setRowStretch(1, 1)
        self.setLayout(self.mainLyt)

        self.toggleButton.toggled.connect(self.toggle)

    def setContentLayout(self, contentLayout):
        self.contentArea.setLayout(contentLayout)

    def toggle(self, collapsed):
        if collapsed:
            self.toggleButton.setIcon(self.downArrowIcon)
            self.contentArea.setVisible(True)
            self.window().setMinimumSize(600,400)
        else:
            self.toggleButton.setIcon(self.rightArrowIcon)
            self.contentArea.setVisible(False)
            self.window().resize(600,200)
            self.window().setMinimumSize(600,200)

        window = self.window()
        if window:
            size = window.size()
            size.setHeight(window.sizeHint().height())
            window.resize(size)