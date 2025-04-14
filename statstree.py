from PyQt5.QtWidgets import  QTreeWidget,QTreeWidgetItem
from PyQt5.QtCore import pyqtSlot


class statsTree(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderLabels(["Name", "PDV", "PDV Max", "PA", "PM"])
        monsterItem = QTreeWidgetItem(["Monsters"])
        playerItem = QTreeWidgetItem(["Players"])
        self.addTopLevelItem(monsterItem)
        self.addTopLevelItem(playerItem)
        self.monsteritems = dict()
        self.playeritems = dict()
        self.show()
        
    @pyqtSlot(dict)
    def addItemUnderMonster(self, stats):
        if stats["id"] in self.monsteritems:
            self.updateItemById(stats)
            return
        
        monsterItem = self.topLevelItem(0)
        item = QTreeWidgetItem(["Monster", str(stats["pdv"]), str(stats["pdvmax"]), str(stats["pa"]), str(stats["pm"])])
        monsterItem.addChild(item)
        self.monsteritems[stats["id"]] = item
        
    @pyqtSlot(dict)
    def addItemUnderPlayer(self, stats):
        if stats["id"] in self.playeritems:
            self.updateItemById(stats)
            return
        
        playerItem = self.topLevelItem(1)
        item = QTreeWidgetItem(["Player", str(stats["pdv"]), str(stats["pdvmax"]), str(stats["pa"]), str(stats["pm"])])
        playerItem.addChild(item)
        self.playeritems[stats["id"]] = item
        
    def clearAllItems(self):
        monsterItem = self.topLevelItem(0)
        playerItem = self.topLevelItem(1)
        monsterItem.takeChildren()
        playerItem.takeChildren()
        
    def updateItemById(self,stats):
        if stats["id"] in self.monsteritems:
            item = self.monsteritems[stats["id"]]
            item.setText(1, str(stats["pdv"]))
            item.setText(2, str(stats["pdvmax"]))
            item.setText(3, str(stats["pa"]))
            item.setText(4, str(stats["pm"]))
        
        if stats["id"] in self.playeritems:
            item = self.playeritems[stats["id"]]
            item.setText(1, str(stats["pdv"]))
            item.setText(2, str(stats["pdvmax"]))
            item.setText(3, str(stats["pa"]))
            item.setText(4, str(stats["pm"]))