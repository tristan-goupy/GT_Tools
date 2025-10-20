import os, platform, os.path
import hou

def getBinary(binary):
    # Locate Houdini root path
    root = None
    binaryFolder = None
    executable = None
    slash = None

    # Determine OS filepaths
    if platform.system() == "Linux":

        root = ""
        houdiniPaths = hou.houdiniPath()
        #Check for Houdini bin folder (this is to make the search adaptable to each inviduals' Houdini installation)
        for path in houdiniPaths:
            if "bin" in path:
                root = path
                break
        
        slash = "/"
        binaryFolder = slash + "bin" + slash
        executable = binary + " "

        #Linux Houdini root path is /opt/hfs{version}/houdini
        root = root.rpartition(slash)[0]

    # Filepaths for Windows
    elif platform.system() == "Windows":

        root = ""
        houdiniPaths = hou.houdiniPath()
        #Check for Houdini bin folder (this is to make the search adaptable to each inviduals' Houdini installation)
        for path in houdiniPaths:
            if "bin" in path:
                root = path
                break

        root.replace("/", "\\")
        slash = "\\"
        binaryFolder = slash
        executable = binary + ".exe"

    binaryString = root + binaryFolder + executable + " "
    return binaryString