from PyQt5.QtCore import pyqtSignal, QObject
from scapy.all import sniff
from scapy.all import Raw
import socket, time
from map import mapDecrypt
from entity import Entity

TARGET_IP = ["52.214.173.25","54.216.162.213"] 

class snifferWorker(QObject):
    updateTextZone = pyqtSignal(str)
    updateMapView = pyqtSignal(dict)
    clearScene = pyqtSignal()
    entityOnCell = pyqtSignal(int,tuple)
    
    def __init__(self, mapManager):
        super().__init__()
        self.mapDecrypter = mapDecrypt()
        self.mapManager = mapManager
        
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
        #print(f"packet {packet[:2]}")
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
                    self.mapManager.changeTileColorForHarvets("spawn", int(TramGDKSplit[0]))
                elif TramGDKSplit[1] == "4":
                    self.updateTextZone.emit(f"ressource absent on {TramGDKSplit[0]}")
                    self.mapManager.changeTileColorForHarvets("notpresent", int(TramGDKSplit[0]))
                elif TramGDKSplit[1] == "3":
                    self.updateTextZone.emit(f"end harveste on {TramGDKSplit[0]}")
                    self.mapManager.changeTileColorForHarvets("harvested", int(TramGDKSplit[0]))
                elif TramGDKSplit[1] == "2":
                    self.updateTextZone.emit(f"start harvest on {TramGDKSplit[0]}")
                    self.mapManager.changeTileColorForHarvets("harvesting", int(TramGDKSplit[0]))
                    
        if packet[:2] == "GA":
            self.parseGAPacket(packet)
        elif packet[:3] == "GIC":
            #self.combat.mouv_start_cell(packet)
            pass
        elif packet[:2] == "GE":
            #self.character.isfighting = False
            pass
        elif packet[:3] == "GTM":
            #self.combat.update_carac_entity(packet)          
            pass
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
            #self.entityOnCell.emit(entity_id,end_cell,(0,0,255))
            self.mapManager.entityMovedToCell(entity_id, end_cell)
            
        #Le personnage recolte
        elif action_id == 501:     
            harvest_time = int(data[3].split(",")[1]) / 1000
            cell_id = data[3].split(",")[0]
            type_of_harvest = data[0]
            self.updateTextZone.emit(f"harvest time {harvest_time} cell {cell_id} type {type_of_harvest}")
            
        #combat
        elif action_id == 905:
            self.updateTextZone.emit("combat start")

        #entity pousser
        elif action_id == 5:
            data_entity_cible = data[3].split(",")
            self.updateTextZone.emit(f"entity {entity_id} pushed to cell {data_entity_cible[0]}")
            
        elif action_id == 103:
            id_du_mort = int(data[3])
            self.updateTextZone.emit(f"mort du mob {id_du_mort}")
            
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
                    # if not self.character_state.isFighting:
                    #    return
                    #monster_team = infos[15] if len(infos) <= 18 else infos[22]
                    levels = list(map(int, infos[7].split(',')))
                    if len(infos) == 12:
                        self.updateTextZone.emit(f"mob {entity_id} added to cell {cell} pa {infos[12]} vie {infos[13]} pm {infos[14]}")                        
                    else:
                        self.updateTextZone.emit(f"mob {entity_id} added to cell {cell}")            
                        
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
        sniff(filter=filterStr, prn=self.updateWindowFeedText, store=0)