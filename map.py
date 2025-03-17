import yaswfp.swfparser as swfparser
from urllib.parse import unquote
from cell import Cell

PATH = r"C:\Users\UltraPc\AppData\Local\Ankama\Retro\resources\app\retroclient\data\maps"
HEX_CHARS = "0123456789ABCDEF"
ZKARRAY = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
SUN_MAGICS = [1030, 1029, 4088]

class mapDecrypt():
    
    def __init__(self):
        self.binairemap = []
        self.carreau = []
        self.mapswidth = 0
        self.sun = []
        self.entity = []
        self.resource = []
        self.resource = []
        self.cells = list() 

    def getMapData(self, mapID, map_date, decryption_key):
        self.mapID = mapID
        self.map_date =map_date
        self.decryption_key = decryption_key
        #self.entityself.entity = None
        MAP_DIR = PATH
        self.path = '{}/{}_{}{}.swf'.format(MAP_DIR, mapID, map_date, 'X' if decryption_key else '')
        #pos = MAPID_TO_POS[mapID]
        #self.x = pos[0]
        #self.y = pos[1]
        swf = swfparser.parsefile(self.path)
        raw_map_data = swf.tags[1].Actions[0].ConstantPool[14]   
        self.width = int(swf.tags[1].Actions[17].Integer)
        self.height = (int(swf.tags[1].Actions[20].Integer) - 1) * 2
        data = self.decrypt_mapdata(raw_map_data, decryption_key)
        raw_cells = [data[i:i+10] for i in range(0, len(data), 10)]
        #print(f"all map data {raw_cells}, {self.width}, {self.height} data : {data}")
        self.cells = [Cell(raw_cells[i],i) for i in range(len(raw_cells))]
        #for cell in self.cells:
        #    cell.print_cell()
        return {'width': self.width, 'height': self.height, 'cells': self.cells}
    

    def decrypt_mapdata(self, raw_data, raw_key):
        key = unquote(''.join([chr(int(raw_key[i:i+2], 16)) for i in range(0, len(raw_key), 2)]))
        checksum = int(HEX_CHARS[sum(map(lambda x: ord(x) & 0xf, key)) & 0xf], 16) * 2
        key_length = len(key)
        data = ''
        for i in range(0, len(raw_data), 2):
            data += chr(int(raw_data[i:i+2], 16) ^ ord(key[(int(i / 2) + checksum) % key_length]))
        return data
    
    def unhash_cell(self,raw_cell):
        return [ZKARRAY.index(i) for i in raw_cell]
