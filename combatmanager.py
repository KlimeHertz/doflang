from PyQt5.QtCore import pyqtSignal, QObject
from entity import Entity

class combatManager(QObject):
    
    drawcombatScene = pyqtSignal(dict)
    combatPositionRollback = pyqtSignal(int)
    
    def __init__(self): 
        super().__init__()    
        self.players = list()
        self.monsters = list()
        self.isFighting = False
        
    def combatStart(self):
        self.isFighting = True
        
    def combatEnd(self):
        self.isFighting = False
    
    def getEntityTypeById(self, id):
        for player in self.players:
            if player.id == id:
                return player.type
        
        for monster in self.monsters:
            if monster.id == id:
                return monster.type
    
    def addPlayerEntity(self,Entity):
        self.players.append(Entity)
        
    def isInCombat(self):
        return self.isFighting
    
    def addMonsterEntity(self,Entity):
        self.monsters.append(Entity)
    
    def updateEntityPosition(self, entityid, cellid):
        for player in self.players:
            if player.id == entityid:
                player.OldCell = player.currentCell
                player.currentCell = cellid
                break
        
        for monster in self.monsters:
            if monster.id == entityid:
                monster.OldCell = monster.currentCell
                monster.currentCell = cellid
                break
    
    def entitySetStartCell(self, entityid, cellid):
        for player in self.players:
            if player.id == entityid:
                player.currentCell = cellid
                player.OldCell = cellid
                break
        
        for monster in self.monsters:
            if monster.id == entityid:
                monster.currentCell = cellid
                monster.OldCell = cellid
                break
            
    def deleteEntity(self, entityid):
        for i, entity in enumerate(self.players):
            if entity.id == entityid:
                del self.players[i]
                return
            
        for i, entity in enumerate(self.monsters):
            if entity.id == entityid:
                del self.monsters[i]
                return
    
    def rollbackOldCellColor(self, entityid):
        for player in self.players:
            if player.id == entityid:
                print("Rollbacking player color to cell: ", player.OldCell)
                self.combatPositionRollback.emit(player.OldCell)
                break
        
        for monster in self.monsters:
            if monster.id == entityid:
                print("Rollbacking monster color to cell: ", monster.OldCell)
                self.combatPositionRollback.emit(monster.OldCell)
                break
            
    def getEntityById(self, entityid):
        for player in self.players:
            if player.id == entityid:
                return player
        
        for monster in self.monsters:
            if monster.id == entityid:
                return monster
            
    def updateEntityStats(self, entityid, stats):
        for player in self.players:
            if player.id == entityid:
                player.pa = stats["pa"]
                player.pm = stats["pm"]
                player.pdv = stats["pdv"]
                player.pdvmax = stats["pdvmax"]
                break
        
        for monster in self.monsters:
            if monster.id == entityid:
                monster.pa = stats["pa"]
                monster.pm = stats["pm"]
                monster.pdv = stats["pdv"]
                monster.pdvmax = stats["pdvmax"]
                break
        
    def playerTurnStart(self, playerid):
        for player in self.players:
            if player.id == playerid:
                pass
            else:
                return
            
    def startBoosting(self, playerid):
        pass
    
    def castSpellWithLineOfView(self, playerid, spellid, cellid):
        pass
    
    def castSpellWithoutLineOfView(self, playerid, spellid, cellid):
        pass