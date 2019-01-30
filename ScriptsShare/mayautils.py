import maya.OpenMayaUI as OpenMayaUI
import pymel.core as pmc
from qtshim import QtGui, wrapinstance


def get_maya_window():
    """Return the QMainWindow for the main Maya window."""
    winptr = OpenMayaUI.MQtUtil.mainWindow()
    if winptr is None:
        raise RuntimeError('No Maya window found.')
    window = wrapinstance(winptr)
    assert isinstance(window, QtGui.QMainWindow)
    return window


def uipath_to_qtobject(pathstr):
    """Return the QtObject for a Maya UI path to a control,
    layout, or menu item.
    Return None if no item is found.
    """
    ptr = OpenMayaUI.MQtUtil.findControl(pathstr)
    if ptr is None:
        ptr = OpenMayaUI.MQtUtil.findLayout(pathstr)
    if ptr is None:
        ptr = OpenMayaUI.MQtUtil.findMenuItem(pathstr)
    if ptr is not None:
        return wrapinstance(ptr)
    return None


def get_main_window_name():
    return pmc.MelGlobals()['gMainWindow']
    
class CollapsableGroup(QtGui.QGroupBox):
    """A QGroupBox which collapses when unchecked."""

    def __init__(self, title, parent=None, checkState=True):
        """Creates a GroupBox which collapses when unchecked.

        Args:
            title: The title message of this GroupBox

        Keyword Args
            parent: The QWidget parent of this GroupBox
            checkState: Whether the GroupBox should be expanded - default True: expanded
        """
        QtGui.QGroupBox.__init__(self, title, parent)
        self.setCheckable(True)
        self.toggled.connect(self.toggle)
        self.setChecked(checkState)

    def toggle(self, on):
        """Collapses or Expands the GroupBox.

        Modifies the maximum height of the groupbox to expand/collapse it.
        Args:
            on: Whether to Expand (True) or Collapse (False) the GroupBox
        """
        if on:
            self.setMaximumHeight(16777215)
        else:
            self.setMaximumHeight(20)
