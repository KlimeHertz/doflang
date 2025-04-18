ZKARRAY = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
SUN_MAGICS = [1030, 1029, 4088]



def unhash_cell(raw_cell):
    return [ZKARRAY.index(i) for i in raw_cell]


class Cell:
    def __init__(self, raw_data,CellID):
        self.raw_data = raw_data
        self.entity = []
        self.color = 'black'
        self.CellID = CellID
        cd =  unhash_cell(raw_data)
        self.cd = cd
        if cd[2] == 0 or cd[0]==1 or cd[0] == 33 and cd[2]==1:
            self.isActive = False 
        else:
            self.isActive = (cd[0] & 32 >> 5) != 0
            
        self.isInteractive = ((cd[7] & 2) >> 1) != 0   
        self.lineOfSight = (cd[0] & 1) == 1
        self.layerGroundRot = cd[1] & 48 >> 4
        self.groundLevel = cd[1] & 15
        self.movement = ((cd[2] & 56) >> 3)
        self.layerGroundNum = (cd[0] & 24 << 6) + (cd[2] & 7 << 6) + cd[3]
        self.layerObject1Num = ((cd[0] & 4) << 11) + ((cd[4] & 1) << 12) + (cd[5] << 6) + cd[6]
        self.layerObject2Num = ((cd[0]&2)<<12) + ((cd[7]&1)<<12) + (cd[8]<<6) + cd[9]
        self.isSun = self.layerObject1Num in SUN_MAGICS or self.layerObject2Num in SUN_MAGICS
        self.text = str(self.movement)
        self.set_default_color()
    
    def print_cell(self):
        print(f"CellID : cell cd {self.cd} {self.CellID} isActive : {self.isActive} isInteractive : {self.isInteractive} lineOfSight : {self.lineOfSight} layerGroundRot : {self.layerGroundRot} groundLevel : {self.groundLevel} movement : {self.movement} layerGroundNum : {self.layerGroundNum} layerObject1Num : {self.layerObject1Num} layerObject2Num : {self.layerObject2Num} isSun : {self.isSun}")
        
    def getAdjacentCells(self):
        return [self.CellID - 1, self.CellID + 1, self.CellID - 14, self.CellID + 14, self.CellID - 15, self.CellID + 15]

    def set_default_color(self):
        if self.entity != []:
            self.color = 'red'
        elif self.isSun:
            self.color = 'yellow'
            self.text = 'S'
        elif self.isInteractive:
            self.text = ' '
            self.color = 'green'
        elif self.isActive:
            self.text = ' '
            self.color = 'white'
    
    def get_entity(self,entity_id):
        for entity in self.entity:
            if entity.id == entity_id:
                return entity
                
    def set_not_interactive(self, good):
        if good:
            self.color = 'green'
            self.isInteractive = True
        else:
            self.color = 'brown'
            self.isInteractive = False
    
    def __str__(self):
        return self.text