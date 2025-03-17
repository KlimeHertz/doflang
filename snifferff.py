from scapy.all import sniff
from scapy.all import Raw
from map import Map
import socket, time
from mapview import MapViewer
import threading

# Define the IP address to filter
TARGET_IP = ["52.214.173.25","54.216.162.213"]  # Change this to the desired IP address

def get_Cell_Id_From_Hash(cell_code):
    char1 = cell_code[0]
    char2 = cell_code[1]
    
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
    print((code1 + code2))
    return (code1 + code2)

def update_entity(packet):
        if packet[:4] == "GA;0" or packet[:3] == "GAS" or packet[:3] == "GAF":
            return
        data = packet[2:].split(";")
        action_id = int(data[1])
        entity_id = int(data[2])
        #Travel on the map
        if action_id == 1:
            end_cell = get_Cell_Id_From_Hash(data[3][len(data[3]) - 2:])
            print(f"entity {entity_id} moved to cell {end_cell}")
        #Le personnage recolte
        elif action_id == 501:
            
            harvest_time = int(data[3].split(",")[1]) / 1000
            cell_id = data[3].split(",")[0]
            type_of_harvest = data[0]
            print(f"harvest time {harvest_time} cell {cell_id} type {type_of_harvest}")
            
        #combat
        elif action_id == 905:
            print("combat start")
            
        #entity pousser
        elif action_id == 5:
            data_entity_cible = data[3].split(",")
            print(f"entity {entity_id} pushed to cell {data_entity_cible[0]}")
            
        elif action_id == 103:
            id_du_mort = int(data[3])
            print(f"mort du mob {id_du_mort}")

def parse_data(packet):
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
                        print(f"mob {entity_id} added cell {cell} pa {infos[12]} vie {infos[13]} pm {infos[14]}")
                    else:
                        print(f"mob {entity_id} added cell {cell}")
                    #self.entities.append(Entity('Mob', cell=cell, id=entity_id, template=template, pa=infos[12], vie=infos[13], pm=infos[14]))
                elif type_ == -3:  # group of mob
                    templates = list(map(int, template.split(',')))
                    levels = list(map(int, infos[7].split(',')))
                    entity_id = int(infos[3])

                    print(f"group of mob {entity_id} added cell {cell}, templates {templates}, levels {levels}")
                elif type_ == -4:  # NPC
                    pass  # map.entities.add(id, Npc(id, int(nombre_template), cell))
                elif type_ == -5:  # Merchants
                    pass  # map.entities.add(id, Mercantes(id, cell))
                elif type_ == -6:  # resources
                    pass
                else:  # players
                    print(f"player {infos[4]} added cell {cell}")
            
            elif instance[0] == '-':  # player leave
                print("player leave")

def server_packet(packet):
        print(f"packet {packet[:2]}")
        #character information
        if packet[:3] == "ASK":
            info_perso = packet[3:].split("|")
            print(f"info perso {info_perso}")
        #spell   (lvl,available spell...)
        elif packet[:2] == "SL" and packet[2:4] != "o+":
            spells_data = packet[2:].split(";")
            print(f"spells data {spells_data}")
        #character stats (all stats pa, pm, res fix, rex....)
        elif packet[:2] == "As":
            stats = packet[2:].split("|")           
            print(f"stats {stats}")
        #map information (mapid, date of creation,key)
        elif packet[:3] == "GDM":
                data = packet.split("|")
                mapID = data[1]
                map_date = data[2]
                decryption_key = data[3]
                #print(f"mapID: {mapID}, date: {map_date}, key: {decryption_key}")
                map = Map()
                dictmapdata=map.data(mapID, map_date, decryption_key)
                mapviewer = MapViewer(dictmapdata)
                mapviewer.draw()
        #entity map information
        elif packet[:2] == "GM":
            parse_data(packet)
        elif packet[:3] == "GDF" and len(packet) > 7:
            #self.map_frame.update_interactive(packet)
            pass
        if packet[:2] == "GA":
            print("update entity")
            update_entity(packet)
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

def packet_callback(packet):
    if packet.haslayer("IP") and packet["IP"].src in TARGET_IP:
        if packet.haslayer(Raw):
            payload = packet[Raw].load.decode()
            for packet in payload.split("\x00"):
                print(packet)
                server_packet(packet)
        else:
            payload = None
        #print(f"Captured Packet from {packet["IP"].src}: {payload}")


if __name__ == "__main__":
    # Start sniffing packets in a background thread and run pygame in the main thread
    filter_str = " or ".join([f"src host {ip}" for ip in TARGET_IP])
    sniff_thread = threading.Thread(target=sniff, kwargs={'filter': filter_str, 'prn': packet_callback, 'store': 0}, daemon=True)
    sniff_thread.start()
    #sniff(filter=filter_str, prn=packet_callback, store=0)
    while True:
        time.sleep(0.1)
    
    