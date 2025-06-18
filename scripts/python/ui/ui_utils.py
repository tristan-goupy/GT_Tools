import os
from PySide2.QtGui import QIcon, QPixmap, QColor, QPainter
from PySide2.QtSvg import QSvgRenderer 

def getIconPath(icon_name):
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    gtToolsDir = os.path.abspath(os.path.join(scriptDir, "..", "..", ".."))
    iconPath = os.path.join(gtToolsDir, "config", "icons", icon_name)
    return iconPath

def loadSVGIcon(svg_name, size):
    iconPath = getIconPath(svg_name)
    renderer = QSvgRenderer(iconPath)
    pixmap = QPixmap(size)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)