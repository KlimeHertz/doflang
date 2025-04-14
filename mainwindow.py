from PyQt5.QtWidgets import QMainWindow, QApplication
import sys
from PyQt5.QtWidgets import  QGraphicsView,QTabWidget, QAction, QMessageBox
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTextEdit, QVBoxLayout, QFileDialog
from PyQt5.QtCore import QTimer, pyqtSlot, QThread, pyqtSignal, QObject
from sniffer import snifferWorker
from mapdrawer import mapScene, mapManager, combatScene
from combatmanager import combatManager
from statstree import statsTree
from mouseworker import MouseWorker
from scriptrunner import scriptRunner



class mainwindow(QObject):
    
    fileLoaded = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
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
        self.combatscene = None
        #end of temporary tab setup
        
        mainLayout = QHBoxLayout(self.mainTab)
        self.view = QGraphicsView(self.scene, self.mainTab)
        mainLayout.addWidget(self.view, 10)
        self.textedit = QTextEdit(self.mainTab)
        mainLayout.addWidget(self.textedit, 4)   
        
        #objects management and connnections
        self.snifferThread = QThread()
        self.mouseThread = QThread()
        self.scriptThread = QThread()
        
        self.mapManager = mapManager()
        self.combatMngr = combatManager()
        self.mouseWorker = MouseWorker() 
        self.scriptWorker = scriptRunner()
         
        self.mapManager.changeTileColor.connect(self.scene.updateTileColor)
        self.mapManager.rollbackTileColor.connect(self.scene.rollbackTileColor)
        
        menuBar = self.window.menuBar()
        toolsMenu = menuBar.addMenu("Tools")
        calibrateAction = QAction("Calibrate", self.window)
        loadScriptAction = QAction("Load Script", self.window)
        toolsMenu.addAction(calibrateAction)
        toolsMenu.addAction(loadScriptAction)
        
        def start_calibration():
            self.calibrateMsg = QMessageBox(self.window)
            self.calibrateMsg.setWindowTitle("Calibrate")
            self.calibrateMsg.setText("Calibrate Map action triggered \n 'Click on the up left corner then on the right down corner of the dofus map'.")
            self.calibrateMsg.setStandardButtons(QMessageBox.NoButton)
            self.calibrateMsg.show()
            self.mouseWorker.endCalibration.connect(self.calibrateMsg.accept)            
                
        calibrateAction.triggered.connect(start_calibration)
        calibrateAction.triggered.connect(self.mouseWorker.startCalibration)
        
        loadScriptAction.triggered.connect(self.scriptFileDialog)

    def changeCalibrationMsg(self):
        self.calibrateMsg.setText("Calibrate Screen action triggered \n 'Click on the up left corner then on the right down corner of the screen'.")
        
    def scriptFileDialog(self):
        # Open a file dialog to select a script file
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self.window, "Open Script File", "", "Script Files (*.scp)", options=options)
        if fileName:
            self.fileLoaded.emit(fileName)
        

    def openCombatTab(self):
        if self.combatTab is None:
            # Create a new combat widget with a horizontal layout to hold both the combat view and the stats tree view
            combatWidget = QWidget()
            combatLayout = QHBoxLayout(combatWidget)
            
            # Left side: Combat view with its own vertical layout (in case you want to add more combat controls later)
            combatViewContainer = QWidget()
            combatViewLayout = QVBoxLayout(combatViewContainer)
            self.combatscene = combatScene(50*15, 50*15)
            combatView = QGraphicsView(self.combatscene, combatViewContainer)
            combatViewLayout.addWidget(combatView)
            
            # Right side: Tree view for monsters and player stats
            # Using QTreeWidget for simplicity
            statstree = statsTree()
            
            # Add the combat view and the stats tree to the horizontal layout
            combatLayout.addWidget(combatViewContainer, 3)
            combatLayout.addWidget(statstree, 1)
            
            # Connect signals for combat updates
            self.snifferWorker.combatPositionUpdate.connect(self.combatscene.updateTileColor)
            self.combatMngr.combatPositionRollback.connect(self.combatscene.rollbackTileColor)
            self.snifferWorker.addPlayerToTree.connect(statstree.addItemUnderPlayer)
            self.snifferWorker.addMonsterToTree.connect(statstree.addItemUnderMonster)
            
            # Add the new tab to the tab widget and set focus on it
            self.tabWidget.addTab(combatWidget, "Combat")
            self.tabWidget.setCurrentWidget(combatWidget)
            self.combatTab = combatWidget
            self.combatscene.drawCombatScene(self.scene)

    def closeCombatTab(self):
        if self.combatTab:
            # Remove the combat tab from the tab widget and clean up a
            index = self.tabWidget.indexOf(self.combatTab)
            if index != -1:
                self.tabWidget.removeTab(index)
            self.combatTab = None
            self.combatscene.clearScene()
            self.combatscene = None
        
    def showWindow(self):
        self.snifferWorker = snifferWorker(self.mapManager,self.combatMngr)
        self.snifferWorker.moveToThread(self.snifferThread)
        self.mouseWorker.moveToThread(self.mouseThread)
        self.scriptWorker.moveToThread(self.scriptThread)
        
        self.mouseThread.start()
        self.scriptThread.start()
        
        self.fileLoaded.connect(self.scriptWorker.loadScript)
        self.connectScriptRunnner()
        
        self.snifferThread.started.connect(self.snifferWorker.run)
        self.snifferWorker.updateTextZone.connect(self.updateText)
        self.snifferWorker.updateMapView.connect(self.scene.drawMap)
        self.snifferWorker.combatStart.connect(self.openCombatTab)
        self.snifferWorker.combatEnd.connect(self.closeCombatTab)
        self.mouseWorker.changeCalibrationMsg.connect(self.changeCalibrationMsg)        
        self.snifferWorker.moveToTest.connect(self.mouseWorker.clickOnCell)
        #self.snifferWorker.entityOnCell.connect(self.scene.updateTileColorById)
        self.snifferThread.start()
        self.window.show()
        self.app.exec_()
        
    def updateText(self, text):
        QTimer.singleShot(0, lambda: self.textedit.append(text))
    
    def updateMapView(self,mapdata):
        QTimer.singleShot(0, lambda: self.__drawMap(mapdata))
        
    
    def connectScriptRunnner(self):
        self.scriptWorker.moveToCell.connect(self.mouseWorker.clickOnCell)
        self.scriptWorker.moveToPosition.connect(self.mouseWorker.moveToPosition)
        self.scriptWorker.clickPosition.connect(self.mouseWorker.clickOnPosition)
        self.scriptWorker.harvest.connect(self.mouseWorker.harvest)