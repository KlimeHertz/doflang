import pygame
import time


class MapViewer():
    
    def __init__(self,mapdata):
        pygame.init()
        self.mapdata = mapdata
        self.cellsize = 50
        self.mapcells = mapdata['cells']
        self.mapXcellCount = mapdata['width']
        self.mapYcellCount = int(mapdata['height'])
        self.width = (self.cellsize * self.mapXcellCount) + self.cellsize * 2
        self.height = (self.cellsize * self.mapYcellCount/2) + self.cellsize * 2
        self.font = pygame.font.Font(None, 18)
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.defaultColor = (0,0,0)
        self.x_offset = self.cellsize
        self.y_offset = self.cellsize
        
        
    def draw(self):
        print(f"map width {self.mapXcellCount} map height {self.mapYcellCount}")
        count  = 0
        running = True
        while running:
            count  = 0
            for i in range(0,self.mapYcellCount):                
                for j in range(0,self.mapXcellCount):
                    
                    if i % 2 != 0 and j == self.mapXcellCount - 1:
                        continue
                    
                    if i % 2 == 0:
                        x_offset = 0
                    else:
                        x_offset = (self.cellsize)/2
                        
                    x = self.x_offset + (j * self.cellsize) + x_offset
                    y = self.y_offset + (i * self.cellsize/2)
                    
                    diamond = [(x, y - self.cellsize // 2),
                            (x + self.cellsize // 2, y),
                            (x, y + self.cellsize // 2),
                            (x - self.cellsize // 2, y)]
                    
                    for cell in self.mapcells:
                        if cell.CellID == count:
                            if cell.isActive and not cell.isSun and not cell.isInteractive:
                                cellcolor = (255,0,0)
                            elif cell.isSun:                            
                                cellcolor = (255,255,0)
                            elif cell.isInteractive:
                                cellcolor = (0,255,0)
                            else:                          
                                cellcolor = self.defaultColor
                    
                    pygame.draw.polygon(self.screen, cellcolor, diamond)
                    pygame.draw.polygon(self.screen, (255,255,255), diamond, 2)
                    
                    text = self.font.render(str(count), True, (255,255,255))
                    text_rect = text.get_rect(center=(x, y))
                    self.screen.blit(text, text_rect)
                    count += 1
        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            pygame.display.update()
            time.sleep(0.1)
        pygame.quit()
            