
from PyQt5.QtCore import pyqtSignal, QObject

class Entity(QObject):
    def __init__(self, id, startCell, level, template, type, ismonstergroup):
        super().__init__()
        self.isAlive = True
        self.id = id
        self.currentCell = startCell
        self.OldCell = None
        self.template = template
        self.level = level
        self.type = type
        self.stats = {}
        self.spells = []
        self.isFighting = False
        self.isMonsterGroup = ismonstergroup