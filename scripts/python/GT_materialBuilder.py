import os
import hou, voptoolutils
import re

from PySide2.QtCore import Signal
from PySide2.QtWidgets import (QApplication, QDialog)
from ui import GT_materialBuilder_ui as ui

try:
    import PrismInit
except ImportError:
    PrismInit = None

class MainApp(QDialog):

    channelsExport = Signal(list)

    def __init__(self, parent = QApplication.activeWindow()):
        super(MainApp, self).__init__(parent)

        # Initialize project start directories
        # Prism Project
        if PrismInit:
            self.prismProject = hou.getenv("PRISMJOB")

        # Houdini Job
        self.houdiniJob = hou.getenv("JOB")
        self.hipDir = os.path.dirname(hou.hipFile.path())

        # Create the masks for the different material subnets
        self.karmaSetup = [voptoolutils.KARMAMTLX_TAB_MASK,'karmamaterial','Karma Material Builder','kma']
        self.mtlxSetup = [voptoolutils.MTLX_TAB_MASK, 'mtlxmaterial', 'MaterialX Builder', 'mtlx']
        self.usdSetup = [voptoolutils.USDPREVIEW_TAB_MASK, 'usdmaterial', 'USD Preview Material Builder', '']

        # Dictionary to map channels to their possible names
        self.channelNames = {
            'BaseColor': ['BaseColor', 'Diffuse', 'Albedo', 'Color', 'DIFF', 'BC'],
            'AO': ['AmbientOcclusion', 'AO'],
            'Specular': ['Specular', 'SPC'],
            'SpecularColor': ['SpecularColor', 'SpecColor', 'SPCC'],
            'SpecularRoughness': ['Roughness', 'Rough', 'SPCR'],
            'Metallic': ['Metalness', 'Metallic', 'MTC'],
            'Normal': ['Normal', 'NRM'],
            'Bump': ['Bump', 'BMP'],
            'Displacement': ['Displacement', 'DISP'],
            'Opacity': ['Opacity', 'Alpha', 'OPA'],
            'Subsurface': ['Subsurface', 'SSS'],
            'SubsurfaceColor': ['SubsurfaceColor', 'SSC'],
            'SubsurfaceRadius': ['SubsurfaceRadius', 'SSR'],
            'Emissive': ['Emissive', 'Emission', 'EMIS'],
            'EmissiveColor': ['EmissiveColor', 'EmissionColor', 'EMIC'],
            'Glossiness': ['Glossiness', 'GLS'],
            'Height': ['Height', 'HGT'],
            'Reflection': ['Reflection', 'RFL']
            }

        # Instantiate UI
                
        self.mainWindow = ui.mainWindow(parent = self)
        self.channelSelWindow = ui.channelSelWindow(parent = self)
        
        self.mainWindow.confirm.connect(self.scanDirectory)
        self.channelSelWindow.launch.connect(self.materialBuilder)

        self.mainWindow.show()
 
    def scanDirectory(self, settings):
        # Get all the settings from the UI
        self.textureDir = settings.get("textureFolder", "")
        self.baseName = settings.get("materialName", "")
        self.materialList = settings.get("materialList", "")
        self.relativePathParm = settings.get("relativePath", True)

        if self.textureDir != "" and self.baseName != "":
            #Change the relative path to the absolute path
            if PrismInit and "$PRISMJOB" in self.textureDir:
                self.absTextureDir = self.textureDir.replace("$PRISMJOB", self.prismProject)
            elif "$JOB" in self.textureDir:
                self.absTextureDir = self.textureDir.replace("$JOB", self.houdiniJob)
            elif "$HIP" in self.textureDir:
                self.absTextureDir = self.textureDir.replace("$HIP", self.hipDir)
            else:
                self.absTextureDir = self.textureDir

            if not os.path.isdir(self.absTextureDir):
                self.channelsExport.emit([])
                return
            # Identify channels with UDIM textures
            self.udimChannels = {}
            for texture in os.listdir(self.absTextureDir):
                for channel, names in self.channelNames.items():
                    if self.baseName in texture and any(name in texture for name in names) and ".rat" not in texture:
                        # Check for UDIM pattern
                        udim_match = re.search(r'\.\d{4}\.', texture)
                        if udim_match:
                            texturePattern = texture.replace(udim_match.group(0), ".<UDIM>.")
                            self.udimChannels[channel] = texturePattern
                        else:
                            texturePattern = texture
                            self.udimChannels[channel] = texturePattern

            # Create channel selection menu
            self.foundChannels = list(self.udimChannels.keys())
            self.channelSelWindow.populateChannelList(self.foundChannels)

            if len(self.foundChannels) != 0 and self.materialList != []:
                self.channelSelWindow.show()
            

    def materialBuilder(self, getSelectedChannels):
            channelSel = getSelectedChannels
            # Get the current context
            desktop = hou.ui.curDesktop()
            pane = desktop.paneTabOfType(hou.paneTabType.NetworkEditor)
            currentNetwork = pane.pwd()

            # Create subnets depending on context
            def contextHandler(searchedNode: str):
                selNodes = hou.selectedNodes()
                if len(list(selNodes)) != 0:
                    if searchedNode in str(selNodes[0].type):
                        target = selNodes[0]
                    else:
                        target = currentNetwork.createNode(searchedNode)
                else:
                    target = currentNetwork.createNode(searchedNode)
                return target

            netContext = str(pane.pwd().childTypeCategory())
            if "Vop" in netContext:
                target = currentNetwork
            elif "Vop" not in netContext and "Lop" not in netContext:
                target = contextHandler("matnet")
            elif "Vop" not in netContext and "Lop" in netContext:
                target = contextHandler("materiallibrary")

            def VopNetSetup(matNet:str, materialType:str, matMask:str, folderLabel:str, renderCtxt:str):
                voptoolutils._setupMtlXBuilderSubnet(matNet, materialType, materialType, matMask, folderLabel, renderCtxt)

                # Create Karma material subnet
            def createRenderMaterials(matSetup, usdSetup = self.usdSetup):
                matNet = target.createNode("subnet", matPrefix + self.baseName + "_MTL")
                if matSetup != usdSetup:
                    VopNetSetup(matNet, matSetup[1], matSetup[0], matSetup[2], matSetup[3])

                # Rename the mtlxstandard_surface node
                surfaceNode = matNet.node("mtlxstandard_surface")
                surfaceNode.setName(self.baseName + "_surface")
                dispNode = matNet.node("mtlxdisplacement")

                # Create mtlxtexcoord node inside the subnet
                UVNode = matNet.createNode("mtlxtexcoord", "UV")
                UVNode.parm("signature").set("vector2")
                transform2DNode = matNet.createNode("usdtransform2d")
                transform2DNode.setInput(0, UVNode, 0)
                
                # Add textures nodes for selected channels
                for index in channelSel:
                    channel = self.foundChannels[index]
                    texturePattern = self.udimChannels[channel]
                    # Create texture node
                    textureNode = matNet.createNode("mtlximage", channel)
                    indexOfChannel = list(self.channelNames.keys()).index(channel)
                    
                    # Path to the texture channel
                    if self.relativePathParm is True:
                        pathToTexture = os.path.join(self.textureDir, texturePattern)
                    else:
                        pathToTexture = os.path.join(self.absTextureDir, texturePattern)
                        
                    # Set path to texture
                    textureNode.parm("file").set(pathToTexture)
                        
                    # Check and set colorspace
                    if 'sRGB' in texturePattern:
                        textureNode.parm("filecolorspace").set("srgb_tx")
                    elif 'ACEScg' in texturePattern:
                        textureNode.parm("filecolorspace").set("ACEScg")
                    else:
                        textureNode.parm("filecolorspace").set("Raw")
                        
                    # Set the signature
                    if channel == 'BaseColor' or channel == 'Opacity' or channel == 'Emissive':
                        textureNode.parm("signature").set("color3")
                    elif channel == 'Roughness' or channel == 'Height' or channel == 'Metalness' or channel == 'AO' or channel == 'Specular' or channel == 'Displacement':
                        textureNode.parm("signature").set("float")
                    elif channel == 'Normal':
                        textureNode.parm("signature").set("vector3")
                        
                    # Connect the texture node to the UV node
                    textureNode.setInput(3, transform2DNode)
                        
                    # Connect the texture node to the surface node
                    # BaseColor
                    if indexOfChannel == 0:
                        surfaceNode.setInput(1, textureNode)
                    # Specular
                    if indexOfChannel == 2:
                        surfaceNode.setInput(4, textureNode)
                    # SpecularColor
                    if indexOfChannel == 3:
                        surfaceNode.setInput(5, textureNode)
                    # SpecularRoughness
                    if indexOfChannel == 4:
                        surfaceNode.setInput(6, textureNode)
                    # Metallic
                    if indexOfChannel == 5:
                        surfaceNode.setInput(3, textureNode)
                    # Normal
                    if indexOfChannel == 6:
                        normalMapNode = matNet.createNode("mtlxnormalmap")
                        normalMapNode.setInput(0, textureNode)
                        surfaceNode.setInput(40, normalMapNode)
                    # Bump
                    if indexOfChannel == 7:
                        bumpNode = matNet.createNode("mtlxbump")
                        bumpNode.setInput(0, textureNode)
                        surfaceNode.setInput(40, bumpNode)
                    # Displacement
                    if indexOfChannel == 8:
                        dispNode.setInput(0, textureNode)
                    # Opacity
                    if indexOfChannel == 9:
                        surfaceNode.setInput(38, textureNode)
                    # Subsurface
                    if indexOfChannel == 10:
                        surfaceNode.setInput(29, textureNode)
                    # SubsurfaceColor
                    if indexOfChannel == 11:
                        surfaceNode.setInput(30, textureNode)
                    # SubsurfaceRadius
                    if indexOfChannel == 12:
                        surfaceNode.setInput(31, textureNode)
                    # Emissive
                    if indexOfChannel == 13:
                        surfaceNode.setInput(34, textureNode)
                    # EmissiveColor
                    if indexOfChannel == 14:
                        surfaceNode.setInput(35, textureNode)
                    # Glossiness
                    if indexOfChannel == 15:
                        glossInvertNode = matNet.createNode("mtlxinvert")
                        glossInvertNode.setInput(0, textureNode)
                        surfaceNode.setInput(6, glossInvertNode)
                    # Height
                    if indexOfChannel == 16:
                        heightToNormalNode = matNet.createNode("mtlxheighttonormal")
                        heightToNormalNode.setInput(0, textureNode)
                        if matNet.node("mtlxnormalmap") is None:
                            normalMapNode = matNet.createNode("mtlxnormalmap")
                            normalMapNode.setInput(0, heightToNormalNode)
                            surfaceNode.setInput(40, normalMapNode)
                        else:
                            matNet.node("mtlxnormalmap").setInput(3, heightToNormalNode)
                    
                # Multiply AO with BaseColor
                if matNet.node("BaseColor") is not None and matNet.node("AO") is not None:
                        aoMultNode = matNet.createNode("mtlxmultiply")
                        aoMultNode.setInput(0, matNet.node("BaseColor"))
                        aoMultNode.setInput(1, matNet.node("AO"))
                        surfaceNode.setInput(1, aoMultNode)
                    
                # If there is no displacement map, remove the displacement node
                if matNet.node("Displacement") is None:
                        matNet.node("mtlxdisplacement").destroy()
                        displacementOutput = matNet.node("displacement_output")
                        if displacementOutput:
                            displacementOutput.destroy()                    
                    
                matNet.layoutChildren()
                matNet.moveToGoodPosition()

            def createUSDPreviewMat(matSetup):
                # Create USD Material Preview Subnet
                matNet = target.createNode("subnet", matPrefix + self.baseName + "_MTL")
                voptoolutils._setupUsdPreviewBuilderSubnet(matNet, matSetup[1], matSetup[1], matSetup[0], matSetup[2])
                
                # Rename the surface node
                surfaceNode = matNet.node("usdpreviewsurface")
                surfaceNode.setName(self.baseName + "_surface")

                # Add the UV node
                UVNode = matNet.createNode("usdprimvarreader",'UV')
                UVNode.parm("signature").set("float2")
                UVNode.parm("varname").set("st")
                # Add a transform2D Node
                transform2DNode = matNet.createNode("usdtransform2d")
                transform2DNode.setInput(0, UVNode, 0)

                #Iterate through each channel
                for index in channelSel:
                    channel = self.foundChannels[index]
                    texturePattern = self.udimChannels[channel]

                    textureNode = matNet.createNode("usduvtexture", channel)
                    indexOfChannel = list(self.channelNames.keys()).index(channel)

                    # Path to the texture channel
                    if self.relativePathParm is True:
                        pathToTexture = os.path.join(self.textureDir, texturePattern)
                    else:
                        pathToTexture = os.path.join(self.absTextureDir, texturePattern)
                        
                    # Set path to texture
                    textureNode.parm("file").set(pathToTexture)

                    # Check and set colorspace
                    if 'sRGB' in texturePattern:
                        textureNode.parm("sourceColorSpace").set("sRGB")
                    else:
                        textureNode.parm("sourceColorSpace").set("raw")

                    # Connect the texture node to the UV node
                    textureNode.setInput(1, transform2DNode)

                    # Connect the texture node to the surface node
                    # BaseColor
                    if indexOfChannel == 0:
                        surfaceNode.setInput(0, textureNode, 4)
                    # Ambient Occlusion
                    if indexOfChannel == 1:
                        textureNode.destroy() # USD Preview Surface is currently bugged with Python
                    # Specular
                    if indexOfChannel == 2:
                        textureNode.destroy()
                    # SpecularRoughness
                    if indexOfChannel == 4:
                        surfaceNode.setInput(5, textureNode, 0)
                    # Metallic
                    if indexOfChannel == 5:
                        surfaceNode.setInput(4, textureNode, 0)
                    # Normal
                    if indexOfChannel == 6:
                        surfaceNode.setInput(10, textureNode, 4)
                    # Opacity
                    if indexOfChannel == 9:
                        surfaceNode.setInput(8, textureNode, 0)
                    # EmissiveColor
                    if indexOfChannel == 14:
                        surfaceNode.setInput(1, textureNode, 4)

                matNet.layoutChildren()
                matNet.moveToGoodPosition()

            # Iterate through each material
            if channelSel != [] and self.materialList != []:
                for material in self.materialList:
                    if "Karma" in material:
                        matSetup = self.karmaSetup
                        matPrefix = 'KMA_'
                        createRenderMaterials(matSetup)
                    elif "MaterialX" in material:
                        matSetup = self.mtlxSetup
                        matPrefix = 'MTLX_'
                        createRenderMaterials(matSetup)
                    elif "USD Preview Material" in material:
                        matSetup = self.usdSetup
                        matPrefix = 'USD_'
                        createUSDPreviewMat(matSetup)
                self.mainWindow.close()
