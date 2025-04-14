
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
        self.pa = 0
        self.pm = 0
        self.pdv = 0
        self.pdvmax = 0
        self.initiative = 0
        self.resists = {}
        self.spells = []
        
    def withInfos(self, pa, pm, pdv, pdvmax, initiative, resists):
        self.pa = pa
        self.pm = pm
        self.pdv = pdv
        self.pdvmax = pdvmax
        self.initiative = initiative
        self.resists = resists
        return self