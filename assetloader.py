from settings import *
from support import load, load_list, load_dict, single_sheet, load_sheet, file_names

class AssetLoader:
    def __init__(self):
        self.assets = {}
        self.load()

    def load(self):
        self.assets["player"] = {
            (f"{atype}_{item}" if item else f"{atype}"): load_list((f"player/{atype}_{item}" if item else f"player/{atype}"), True, SCALE) 
            for item in ["", "axe", "water", "hoe", "idle"] 
            for atype in ["down", "up", "left", "right"]
        }
        self.assets["fruit"] = {
            "apple": load("fruit/apple", True, SCALE),
            "corn": load_list("fruit/corn", True, SCALE),
            "tomato": load_list("fruit/tomato", True, SCALE),
        }
        self.assets["objs"] = load_dict("objects", True, SCALE)
        self.assets["items"] = load_dict("items", True, MID_SCALE)
        self.assets["rain"] = {
            "drop": load_list("rain/drops", True, SCALE),
            "floor": load_list("rain/floor", True, SCALE),
        }
        self.assets["soil"] = load_dict("soil", True, SCALE)
        self.assets["wet-soil"] = load_list("soil_water", True, SCALE)
        self.assets["stump"] = load_dict("stumps", True, SCALE)
        self.assets["water"] = load_list("water", True, SCALE)
        self.assets["world"] = {
            file_name.lower(): load_sheet(f"world/{file_name}", True, SMALL_SCALE if file_name in USE_SMALL else SCALE, SMALL_REAL_TILE_SIZE if file_name in USE_SMALL else REAL_TILE_SIZE)
              for file_name in file_names("assets/graphics/world/")
        }
        self.assets["house"] = {
            "chicken-house": load("house/chicken-house", True, SMALL_SCALE),
            "fences": load_sheet("house/fences", True, SCALE),
            "house-decoration": load_sheet("house/house-decoration", True, SCALE),
            "house": load_sheet("house/house", True, SMALL_SCALE, SMALL_REAL_TILE_SIZE),
            "paths": load_sheet("house/paths", True, SCALE),
        }
        self.assets["animals"] = {
            "chicken":{
                "idle":single_sheet("animals/chicken-idle", True, SMALL_SCALE, w=SMALL_REAL_TILE_SIZE),
                "walk":single_sheet("animals/chicken-walk", True, SMALL_SCALE, w=SMALL_REAL_TILE_SIZE),
            },
            "cow":{
                "idle":single_sheet("animals/cow-idle", True, SMALL_SCALE, w=MID_REAL_TILE_SIZE),
                "walk":single_sheet("animals/cow-walk", True, SMALL_SCALE, w=MID_REAL_TILE_SIZE),
            },
            "egg": single_sheet("animals/egg", True, SMALL_SCALE),
            "merchant": load_list("animals/merchant", True, SCALE),
        }
        self.assets["farming"] = {
            "tomato": load_list("farming/tomato", True, SMALL_SCALE),
            "wheat": load_list("farming/wheat", True, SMALL_SCALE),
            "apple": load_list("farming/apple", True, SMALL_SCALE),
            "berry": load_list("farming/berry", True, SMALL_SCALE),
        }
        self.assets["ui"] = {
            "frame": load("ui/frame", True, UI_SCALE_B),
            "btn": load("ui/btn", True, UI_SCALE_B),
            
            "settings-menu": load("ui/settings-menu", True, UI_SCALE),
            "original-menu": load("ui/menu", True, 1),
            "menu": load("ui/menu", True, UI_SCALE),
            "long-menu": load("ui/long-menu", True, UI_SCALE),
            "frame-big": load("ui/frame-big", True, UI_SCALE),
            "sign": load("ui/sign", True, UI_SCALE),
            "signs": load("ui/signs", True, UI_SCALE),
            "square-m": load("ui/square-m", True, UI_SCALE),
            "button": load("ui/button", True, UI_SCALE),
            "button-pressed": load("ui/button-pressed", True, UI_SCALE),
            "bar": load("ui/bar", True, UI_SCALE),
            "bar-full": load("ui/bar-full", True, UI_SCALE),
            "double-arrow": load("ui/double-arrow", True, UI_SCALE),
            
            "sun": load("ui/sun", True, 1),
            "moon": load("ui/moon", True, 1),
            
            "dialogue": load_dict("ui/dialogue", True, UI_SCALE),
            "mouse": load_dict("ui/mouse", True, UI_SCALE_S),
            "selector": load_sheet("ui/sheets/selector", True, UI_SCALE, 12),
            
            "icons": {
                "emotes": load_sheet("ui/sheets/emotes", True, UI_SCALE, MID_REAL_TILE_SIZE),
                "all": load_sheet("ui/sheets/icons-all", True, UI_SCALE_B, SMALL_REAL_TILE_SIZE),
                "special":load_sheet("ui/sheets/icons-special", True, UI_SCALE_B, SMALL_REAL_TILE_SIZE),
                "white":load_sheet("ui/sheets/icons", True, UI_SCALE_B, SMALL_REAL_TILE_SIZE),
                "emoji":load_sheet("ui/sheets/icons-emoji", True, UI_SCALE_B, SMALL_REAL_TILE_SIZE),
            },
            
            "items": load_dict("items", True, UI_SCALE_B),
            "items-small": load_dict("items", True, UI_SCALE)
        }

    def __getitem__(self, name):
        return self.assets[name]