from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class HasrvestManager(QObject):
    
    harvestClick = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.isHarvesting = False
        self.harvestType = None
        self.harvestTime = 0
        self.harvestCellId = None
    
    def startHarvest(self, cellid):        
        self.harvestCellId = cellid
        self.harvestClick.emit(cellid)
    
    def harvestStart(self, harvestType, harvestTime):
        self.isHarvesting = True
        self.harvestType = harvestType
        self.harvestTime = harvestTime
    
    def canNotHarvest(self):
        self.isHarvesting = False
    
    def HarvestEnd(self, cellid):
        self.isHarvesting = False
    