'''
scriptssharetoolbox.py
UI that utilizes the scriptsshare folder to generate a toolbox.

Notes: Accept extra modifiers to pass to commands -- ie flipObjectAlongAxis with x and + held could flip it in the positive along the x axis instead of multiple icons
'''

from qtshim import QtGui, QtCore, Signal
import sys
import os
import random
import json
import pymel.core as pm

###########
# Signals #
###########
class ScriptsShareController(QtCore.QObject):
    selectionChanged = Signal(list)
    
class ConverterWindow(QtGui.QMainWindow):
    convertClicked = Signal(str)   
    
##############    
# Widgets/UI #
##############

""" A Flow Layout to make grid like flow nicely """
class FlowLayout(QtGui.QLayout):
    """
    Standard PyQt examples FlowLayout modified to work with a scollable parent
    """
    
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)

        if parent is not None:
            self.setMargin(margin)
        else:
            self.setMargin(0)
        self.setSpacing(spacing)

        self.itemList = []


    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)


    def addItem(self, item):
        self.itemList.append(item)


    def count(self):
        return len(self.itemList)


    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]
        return None


    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)
        return None


    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))


    def hasHeightForWidth(self):
        return True


    def heightForWidth(self, width):
        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height


    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)


    def sizeHint(self):
        return self.minimumSize()


    def minimumSize(self):
        size = QtCore.QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        size += QtCore.QSize(2 * self.margin(), 2 * self.margin())
        return size

    def minimumSize(self):
        w = self.geometry().width()
        h = self.doLayout(QtCore.QRect(0, 0, w, 0), True)
        return QtCore.QSize(w + 2 * self.margin(), h + 2 * self.margin())
    

    def doLayout(self, rect, testOnly=False):
        """
        """
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing() + wid.style().layoutSpacing(QtGui.QSizePolicy.PushButton, QtGui.QSizePolicy.PushButton, QtCore.Qt.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(QtGui.QSizePolicy.PushButton, QtGui.QSizePolicy.PushButton, QtCore.Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()

    def margin(self):
        """margin - return margin
        """

        return self._margin

    def setMargin(self, margin):
        """setMargin - set margin
        :param int margin: margin to set
        """

        self._margin = margin

""" A Helper class to allow for resizing with Flow & Scroll """       
class ResizeScrollArea(QtGui.QScrollArea):
    """
    A QScrollArea that propagates the resizing to any FlowLayout children.
    """
    
    def __init(self, parent=None):  
        QtGui.QScrollArea.__init__(self, parent)


    def resizeEvent(self, event):
        wrapper = self.findChild(QtGui.QWidget)
        flow = wrapper.findChild(FlowLayout)
        
        if wrapper and flow:            
            width = self.viewport().width()
            height = flow.heightForWidth(width)
            size = QtCore.QSize(width, height)
            point = self.viewport().rect().topLeft()
            flow.setGeometry(QtCore.QRect(point, size))
            self.viewport().update()

        super(ResizeScrollArea, self).resizeEvent(event)

"""A Scroll Widget that utilizes the above flow and resize to enable a flow inside"""
class ScrollingFlowWidget(QtGui.QWidget):
    """
    A resizable and scrollable widget that uses a flow layout.
    Use its addWidget() method to flow children into it.
    """
    
    def __init__(self,parent=None):
        super(ScrollingFlowWidget,self).__init__(parent)
        grid = QtGui.QGridLayout(self)
        scroll = ResizeScrollArea()
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._wrapper = QtGui.QWidget(scroll)
        self.flowLayout = FlowLayout(self._wrapper)
        self._wrapper.setLayout(self.flowLayout)
        scroll.setWidget(self._wrapper)
        scroll.setWidgetResizable(True)
        scroll.setMinimumSize(QtCore.QSize(0, 80))
        grid.addWidget(scroll)


    def addWidget(self, widget):
        self.flowLayout.addWidget(widget)
        widget.setParent(self._wrapper)

    def getChildren(self):
        return self.flowLayout.itemLis
 
"""A QGroupBox which collapses when unchecked."""
class CollapsableGroup(QtGui.QGroupBox):
    
    """Creates a GroupBox which collapses when unchecked.

    Args:
        title: The title message of this GroupBox

    Keyword Args
        parent: The QWidget parent of this GroupBox
        checkState: Whether the GroupBox should be expanded - default True: expanded
    """
    def __init__(self, title, parent=None, checkState=True):

        QtGui.QGroupBox.__init__(self, title, parent)
        self.setCheckable(True)
        self.toggled.connect(self.toggle)
        self.setChecked(checkState)
        
        flow_wdgt = QtGui.QWidget()
        tasktype_scrl = QtGui.QScrollArea()
        tasktype_scrl.setWidget(flow_wdgt)
        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(flow_wdgt)
        
    """Collapses or Expands the GroupBox.

    Modifies the maximum height of the groupbox to expand/collapse it.
    Args:
        on: Whether to Expand (True) or Collapse (False) the GroupBox
    """
    def toggle(self, on):

        if on:
            self.setMaximumHeight(16777215)
        else:
            self.setMaximumHeight(20)

"""A QLabel that makese la little text bubble"""            
class TextBubble(QtGui.QLabel):
    def __init__(self, text):
        super(TextBubble, self).__init__(text)
        self.word = text
        self.setContentsMargins(5, 5, 5, 5)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.drawRoundedRect(
            0, 0, self.width() - 1, self.height() - 1, 5, 5)
        super(TextBubble, self).paintEvent(event)

""" A QTabWidget that will hold the tabs for projects - Should be broken down more but eh"""
class TypeWidget(QtGui.QWidget): # Tabs are the Project
    """Initialize the TabWidget(QtGui.QTabWidget):"""
    def __init__(self, tab, title, icons, parent=None):
        super(TypeWidget, self).__init__(parent)

        self.tasktype_grpbxlayout = QtGui.QVBoxLayout(self)
        self.titleBubble = TextBubble(title)
        self.titleBubble.setMinimumSize(64, 20)
        self.tasktype_scroll = ScrollingFlowWidget()
        # Create the icons widgets
        icon_objects = []
        for icon_info in icons:
   
            label = IconLabelWidget(icon_info=icon_info)
            self.tasktype_scroll.addWidget(label)
            
        self.tasktype_grpbxlayout.addWidget(self.titleBubble)    
        self.tasktype_grpbxlayout.addWidget(self.tasktype_scroll)

        
""" A QTabWidget that will hold the tabs for projects - Should be broken down more but eh"""
class TabWidget(QtGui.QTabWidget): # Tabs are the Project
    """Initialize the TabWidget(QtGui.QTabWidget):"""
    def __init__(self, parent=None):
        super(TabWidget, self).__init__(parent)
        self.tabs = list()
        
        '''
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        '''
        self.setMinimumSize(200, 200)
    def addNewTab(self, collapse_groups, title):
        new_tab_wid = QtGui.QWidget()
        new_tab_wid.setContentsMargins(-10, -10, -10, -10)
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.setSpacing(0)
        
        self.addTab(new_tab_wid, title)
        self.setTabText(len(self.tabs), title)        
        
        new_tab_wid.setLayout(self.layout)
        splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        for key, value in collapse_groups.items():
            type_group = TypeWidget(new_tab_wid, key, value)
            splitter.addWidget(type_group)
            
        self.layout.addWidget(splitter)
        
        self.tabs.append(new_tab_wid)


"""Creates a Widget to hold information about the script and icon for the user to drag from the UI and drop to the shelf"""
class IconLabelWidget(QtGui.QWidget):

    """ IconLabelWidget(QtGui.QWidget): Init """
    def __init__(self, parent=None, icon_info=None):
        super(IconLabelWidget, self).__init__(parent)
        
        self.initUIIconLabel(parent, icon_info)
        self.setFixedWidth(32)
        self.setFixedHeight(32)
        
        
    """ Initialize the UI for IconLabelWidget(QtGui.QWidget):"""    
    def initUIIconLabel(self, parent, icon_info):
        # Generic layout for the widget
        self.layout = QtGui.QHBoxLayout()
        self.layout.addStretch(False)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setAlignment(self, QtCore.Qt.AlignHCenter)
        self.user_icon_path = os.path.dirname(os.path.realpath(__file__)).replace("\\","/")
        
        try:
            icon = icon_info.get('icon')
            command = icon_info.get('command')
            tooltip = icon_info.get('tooltip')
        except:
            icon = "%s/icon_error.jpg"%self.user_icon_path
            command = 'ERROR'
            tooltip = 'ERROR'
            
        # For now - need something better
        if icon  == None or command  == None or tooltip  == None:
            icon = "%s/icon_error.jpg"%self.user_icon_path
            command = 'ERROR'
            tooltip = 'ERROR'
            print 'Something has gone wrong with a script pack in icons'
            
        # Turn Icons into a proper widget object
        self.icon = QtGui.QPixmap(icon)
        self.command_text = str(command)
        
        self.label = QtGui.QLabel('', parent)
        self.label.setToolTip(tooltip)
        
        self.icon.scaled(32, 32, QtCore.Qt.KeepAspectRatio)
        self.label.setPixmap(self.icon)

        
        self.label.show()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
    def runMayaCommand(self): # TEMP needs more robust run command for click
        print self.command_text;
        try:
            exec(self.command_text)
        except:
            print 'Sorry only python commands are currently supported on a click basis. Please feel free to drag the icon to the shelf to make a shelf button'
            
    """Mouse Press event for drag drpo functionality for TabWidget(QtGui.QTabWidget):"""   
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.runMayaCommand()
    
    """Mouse Press event for drag drpo functionality for TabWidget(QtGui.QTabWidget):"""   
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_start_position = event.pos()
            
    """Mouse Move event for drag drpo functionality for TabWidget(QtGui.QTabWidget):"""
    def mouseMoveEvent(self, event):
        if not (event.buttons() & QtCore.Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QtGui.QApplication.startDragDistance():
            return
        drag = QtGui.QDrag(self)
        mimedata = QtCore.QMimeData()
        mimedata.setText(self.command_text)
        drag.setMimeData(mimedata)
        painter = QtGui.QPainter(self.icon) #(int x, int y, int w, int h, const QPixmap &pixmap, int sx, int sy, int sw, int sh
        #painter.drawPixmap(self.rect(), self.grab())
        painter.drawPixmap(0, 0, 20, 20, self.icon, 20, 20, 20, 20)
        painter.end()
        drag.setPixmap(self.icon)
        drag.setHotSpot(event.pos())
        drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction)

""" Main Dialog entry point for creating the UI MainScriptsShareWidget(QtGui.QDialog)"""
class MainScriptsShareWidget(QtGui.QWidget):

    """Init for MainScriptsShareWidget(QtGui.QDialog)"""
    def __init__(self, parent, scripts_uibuildinfo):
        super(MainScriptsShareWidget, self).__init__(parent)
        self.initUIMain(parent,scripts_uibuildinfo)
        
        
    """ Ui init for MainScriptsShareWidget(QtGui.QDialog) """    
    def initUIMain(self, parent, scripts_uibuildinfo):
        # Fix this QLayout: Attempting to add QLayout "" to MainScriptsShareWidget "", which already has a layout - it works as expected but says that 
        layout_main = QtGui.QVBoxLayout(self)
        self.tabs_wdgt = TabWidget()
        layout_main.addWidget(self.tabs_wdgt)
        self.tabs_wdgt.currentChanged.connect(self.curTabChange)
        
        # Go through and create all the tabs and gubbins
        for key, value in scripts_uibuildinfo.ui_build_info.items():
            # Add in all of the tabs - will be based on folder structure
            self.tabs_wdgt.addNewTab(collapse_groups=value, title=key)
            #layout_main.addWidget( self.tab) 

        #self.setLayout(layout_main)
        self.setWindowTitle('Drag and Drop shelf buttons')

    def curTabChange(self, index):
        for i in range(self.tabs_wdgt.count()):
            if i == index:
                self.tabs_wdgt.widget(i).setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
            else:
                self.tabs_wdgt.widget(i).setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)

""" Class to bundle the information on the script """
class ScriptInfo():
    """Init for ScriptInfo(): """
    def __init__(self, json_path=None, program=None):
        """
            json_path: full path to the json that contains the run command information
        """
        self.command = ''
        self.icon = ''
        self.tooltip = ''
        self.parent_projects = list()
        self.parent_types = list()
        self.program = program
        self.command_type = ''
        
        dir_head, dir_tail = os.path.split(json_path)
        
        if dir_tail[:2] != '__' and os.path.isdir(json_path):
            scripts_info = self.get_scriptInfoJson(json_path, program=self.program) # This hsould be turned into setters/getters but for now - this
            self.command = scripts_info.get('command')
            self.icon = scripts_info.get('icon')
            self.tooltip = scripts_info.get('tooltip')
            self.parent_projects = scripts_info.get('parent_projects')
            self.parent_types = scripts_info.get('parent_types')
            self.command_type = scripts_info.get('command_type')

    """ Gets the information from the script info .json """
    def get_scriptInfoJson(self, path, program):
        """
        path - full directory path to the json file with the script run information
        
        Returns: dictionary with the json information
        """
        json_file = os.path.join(path, 'scriptInformation_' + program + '.json')
        content = dict()
        if os.path.isfile(json_file):
            with open(json_file) as json_file:  
                content = json.load(json_file)

        return content
        
    """ Generates the .json file that holds the script information """
    def generate_scriptInfoJson(self, path, command, icon_path, tooltip, parent_projectlist, parent_typelist):
        """
            path - path to where the json run command script information document well be placed
            program - valid programs for this tool
            command - the text that will be placed on Maya's command shelf
            icon_path - the path to the icon jpg
            tooltip - a tooltip string when someone hovers over the icon
            parent_projectlist - list of all projects you want this script to be placed under in the UI
            parent_typelist - list of all types you want this script to be placed under in the UI
        """
        content = {'command': command, 'icon':icon_path, 'tooltip':tooltip, 'parent_projects':parent_projectlist, 'parent_types':parent_typelist}
        with open(os.path.join(path, 'scriptInformation.json'), 'w') as f:
                    json.dump(content, f, indent=4, sort_keys=True)
                    f.close()

#class WindowUITabInfo():

#class WindowUIGroupInfo():

""" To bundle in the list of ScriptInfo()s and the Final UI Build Information for those Scripts """
class WindowUIBuildInfo():
    """Init for ScriptsUIBuild(): """
    def __init__(self, full_path=None, program=None):
        """
            full_path: full path to the directory where the script directories are
        """
        
        self.ui_build_info = dict() # Quick and dirty - shoudl be more robust/refactored
        self.script_infos = list()
        self.scripts_path = full_path
        self.program = program

        if os.path.isdir(full_path):
            self.generate_UIBuildInfo()

    """ Takes a path and sorts a list of ScriptInfo()s that you want to uses in the UI building process & creates a build info dict - needs refactor/cleanup """
    def generate_UIBuildInfo(self):
        """
            Return: for funsies also simply returns the scripts list
        """

        # Get all of the script objects were adding
        if os.path.isdir(self.scripts_path):
            script_dirs = os.listdir(self.scripts_path)
            scripts = list()
            for dir in script_dirs:
                final_script_path = os.path.join(self.scripts_path,dir)
                if dir[:2] != '__' and os.path.isdir(final_script_path):
                    info = ScriptInfo(json_path=final_script_path, program=self.program)                    
                    script_command_info = {'command': info.command, 'icon':info.icon, 'tooltip':info.tooltip}
                    if info.parent_projects != None:
                        scripts.append(info)
                        for project in info.parent_projects:
                            tab_info = self.ui_build_info.get(project)

                            if tab_info == None:
                                types = dict()
                                for type in info.parent_types: 
                                    types[type] = [script_command_info]
                                self.ui_build_info[project] = types
                                '''
                                print 'New Tab'
                                print project
                                print types
                                print ''
                                '''
                            else:
                                for type in info.parent_types:
                                    type_info = tab_info.get(type)
                                    if type_info:
                                        '''
                                        print 'existing group'
                                        print type
                                        print self.ui_build_info[project][type]
                                        print ''
                                        '''
                                        self.ui_build_info[project][type].extend([script_command_info])
                                        '''
                                        print 'after extend'                                    
                                        print self.ui_build_info[project][type]
                                        print ''
                                        '''
                                    else:                                    
                                        self.ui_build_info[project][type] = [script_command_info]
                                        '''
                                        print 'new group'
                                        print type
                                        print self.ui_build_info[project][type]
                                        print ''
                                        '''
  

            self.script_infos = scripts
        else:
            print 'Sorry ' + self.scripts_path + ' is not a valid directory.'
        
        
        return self.script_infos
 
    
""" Connection point window creation for Maya """
def create_window(controller, parent=None, scripts_share_path=None, program=None):
    """
        controller - the parent controller object to connect to
        parent - the parent window to attach to
        ui_build_info - dictionary of {tab_name: {collapsGroup1: {tooltip:'foo', icon:'c:\bluepath', command:'command string}, collapsGroup2: {...}}
                    NOTE: I chose to have a flat hierarchy and a `build info` -parent_projects/parent_types for tools that a user would like to share to multiple places for ease of end user discovery - IE they work in Animation so tend to stay on the animation tab but a tool made more with Environment in mind but is useful for animation can be posted to both sections if desired
    """

    # package up the information we want to build the ui with
    scripts_uibuildinfo =  WindowUIBuildInfo(full_path=scripts_share_path, program=program)
    
    # sanity check
    if scripts_uibuildinfo.ui_build_info:
        window = ConverterWindow(parent)
        window.setWindowTitle('Scripts Share Toolbox')   
        container = MainScriptsShareWidget(window, scripts_uibuildinfo)
        window.resize(400, 600)
        
        all_scripts = list()
        
        
        layout = QtGui.QHBoxLayout(container)
        container.setLayout(layout)
        
        window.setCentralWidget(container)
        return window 
    else:
        print 'Sorry, there is no build information for this ui.'
    
##################################
# Test Calls to UI functionality #
##################################
""" Main Functionality to test call UI only"""
def _pytest():
    controller = ScriptsShareController()
    de
    path_test = 'C:\Users\kristen.griffin\Documents\maya\scripts\RebellionScripts\Misc\ScriptsShare'

    app = QtGui.QApplication([])

    win = create_window(controller, scripts_share_path=path_test, program='maya')
    
    win.show()
    app.exec_()
    
    
if __name__ == '__main__':
   _pytest()
