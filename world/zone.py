from settings import *
from support import get_window, randoffset, lerp, weighted_choice
from world.generic import CameraGroup, Group, BorderTreePack
from world.sprites import BorderTree, Water, Tile, Decoration, Tree, Bush, HouseExteriorTile, HouseDecoration, HouseTile, Stump, Cow, Chicken, ChickenHouse, Merchant
from world.soil import Soil
from world.house import House, Fences
import json, datetime

class Zone:
    def __init__(self, world, zone_pos, from_file):
        self.world = world
        self.player = world.player
        self.assets = world.assets
        self.display_surface = get_window()
        self.soil = Soil(self)

        self.string_pos = f"{int(zone_pos[0])};{int(zone_pos[1])}"
        self.zone_pos = vector(zone_pos)
        self.pixel_center = vector(self.zone_pos.x*ZONE_SIZE,self.zone_pos.y*ZONE_SIZE)
        self.pixel_topleft = vector(self.pixel_center.x-H_ZONE_SIZE, self.pixel_center.y-H_ZONE_SIZE)

        self.visible_water = CameraGroup(self.world)
        self.visible_behind = CameraGroup(self.world)
        self.visible_bottom = CameraGroup(self.world)
        self.visible = CameraGroup(self.world)
        self.visible_top = CameraGroup(self.world)

        self.all = Group()
        self.updates = Group()
        self.collidable = Group()
        self.waters = Group()
        self.trees = Group()
        self.bushes = Group()
        self.stumps = Group()
        self.interactable = Group()
        self.collectable = Group()
        self.decorations = Group()
        self.animals = Group()
        self.soil_dirts = Group()
        self.soil_waters = Group()
        self.soil_plants = Group()
        self.village_elements = Group()
        self.invis_village_elements = Group()
        self.village_doors = Group()
        self.tiles = Group()
        self.placeables = Group()
        
        self.border_trees = []
        self.village_houses:list[House] = []
        self.village_grid = []
        self.current_house:House = None
        self.in_house = False
        self.chicken_zones = []

        self.visible.add(self.player)
        self.soil.setup()
        if from_file: self.load()
        else: self.build()

    def save(self):
        data = {
            "village-elements": [
                {
                    "topleft": village_element.rect.topleft,
                    "asset-index": village_element.asset_index,
                    "asset-name": village_element.asset_name,
                    "hitbox-change": village_element.hitbox_change,
                    "roof": village_element.roof,
                    "behind": village_element.behind,
                    "door": village_element.door,
                    "kinematic": village_element.kinematic,
                    "tint": village_element.tint,
                    "chimney": village_element.chimney
                } for village_element in self.village_elements
            ],
            "village-houses": [
                {
                    "topleft": (house.topleft.x, house.topleft.y),
                    "grid-pos": (house.grid_pos.x, house.grid_pos.y),
                    "exit-loc": (house.exterior.exit_loc.x, house.exterior.exit_loc.y),
                    "enter-loc": (house.interior.enter_loc.x, house.interior.enter_loc.y),
                    "sizex": house.interior.size_x,
                    "sizey": house.interior.size_y,
                    "tint": house.tint,
                    "tiles" : [
                        {
                            "pos": tile.rect.center if tile.pos_center else tile.rect.topleft,
                            "asset-index": tile.asset_index,
                            "collidable": tile.collidable,
                            "door": tile.door,
                            "floor": tile.floor,
                            "top": tile.top,
                            "pos-center": tile.pos_center,
                            "is-tile": tile.is_tile,
                        } for tile in house.interior.all if tile.can_save
                    ],
                    "villagers": [
                        {
                            "center": villager.rect.center,
                            "name": villager.name,
                            "data": villager.data,
                        } for villager in house.interior.villagers
                    ]
                } for house in self.village_houses
            ],
            "trees": [
                {
                    "center": tree.rect.center,
                    "size": tree.size,
                    "apple-count": len(tree.apples)
                } for tree in self.trees
            ],
            "bushes": [
                {
                    "center": bush.rect.center,
                    "berry-count": len(bush.berries)
                } for bush in self.bushes
            ],
            "water": [
                {
                    "topleft": water.rect.topleft
                } for water in self.waters
            ],
            "tiles": [
                {
                    "topleft": tile.rect.topleft,
                    "asset-name": tile.asset_name,
                    "asset-index": tile.asset_index,
                } for tile in self.tiles
            ],
            "decorations": [
                {
                    "center": dec.rect.center,
                    "interact-item": dec.interact_item,
                    "drop-item": dec.drop_item,
                    "drop-amount": dec.drop_amount,
                    "data": dec.data,
                } for dec in self.decorations
            ],
            "border-trees": {
                pack.side: [
                    {
                        "center": tree.rect.center,
                        "size": tree.size,
                    } for tree in pack.trees
                ] for pack in self.border_trees
            },
            "soil": {
                "grid": self.soil.grid,
                "plants" : [
                    {
                        "center": plant.rect.center,
                        "stage": plant.stage,
                        "crop-name": plant.crop_name,
                        "grown": plant.grown,
                        "grid-pos": plant.grid_pos,
                    } for plant in self.soil_plants
                ],
            },
            "stumps": [
                {
                    "tree-size": stump.tree_size,
                    "tree-rel": (stump.tree_rel.x, stump.tree_rel.y),
                    "center": stump.rect.center
                } for stump in self.stumps if stump.tree is None
            ],
            "chicken-houses" : [
                {
                    "rect": (rect.x, rect.y, rect.w, rect.h),
                    "house": chouse.rect.center
                } for rect, chouse in self.chicken_zones
            ],
            "animals" : [
                {
                    "center": animal.rect.center,
                    "type": animal.animal_type,
                    "bounds": (animal.bounds_rect.x, animal.bounds_rect.y,animal.bounds_rect.w,animal.bounds_rect.h,) if animal.bounds_rect else None
                } for animal in self.animals
            ]
        }
        with open(f"data/{self.world.name}/{self.string_pos}.json", "w") as save_file:
            json.dump(data, save_file)
        pygame.image.save(self.floor_surf, f"data/{self.world.name}/{self.string_pos}.png")

    def load(self):
        data = None
        with open(f"data/{self.world.name}/{self.string_pos}.json", "r") as save_file:
            data = json.load(save_file)
        if data is None: raise Exception("I don't fucking know why but data is None so something is fucking wrong fix it please.")

        self.floor_surf = pygame.image.load(f"data/{self.world.name}/{self.string_pos}.png").convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=self.pixel_topleft)
        self.build_fog()
        for element in data["village-elements"]:
            h = HouseExteriorTile(element["topleft"], element["asset-index"], self, element["tint"], element["hitbox-change"], element["roof"], element["door"], element["asset-name"], element["behind"], element["chimney"])
            h.kinematic = element["kinematic"]
        for side, border_tree in data["border-trees"].items():
            pack = BorderTreePack(side, self)
            for tree in border_tree:
                pack.register(BorderTree(tree["center"], self, tree["size"]))
            pack.build()
        for dec in data["decorations"]:
            if dec["data"] == "sunflower":
                Decoration(dec["center"], self.assets["objs"]["sunflower"], self, "axe;hoe", data="sunflower")
            elif isinstance(dec["data"], str) and "water" in dec["data"]:
                Decoration(dec["center"], self.assets["world"]["water-decoration"][int(dec["data"].split(";")[0])], self, "axe;hoe", data=dec["data"])
            else:
                Decoration(dec["center"], self.assets["world"]["plant-decoration"][dec["data"]], self, "axe;hoe", data=dec["data"])
        for bush in data["bushes"]:
            Bush(bush["center"], self, bush["berry-count"])
        for tree in data["trees"]:
            Tree(tree["center"], self, tree["size"], tree["apple-count"])
        for stump in data["stumps"]:
            Stump(None, self, stump["center"], stump["tree-size"], vector(stump["tree-rel"]))
        for water in data["water"]:
            Water(water["topleft"], self)
        for tile in data["tiles"]:
            wat_tile = None
            for water in self.waters:
                if water.rect.collidepoint(vector(tile["topleft"][0]+H_TILE_SIZE, tile["topleft"][1]+H_TILE_SIZE)): wat_tile = water; break
            Tile(tile["topleft"], self.assets["world"][tile["asset-name"]][tile["asset-index"]], self, tile["asset-name"], tile["asset-index"], wat_tile)
        for house in data["village-houses"]:
            h = House(house["topleft"],house["grid-pos"], self, True, house["tint"], sizex=house["sizex"], sizey=house["sizey"])
            self.village_houses.append(h)
            self.village_grid.append(f"{int(house['grid-pos'][0])};{int(house['grid-pos'][1])}")
            h.exterior.exit_loc = vector(house["exit-loc"])
            h.interior.enter_loc = vector(house["enter-loc"])
            for tile in house["tiles"]:
                if tile["is-tile"]:
                    HouseTile(tile["pos"], tile["asset-index"], h.interior, tile["collidable"], tile["door"], tile["floor"], tile["top"])
                else:
                    HouseDecoration(tile["pos"], tile["asset-index"], h.interior, tile["collidable"], tile["floor"], tile["pos-center"])
            for villager in house["villagers"]:
                Merchant(villager["center"], h.interior, villager["name"], villager["data"])
        for zone in data["chicken-houses"]:
            self.chicken_zones.append([pygame.Rect(zone["rect"]),ChickenHouse(zone["house"], self)])
        for animal in data["animals"]:
            if animal["type"] == "chicken":
                Chicken(animal["center"], self, pygame.Rect(animal["bounds"]))
            elif animal["type"] == "cow":
                Cow(animal["center"], self)
        self.soil.load(data["soil"])

    def unload(self):
        for sprite in self.all: sprite.kill()
        for house in self.village_houses: house.kill()
        for tree in self.border_trees: tree.kill()
        self.soil.kill()

        self.village_houses.clear()
        self.border_trees.clear()
        self.visible_water.empty()
        self.visible_behind.empty()
        self.visible_bottom.empty()
        self.visible.empty()
        self.visible_top.empty()
        self.all.empty()
        self.updates.empty()
        self.collidable.empty()
        self.waters.empty()
        self.trees.empty()
        self.bushes.empty()
        self.stumps.empty()
        self.interactable.empty()
        self.decorations.empty()
        self.soil_dirts.empty()
        self.soil_waters.empty()
        self.soil_plants.empty()
        self.village_elements.empty()
        self.village_doors.empty()
        self.tiles.empty()
        self.placeables.empty()

        del self.floor_surf
        del self.floor_rect
        del self.string_pos
        del self.pixel_topleft
        del self.pixel_center
        del self.soil
        del self.current_house
        del self

    def enter_house(self, house:House):
        self.current_house = house
        self.world.transition.start("y",-1,"House", self.enter_midway, HOUSE_BG_COL)

    def enter_midway(self):
        self.in_house = True
        self.player.teleport(self.current_house.interior.enter_loc)

    def exit_house(self):
        self.world.transition.start("y",1,"House",self.exit_midway, HOUSE_BG_COL)

    def exit_midway(self):
        self.player.teleport(self.current_house.exterior.exit_loc)
        self.in_house = False
        self.current_house = None

    def build(self):
        self.build_floor()
        self.build_borders()
        self.build_fog()
        self.build_village()
        self.build_water()
        self.build_decorations()
        self.build_trees()
        self.build_sunflowers()

    def build_village(self):
        if randint(0,100) > 40: return
        house_amount = randint(3,12)
        first_house = House(self.pixel_center,(0,0),self)
        self.village_houses.append(first_house)
        self.village_grid.append("0;0")
        houses_left = house_amount-1
        while houses_left > 0:
            neighbor_house = choice(self.village_houses)
            for offset_name, offset in neighbor_house.neighbor_pos.items():
                pos = neighbor_house.grid_pos+offset
                str_offset = f"{int(pos.x)};{int(pos.y)}"
                topleft = neighbor_house.topleft+offset*neighbor_house.max_size
                if topleft.x < self.pixel_topleft.x: continue
                if topleft.y < self.pixel_topleft.y: continue
                if topleft.x > self.pixel_topleft.x+ZONE_SIZE-House.max_size: continue 
                if topleft.y > self.pixel_topleft.y+ZONE_SIZE-House.max_size: continue 
                if str_offset not in self.village_grid:
                    if randint(0,100) > 20:
                        slight_offset = vector(randint(-1,1)*TILE_SIZE,randint(-1,1)*TILE_SIZE)
                        house = House(topleft+slight_offset, pos, self)
                        self.village_houses.append(house)
                        self.village_grid.append(str_offset)
                        houses_left -= 1
                        break
                    else:
                        bounds_rect = Fences.generate(topleft, self)
                        self.village_grid.append(str_offset)
                        houses_left-=1
                        animal_type = choice(["cow","chicken"])
                        if animal_type == "cow":
                            for i in range(randint(2,4)):
                                Cow(bounds_rect.center,self)
                        elif animal_type == "chicken":
                            for i in range(randint(3,6)):
                                Chicken(bounds_rect.center, self, bounds_rect)
                            chicken_house = ChickenHouse(bounds_rect.center, self)
                            self.chicken_zones.append([bounds_rect, chicken_house])
                        break
        
    def build_borders(self):
        left = BorderTreePack("left", self)
        right = BorderTreePack("right", self)
        top = BorderTreePack("top", self)
        bottom = BorderTreePack("bottom", self)

        x = self.pixel_center.x - H_ZONE_SIZE
        for _ in range(ZONE_TILE_NUM*2):
            for _ in range(choice([1,2])):
                top.register(BorderTree((x+randoffset(H_TILE_SIZE), self.pixel_center.y - H_ZONE_SIZE+randoffset(H_TILE_SIZE)), self, choice(TREE_SIZES)))
                bottom.register(BorderTree((x+randoffset(H_TILE_SIZE), self.pixel_center.y + H_ZONE_SIZE+randoffset(H_TILE_SIZE)), self, choice(TREE_SIZES)))
            x += H_TILE_SIZE

        y = self.pixel_center.y - H_ZONE_SIZE
        for _ in range(ZONE_TILE_NUM*2):
            for _ in range(choice([1,2])):
                left.register(BorderTree((self.pixel_center.x - H_ZONE_SIZE+randoffset(H_TILE_SIZE), y+randoffset(H_TILE_SIZE)), self, choice(TREE_SIZES)))
                right.register(BorderTree((self.pixel_center.x + H_ZONE_SIZE+randoffset(H_TILE_SIZE), y+randoffset(H_TILE_SIZE)), self, choice(TREE_SIZES)))
            y += H_TILE_SIZE

        for tree in self.border_trees: tree.build()

    def build_floor(self):
        self.floor_surf = pygame.Surface((ZONE_SIZE, ZONE_SIZE))
        self.floor_surf.fill("black")
        for zx in range(ZONE_TILE_NUM+2):
            for zy in range(ZONE_TILE_NUM+2):
                pos = (zx*TILE_SIZE-TILE_SIZE, zy*TILE_SIZE-TILE_SIZE)
                image = weighted_choice(self.assets["world"]["floor-grass"]+[self.assets["world"]["border-grass"][4]], FLOOR_WEIGHTS)
                self.floor_surf.blit(image, pos)
        self.floor_rect = self.floor_surf.get_rect(topleft=self.pixel_topleft)

    def build_fog(self):
        fog_h = pygame.Surface((FOG_SIZE, 1), pygame.SRCALPHA); fog_h.fill(0)
        fog_v = pygame.Surface((1, FOG_SIZE), pygame.SRCALPHA); fog_v.fill(0)
        for px in range((fog_h_w:=fog_h.get_width())):
            fog_h.set_at((px,0), pygame.Color(FOG_COLOR[0], FOG_COLOR[1], FOG_COLOR[2], 
                                              int(pygame.math.clamp(lerp(0,255,px/(fog_h_w//1.5)), 0, 255))))
        self.fog_h = pygame.transform.scale(fog_h, (FOG_SIZE, self.floor_rect.h*1.2))
        for py in range((fog_v_h:=fog_v.get_height())):
            fog_v.set_at((0,py), pygame.Color(FOG_COLOR[0], FOG_COLOR[1], FOG_COLOR[2], 
                                              int(pygame.math.clamp(lerp(0,255,py/(fog_v_h//1.5)), 0, 255))))
        self.fog_v = pygame.transform.scale(fog_v, (self.floor_rect.w*1.2, FOG_SIZE))
        self.fog_h_rects = [
            self.fog_h.get_rect(midright=(self.floor_rect.left+TILE_SIZE,self.floor_rect.centery)),
            self.fog_h.get_rect(midleft=(self.floor_rect.right-TILE_SIZE,self.floor_rect.centery))
        ]
        self.fog_v_rects = [
            self.fog_v.get_rect(midbottom=(self.floor_rect.centerx, self.floor_rect.top+TILE_SIZE)),
            self.fog_v.get_rect(midtop=(self.floor_rect.centerx, self.floor_rect.bottom-TILE_SIZE))
        ]
        self.flipped_fog_h = pygame.transform.flip(self.fog_h, True, False)
        self.flipped_fog_v = pygame.transform.flip(self.fog_v, False, True)

    def build_water(self):
        for i in range(randint(1,3)):
            amount_x = randint(6, 11)
            amount_y = randint(6,11)
            topleft = vector(randint(self.pixel_topleft.x,self.pixel_center.x+H_ZONE_SIZE//2), randint(self.pixel_topleft.y,self.pixel_center.y+H_ZONE_SIZE//2))
            rect = pygame.Rect(topleft, (amount_x*TILE_SIZE, amount_y*TILE_SIZE))
            stop = False
            for village in self.village_elements:
                if village.hitbox.colliderect(rect): stop=True
            for water in self.waters:
                if water.hitbox.colliderect(rect): stop=True
            if stop: continue

            for x in range(amount_x):
                for y in range(amount_y):
                    pos = vector(x*TILE_SIZE+topleft.x,y*TILE_SIZE+topleft.y)
                    water = Water(pos, self)
                    
                    if x == 0 and y == 0: Tile(pos,self.assets["world"]["corner-grass"][0], self, "corner-grass", 0, water)
                    elif x == 0 and y == amount_y-1: Tile(pos,self.assets["world"]["corner-grass"][2], self,"corner-grass", 2, water)
                    elif x == amount_x-1 and y == 0: Tile(pos,self.assets["world"]["corner-grass"][1], self, "corner-grass", 1,water)
                    elif x == amount_x-1 and y == amount_y-1: Tile(pos,self.assets["world"]["corner-grass"][3], self, "corner-grass", 3,water)
                    elif x == 0 and y > 0 and y < amount_y-1: Tile(pos,self.assets["world"]["border-grass"][5], self,"border-grass", 5, water)
                    elif x == amount_x-1 and y > 0 and y < amount_y-1: Tile(pos,self.assets["world"]["border-grass"][3], self,"border-grass", 3, water)
                    elif y == 0 and x > 0 and x < amount_x-1: Tile(pos,self.assets["world"]["border-grass"][7], self,"border-grass", 7, water)
                    elif y == amount_y-1 and x > 0 and x < amount_x-1: Tile(pos,self.assets["world"]["border-grass"][1], self, "border-grass", 1,water)
                    if x > 1 and x < amount_x-2 and y > 1 and y < amount_y-2:
                        asset_index = choice(list(range(len(self.assets["world"]["water-decoration"])-1)))
                        if randint(0,100) < 10: Decoration(water.pos, self.assets["world"]["water-decoration"][asset_index], self, "axe;hoe", data=f"{asset_index};water")

    def build_decorations(self):
        for i in range(randint(ZONE_TILE_NUM, ZONE_TILE_NUM*2)):
            pos = (self.pixel_topleft.x+randint(0,ZONE_SIZE),self.pixel_topleft.y+ randint(0,ZONE_SIZE))
            if self.water_there(pos) or self.village_there(pos): continue
            asset_index = weighted_choice(list(range(len(self.assets["world"]["plant-decoration"])-1)), PLANT_WEIGHTS)
            Decoration(pos, self.assets["world"]["plant-decoration"][asset_index], self, "axe", data=asset_index)

    def build_trees(self):
        for i in range(randint(1,3)):
            max_offset = randint(ZONE_SIZE//8, ZONE_SIZE//4)
            center = vector(self.pixel_topleft.x+randint(max_offset,ZONE_SIZE-max_offset), self.pixel_topleft.y+randint(max_offset,ZONE_SIZE-max_offset))
            for i in range(randint((max_offset//TILE_SIZE)*5, (max_offset//TILE_SIZE)*8)):
                if randint(0,100) < 30:
                    pos = center+vector(randoffset(max_offset), randoffset(max_offset))
                    if not self.water_there(pos) and not self.village_there(pos):
                        asset_index = weighted_choice(list(range(len(self.assets["world"]["plant-decoration"])-1)), FUNGUS_WEIGHTS)
                        Decoration(pos, self.assets["world"]["plant-decoration"][asset_index], self, "axe;hoe", data=asset_index)
                pos = center+vector(randoffset(max_offset), randoffset(max_offset))
                if not self.water_there(pos) and not self.village_there(pos):
                    if randint(0,100) < 80:
                        Tree(pos, self, choice(["small", "medium"]))
                    else:
                        Bush(pos, self)

    def build_sunflowers(self):
        for i in range(randint(1,2)):
            max_offset = randint(ZONE_SIZE//10, ZONE_SIZE//5)
            center = vector(self.pixel_topleft.x+randint(max_offset,ZONE_SIZE-max_offset), self.pixel_topleft.y+randint(max_offset,ZONE_SIZE-max_offset))
            for i in range(randint((max_offset//TILE_SIZE)*3, (max_offset//TILE_SIZE)*6)):
                pos = center+vector(randoffset(max_offset), randoffset(max_offset))
                if not self.water_there(pos) and not self.tree_there(pos) and not self.village_there(pos):
                    Decoration(pos, self.assets["objs"]["sunflower"], self, "axe;hoe", data="sunflower")

    def water_there(self, pos):
        for water in self.waters:
            if water.rect.collidepoint(pos): return True
        return False
    
    def village_there(self, pos):
        for element in self.village_elements:
            if element.rect.collidepoint(pos): return True
        for element in self.invis_village_elements:
            if element.rect.collidepoint(pos): return True
        return False

    def tree_there(self, pos):
        for tree in self.trees:
            if tree.rect.collidepoint(pos): return True
        for tree in self.border_trees:
            if tree.rect.collidepoint(pos): return True
        return False
    
    def decoration_there(self, pos):
        for dec in self.decorations:
            if dec.rect.collidepoint(pos): return True
        return False
    
    def placeable_there(self, pos):
        for placeable in self.placeables:
            if placeable.rect.collidepoint(pos): return True
        return False

    def is_farmable(self, pos):
        return not self.tree_there(pos) and not self.water_there(pos) and not self.decoration_there(pos) and not self.village_there(pos) and not self.placeable_there(pos)

    def can_place(self, pos):
        return not self.tree_there(pos) and not self.water_there(pos) and not self.decoration_there(pos) and not self.village_there(pos) and not self.placeable_there(pos) and not self.player.hitbox.collidepoint(pos)
    
    def update(self, dt):
        if self.in_house:
            self.current_house.interior.update(dt)
        self.updates.update(dt)

    def draw(self):
        if self.in_house:
            self.current_house.interior.draw()
            return
        self.display_surface.blit(self.floor_surf, vector(self.floor_rect.topleft)-self.world.offset)
        self.visible_water.custom_draw()
        self.visible_behind.custom_draw()
        self.visible_bottom.custom_draw()
        self.visible.custom_draw()
        self.visible_top.custom_draw()
        
        for tree in self.border_trees: tree.draw()
        self.display_surface.blit(self.flipped_fog_h, vector(self.fog_h_rects[0].topleft)-self.world.offset)
        self.display_surface.blit(self.fog_h, vector(self.fog_h_rects[1].topleft)-self.world.offset)
        self.display_surface.blit(self.flipped_fog_v, vector(self.fog_v_rects[0].topleft)-self.world.offset)
        self.display_surface.blit(self.fog_v, vector(self.fog_v_rects[1].topleft)-self.world.offset)

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.take_screenshot()

    def take_screenshot(self):
        if self.in_house:
            self.current_house.interior.take_screenshot()
            return
        screenshot = pygame.Surface((ZONE_SIZE, ZONE_SIZE))
        screenshot.fill(0)
        screenshot.blit(self.floor_surf, self.floor_rect.topleft-self.pixel_topleft)
        self.visible_water.screenshot(screenshot)
        self.visible_behind.screenshot(screenshot)
        self.visible_bottom.screenshot(screenshot)
        self.visible.screenshot(screenshot)
        self.visible_top.screenshot(screenshot)
        for tree in self.border_trees: tree.screenshot(screenshot)
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%B-%d_%H-%M-%S")
        pygame.image.save(screenshot, f"screenshots/{formatted_time}.png")