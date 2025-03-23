import os
import sys
import getpass
import hou, voptoolutils
import re

try:
    import PrismInit
except ImportError:
    PrismInit = None

def materialBuilder():
    # Material menu chooser
    
    # Create the masks for the different subnets
    karmaMask = voptoolutils.KARMAMTLX_TAB_MASK
    # Dictionary to map channels to their possible names
    channelNames = {
        'BaseColor': ['BaseColor', 'Diffuse', 'Albedo', 'Color'],
        'Roughness': ['Roughness', 'Rough'],
        'Specular': ['Specular'],
        'Opacity': ['Opacity', 'Alpha'],
        'Metalness': ['Metalness', 'Metallic'],
        'Normal': ['Normal'],
        'AO': ['AO', 'AmbientOcclusion'],
        'Emissive': ['Emissive'],
        'Glossiness': ['Glossiness'],
        'Displacement': ['Displacement'],
        'Bump': ['Bump'],
        'Height': ['Height'],
        'Reflection': ['Reflection']
    }
    # Set the base name with prompt 
    baseName = hou.ui.readInput(initial_contents = "Spartan_Chest", message = "Set the base material name", buttons=["OK", "Cancel"], title = "Material Base Name")

    if baseName[0] == 0 and baseName[1] != "":
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
                
        textureDir = hou.ui.selectFile(file_type = hou.fileType.Directory, start_directory = startDirectory, title = "Select the texture directory", pattern = "*")
        if textureDir != "":

            #Change the relative path to the absolute path
            if PrismInit and "$PRISMJOB" in textureDir:
                absTextureDir = textureDir.replace("$PRISMJOB", prismProject)
            elif "$JOB" in textureDir:
                absTextureDir = textureDir.replace("$JOB", houdiniJob)
            elif "$HIP" in textureDir:
                absTextureDir = textureDir.replace("$HIP", hipDir)

            # Get the current context
            desktop = hou.ui.curDesktop()
            pane = desktop.paneTabOfType(hou.paneTabType.NetworkEditor)
            currentNetwork = pane.pwd()

            # Create Karma material subnet
            kmaNet = currentNetwork.createNode("subnet", "KMA_" + baseName[1] + "_MTL")
            voptoolutils._setupMtlXBuilderSubnet(kmaNet, "karmamaterial", "karmamaterial", karmaMask, "Karma Material Builder", "kma")

            # Rename the mtlxstandard_surface node
            surfaceNode = kmaNet.node("mtlxstandard_surface")
            surfaceNode.setName(baseName[1] + "_surface")
            dispNode = kmaNet.node("mtlxdisplacement")

            # Create mtlxtexcoord node inside the subnet
            UVNode = kmaNet.createNode("mtlxtexcoord", "UV")
            UVNode.parm("signature").set("vector2")
            transform2DNode = kmaNet.createNode("usdtransform2d")
            transform2DNode.setInput(0, UVNode, 0)

            # Identify channels with UDIM textures
            udimChannels = {}
            for texture in os.listdir(absTextureDir):
                for channel, names in channelNames.items():
                    if baseName[1] in texture and any(name in texture for name in names) and ".rat" not in texture:
                        # Check for UDIM pattern
                        udim_match = re.search(r'\.\d{4}\.', texture)
                        if udim_match:
                            texturePattern = texture.replace(udim_match.group(0), ".<UDIM>.")
                            udimChannels[channel] = texturePattern
                        else:
                            texturePattern = texture
                            udimChannels[channel] = texturePattern

            # Create channel selection menu
            foundChannels = list(udimChannels.keys())
            channelSel = hou.ui.selectFromList(choices = foundChannels, default_choices = list(range(len(foundChannels))), column_header = "Channels", message = "Select the channels you want to import", 
                                               num_visible_rows = len(foundChannels), title = "Choose textures channels", clear_on_cancel = True, width = 5, height = 10)
            
            # Add textures nodes for selected channels
            for index in channelSel:
                channel = foundChannels[index]
                texturePattern = udimChannels[channel]
                # Create texture node
                textureNode = kmaNet.createNode("mtlximage", channel)
                indexOfChannel = list(channelNames.keys()).index(channel)
                
                # Path to the texture channel
                pathToTexture = os.path.join(textureDir, texturePattern)
                
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
                # Roughness
                if indexOfChannel == 1:
                    surfaceNode.setInput(6, textureNode)
                # Specular
                if indexOfChannel == 2:
                    surfaceNode.setInput(4, textureNode)
                # Opacity
                if indexOfChannel == 3:
                    surfaceNode.setInput(38, textureNode)
                # Metalness
                if indexOfChannel == 4:
                    surfaceNode.setInput(3, textureNode)
                # Normal
                if indexOfChannel == 5:
                    normalMapNode = kmaNet.createNode("mtlxnormalmap")
                    normalMapNode.setInput(0, textureNode)
                    surfaceNode.setInput(40, normalMapNode)
                # Emissive
                if indexOfChannel == 7:
                    surfaceNode.setInput(35, textureNode)
                # Glossiness
                if indexOfChannel == 8:
                    glossInvertNode = kmaNet.createNode("mtlxinvert")
                    glossInvertNode.setInput(0, textureNode)
                    surfaceNode.setInput(6, glossInvertNode)
                # Displacement
                if indexOfChannel == 9:
                    dispNode.setInput(0, textureNode)
                # Bump
                if indexOfChannel == 10:
                    bumpNode = kmaNet.createNode("mtlxbump")
                    bumpNode.setInput(0, textureNode)
                    surfaceNode.setInput(40, bumpNode)
                # Height
                if indexOfChannel == 11:
                    heightToNormalNode = kmaNet.createNode("mtlxheighttonormal")
                    heightToNormalNode.setInput(0, textureNode)
                    if kmaNet.node("mtlxnormalmap") is None:
                        normalMapNode = kmaNet.createNode("mtlxnormalmap")
                        normalMapNode.setInput(0, heightToNormalNode)
                        surfaceNode.setInput(40, normalMapNode)
                    else:
                        kmaNet.node("mtlxnormalmap").setInput(3, heightToNormalNode)
            
            # Multiply AO with BaseColor
            if kmaNet.node("BaseColor") is not None and kmaNet.node("AO") is not None:
                aoMultNode = kmaNet.createNode("mtlxmultiply")
                aoMultNode.setInput(0, kmaNet.node("BaseColor"))
                aoMultNode.setInput(1, kmaNet.node("AO"))
                surfaceNode.setInput(1, aoMultNode)
            
            # If there is no displacement map, remove the displacement node
            if kmaNet.node("Displacement") is None:
                kmaNet.node("mtlxdisplacement").destroy()
            
            kmaNet.layoutChildren()
            kmaNet.moveToGoodPosition()
