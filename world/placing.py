from settings import *
from support import get_window, tint_surface
from world.sprites import HouseExteriorTile, InvisibleVillageElementTile

class PlacingSystem:
    def __init__(self, world):
        self.world = world
        self.inventory = self.world.player.inventory
        self.assets = self.world.assets
        self.display_surface = get_window()
        
        self.green_imgs = {name: tint_surface(image, (0, 100, 0)) for name, image in self.assets["ui"]["items"].items()}
        self.red_imgs = {name: tint_surface(image, (80, 0, 0)) for name, image in self.assets["ui"]["items"].items()}
        
        self.can_place = False
        self.preview_topleft = (-100,-100)
        self.world_pos = (0,0)
        self.mode = 0
        
        self.place_table = {
            "fence": self.place_fence
        }
        
    def check(self):
        if not self.world.current_zone or not self.inventory.selected_object or self.inventory.selected_object not in PLACEABLE or self.world.current_zone.in_house:
            self.can_place = False
            return True
        if (WINDOW_CENTER-pygame.mouse.get_pos()).length() > INTERACT_RADIUS:
            self.can_place = False
            return True
        return False
        
    def update(self, dt):
        if self.check(): return
        
        mouse_pos = pygame.mouse.get_pos()
        self.world_pos = mouse_pos+self.world.offset
        self.preview_topleft = (self.world_pos.x-self.world_pos.x % TILE_SIZE, self.world_pos.y-self.world_pos.y % TILE_SIZE)
        center_pos = (self.preview_topleft[0] + H_TILE_SIZE, self.preview_topleft[1] + H_TILE_SIZE)
        
        self.can_place = self.world.current_zone.can_place(center_pos)
        
    def draw(self):
        if self.check(): return
        
        obj_name = self.inventory.selected_object
        if self.mode != 0:
            obj_name += f"{self.mode}"
        self.display_surface.blit(self.green_imgs[obj_name] if self.can_place else self.red_imgs[obj_name],
                                  self.preview_topleft-self.world.offset)
        
    def place(self):
        if self.check(): return
        
        self.place_table[self.inventory.selected_object]()
        
    def destroy(self):
        if self.check(): return
        
        for element in self.world.current_zone.village_elements:
            if element.asset_name in ["fences"] and element.hitbox.collidepoint(self.world_pos):
                element.kill()
                if element.asset_name == "fences":
                    self.inventory.add_object("fence",1)
        
        self.refresh_fences()
        
    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.place()
            else:
                self.destroy()
        if event.type == pygame.MOUSEWHEEL and not self.check():
            self.mode -= event.y
            if self.mode < 0:
                self.mode = PLACEABLE_DATA[self.inventory.selected_object]-1
            if self.mode >= PLACEABLE_DATA[self.inventory.selected_object]:
                self.mode = 0
                
    # fence
    def place_fence(self):
        fence = HouseExteriorTile(self.preview_topleft,12 if self.mode == 1 else 1, self.world.current_zone, NO_TINT, None, False, False, "fences", False, False)
        if self.mode == 1:
            fence.kinematic = True
        self.refresh_fences()
    
    def fence_there(self, pos):
        for element in self.world.current_zone.village_elements:
            if element.asset_name in ["fences"] and not element.kinematic and element.rect.collidepoint(pos):
                return True
        return False
    
    def refresh_fences(self):
        for element in self.world.current_zone.village_elements:
            if element.asset_name in ["fences"] and not element.kinematic:
                self.refresh_fence(element)
                
    def refresh_fence(self, fence):
        center = vector(fence.hitbox.center)
        left = center + vector(-TILE_SIZE, 0)
        right = center + vector(TILE_SIZE, 0)
        top = center + vector(0, -TILE_SIZE)
        bottom = center + vector(0, TILE_SIZE)
        l, r, t, b = self.fence_there(left), self.fence_there(right), self.fence_there(top), self.fence_there(bottom)
        asset_index = 12
        
        if l and r and t and b: asset_index = 6
        elif t and b and r: asset_index = 5
        elif t and b and l: asset_index = 7
        elif l and r and b: asset_index = 2
        elif l and r and t: asset_index = 10
        elif r and b: asset_index = 1
        elif l and b: asset_index = 3
        elif t and r: asset_index = 9
        elif t and l: asset_index = 11
        elif b and t: asset_index = 4
        elif l and r: asset_index = 14
        elif b: asset_index = 0
        elif t: asset_index = 8
        elif r: asset_index = 13
        elif l: asset_index = 15
        
        fence.asset_index = asset_index
        fence.image = self.assets["house"]["fences"][asset_index]
        
        