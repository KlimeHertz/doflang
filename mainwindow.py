from PyQt5.QtWidgets import QMainWindow, QApplication
import sys
from PyQt5.QtWidgets import  QGraphicsView,QTabWidget
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTextEdit, QVBoxLayout
from PyQt5.QtCore import QTimer, pyqtSlot, QThread
from sniffer import snifferWorker
from mapdrawer import mapScene, mapManager, combatScene


class mainwindow():
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.setGeometry(100, 100, 1000, 800)
        self.window.setWindowTitle("Doflang")
        self.scene = mapScene(50*15, 50*15)
        self.tabWidget = QTabWidget(self.window)
        self.window.setCentralWidget(self.tabWidget)
        self.mainTab = QWidget()
        self.tabWidget.addTab(self.mainTab, "Main")
        #temporary tab setup:
        self.combatTab = None
        #end of temporary tab setup
        
        mainLayout = QHBoxLayout(self.mainTab)
        self.view = QGraphicsView(self.scene, self.mainTab)
        mainLayout.addWidget(self.view, 10)
        self.textedit = QTextEdit(self.mainTab)
        mainLayout.addWidget(self.textedit, 4)   
        
        #objects management and connnections
        self.snifferThread = QThread()
        self.mapManager = mapManager()       
        self.mapManager.changeTileColor.connect(self.scene.updateTileColor)
        self.mapManager.rollbackTileColor.connect(self.scene.rollbackTileColor)
        

    def openCombatTab(self):
        if self.combatTab is None:
            # Create combat scene and wrap it in a QGraphicsView inside a new tab
            combatWidget = QWidget()
            combatLayout = QVBoxLayout(combatWidget)
            combatView = QGraphicsView(combatScene(50*15, 50*15), combatWidget)
            combatLayout.addWidget(combatView)
            # Add the new tab to the tab widget and set focus on it
            self.tabWidget.addTab(combatWidget, "Combat")
            self.tabWidget.setCurrentWidget(combatWidget)
            self.combatTab = combatWidget

    def closeCombatTab(self):
        if self.combatTab:
            # Remove the combat tab from the tab widget and clean up
            index = self.tabWidget.indexOf(self.combatTab)
            if index != -1:
                self.tabWidget.removeTab(index)
            self.combatTab = None

    #self.openCombatTab = openCombatTab
    #self.closeCombatTab = closeCombatTab
        
    def showWindow(self):
        self.snifferWorker = snifferWorker(self.mapManager)
        self.snifferWorker.moveToThread(self.snifferThread)
        self.snifferThread.started.connect(self.snifferWorker.run)
        self.snifferWorker.updateTextZone.connect(self.updateText)
        self.snifferWorker.updateMapView.connect(self.scene.drawMap)
        #self.snifferWorker.entityOnCell.connect(self.scene.updateTileColorById)
        self.snifferThread.start()
        self.window.show()
        self.app.exec_()
        
    def updateText(self, text):
        QTimer.singleShot(0, lambda: self.textedit.append(text))
    
    def updateMapView(self,mapdata):
        QTimer.singleShot(0, lambda: self.__drawMap(mapdata))