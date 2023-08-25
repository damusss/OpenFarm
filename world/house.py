from settings import *
from world.generic import Group, CameraGroup
from world.sprites import HouseExteriorTile, HouseTile, HouseDecoration, InvisibleVillageElementTile, Merchant
from support import get_window, weighted_choice, generate_villager
import datetime

class Fences:

    @staticmethod
    def generate(topleft, zone):
        topleft = vector(topleft)
        size_x, size_y = choice([5,7]), choice([5,7])

        for x in range(size_x):
            for y in range(size_y):
                pos = topleft+vector(x*TILE_SIZE, y*TILE_SIZE)
                if x == 0: # left
                    if y == 0: HouseExteriorTile(pos, 1, zone, None, False, False, "fences", False) # topleft
                    elif y == size_y-1: HouseExteriorTile(pos, 9, zone,None, False, False, "fences", False) # bottomleft
                    elif y == int(size_y/2): # left half
                        t = HouseExteriorTile(pos, 12, zone, None, False, False, "fences", False)
                        t.kinematic = True
                    elif y == int(size_y/2)-1: HouseExteriorTile(pos, 8, zone, None, False, False, "fences", False) # left half-1
                    elif y == int(size_y/2)+1: HouseExteriorTile(pos, 0, zone, None, False, False, "fences", False) # left half+1
                    else: HouseExteriorTile(pos, 4, zone, None, False, False, "fences", False) # left middle
                elif x == size_x-1: # right
                    if y == 0: HouseExteriorTile(pos, 3, zone, None, False, False, "fences", False) # topright
                    elif y == size_y-1: HouseExteriorTile(pos, 11, zone, None, False, False, "fences", False) # bottomright
                    elif y == int(size_y/2): # right half
                        t = HouseExteriorTile(pos, 12, zone, None, False, False, "fences", False)
                        t.kinematic = True
                    elif y == int(size_y/2)-1: HouseExteriorTile(pos, 8, zone, None, False, False, "fences", False) # right half-1
                    elif y == int(size_y/2)+1: HouseExteriorTile(pos, 0, zone, None, False, False, "fences", False) # right half+1
                    else: HouseExteriorTile(pos, 4, zone, None, False, False, "fences", False) # right middle
                elif x == int(size_x/2): # half
                    if y == 0 or y == size_y-1:
                        t=HouseExteriorTile(pos, 12, zone, None, False, False, "fences", False)
                        t.kinematic = True
                    else: InvisibleVillageElementTile(pos, zone)
                elif x == int(size_x/2)-1: # half - 1
                    if y == 0 or y == size_y-1: HouseExteriorTile(pos, 15, zone, "left", False, False, "fences", False)
                    else: InvisibleVillageElementTile(pos, zone)
                elif x == int(size_x/2)+1: # half + 1
                    if y == 0 or y == size_y-1: HouseExteriorTile(pos, 13, zone, "right", False, False, "fences", False)
                    else: InvisibleVillageElementTile(pos, zone)
                else: # middle
                    if y == 0 or y == size_y-1: HouseExteriorTile(pos, 14, zone, None, False, False, "fences", False)
                    else: InvisibleVillageElementTile(pos, zone)
        return pygame.Rect((topleft.x, topleft.y), (size_x*TILE_SIZE, size_y*TILE_SIZE))

class House:
    neighbor_pos = {
            "-1;-1":vector(-1,-1),
            "-1;0":vector(-1,0),
            "-1;1":vector(-1,1),
            "0;-1":vector(0,-1),
            "0;1":vector(0,1),
            "1;-1":vector(1,-1),
            "1;0":vector(1,0),
            "1;1":vector(1,1)
        }
    max_size = 8*TILE_SIZE

    def __init__(self, topleft, grid_pos, zone, from_file=False, **kwargs):
        self.topleft = vector(topleft)
        self.grid_pos = vector(grid_pos)
        self.zone = zone
        self.exterior = HouseExterior(self, from_file)
        self.interior = HouseInterior(self, from_file, **kwargs)

    def kill(self):
        self.interior.kill()
        del self.topleft
        del self.grid_pos
        del self.exterior.zone
        del self.interior
        del self.exterior.house
        del self.exterior
        del self.zone
        del self

class HouseExterior:
    def __init__(self, house:House, from_file):
        self.house = house
        self.zone = self.house.zone
        self.house_assets = self.zone.assets["house"]["house"]
        if not from_file: self.build()

    def build(self):
        self.size_x, self.size_y = choice([5,7]), choice([3,5])
        self.rect = pygame.Rect(self.house.topleft, (self.size_x*TILE_SIZE, self.size_y*TILE_SIZE))

        has_chimney = False
        for x in range(self.size_x):
            for y in range(self.size_y):
                pos = (self.house.topleft.x+x*TILE_SIZE, self.house.topleft.y+y*TILE_SIZE)
                if y == self.size_y-1: # bottom
                    if x == 0: # left
                        HouseExteriorTile(pos, 21, self.zone, "right", False) # left wall
                        HouseExteriorTile(pos, 32, self.zone, "right") # bottomleft roof
                    elif x == self.size_x-1: # right
                        HouseExteriorTile(pos, 23, self.zone, "left", False) # right wall
                        HouseExteriorTile(pos, 34, self.zone, "left") # bottomright roof
                    elif x == int(self.size_x/2): # mid
                        door = HouseExteriorTile(pos, 10, self.zone, roof=False, door=True) # door
                        self.exit_loc = vector(door.rect.center)+ vector(0,TILE_SIZE*1.5)
                        HouseExteriorTile(pos, 33, self.zone) # bottom roof
                        # path
                        path_len = randint(3,7)
                        for i in range(path_len):
                            if i == 0:
                                last = HouseExteriorTile(door.rect.bottomleft, 0, self.zone, hitbox_change="none", asset_name="paths", behind=True, roof=False)
                            elif i == path_len-1: 
                                HouseExteriorTile(last.rect.bottomleft, 8, self.zone, hitbox_change="none", asset_name="paths", behind=True, roof=False)
                            else:
                                last = HouseExteriorTile(last.rect.bottomleft, 4, self.zone, hitbox_change="none", asset_name="paths", behind=True, roof=False)
                    else:
                        HouseExteriorTile(pos, 22, self.zone, roof=False) # wall
                        HouseExteriorTile(pos, 33, self.zone) # bottom roof
                elif y == 0: # top
                    if x == 0: HouseExteriorTile(pos, 4, self.zone, "none") # topleft roof
                    elif x == self.size_x-1: HouseExteriorTile(pos, 6, self.zone, "none") # topright roof
                    else: HouseExteriorTile(pos, 5, self.zone, "none") # top roof
                elif y == int(self.size_y/2): # mid
                    if x == 0: HouseExteriorTile(pos, 18, self.zone, "right") # left mid roof
                    elif x == self.size_x-1: HouseExteriorTile(pos, 20, self.zone, "left") # right mid roof
                    else:
                        HouseExteriorTile(pos, 19, self.zone) # mid roof
                        if not has_chimney: HouseExteriorTile(pos, 28, self.zone); has_chimney=True # chimney
                elif y < int(self.size_y/2): # above mid
                    if x == 0: HouseExteriorTile(pos, 11, self.zone, "right") # left above mid roof
                    elif x == self.size_x-1: HouseExteriorTile(pos, 13, self.zone, "left") # right above mid roof
                    else: HouseExteriorTile(pos, 12, self.zone) # above mid roof
                else: # below mid
                    if x == 0: HouseExteriorTile(pos, 25, self.zone, "right") # left below mid roof
                    elif x == self.size_x-1: HouseExteriorTile(pos, 27, self.zone, "left") # right below mid roof
                    else: HouseExteriorTile(pos, 26, self.zone) # below mid roof

class HouseInterior:
    def __init__(self, house:House, from_file, **kwargs):
        self.house = house
        self.zone = self.house.zone
        self.display_surface = get_window()

        self.visible_behind = CameraGroup(self.zone.world)
        self.visible_bottom = CameraGroup(self.zone.world)
        self.visible = CameraGroup(self.zone.world)
        self.visible_top = CameraGroup(self.zone.world)
        
        self.all = Group()
        self.collidable = Group()
        self.updates = Group()
        self.doors = Group()
        self.decorations = Group()
        self.walls = Group()
        self.villagers = Group()

        self.visible.add(self.zone.player)
        if not from_file: self.build()
        else:
            self.size_x = kwargs["sizex"]
            self.size_y = kwargs["sizey"]

    def kill(self):
        for sprite in self.all: sprite.kill()
        self.visible_behind.empty()
        self.visible_bottom.empty()
        self.visible.empty()
        self.visible_top.empty()
        self.all.empty()
        self.collidable.empty()
        self.updates.empty()
        self.doors.empty()
        self.decorations.empty()
        self.walls.empty()
        self.villagers.empty()

        del self.zone
        del self.house
        del self
    
    def build(self):
        self.size_x = randint(10,20)
        self.size_y = min(randint(7,12), self.size_x)
        self.rect = pygame.Rect(self.house.topleft, (self.size_x*TILE_SIZE, self.size_y*TILE_SIZE))

        self.build_main()
        self.build_carpet()
        self.build_tables()

    def build_main(self):
        has_clock = False
        beds = 0
        for x in range(self.size_x):
            for y in range(self.size_y):
                pos = self.house.topleft+vector(x*TILE_SIZE, y*TILE_SIZE)
                if y == 0: # top
                    if x == 0: HouseTile(pos, 7, self) # topleft wall
                    elif x == self.size_x-1: HouseTile(pos, 9, self) # topright wall
                    else:
                        # wall or window, quadro
                        index = weighted_choice([8,1],WINDOW_WEIGHTS)
                        tile = HouseTile(pos, index, self)
                        if index == 8 and randint(0,100) < 30:
                            wall_choices = [0,1,2] if has_clock else [0,1,2,32,33,34]
                            dec=HouseDecoration(tile.rect.center, choice(wall_choices), self)
                            if dec.asset_index in [32,33,34]: has_clock = True
                        # bed
                        if beds < 4 and randint(0,100) < 20:
                            low_center = vector(tile.rect.center) + vector(0,TILE_SIZE)
                            left_center = low_center-vector(TILE_SIZE,0)
                            right_center = low_center+vector(TILE_SIZE,0)
                            if not self.decoration_there(low_center):
                                low_idx = choice([18,19,20])
                                HouseDecoration(low_center, low_idx,self,True)
                                HouseDecoration(vector(tile.rect.center), 10, self,True)
                                # bed left
                                if (not self.decoration_there(left_center)) and (not self.wall_there(left_center)) and (randint(0,100)<80)and\
                                    (x < self.size_x-3):
                                    sel =choice([3,4,5,12,13,14,21,21])
                                    if sel in [12,13,14]: HouseDecoration(left_center, 30, self, True)
                                    HouseDecoration(left_center, sel, self, True)
                                # bed right
                                if (not self.decoration_there(right_center)) and (not self.wall_there(right_center)) and( randint(0,100)<80)and\
                                    (x < self.size_x-3):
                                    sel = choice([3,4,5,12,13,14,21,21])
                                    if sel in [12,13,14]: HouseDecoration(right_center, 30, self, True)
                                    HouseDecoration(right_center, sel, self, True)
                elif y == self.size_y-1:# bottom     
                    if x == 0: HouseTile(pos, 21, self) # bottomleft wall
                    elif x == self.size_x-1: HouseTile(pos, 23, self) # bottomright wall
                    elif x == int(self.size_x/2): # door, carpet
                        HouseTile(pos, 15, self, collidable=False, floor=True)
                        door = HouseTile(pos, 10, self, door=True)
                        o_pos = vector(door.rect.center)-vector(0,TILE_SIZE)
                        HouseDecoration(o_pos, choice([45,46,47]), self, False, True)
                        self.enter_loc = vector(door.rect.center)+vector(0,-TILE_SIZE*1.5)
                    else: HouseTile(pos, 22, self) # wall
                else: # middle y
                    if x == 0: # left wall, decoration
                        tile = HouseTile(pos, 14, self)
                        o_pos = vector(tile.rect.center)+vector(TILE_SIZE,0)
                        if randint(0,100) < 20 and not self.decoration_there(o_pos): HouseDecoration(o_pos, choice([3,4,5]), self, True)
                    elif x == self.size_x-1:# right wall, decoration
                        tile = HouseTile(pos, 16, self)
                        o_pos = vector(tile.rect.center)-vector(TILE_SIZE,0)
                        if randint(0,100) < 20 and not self.decoration_there(o_pos): HouseDecoration(o_pos, choice([3,4,5]), self, True)
                    else: HouseTile(pos, 15, self, collidable=False, floor=True) # floor
    
    def build_carpet(self):
        cx, cy = randint(2,self.size_x-3), randint(1,self.size_y-3)
        cpos_l = self.house.topleft+vector(cx*TILE_SIZE+H_TILE_SIZE, cy*TILE_SIZE+H_TILE_SIZE)
        cpos_r = cpos_l+vector(TILE_SIZE,0)
        lidx = choice([48,50,52]); ridx = lidx+1
        HouseDecoration(cpos_l, lidx, self, False, True) # left carpet
        HouseDecoration(cpos_r, ridx, self, False, True) # right carpet

        name, data = generate_villager()
        Merchant(choice([cpos_l, cpos_r]), self, name, data)

    def build_tables(self):
        tb_x, tb_y = randint(3,self.size_x-4), randint(3,self.size_y-4)
        tb_pos = self.house.topleft+vector(tb_x*TILE_SIZE+H_TILE_SIZE, tb_y*TILE_SIZE+H_TILE_SIZE)
        self.place_table(tb_pos) # main table
        t_pos, b_pos = tb_pos+vector(0,TILE_SIZE),tb_pos-vector(0,TILE_SIZE)
        top_available = bottom_available = True
        if randint(0,100) < 50: bottom_available= self.place_table(b_pos)# bottom table
        if randint(0,100) < 50: top_available= self.place_table(t_pos) # top table
        if bottom_available:
            if not self.decoration_there(b_pos): HouseDecoration(b_pos,choice([45,46,47]),self,False,True) # carpet
            HouseDecoration(b_pos, 25, self) # bottom chair
        if top_available:
            if not self.decoration_there(t_pos): HouseDecoration(t_pos,choice([45,46,47]),self,False,True) # carpet
            HouseDecoration(t_pos, 24, self)# top chair

    def place_table(self, center_pos):
        HouseDecoration(center_pos, 30, self) # table
        cl, cr = center_pos-vector(TILE_SIZE,0), center_pos+vector(TILE_SIZE,0)
        if not self.decoration_there(cl): HouseDecoration(cl,choice([45,46,47]),self,False,True) # carpet
        if not self.decoration_there(cr): HouseDecoration(cr,choice([45,46,47]),self,False,True) # carpet
        HouseDecoration(cl,22,self) # left chair
        HouseDecoration(cr,23,self) # right chair
        return False

    def wall_there(self, pos):
        for wall in self.walls:
            if wall.hitbox.collidepoint(pos): return True
        return False
    
    def decoration_there(self, pos):
        for dec in self.decorations:
            if dec.hitbox.collidepoint(pos): return True
        return False

    def update(self, dt):
        self.updates.update(dt)

    def draw(self):
        self.display_surface.fill(HOUSE_BG_COL)
        self.visible_behind.custom_draw()
        self.visible_bottom.custom_draw()
        self.visible.custom_draw()
        self.visible_top.custom_draw()

    def take_screenshot(self):
        screenshot = pygame.Surface((self.size_x*TILE_SIZE, self.size_y*TILE_SIZE))
        screenshot.fill(HOUSE_BG_COL)
        self.visible_behind.screenshot(screenshot, self.house)
        self.visible_bottom.screenshot(screenshot, self.house)
        self.visible.screenshot(screenshot, self.house)
        self.visible_top.screenshot(screenshot, self.house)
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%B-%d_%H-%M-%S")
        pygame.image.save(screenshot, f"screenshots/{formatted_time}.png")