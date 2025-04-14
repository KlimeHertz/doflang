from PyQt5.QtCore import pyqtSignal, QObject
from scapy.all import sniff
from scapy.all import Raw
import socket, time
from map import mapDecrypt
from entity import Entity
from helper import ressourceStatus
import globalstore

TARGET_IP = ["52.214.173.25","54.216.162.213"] 

class snifferWorker(QObject):
    updateTextZone = pyqtSignal(str)
    updateMapView = pyqtSignal(dict)
    clearScene = pyqtSignal()
    entityOnCell = pyqtSignal(int,tuple)
    combatStart = pyqtSignal()
    combatEnd = pyqtSignal()
    combatPositionUpdate = pyqtSignal(int,tuple)
    addPlayerToTree = pyqtSignal(dict)
    addMonsterToTree = pyqtSignal(dict)
    moveToTest = pyqtSignal(int)
    
    def __init__(self, mapManager,combatManager):
        super().__init__()
        self.mapDecrypter = mapDecrypt()
        self.mapManager = mapManager
        self.combatManager = combatManager
        
    def updateWindowFeedText(self, packet):
        if packet.haslayer("IP") and packet["IP"].src in TARGET_IP:
            if packet.haslayer(Raw):
                payload = packet[Raw].load.decode()
                for packet in payload.split("\x00"):
                    print(packet)
                    self.__parsePacket(packet)
            else:
                payload = None
                
        
    def __parsePacket(self, packet):
        #character information
        if packet[:3] == "ASK":
            info_perso = packet[3:].split("|")
            self.updateTextZone.emit("info perso")
        #spell   (lvl,available spell...)
        
        elif packet[:2] == "SL" and packet[2:4] != "o+":
            spells_data = packet[2:].split(";")
            print(f"spells data {spells_data}")
            self.updateTextZone.emit("spells data")
        #character stats (all stats pa, pm, res fix, rex....)
        
        elif packet[:2] == "As":
            stats = packet[2:].split("|")           
            print(f"stats {stats}")
            self.updateTextZone.emit("stats")
            
        #map information (mapid, date of creation,key)
        elif packet[:3] == "GDM":
                data = packet.split("|")
                mapID = data[1]
                map_date = data[2]
                decryption_key = data[3]
                globalstore.store.mapChangeClear()
                dictmapdata=self.mapDecrypter.getMapData(mapID, map_date, decryption_key)
                self.mapManager.clearAllEntities()
                self.updateMapView.emit(dictmapdata)
                self.updateTextZone.emit("\t\t>>>> map changed <<<<\t\t")
                
        #entity map information
        elif packet[:2] == "GM":
            self.parseGMPacket(packet)
            
        #ressource information
        elif packet[:3] == "GDF" and len(packet) > 7:
            for tramGDK in packet[4:].split("|"):
                TramGDKSplit = tramGDK.split(";")
                if TramGDKSplit[1] == "5":
                    self.updateTextZone.emit(f"ressource spawn on {TramGDKSplit[0]}")
                    self.mapManager.changeTileColorForHarvets(ressourceStatus.SPAWNED, int(TramGDKSplit[0]))                    
                    globalstore.store.updateHarvestTiles({int(TramGDKSplit[0]): ressourceStatus.SPAWNED})
                elif TramGDKSplit[1] == "4":
                    self.updateTextZone.emit(f"ressource absent on {TramGDKSplit[0]}")
                    self.mapManager.changeTileColorForHarvets(ressourceStatus.NOTSPWANED, int(TramGDKSplit[0]))                    
                    globalstore.store.updateHarvestTiles({int(TramGDKSplit[0]): ressourceStatus.NOTSPWANED})
                elif TramGDKSplit[1] == "3":
                    self.updateTextZone.emit(f"end harveste on {TramGDKSplit[0]}")
                    self.mapManager.changeTileColorForHarvets(ressourceStatus.ENDHARVEST, int(TramGDKSplit[0]))
                    globalstore.store.updateHarvestTiles({int(TramGDKSplit[0]): ressourceStatus.ENDHARVEST})
                elif TramGDKSplit[1] == "2":
                    self.updateTextZone.emit(f"start harvest on {TramGDKSplit[0]}")
                    self.mapManager.changeTileColorForHarvets(ressourceStatus.HARVESTING, int(TramGDKSplit[0]))
                    globalstore.store.updateHarvestTiles({int(TramGDKSplit[0]): ressourceStatus.HARVESTING})
                    
        if packet[:2] == "GA":
            self.parseGAPacket(packet)
        elif packet[:3] == "GIC":
            color = None
            for tram in packet[4:].split("|"):
                tramSplit = tram.split(";")
                if self.combatManager.getEntityTypeById(int(tramSplit[0])) == "player":
                    color = (0,0,255)
                else:
                    color = (0,255,0)

                pos = int(tramSplit[1])
                self.combatManager.updateEntityPosition(int(tramSplit[0]), pos) 
                self.combatManager.rollbackOldCellColor(int(tramSplit[0]))                              
                self.combatPositionUpdate.emit(pos,color)
        elif packet[:2] == "GE":
            self.updateTextZone.emit("\t\t>>>> combat end <<<<\t\t")
            self.combatEnd.emit()
            self.combatManager.combatEnd()
        elif packet[:3] == "GTM":
            trams = packet[4:].split("|")                   
            for tram in trams:
                if len(tram) <= 4:
                    tramSplit = tram.split(";")
                    statsDict = {
                    "id": int(tramSplit[0]),
                    "pdv": 0,
                    "pa": 0,
                    "pm": 0,
                    "pdvmax": 0
                }
                else:
                    tramSplit = tram.split(";")
                    statsDict = {
                        "id": int(tramSplit[0]),
                        "pdv": int(tramSplit[2]),
                        "pa": int(tramSplit[3]),
                        "pm": int(tramSplit[4]),
                        "pdvmax": int(tramSplit[7])
                    }
                self.combatManager.updateEntityStats(int(tramSplit[0]), statsDict)
                
                if self.combatManager.getEntityTypeById(int(tramSplit[0])) == "player":
                    self.addPlayerToTree.emit(statsDict)
                else:
                    self.addMonsterToTree.emit(statsDict)
                
        elif packet[:3] == "GTS":
            data =  packet[3:].split("|")
            print("debut du tour...")
            
            
    def parseGAPacket(self,packet):
        if packet[:4] == "GA;0" or packet[:3] == "GAS" or packet[:3] == "GAF":
            return
        data = packet[2:].split(";")
        action_id = int(data[1])
        entity_id = int(data[2])
        
        #Travel on the map
        if action_id == 1:
            end_cell = self.getCellIdFromHash(data[3][len(data[3]) - 2:])
            self.updateTextZone.emit(f"entity {entity_id} moved to cell {end_cell}")
            if self.combatManager.isInCombat():                                
                self.combatManager.updateEntityPosition(int(entity_id), int(end_cell))
                
                color = None
                if self.combatManager.getEntityTypeById(int(entity_id)) == "player":
                    color = (0,0,255)
                else:
                    color = (0,255,0)
                    
                self.combatManager.rollbackOldCellColor(int(entity_id))                              
                self.combatPositionUpdate.emit(int(end_cell),color)                
                
            else:
                self.mapManager.entityMovedToCell(entity_id, int(end_cell))
            
        #Le personnage recolte
        elif action_id == 501:     
            harvest_time = int(data[3].split(",")[1]) / 1000
            cell_id = data[3].split(",")[0]
            type_of_harvest = data[0]
            self.updateTextZone.emit(f"harvest time {harvest_time} cell {cell_id} type {type_of_harvest}")
            
        #combat
        elif action_id == 905:
            self.updateTextZone.emit("\t\t>>>> combat start <<<<\t\t")
            self.combatStart.emit()
            PlayerEntity = Entity(entity_id, 0, 0, 0, "player", False)
            self.combatManager.combatStart()
            self.combatManager.addPlayerEntity(PlayerEntity)

        #entity pousser
        elif action_id == 5:
            data_entity_cible = data[3].split(",")
            self.updateTextZone.emit(f"entity {entity_id} pushed to cell {data_entity_cible[0]}")
            
        elif action_id == 103:
            id_du_mort = int(data[3])
            self.updateTextZone.emit(f"mort du mob {id_du_mort}")
            self.combatPositionUpdate.emit(self.combatManager.getEntityById(id_du_mort).currentCell, (255,0,0))
            self.combatManager.deleteEntity(id_du_mort)            
            
    def getCellIdFromHash(self,cellCode):
        char1 = cellCode[0]
        char2 = cellCode[1]
        
        carac_array = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
        'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F',
        'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
        'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', '_'] 
        
        code1 = 0
        code2 = 0
        a = 0
        
        while (a < len(carac_array)):
        
            if (carac_array[a] == char1):
                code1 = (a * 64)

            if (carac_array[a] == char2):
                code2 = a

            a += 1
        return (code1 + code2)
        
    def parseGMPacket(self,packet):
        entity = None
        instances = packet[3:].split('|')
        for instance in instances:
            if len(instance) < 1:
                continue
            if instance[0] == '+':
                infos = instance[1:].split(';')
                if len(infos) < 6:
                    continue

                cell = int(infos[0])
                template = infos[4]
                try:
                    type_ = int(infos[5]) if ',' not in infos[5] else int(infos[5].split(',')[0])
                except:
                    continue
                
                entity_id = int(infos[3])

                # SWITCH
                if type_ == -1:  # creature
                    pass
                elif type_ == -2:  # mob
                    if not self.combatManager.isInCombat():
                        return
                    #monster_team = infos[15] if len(infos) <= 18 else infos[22]
                    levels = list(map(int, infos[7].split(',')))
                    if len(infos) == 12:
                        self.updateTextZone.emit(f"mob {entity_id} added to cell {cell} vie {infos[12]} pm {infos[13]} pa {infos[14]}")                        
                    else:
                        self.updateTextZone.emit(f"mob {entity_id} added to cell {cell}")
                        
                    entityMonster = Entity(entity_id, cell, levels, 0, "monster", False)
                    entityMonster.withInfos(int(infos[14]), int(infos[13]), int(infos[12]), int(infos[12]), 0, {})         
                    self.combatManager.addMonsterEntity(entityMonster)
                    self.combatManager.rollbackOldCellColor(entity_id)
                    self.combatPositionUpdate.emit(cell, (0,255,0))
                
                elif type_ == 10 and self.combatManager.isInCombat():  # personnage
                    self.updateTextZone.emit(f"player {entity_id} added to cell {cell}")
                    self.combatManager.entitySetStartCell(entity_id, cell)
                    self.combatManager.rollbackOldCellColor(entity_id)
                    self.combatPositionUpdate.emit(cell, (0,0,255))
                    
                elif type_ == -3:  # group of mob
                    templates = list(map(int, template.split(',')))
                    levels = list(map(int, infos[7].split(',')))
                    entity_id = int(infos[3])
                    self.updateTextZone.emit(f"group of mob {entity_id} added to cell {cell}, templates {templates}, levels {levels}")
                    entity = Entity(entity_id, cell, levels, templates, "monster", True)                                        
                elif type_ == -4:  # NPC                    
                    self.updateTextZone.emit(f"npc {entity_id} added to cell {cell}")
                    entity = Entity(entity_id, cell, 0, 0,  "npc", False)
                elif type_ == -5:  # Merchants
                    self.updateTextZone.emit(f"merchant {entity_id} added to cell {cell}")
                    entity = Entity(entity_id, cell, 0, 0,  "merchant", False)
                elif type_ == -6:  # resources                                      
                    globalstore.store.updateHarvestTiles({cell: ressourceStatus.SPAWNED})
                    self.updateTextZone.emit(f"resource {entity_id} added to cell {cell}")
                    entity = Entity(entity_id, cell, 0, 0,  "resource", False)
                else:  # players
                    self.updateTextZone.emit(f"player {infos[4]} entity id : {entity_id} added to cell {cell}")
                    entity = Entity(entity_id, cell, 0, 0, "player", False)
                    
                if entity:
                    self.mapManager.addEntity(entity_id, entity)
                
            elif instance[0] == '-':  # player leave
                self.updateTextZone.emit(f"player {instance[1:]} left")
                self.mapManager.delteEntity(int(instance[1:]))
                        
                        
    def run(self):
        filterStr = " or ".join([f"src host {ip}" for ip in TARGET_IP])
        try:
            sniff(filter=filterStr, prn=self.updateWindowFeedText, store=0)
        except Exception as e:
            print(f"sniffer error {e}")