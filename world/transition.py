from settings import *
from support import lerp, main_font

class Transition:
    def __init__(self,world):
        self.display_surface = pygame.display.get_surface()
        self.world = world
        self.coord1,self.coord2, self.target_coord = 0,0,0
        self.axis, self.direction = "y",1
        self.active, self.stage = False,1
        self.room_name = "Level"
        self.font = main_font(60)
        self.name_surf = self.name_rect = None
        self.visible_name_r = None
        self.midway = False
        self.color = TRANSITION_COL
        self.midway_fun = None
    
    def start(self,axis,direction, room_name, midway_fun, color=TRANSITION_COL): # called by world
        self.midway = False
        #self.level.audio.play_fx("transition")
        self.axis = axis; self.direction = direction
        self.stage = 1; self.active = True
        if self.direction == 1: self.coord1,self.coord2,self.target_coord = 0,0,WIDTH if self.axis == "x" else HEIGHT
        else: self.coord1,self.target_coord = WIDTH if self.axis == "x" else HEIGHT,0; self.coord2 = self.coord1
        self.room_name = room_name
        self.name_surf = self.font.render(self.room_name,False,"white"); self.name_rect = self.name_surf.get_rect(center=(H_WIDTH,H_HEIGHT))
        self.visible_name_r = self.name_rect.copy(); self.visible_name_r.width = WIDTH; self.visible_name_r.center = (H_WIDTH,H_HEIGHT)
        self.color = color
        self.midway_fun = midway_fun
    
    ##### RUNTIME #####

    def update(self, dt):
        if self.active:
            if self.stage == 1:
                self.coord1 = lerp(self.coord1, self.target_coord, TRANSITION_SPEED * dt)
                if (self.direction == 1 and self.coord1 >= self.target_coord-TRANSITION_THRESHOLD) or \
                    (self.direction == -1 and self.coord1 <= self.target_coord+TRANSITION_THRESHOLD):
                    self.coord1 = self.target_coord
                    self.stage += 1
                    self.midway = True
                    self.midway_fun() if self.midway_fun else None
            elif self.stage == 2:
                self.coord2 = lerp(self.coord2, self.target_coord, TRANSITION_SPEED * dt)
                if (self.direction == 1 and self.coord2 >= self.target_coord-TRANSITION_THRESHOLD) or \
                    (self.direction == -1 and self.coord2 <= self.target_coord+TRANSITION_THRESHOLD):
                    self.coord2 = self.target_coord
                    self.active = False
    
    def draw(self):
        if self.active:
            if self.axis == "x":
                pygame.draw.rect(self.display_surface,self.color,
                                 (self.coord1 if self.direction == -1 else self.coord2, 0, abs(self.coord1-self.coord2), HEIGHT))
            elif self.axis == "y":
                pygame.draw.rect(self.display_surface,self.color,
                                 (0, self.coord1 if self.direction == -1 else self.coord2, WIDTH, abs(self.coord1-self.coord2)))