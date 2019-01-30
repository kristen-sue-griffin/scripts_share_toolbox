"""
Adds maya functionality to drag and drop scripts to a custom shelf 
Works with dragdropshelfscripts_ui.py which is the UI for this

To Use in Maya: 
from ScriptsShare import scriptssharetoolbox
reload(scriptssharetoolbox)
toolbox = scriptssharetoolbox.ScriptsShareToolbox()
toolbox.show()

For UI changes testing (Python anywhere but I've been using the Maya interpreter)
mayapy MODULE_LOCATION_ON_YOUR_COMPUTER\ScriptsShare\scriptssharetoolbox_ui.py

scripts_info is a dictionary - jason files currently with the format of
{
    "command": "import EnvironmentTools.skinExporter.skinExporter_UI as sui; reload(sui); suic = sui.asura_skinExporter_UI(); suic.showUI()", 
    "icon_path": "L:/Asura/Tools/Maya/Common/icons/NinjaIcons/Asura_ImportExport.jpg", 
    "parent_projects": [
        "Misc", 
        "EG2", 
        "ZA4"
    ], 
    "parent_types": [
        "Export"
    ], 
    "tooltip": "Batch Exporter for static Asura Meshes"
}
"""
import os
import sys
import maya.OpenMaya as OpenMaya
import pymel.core as pmc
import mayautils
import scriptssharetoolbox_ui as scriptssharegui
import json

""" Main Toolbox class ScriptsShareToolbox()"""
class ScriptsShareToolbox():
    def __init__(self):
        self._scripts_share_path = "%s/scripts/RebellionScripts/Misc/ScriptsShare/"%os.environ["MAYA_APP_DIR"]
        self._window = None

    """Main entry point into the script that shows the UI"""
    def show(self):
        if self._window is None:
            controller = scriptssharegui.ScriptsShareController()
            
            def emit_selchanged(_): 
                controller.selectionChanged.emit(pmc.selected(type='transform'))
            OpenMaya.MEventMessage.addEventCallback('SelectionChanged', emit_selchanged)
            parent = mayautils.get_maya_window()
            self._window = scriptssharegui.create_window(controller, parent, self._scripts_share_path, program='maya')
            def onconvert(prefix):
                settings = dict(
                    'b',
                    prefix=unicode(prefix))
            self._window.convertClicked.connect(onconvert)
        self._window.show()   