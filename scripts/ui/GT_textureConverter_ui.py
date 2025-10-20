####################### GT_textureConvert UI #######################
# Imports
from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QStandardItemModel, QStandardItem, QIcon, QGuiApplication
from PySide2.QtWidgets import (
    QVBoxLayout, QListView, QPushButton, QDialog, QLineEdit, QLabel, QHBoxLayout, QProgressDialog, QFileDialog
)
from ui.ui_utils import getIconPath, loadSVGIcon

# Global variables
TOOLTIPSHORT = 5000
TOOLTIPLONG = 8000

# UI Code
class TextureConverterWindow(QDialog):
    #Signals
    start = Signal(dict)
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
        # Input Browse Button
        self.inputBrowseButton = QPushButton()
        browseIcon = loadSVGIcon('chooser_folder.svg', QSize(20, 20))
        self.inputBrowseButton.setFocusPolicy(Qt.NoFocus)
        self.inputBrowseButton.setIcon(browseIcon)
        self.inputBrowseButton.setIconSize(QSize(20, 20))
        self.inputBrowseButton.setFixedSize(QSize(25, 25))
        self.inputBrowseButton.setStyleSheet("QPushButton {border: none; margin: 1px;}")

        # Output Browse Button
        self.outputBrowseButton = QPushButton()
        self.outputBrowseButton.setFocusPolicy(Qt.NoFocus)
        self.outputBrowseButton.setIcon(browseIcon)
        self.outputBrowseButton.setIconSize(QSize(20, 20))
        self.outputBrowseButton.setFixedSize(QSize(25, 25))
        self.outputBrowseButton.setStyleSheet("QPushButton {border: none; margin: 1px;}")

        # Input Path label
        self.inputFolderPath = QLineEdit()
        self.inputFolderPath.setPlaceholderText("Input Texture folder")

        self.outputFolderPath = QLineEdit()
        self.outputFolderPath.setText("${rootFolder}")
        self.outputFolderPath.setPlaceholderText("Output Texture folder")

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

        # Input Folder Layout
        self.inputBrowseLyt = QHBoxLayout()
        self.inputBrowseLyt.addWidget(self.inputFolderPath)
        self.inputBrowseLyt.addWidget(self.inputBrowseButton)

        # Output Folder Layout
        self.outputBrowseLyt = QHBoxLayout()
        self.outputBrowseLyt.addWidget(self.outputFolderPath)
        self.outputBrowseLyt.addWidget(self.outputBrowseButton)

        self.mainLyt.addWidget(QLabel("Select input texture folder :"))
        self.mainLyt.addLayout(self.inputBrowseLyt)
        self.mainLyt.addWidget(QLabel("Select output texture folder :"))
        self.mainLyt.addLayout(self.outputBrowseLyt)

        self.mainLyt.addWidget(QLabel("Select render engine for bitmap format :"))
        self.mainLyt.addWidget(self.selRenderEngine)

        self.buttonsLyt = QHBoxLayout()
        self.buttonsLyt.addWidget(self.cancelBut)
        self.buttonsLyt.addWidget(self.okBut)

        self.mainLyt.addLayout(self.buttonsLyt)

    def connections(self):
        self.inputBrowseButton.clicked.connect(self.showBrowseFolder)
        self.outputBrowseButton.clicked.connect(self.showOutputFolder)
        self.okBut.clicked.connect(self.export)
        self.cancelBut.clicked.connect(self.close)

    def showBrowseFolder(self):
        self.inputPath = QFileDialog.getExistingDirectory()

        if self.inputPath:
            self.inputFolderPath.setText(self.inputPath)

    def showOutputFolder(self):
        outputPath = QFileDialog.getExistingDirectory()

        if outputPath == self.inputPath:
            self.outputFolderPath.setText("${rootFolder}")
        elif outputPath:
            self.outputFolderPath.setText(outputPath)

    def export(self):
        inputDirectory = self.inputFolderPath.text()
        outputDirectory = self.outputFolderPath.text()
        renderEngine = []
        for index in range(self.selRenderEngine.model().rowCount()):
            item = self.selRenderEngine.model().item(index)
            if item.checkState() == Qt.Checked:
                renderEngine.append(item.text())
        
        settings = {
            "inputDirectory": inputDirectory,
            "outputDirectory": outputDirectory,
            "renderEngine": renderEngine
        }

        self.start.emit(settings)

class progressConversionWindow(QProgressDialog):
    def __init__(self, label = "Converting textures...", maximum = 100, parent=None):
        super().__init__(label, "Cancel", 0, maximum, parent)
        self.setWindowTitle("Texture Conversion Progress")
        self.setWindowModality(Qt.WindowModal)
        self.setMinimumDuration(0)
        self.setValue(0)
        self.setMinimumSize(450, 100)