
from qtshim import QtGui, QtCore, Signal

import sys
#FLOW LAYOUT WIDGETS
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
        scroll.setMinimumSize(QtCore.QSize(5, 330))
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
    def __init__(self, title, parent=None, checkState=False):

        QtGui.QGroupBox.__init__(self, title, parent)
        self.setCheckable(True)
        self.toggled.connect(self.toggle)
        self.setChecked(checkState)
        
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

class Bubble(QtGui.QLabel):
    def __init__(self, text):
        super(Bubble, self).__init__(text)
        self.word = text
        self.setContentsMargins(5, 5, 5, 5)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.drawRoundedRect(
            0, 0, self.width() - 1, self.height() - 1, 5, 5)
        super(Bubble, self).paintEvent(event)

class MainWindow(QtGui.QMainWindow):
    def __init__(self, text, parent=None):
        super(MainWindow, self).__init__(parent)
        
        tab = QtGui.QTabWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        tab.setSizePolicy(sizePolicy)
        tab_wid = QtGui.QWidget()
        
        layout = QtGui.QVBoxLayout()
        tab.setLayout(layout)
        
        # Collapse group with a grid layout
        tasktype_grpbx = CollapsableGroup('frog')
        tasktype_grpbxlayout = QtGui.QVBoxLayout()
        #tasktype_grpbxlayout.addStretch()
        
        self.tasktype_scroll = ScrollingFlowWidget()

        #def add_to_scrollingFlowWidget(self, widget):
        #    self.tasktype_scroll.addWidget(widget)
        #    self.templates.append(widget)
            
        
        # Create the icons widgets
        words = []
        row =0
        column = 0
        for word in text.split():
            label = Bubble(word)
            label.setFont(QtGui.QFont('SblHebrew', 18))
            label.setFixedWidth(label.sizeHint().width())
            words.append(label)
            self.tasktype_scroll.addWidget(label)
            #self.templates.append(label)
            if column == 3:
                column = 0
            column = column+ 1
            row = row + 1

        #tasktype_scroll.setWidget(tasktype_scrollwdgt)
        
        
        # Assign and parent layouts
        tasktype_grpbx.setLayout(tasktype_grpbxlayout)        
        layout.addWidget(tasktype_grpbx)
        
        tasktype_grpbxlayout.addWidget(self.tasktype_scroll)
        '''
        #############2
         # Collapse group with a grid layout
        tasktype_grpbx2 = CollapsableGroup('frogls')
        tasktype_layout2=FlowLayout(tasktype_grpbx2)

        # Create the icons widgets
        row =0
        column = 0
        for word in text.split():
            label = Bubble(word)
            label.setFont(QtGui.QFont('SblHebrew', 18))
            label.setFixedWidth(label.sizeHint().width())
            words.append(label)
            tasktype_layout2.addWidget(label)
            if column == 3:
                column = 0
            column = column+ 1
            row = row + 1
            
        tasktype_grpbx2.setLayout(tasktype_layout2)
        layout.addWidget(tasktype_grpbx2)
        ### END COLLAPSE 2
        
        #############3
         # Collapse group with a grid layout
        tasktype_grpbx3 = CollapsableGroup('ponies')
        tasktype_grpbxlayout3 = QtGui.QVBoxLayout()
        tasktype_grpbxlayout3.addStretch()
        
        scroll = ScrollPanelWidget()
        
       
        tasktype_grpbxlayout3.addWidget(scroll)    
        tasktype_grpbx3.setLayout(tasktype_grpbxlayout3)
        layout.addWidget(tasktype_grpbx3)
        ### END COLLAPSE 3
        
        
        #############4
         # Collapse group with a grid layout
        tasktype_grpbx4 = CollapsableGroup('Spots')
        tasktype_grpbxlayout4 = QtGui.QVBoxLayout()
        #tasktype_grpbxlayout4.addStretch()
        
        scroll = ScrollFormPanelWidget(child_widgets=words)
        
       
        tasktype_grpbxlayout4.addWidget(scroll)    
        tasktype_grpbx4.setLayout(tasktype_grpbxlayout4)
        layout.addWidget(tasktype_grpbx4)
        ### END COLLAPSE 4
        
        # Splitter
        splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(tasktype_grpbx)
        splitter.addWidget(tasktype_grpbx2)
        splitter.addWidget(tasktype_grpbx3)
        
        layout.addWidget(splitter)
        '''
        self.setCentralWidget(tab)

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    window = MainWindow('Harry Potter is a series of fantasy literature')
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec_())