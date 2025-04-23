import sys
import os
import getpass
import hou
import re
import importlib

from PySide2.QtCore import Qt, QSize, Signal
from PySide2.QtGui import QStandardItemModel, QStandardItem, QIcon
from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QListView, QPushButton, QToolButton, QDialog, QLineEdit, QLabel, QCheckBox, QHBoxLayout, QSpacerItem
)
import ui.collapsibleSection as collapsibleSection

importlib.reload(collapsibleSection)

Section = collapsibleSection.Section

try:
    import PrismInit
except ImportError:
    PrismInit = None

class mainWindow(QDialog):

    confirm = Signal(dict)

    def __init__(self, parent=hou.qt.mainWindow()):
        super(mainWindow, self).__init__(parent)
        self.configureWindow()
        self.widgets()
        self.layouts()
        self.connections()
        
    def configureWindow(self):
        self.setWindowTitle("Fast Material Builder")
        self.setMinimumSize(600,230)

    def get_icon_path(self, icon_name):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        gtToolsDir = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
        icon_path = os.path.join(gtToolsDir, "config", "icons", icon_name)
        return icon_path
   
    def widgets(self):
        tooltipShort = 5000
        tooltipLong = 8000

        # Base Material Name
        self.baseMaterialNameTitle = QLabel("Base Material Name")
        self.baseMaterialName = QLineEdit()
        self.baseMaterialName.setFocus()
        self.baseMaterialName.setPlaceholderText("Material Name")
        self.baseMaterialName.setToolTip("The name of the base material. It should be similar to the name of the textures")
        self.baseMaterialName.setToolTipDuration(tooltipLong)

        # Folder Path
        self.folderTitle = QLabel("Texture Folder Path")
        self.folderSearch = QLineEdit()
        self.folderSearch.setFocus()
        self.folderSearch.setPlaceholderText("Texture Folder")
        self.folderSearch.setToolTip(" The path of the texture folder")
        self.folderSearch.setToolTipDuration(tooltipShort)
        
        # Folder Chooser Button
        self.floatingChooserBut = QPushButton()
        self.floatingChooserBut.setStyleSheet("QPushButton { margin: 1px; border: none;}")
        self.floatingChooserBut.setFixedSize(45, 45)
        floatingChooserIconPath = self.get_icon_path("chooser_folder.svg")
        self.floatingChooserIcon = QIcon(floatingChooserIconPath)
        self.floatingChooserBut.setIcon(self.floatingChooserIcon)
        self.floatingChooserBut.setIconSize(QSize(30, 30))

        # Separator
        self.sep = hou.qt.Separator()

        #USD Preview Checkbox
        self.chckUSDPreview = QCheckBox("Create a USD Preview Material")
        self.chckUSDPreview.setCheckable(True)
        self.chckUSDPreview.setChecked(True)
        self.chckUSDPreview.setToolTip("Create a USD Preview Material for the Solaris viewport")
        self.chckUSDPreview.setToolTipDuration(tooltipShort)

        #Relative path checkbox
        self.chckrelativePath = QCheckBox("Use relative path")
        self.chckrelativePath.setCheckable(True)
        self.chckrelativePath.setChecked(True)
        self.chckrelativePath.setToolTip("Replace the textures absolute paths by their environment variables relatives")
        self.chckrelativePath.setToolTipDuration(tooltipLong)

        #Material Engines List Title
        self.materialEnginesTitle = QLabel("Material List")
        self.materialEnginesTitle.setToolTip("Select the materials for the different render engines")
        self.materialEnginesTitle.setToolTipDuration(tooltipShort)

        #Material Engines List Selection List
        self.selMaterialEngines = QListView()
        Materialsmodel = QStandardItemModel(self.selMaterialEngines)
        materials = ["Karma Material", "MaterialX"]
        for index, name in enumerate(materials):
            material = QStandardItem(name)
            material.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)

            if index == 0:
                material.setCheckState(Qt.Checked)
            else:
                material.setCheckState(Qt.Unchecked)
            Materialsmodel.appendRow(material)

        self.selMaterialEngines.setModel(Materialsmodel)

        # Advanced options section
        self.advancedOptionSec = Section("Advanced options", self)

        # OK and Cancel Buttons
        self.okBut = QPushButton("OK")
        self.cancelBut = QPushButton("Cancel")

    
    def layouts(self):
        self.mainLyt = QVBoxLayout(self)

        self.materialLayout = QHBoxLayout(self)
        self.materialLayout.addWidget(self.baseMaterialNameTitle)
        self.materialLayout.addWidget(self.baseMaterialName)

        self.folderLyt = QHBoxLayout(self)
        self.folderLyt.addWidget(self.folderTitle)
        self.folderLyt.addWidget(self.folderSearch)
        self.folderLyt.addWidget(self.floatingChooserBut)

        self.buttonsLyt = QHBoxLayout(self)
        self.buttonsLyt.addWidget(self.cancelBut)
        self.buttonsLyt.addWidget(self.okBut)

        self.mainLyt.addLayout(self.materialLayout)
        self.mainLyt.addLayout(self.folderLyt)
        self.mainLyt.addWidget(self.chckUSDPreview)

        # Add widgets to advanced options sections
        advancedOptionsLyt = QVBoxLayout()
        advancedOptionsLyt.setContentsMargins(0,0,0,0)
        advancedOptionsLyt.addWidget(self.materialEnginesTitle)
        advancedOptionsLyt.addWidget(self.selMaterialEngines)
        advancedOptionsLyt.addWidget(self.chckrelativePath)

        self.advancedOptionSec.setContentLayout(advancedOptionsLyt)

        self.mainLyt.addWidget(self.advancedOptionSec)

        self.mainLyt.addLayout(self.buttonsLyt)

    def connections(self):
        self.floatingChooserBut.clicked.connect(self.folderChooser)

        self.cancelBut.clicked.connect(self.close)
        self.okBut.clicked.connect(self.exportSettings)
        #self.okBut.clicked.connect(self.close)

    def folderChooser(self):
        # Get the current Prism Project
        if PrismInit:
            startDirectory = "$PRISMJOB"
            prismProject = hou.getenv("PRISMJOB")
        
        # Set the texture directory with file input
        houdiniJob = hou.getenv("JOB")
        hipDir = os.path.dirname(hou.hipFile.path())
        # Check if the JOB variable is set
        winUser = getpass.getuser()
        if houdiniJob == "C:/Users/" + winUser:
            startDirectory = "$HIP"
        else:
            startDirectory = "$JOB"

        textureDir = hou.ui.selectFile(file_type = hou.fileType.Directory, start_directory = startDirectory, title = "Select the texture folder", pattern = "*")
        self.folderSearch.setText(textureDir)
   
    def exportSettings(self):
        # Get the material list to be built
        materialList = []
        model = self.selMaterialEngines.model()
        for row in range(model.rowCount()):
            item = model.item(row)
            if item.checkState() == Qt.Checked:
                materialList.append(item.text())

        # Get the texture folder and the material base name
        inputMaterial = self.baseMaterialName.text()
        textureFolder = self.folderSearch.text()

        # Activate relative paths
        if self.chckrelativePath.isChecked():
            relativePath = True
        else:
            relativePath = False

        # Create USD Preview Material
        if self.chckUSDPreview.isChecked():
            materialList.append("USD Preview Material")
            
        settings = { "materialName" : inputMaterial,
                     "textureFolder" : textureFolder,
                     "materialList" : materialList,
                     "relativePath" : relativePath,
                    }
        self.confirm.emit(settings)

class ChannelSelWindow(QDialog):

    launch = Signal(bool)

    def __init__(self):
        super().__init__(parent=mainWindow)
        self.configureWindow()
        self.widgets()
    
    def configureWindow(self):
        self.setWindowTitle("Choose the textures channels")
        self.setMinimumSize(600,300)

    def widgets(self):
        # Channel selection list
        self.channelSelList = QListView()
        channelModel = QStandardItemModel(self.channelSelList)