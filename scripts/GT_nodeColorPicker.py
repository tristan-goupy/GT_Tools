import hou

def nodeColorPicker():
    sel = hou.selectedItems()

    if len(sel) <= 0:
        hou.ui.displayMessage('Select an item to color first.')

    else:
        last_item = sel[-1]
        cl = last_item.color()
        color = hou.ui.selectColor(cl)
        
        ## If the user press close, end the script
        if color == None:
            None
            
        else:
            color = hou.Color.ocio_viewTransform(color, "ACEScg", "sRGB - Display", "ACES 1.0 - SDR Video")
            for item in sel:
                item.setColor(color)