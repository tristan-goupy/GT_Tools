import hou

from PySide2.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget

class materialBuilder_menu(QMainWindow):
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle('GT Fast Material Builder')
        self.resize(250,100)