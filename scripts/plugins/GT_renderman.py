from scripts import register_plugin
import os, platform
from utils import helpers

class RendermanPlugin:
    name = "RendermanPlugin"
    version = "0.1.0"

    def __init__(self):
        self.is_available = self.check_renderman_installed()

    def check_renderman_installed(self):
        rendermanPath = os.getenv("RMANTREE")
        houdiniRenderman = os.getenv("RFHTREE")

        if not rendermanPath or not os.path.exists(rendermanPath):
            raise ImportError("Renderman not found (missing RMANTREE environment variable).")
        if not houdiniRenderman or not os.path.exists(houdiniRenderman):
            raise ImportError("Renderman for Houdini not found (missing RFHTREE environment variable).")
        
        print(f"Renderman found: {rendermanPath}")
        return True
    
    def run(self):
        if not self.is_available:
            raise RuntimeError("Renderman not available. Cannot execute plugin actions.")
        def get_executable(binary):
            # Return the path to txmake
            root = None
            binaryFolder = None
            executable = None
            slash = None

            if platform.system() == "Linux":
                root = os.getenv("RMANTREE")
                slash = "/"
                binaryFolder = slash + "bin" + slash
                executable = binary + " "
            elif platform.system() == "Windows":
                root = os.getenv('RMANTREE').replace("/", "\\")
                slash = "\\"
                binaryFolder = slash
                executable = binary + ".exe"
            
            binaryString = root + binaryFolder + executable + ""
            return binaryString

        def get_extension(self):
            return ".tex"

register_plugin(RendermanPlugin.name, RendermanPlugin)