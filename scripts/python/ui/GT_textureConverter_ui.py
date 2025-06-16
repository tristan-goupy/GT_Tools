####################### GT_textureConvert UI #######################
# Imports
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QStandardItemModel, QStandardItem, QIcon
from PySide2.QtWidgets import (
    QVBoxLayout, QListView, QPushButton, QDialog, QLineEdit, QLabel, QHBoxLayout, QProgressDialog, QFileDialog
)
from ui.ui_utils import getIconPath

# Global variables
TOOLTIPSHORT = 5000
TOOLTIPLONG = 8000

# UI Code
class TextureConverterWindow(QDialog):
    #Signals
    start = Signal(str, list)
    def __init__(self, parent=None):
        self.parent = parent
        super(TextureConverterWindow, self).__init__(parent)
        self.configureWindow()
        self.widgets()
        self.layouts()
        self.connections()

    def configureWindow(self):
        self.setWindowTitle("Texture Converter")
        self.setMinimumSize(500, 300)

    def widgets(self):
        # Browse Button
        self.browseButton = QPushButton("Browse")
        self.browseButton.setFocusPolicy(Qt.NoFocus)

        # Path label
        self.folderPath = QLineEdit()
        self.folderPath.setPlaceholderText("Texture folder")

        # Render Engine Selection List
        self.selRenderEngine = QListView()
        rendererModel = QStandardItemModel(self.selRenderEngine)
        renderers = ["Karma"]
        for index, name in enumerate(renderers):
            renderer = QStandardItem(name)
            renderer.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            renderer.setCheckState(Qt.Checked)

            if index == 0:
                renderer.setIcon(QIcon(getIconPath("karma.svg")))
            rendererModel.appendRow(renderer)


        self.selRenderEngine.setModel(rendererModel)


        # OK and Cancel Buttons
        self.okBut = QPushButton("OK")
        self.cancelBut = QPushButton("Cancel")

    def layouts(self):
        # Main Layout
        self.mainLyt = QVBoxLayout(self)

        self.mainLyt.setContentsMargins(10, 10, 10, 10)

        self.mainLyt.addWidget(self.folderPath)
        self.mainLyt.addWidget(self.browseButton)
        self.mainLyt.addWidget(QLabel("Select Render Engine for bitmap format :"))
        self.mainLyt.addWidget(self.selRenderEngine)

        self.buttonsLyt = QHBoxLayout()
        self.buttonsLyt.addWidget(self.okBut)
        self.buttonsLyt.addWidget(self.cancelBut)

        self.mainLyt.addLayout(self.buttonsLyt)

    def connections(self):
        self.browseButton.clicked.connect(self.showBrowseFolder)
        self.okBut.clicked.connect(self.export)
        self.cancelBut.clicked.connect(self.close)

    def showBrowseFolder(self):
        path = QFileDialog.getExistingDirectory()

        if path:
            self.folderPath.setText(path)
            self.path = path

    def export(self):
        textureDirectory = self.folderPath.text()
        renderEngine = []
        for index in range(self.selRenderEngine.model().rowCount()):
            item = self.selRenderEngine.model().item(index)
            if item.checkState() == Qt.Checked:
                renderEngine.append(item.text())

        self.start.emit(textureDirectory, renderEngine)

class progressConversionWindow(QProgressDialog):
    def __init__(self, label = "Converting textures...", maximum = 100, parent=None):
        super().__init__(label, "Cancel", 0, maximum, parent)
        self.setWindowTitle("Texture Conversion Progress")
        self.setWindowModality(Qt.WindowModal)
        self.setMinimumDuration(0)
        self.setValue(0)
        self.setMinimumSize(450, 100)