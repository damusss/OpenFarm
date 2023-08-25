from settings import *
from support import get_window
from world.sprites import SoilDirt, SoilWater, SoilPlant

class Soil:
    def __init__(self, zone):
        self.zone = zone
        self.assets = zone.assets
        self.display_surface = get_window()
        self.player = zone.player

    def plant_collected(self, plant):
        self.grid[plant.grid_pos[1]][plant.grid_pos[0]]["plant"] = False

    def has_water(self, plant):
        return self.grid[plant.grid_pos[1]][plant.grid_pos[0]]["water"]
    
    def consume_water(self, plant):
        cell = self.grid[plant.grid_pos[1]][plant.grid_pos[0]]
        if not cell["water"]: return
        cell["water"] = False
        for water in self.zone.soil_waters:
            if water.grid_pos == plant.grid_pos: water.kill()

    def interact(self, selected_tool, selected_object, interact_point):
        match selected_tool:
            case "hoe": self.hoe_interact(interact_point)
            case "water": self.water_interact(interact_point)
            case "axe": self.axe_interact(interact_point)
        if "seeds" in selected_object:
            self.seed_interact(selected_object, interact_point)

    def can_interact(self, selected_tool, selected_object, interact_point):
        if selected_tool not in ["hoe", "water", "axe"] and not "seeds" in selected_object: return None
        if selected_tool == "hoe":
            for hit_rect in self.hit_rects:
                if hit_rect.collidepoint(interact_point): return hit_rect
        else:
            for soil in self.zone.soil_dirts:
                if soil.hitbox.collidepoint(interact_point): return soil.hitbox
        return None

    def hoe_interact(self, interact_point):
        if not self.zone.is_farmable(interact_point): return
        for hit_rect in self.hit_rects:
            if hit_rect.collidepoint(interact_point):
                x = int((hit_rect.x-self.zone.pixel_topleft.x) // TILE_SIZE)
                y = int((hit_rect.y-self.zone.pixel_topleft.y) // TILE_SIZE)

                self.grid[y][x]["soil"] = True
                self.create_soils()
                return 

    def water_interact(self, interact_point):
        if not self.player.inventory.has_water(): return
        for soil in self.zone.soil_dirts:
            if soil.hitbox.collidepoint(interact_point):
                cell = self.grid[soil.grid_pos[1]][soil.grid_pos[0]]
                if cell["water"]: return
                cell["water"] = True

                SoilWater(soil.rect.center, soil.grid_pos, choice(self.assets["wet-soil"]),self.zone)
                self.player.inventory.use_water()
                return
            
    def seed_interact(self, seed, interact_point):
        for soil in self.zone.soil_dirts:
            if soil.hitbox.collidepoint(interact_point):
                cell = self.grid[soil.grid_pos[1]][soil.grid_pos[0]]
                if cell["plant"]: return
                cell["plant"] = True

                SoilPlant(soil.rect.center, soil.grid_pos, self.zone, seed.replace("-seeds",""), self)
                self.player.inventory.remove_object(seed)
                return

    def axe_interact(self, interact_point):
        for hit_rect in self.hit_rects:
            if hit_rect.collidepoint(interact_point):
                x = int((hit_rect.x-self.zone.pixel_topleft.x) // TILE_SIZE)
                y = int((hit_rect.y-self.zone.pixel_topleft.y) // TILE_SIZE)
                self.grid[y][x] = {"soil":False, "water":False, "plant":False}
                self.create_soils()

                for water in self.zone.soil_waters:
                    if water.grid_pos == (x,y): water.kill()
                for plant in self.zone.soil_plants:
                    if plant.grid_pos == (x,y): plant.kill()
                return

    def create_soils(self):
        for soil in self.zone.soil_dirts: soil.kill()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if cell["soil"]:
                    # tile options 
                    t = self.grid[index_row - 1][index_col]["soil"]
                    b = self.grid[index_row + 1][index_col]["soil"]
                    r = row[index_col + 1]["soil"]
                    l = row[index_col - 1]["soil"]

                    tile_type = 'o'

                    # all sides
                    if all((t,r,b,l)): tile_type = 'x'

                    # horizontal tiles only
                    if l and not any((t,r,b)): tile_type = 'r'
                    if r and not any((t,l,b)): tile_type = 'l'
                    if r and l and not any((t,b)): tile_type = 'lr'

                    # vertical only 
                    if t and not any((r,l,b)): tile_type = 'b'
                    if b and not any((r,l,t)): tile_type = 't'
                    if b and t and not any((r,l)): tile_type = 'tb'

                    # corners 
                    if l and b and not any((t,r)): tile_type = 'tr'
                    if r and b and not any((t,l)): tile_type = 'tl'
                    if l and t and not any((b,r)): tile_type = 'br'
                    if r and t and not any((b,l)): tile_type = 'bl'

                    # T shapes
                    if all((t,b,r)) and not l: tile_type = 'tbr'
                    if all((t,b,l)) and not r: tile_type = 'tbl'
                    if all((l,r,t)) and not b: tile_type = 'lrb'
                    if all((l,r,b)) and not t: tile_type = 'lrt'

                    SoilDirt((self.zone.pixel_topleft.x+index_col*TILE_SIZE, self.zone.pixel_topleft.y+index_row*TILE_SIZE), (index_col, index_row),tile_type, self.zone)

    def setup(self):
        self.grid = [[{"soil":False, "water":False, "plant":False} for col in range(ZONE_TILE_NUM)] for row in range(ZONE_TILE_NUM)]

        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                pos = vector(self.zone.pixel_topleft.x + index_col*TILE_SIZE, self.zone.pixel_topleft.y + index_row*TILE_SIZE)
                rect = pygame.Rect(pos, (TILE_SIZE, TILE_SIZE))
                self.hit_rects.append(rect)

    def load(self, data):
        self.grid = data["grid"]
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if cell["water"]:
                    SoilWater((self.zone.pixel_topleft.x+index_col*TILE_SIZE+H_TILE_SIZE, self.zone.pixel_topleft.y+index_row*TILE_SIZE+H_TILE_SIZE), (index_col, index_row), choice(self.assets["wet-soil"]),self.zone )
        for plant in data["plants"]:
            SoilPlant(plant["center"], plant["grid-pos"], self.zone, plant["crop-name"], self, plant["stage"], plant["grown"])
        self.create_soils()

    def kill(self):
        for rect in self.hit_rects: del rect
        
        self.grid.clear()
        self.hit_rects.clear()

        del self.grid
        del self.hit_rects
        del self

