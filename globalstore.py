from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from helper import ressourceStatus

class globalStore(QObject):
    def __init__(self):
        super().__init__()
        self.harvestableTiles = dict()
        self.changeMapTiles = list()
        self.dictPaysant = {"ble" : 7511}

    def updateHarvestTiles(self, data):
        if data:
            for key in data.keys():
                self.harvestableTiles[key] = data[key]
    
    def updateChangeMapTiles(self, data):
        if data:
            self.changeMapTiles.append(data)
                
    def mapChangeClear(self):
        self.harvestableTiles.clear()
        self.changeMapTiles.clear()
    
    def updateCombatData(self, data):  
        pass
    
    def printData(self):
        print(f"Harvestable Tiles: {self.harvestableTiles}")
    


store = globalStore()