import time
from pynput.mouse import Button, Controller
from PyQt5.QtCore import pyqtSlot, QObject , pyqtSignal
from pynput.mouse import Listener
import json
from helper import HarvestType

class MouseWorker(QObject):
    
    endCalibration = pyqtSignal()
    changeCalibrationMsg = pyqtSignal()    

    def __init__(self):
        super().__init__()
        self.mouse = Controller()
        self.calibClicks = 0
        self.loadConfig()
        self.cellsPositions = {}
        self.calculateCellsPosition()
        
    @pyqtSlot(int)
    def clickOnCell(self, cellid):
        x,y = self.getPositionFromCellId(cellid)
        if x is not None and y is not None:
            self.mouse.position = (x, y)
        btn = Button.left
        self.mouse.click(btn)
        time.sleep(self.sleepTime)
        
    @pyqtSlot(int, int)
    def clickOnPosition(self, x, y):
        self.mouse.position = (x, y)
        btn = Button.left
        self.mouse.click(btn)
        time.sleep(self.sleepTime)
    
    @pyqtSlot(int, int)
    def moveToPosition(self, x, y):
        self.mouse.position = (x, y)
        time.sleep(self.sleepTime)
    
    
    def harvest(self, cellid, harvestType :  HarvestType):
        deltaY = 0
        if harvestType == HarvestType.CLICKONLVL1:
            deltaY  = self.deltaYhA
        else:
            deltaY  = self.deltaYhB
            
        x,y = self.getPositionFromCellId(cellid)
        self.clickOnCell(cellid)
        if x is not None and y is not None:
            self.mouse.position = (x + self.deltaXh, y + deltaY)
            self.mouse.click(Button.left)
            time.sleep(self.sleepTime)
            
    def loadConfig(self):
        with open('config.json', 'r') as file:
            data = json.load(file)
            self.sleepTime = data["sleepTime"]
            self.deltaXh = data["deltaXh"]
            self.deltaYhA = data["deltaYhA"]
            self.deltaYhB = data["deltaYhB"]
            self.mapStartX = data["dofX"]
            self.mapStartY = data["dofY"]
            self.screenUpLeftX = data["screenUpLeftX"]
            self.screenUpLeftY = data["screenUpLeftY"]
            self.cellHeight = data["cellheight"]
            self.cellWidth = data["cellwidth"]
            self.firstSpellX = data["firstSpellX"]
            self.firstSpellY = data["firstSpellY"]
            
    def updateVarOnConfigFile(self, varName, value):
        with open('config.json', 'r') as file:
            data = json.load(file)
            data[varName] = value
        with open('config.json', 'w') as file:
            json.dump(data, file)
            
    @pyqtSlot()
    def startCalibration(self):
        downRightCorner = None
        upLeftCorner = None
        self.calibClicks = 0
        def on_click(x, y, button, pressed):
            nonlocal downRightCorner, upLeftCorner   
            if not pressed and button == Button.left and self.calibClicks <= 1:               
                print(f"Mouse released at ({x}, {y})")               
                upLeftCorner = (x, y)
                #elif self.calibClicks == 2 or self.calibClicks == 4:
                #    downRightCorner = (x, y)
    
                if self.calibClicks == 0:    
                    self.mapStartX = upLeftCorner[0]
                    self.mapStartY = upLeftCorner[1]
                    self.updateVarOnConfigFile("dofX", self.mapStartX)
                    self.updateVarOnConfigFile("dofY", self.mapStartY)
                    print(f"up Left dofus X : {self.mapStartX}, up Left dofus Y: {self.mapStartY}")
                    self.changeCalibrationMsg.emit()

                elif self.calibClicks == 1:
                    print(f"up Left screen X : {upLeftCorner[0]}, up Left screen Y: {upLeftCorner[1]}")
                    self.updateVarOnConfigFile("screenUpLeftX", upLeftCorner[0])
                    self.updateVarOnConfigFile("screenUpLeftY", upLeftCorner[1])
                    self.calibClicks = 0
                    self.endCalibration.emit()
                    listener.stop()
                    
                self.calibClicks += 1 
                
        listener = Listener(on_click=on_click)
        listener.start()
        
    def calculateCellsPosition(self):
        #cellNeighboors = (cellid + 14 , cellid - 14, cellid + 15, cellid - 15 , cellid + 1, cellid - 1, cellid + 29, cellid - 29)
        count = 0
        
        count  = 0
        xInit = self.mapStartX
        yInit = self.mapStartY
        
        for i in range(0,32):                
            for j in range(0,15):
                if i % 2 != 0 and j == 14:
                    continue
                
                if i % 2 == 0:
                    x_offset = 0
                else:
                    x_offset = (self.cellWidth)/2
                    
                x = xInit + (j * self.cellWidth) + x_offset
                y = yInit + (i * self.cellHeight/2)
                                
                self.cellsPositions[count] = (x, y)
                count += 1
        
                           
    def getPositionFromCellId(self, cellid):
        if cellid in self.cellsPositions.keys():
            return self.cellsPositions[cellid]
        return (None, None)
        
    def run(self):
        pass