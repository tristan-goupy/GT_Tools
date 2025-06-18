####################### GT_textureConvert #######################

# Imports
import os, subprocess, re

from utils import helpers
from utils.decorators import err_catcher

#PySide2 and Qt imports
from PySide2.QtCore import Signal
from PySide2.QtWidgets import (QApplication, QDialog)

# UI Imports
from ui import GT_textureConverter_ui as ui

# Importlib temp
import importlib
importlib.reload(ui)
importlib.reload(helpers)

# Global variables
FILTER = [".png", ".jpg", ".jpeg", ".tif", ".tiff", ".exr"]
# Texture Converter code

class textureConverter(QDialog):
    def __init__(self, parent = QApplication.activeWindow()):
        super(textureConverter, self).__init__(parent)
        
        #Instantiate UI
        self.converterWindow = ui.TextureConverterWindow(self)
        self.converterWindow.start.connect(self.startConversion)

        self.converterWindow.show()

    @err_catcher(name = __name__, silent=True)
    def startConversion(self, textureDirectory, renderEngine, texturePattern=[]):
        if textureDirectory != "":

            filesToConvert = []
            for engine in renderEngine:
                if "Karma" in renderEngine:
                    executable = helpers.getBinary("iconvert")
                    extension = ".rat"
                if not executable:
                    raise Exception("iconvert not found. Please check your Houdini installation.")
                # Handle UDIM patterns
                
                if texturePattern != []:
                    for pattern in texturePattern:
                        if "<UDIM>" in pattern:
                            # Find all matching UDIM files
                            basePattern = pattern.replace("<UDIM>", r"\d{4}")
                            regex = re.compile(basePattern.replace(".", r"\."))
                            for fileName in os.listdir(self.absTextureDir):
                                if regex.match(fileName) and any(fileName.endswith(ext) for ext in FILTER):
                                    inputFile = os.path.join(self.absTextureDir, fileName)
                                    outputFile = os.path.splitext(inputFile)[0] + extension
                                    if not os.path.isfile(outputFile):
                                        filesToConvert.append((inputFile, outputFile))
                else:
                    for fileName in os.listdir(textureDirectory):
                        if not any(fileName.endswith(ext) for ext in FILTER):
                            continue
                        inputFile = os.path.join(textureDirectory, fileName)
                        outputFile = os.path.splitext(inputFile)[0] + extension
                        if not os.path.isfile(outputFile):
                            filesToConvert.append((inputFile, outputFile))
        
            progress = ui.progressConversionWindow(label = "Converting textures...", maximum = len(filesToConvert), parent=self)
            for i, (inputFile, outputFile) in enumerate(filesToConvert):
                if progress.wasCanceled():
                    break
                command = f'"{executable}" "{inputFile}" "{outputFile}"'
                subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
                progress.setValue(i + 1)
                QApplication.processEvents()
            progress.close()
    
            self.converterWindow.close()
        else:
            raise Exception("Plase select a valid texture directory.")