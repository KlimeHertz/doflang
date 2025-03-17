from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import  QColor, QFont, QPen, QPolygon , QPainter
from PyQt5.QtCore import Qt, QPoint
import sys
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTextEdit
from PyQt5.QtCore import QTimer, pyqtSlot, QThread
from sniffer import snifferWorker
from mapdrawer import mapScene, mapManager


class mainwindow():
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.setGeometry(100, 100, 1000, 800)
        self.window.setWindowTitle("Doflang")
        self.scene = mapScene(50*15, 50*15)
        central_widget = QWidget()
        self.window.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        self.view = QGraphicsView(self.scene, central_widget)
        layout.addWidget(self.view,10)
        self.textedit = QTextEdit(central_widget)
        layout.addWidget(self.textedit,4)
        self.snifferThread = QThread()
        self.mapManager = mapManager()
        self.mapManager.changeTileColor.connect(self.scene.updateTileColor)
        self.mapManager.rollbackTileColor.connect(self.scene.rollbackTileColor)
        
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