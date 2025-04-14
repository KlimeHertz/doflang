from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPolygonItem, QGraphicsTextItem
from PyQt5.QtGui import QPolygonF, QColor, QFont, QPen
from PyQt5.QtCore import QPointF, pyqtSlot, QObject, pyqtSignal
from entity import Entity
from PyQt5.QtWidgets import QGraphicsTextItem
from helper import ressourceStatus
import globalstore

class mapTile(QGraphicsPolygonItem):
    
    def __init__(self, x, y ,color : tuple, tileid):
        super().__init__()
        self.tileid = tileid
        self.cellsize = 50
        self.color = color
        self.originalColor = color
                    
        self.setPolygon(QPolygonF([QPointF(x, y - self.cellsize // 2),
                                  QPointF(x + self.cellsize // 2, y),
                                  QPointF(x, y + self.cellsize // 2),
                                  QPointF(x - self.cellsize // 2, y)]))
        
        self.setBrush(QColor(*self.color))
        self.setPen(QPen(QColor(0,0,0)))
        
        self.textItem = QGraphicsTextItem(str(self.tileid), self)
        self.textItem.setDefaultTextColor(QColor(0,0,0))
        self.textItem.setFont(QFont("Arial", 8))
        self.textItem.setPos(x - 10, y - 10)
        

class combatScene(QGraphicsScene):
    
    def __init__(self, sceneWidth, sceneHeight):
        super().__init__()
        self.cellsize = 50
        self.width = sceneWidth
        self.height = sceneHeight
        self.defaultColor = (0,0,0)
        self.setSceneRect(50, 50, self.width, self.height)
        
    def clearScene(self):     
        for item in self.items():
            self.removeItem(item)
            
    def drawCombatScene(self, fromScene):
        self.clearScene()
        self._copyItemsFromScene(fromScene)
        
    @pyqtSlot(int)
    def rollbackTileColor(self, tileid):
        tile = self.getTileByid(tileid)
        if tile:
            tile.setBrush(QColor(*tile.originalColor))
            
    def _duplicateItem(self, item):
        # Duplicate known item types. For custom items like mapTile,
        # we re-instantiate with similar properties.
        if isinstance(item, mapTile):
            # Use the center of the polygon's bounding rectangle as reference point.
            center = item.polygon().boundingRect().center()
            if item.brush().color() != QColor(255,0,0) and item.brush().color() != QColor(*self.defaultColor):
                cellcolor = (255,0,0)
            else:
                cellcolor = (item.brush().color().red(), item.brush().color().green(), item.brush().color().blue())
            
            new_item = mapTile(center.x(), center.y(),
                               cellcolor,
                               item.tileid)
            
            # Duplicate the text item
            new_item.textItem.setHtml(item.textItem.toHtml())
            new_item.textItem.setFont(item.textItem.font())
            new_item.textItem.setDefaultTextColor(item.textItem.defaultTextColor())
            new_item.textItem.setPos(item.textItem.pos())
            return new_item
        elif isinstance(item, QGraphicsTextItem):
            new_text = QGraphicsTextItem(item.toPlainText())
            new_text.setFont(item.font())
            new_text.setDefaultTextColor(item.defaultTextColor())
            new_text.setPos(item.pos())
            return new_text
        # Add duplication logic for other QGraphicsItem types as needed.
        return None

    def _copyItemsFromScene(self, other_scene):
        for item in other_scene.items():
            copy = self._duplicateItem(item)
            if copy:
                self.addItem(copy)
    
    @pyqtSlot(int,tuple)
    def updateTileColor(self, tileid, color):
        print(f"change tile color {tileid} {color}")
        tile = self.getTileByid(tileid)
        if tile:
            tile.setBrush(QColor(*color))
            
    def getTileByid(self, tileid):
        for item in self.items():
            if isinstance(item, mapTile):
                if item.tileid == tileid:
                    return item
        return None
            
    
    def drawCombatSceneFromDict(self, mapdata):
        self.clearScene()
        
        count  = 0
        for i in range(0,mapdata['height']):                
            for j in range(0,mapdata['width']):
                
                if i % 2 != 0 and j == mapdata['width'] - 1:
                    continue
                
                if i % 2 == 0:
                    x_offset = 0
                else:
                    x_offset = (self.cellsize)/2
                    
                x = 50 + (j * self.cellsize) + x_offset
                y = 50 + (i * self.cellsize/2)
                
                for cell in mapdata['cells']:
                    if cell.CellID == count:
                        if cell.isActive and not cell.isSun and not cell.isInteractive:
                            cellcolor = (255,0,0)
                        else:                          
                            cellcolor = self.defaultColor
                
                tile = mapTile(x, y, cellcolor, count)
                self.addItem(tile)
                self.addItem(tile.textItem)
                count += 1

class mapScene(QGraphicsScene):
    
    def __init__(self, sceneWidth, sceneHeight):
        super().__init__()
        self.cellsize = 50
        self.width = sceneWidth
        self.height = sceneHeight
        self.defaultColor = (0,0,0)
        self.setSceneRect(50, 50, self.width, self.height)
        
    def clearScene(self):
        for item in self.items():
            self.removeItem(item)
            
    @pyqtSlot(int,tuple)
    def updateTileColor(self, tileid, color):
        tile = self.getTileByid(tileid)
        if tile:
            tile.setBrush(QColor(*color))
            
    @pyqtSlot(int)
    def rollbackTileColor(self, tileid):
        tile = self.getTileByid(tileid)
        if tile:
            tile.setBrush(QColor(*tile.originalColor))
    
        
    @pyqtSlot(dict)
    def drawMap(self, mapdata):
        self.clearScene()
        
        for cell in mapdata['cells']:
            print(f"cell all data {cell.CellID} {cell.layerGroundNum} {cell.layerObject1Num} {cell.layerObject2Num}")                    
        count  = 0
        for i in range(0,mapdata['height']):                
            for j in range(0,mapdata['width']):
                if i % 2 != 0 and j == mapdata['width'] - 1:
                    continue
                
                if i % 2 == 0:
                    x_offset = 0
                else:
                    x_offset = (self.cellsize)/2
                    
                x = 50 + (j * self.cellsize) + x_offset
                y = 50 + (i * self.cellsize/2)
                
                for cell in mapdata['cells']:                    
                    if cell.CellID == count:
                        if cell.isActive and not cell.isSun and not cell.isInteractive:
                            cellcolor = (255,0,0)
                        elif cell.isSun:
                            globalstore.store.updateChangeMapTiles(cell.CellID)                            
                            cellcolor = (255,255,0)
                        elif cell.isInteractive:
                            cellcolor = (0,255,0)
                            if cell.layerObject2Num in globalstore.store.dictPaysant.values():
                                globalstore.store.updateHarvestTiles({cell.CellID: ressourceStatus.SPAWNED})
                        else:                          
                            cellcolor = self.defaultColor
                
                tile = mapTile(x, y, cellcolor, count)
                self.addItem(tile)
                self.addItem(tile.textItem)
                count += 1        
        
    def getTileByid(self, tileid):
        for item in self.items():
            if isinstance(item, mapTile):
                if item.tileid == tileid:
                    return item
        return None
    
class mapManager(QObject):
    
    changeTileColor = pyqtSignal(int,tuple)
    rollbackTileColor = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.entities = dict()
        self.defaultColor = (0,0,0)
        
    def getCellColorByType(self, type):
        print(f"get cell color by type {type}")
        if type == "player":
            return (0,150,150)
        elif type == "monster":
            return (0,0,255)
        elif type == "npc":
            return (0,255,0)
        elif type == "merchant":
            return (117, 0, 246)
        elif type == "resource":
            return (255,0,255)
        else:
            return (255,0,0)
        
    def changeTileColorForHarvets(self, event, tileid):
        if event == ressourceStatus.SPAWNED:
            self.changeTileColor.emit(tileid, (0,255,0))
        elif event == ressourceStatus.NOTSPWANED:
            self.changeTileColor.emit(tileid, (0, 80, 24))
        elif event == ressourceStatus.HARVESTING:
            self.changeTileColor.emit(tileid, (0, 239, 197))
        elif event == ressourceStatus.ENDHARVEST:
            self.changeTileColor.emit(tileid, (0, 80, 24))
        
    def addEntity(self,id, entity : Entity):
        self.entities[f"{id}"] = entity
        if entity.currentCell:
            self.changeTileColor.emit(entity.currentCell, self.getCellColorByType(entity.type))

        if entity.OldCell:
            self.changeTileColor.emit(entity.OldCell, self.defaultColor)
    
    def delteEntity(self, id):
        entity = self.entities.get(f"{id}")
        if entity:
            if entity.currentCell and not self.checkForOtherEntitiesOnCell(entity.currentCell,id):
                self.rollbackTileColor.emit(entity.currentCell)
                
            del self.entities[f"{id}"]
    
    def clearAllEntities(self):
        self.entities.clear()
            
    def checkForOtherEntitiesOnCell(self, cellid , currententityid):
        for entity in self.entities.values():
            if entity.currentCell == cellid and entity.id != currententityid:
                print(f"other entity {entity.id} is on cell {cellid}")
                return True
            
    def entityMovedToCell(self, entityid, cellid):
        entity = self.entities.get(f"{entityid}")
        if not entity:
            return
        
        if entity :
            entity.OldCell = entity.currentCell
            entity.currentCell = cellid
            
            if entity.OldCell and not self.checkForOtherEntitiesOnCell(entity.OldCell,entityid):
                self.rollbackTileColor.emit(entity.OldCell)
                
            self.changeTileColor.emit(entity.currentCell, self.getCellColorByType(entity.type))
        
    def entityFight(self, entityid, isfighting):
        entity = self.entities[f"{entityid}"]
        entity.isFighting = isfighting
                     
        
    