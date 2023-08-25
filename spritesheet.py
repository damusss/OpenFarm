from settings import *

class SingleSpritesheet:
    def __init__(self, surface:pygame.Surface, w=None):
        self.sheet = surface
        self.size = self.sheet.get_height()
        self.w = w if w else self.size
        self.len = self.sheet.get_width()//self.w
    
    def frames(self):
        return [self.sheet.subsurface((i*self.w,0,self.w,self.size)) for i in range(self.len)]
    
class Spritesheet:
    def __init__(self, surface:pygame.Surface, size:int):
        self.sheet = surface
        self.size = size
        self.len_w,self.len_h = self.sheet.get_width()//self.size,self.sheet.get_height()//self.size
        
    def frames(self,scale=1):
        return [pygame.transform.scale_by(self.sheet.subsurface((self.size*col,self.size*row,self.size,self.size)),scale) \
            for row in range(self.len_h) for col in range(self.len_w)]
    
    def frames_grid(self,scale=1):
        return [[pygame.transform.scale_by(self.sheet.subsurface((self.size*col,self.size*row_i,self.size,self.size)),scale) \
            for col in range(self.len_w)] for row_i in range(self.len_h) ]
    