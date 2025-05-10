import os

def getIconPath(icon_name):
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    gtToolsDir = os.path.abspath(os.path.join(scriptDir, "..", "..", ".."))
    iconPath = os.path.join(gtToolsDir, "config", "icons", icon_name)
    return iconPath