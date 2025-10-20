import hou
import os
from pxr import Usd, UsdGeom, Sdf

houdiniVersion = hou.applicationVersionString()

OCIO_ACTIVE_VIEWS = os.getenv("OCIO_ACTIVE_VIEWS")
OCIO_ACTIVE_DISPLAYS = os.getenv("OCIO_ACTIVE_DISPLAYS")
#print("OCIO_ACTIVE_DISPLAYS:" + OCIO_ACTIVE_DISPLAYS)
if OCIO_ACTIVE_VIEWS==None or OCIO_ACTIVE_VIEWS=="ACES 1.0 - SDR Video":
    colorspace = "Rec.1886 Rec.709 - Display"
else:
    colorspace = OCIO_ACTIVE_VIEWS
print("Colorspace used: " + colorspace)

def getProductName():
    sampleFrame = hou.frame()
    stage = Usd.Stage.Open
    renderProductPath = stage.Get()
    renderProducts = []
    pathsRenderProducts = [renderProductPath]
    for path in pathsRenderProducts:
        primPath = str(path)
        renderProducts.append(primPath)

    renderOutputList = []

    for renderProduct in renderProducts:
        prim = stage.GetPrimAtPath(renderProduct)
        renderOutputProductName = str(prim.GetAttribute("productName").Get(sampleFrame))
        if "Deep" not in renderOutputProductName.split("/")[-1]:
            renderOutputList.append(renderOutputProductName)

    return renderOutputList

def getOutputLocation():
    renderOutputList = getProductName()
    renderOutputListSplit = renderOutputList.replace("\\", "/").split("/")
    renderOutputFolder = "/".join(renderOutputListSplit[0:-2])+"/"+ renderOutputListSplit[-2] + "(Overlay)(jpg)"
    renderOutputSaveFile = "/".join(renderOutputListSplit[0:-2])+"/"+renderOutputListSplit[-2]+"(Overlay)(jpg)"+"/"+renderOutputListSplit[-1].split(".")[0]+"."+renderOutputListSplit[-1].split(".")[-2]

    outputList = [renderOutputFolder, renderOutputSaveFile]

    return outputList

def createFolderIfDontExist(folderPath=None):
    if folderPath == None:
        pass
    else:
        folderPathSplit = folderPath.split("/")

        if folderPathSplit[8] == "Renders" and folderPathSplit[9] == "3dRender":
            if os.path.exists(folderPath) != True:
                os.makedirs(folderPath)
            else:
                pass
        else:
            print("Sanity check folder 1 test: " + folderPathSplit[8])
            print("Sanity check folder 2 test: " + folderPathSplit[9])

def renderStatsOverlay(preset = 0):
    renderOutputList = getProductName()
    renderOutputFolder = getOutputLocation()[0]
    renderOutputSaveFile = getOutputLocation()[1]
    createFolderIfDontExist(folderPath=renderOutputFolder)

    preset_01 = '"C:/Program Files/Side Effects Software/Houdini" + houdiniVersion + "bin/renderstatoverlay.bat" --colorspace' + '"' + colorspace + '"' + '"' + renderOutputList[0] + '"' + '"' + renderOutputSaveFile + ".jpg"'"'+"--overlay --template" + '"D:/Tristan_Goupy/5_PFE/Pipeline/Sripts/renderStatsOverlay/render_stats_overlay.json"'
    preset_02 = "Pause"

    presets = [preset_01, preset_02]
    cmd = presets[preset]
    print(cmd)
    return cmd

'''def renderStatsReports(preset = 1):
    renderOutputList = getProductName()
    renderOutputFolder = getOutputLocation()[0]
    renderOutputSaveFile = getOutputLocation()[1]
    createFolderIfDontExist(folderPath=renderOutputFolder)

    preset_01 = '"C:/Program Files/Side Effects Software/Houdini '+houdiniVersion+'/bin/renderstatsreport.bat" --color-space '+'"'+colorspace+'" '+'"'+renderOutputList[0]+'"'
    preset_02 = '"C:/Program Files/Side Effects Software/Houdini '+houdiniVersion+'/bin/renderstatsreport.bat" --color-space '+'"'+colorspace+'" '+'"'+renderOutputList[0]+'"'+' "'+renderOutputSaveFile+".html"+'"'

    presets = [preset_01, preset_02]
    cmd = presets[preset - 1]
    print(cmd)
    return cmd'''

run = renderStatsOverlay(preset=0)