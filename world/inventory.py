from settings import *
from support import item_shortcut

class Inventory:
    def __init__(self, player):
        self.player = player

        self.coins = self.water = self.stars = 0
        self.selected_tool = TOOLS[0]
        self.selected_object = ""

        self.tools = {name:1 for name in TOOLS}
        self.objects = {name:1 for name in OBJECTS}
        self.items = {name:0 for name in ITEMS}

    # OBJECT
    def add_object(self, name, amount=1): self.objects[name] += amount

    def has_object(self, name, amount=1): return self.objects[name] >= amount

    def remove_object(self, name, amount=1):
        self.objects[name] -= amount
        if self.objects[name] <= 0 and self.selected_object == name: self.selected_object = ""
    
    # ITEM
    def add_item(self, name, amount=1): self.items[name] += amount
    
    def has_item(self, name, amount=1): return self.items[name] >= amount

    def remove_item(self, name, amount=1): self.items[name] -= amount

    # MONEY
    def add_money(self, amount=1): self.coins += amount

    def has_money(self, amount): return self.coins >= amount

    def remove_money(self, amount): self.coins -= amount
    
    # STARS
    def add_stars(self, amount=1): self.coins += amount

    def has_stars(self, amount): return self.coins >= amount

    def remove_stars(self, amount): self.coins -= amount
    
    # SELECT
    def select_tool(self, tool):
        self.selected_tool = tool
        self.selected_object = ""
        
    def select_object(self, obj):
        self.selected_object = obj
        self.select_tool = ""

    # THING
    def has_thing(self, name, amount=1):
        if name in OBJECTS: return self.objects[name] >= amount
        else: return self.items[name] >= amount

    def add_thing(self, name, amount=1):
        if name in OBJECTS: self.objects[name] += amount   
        else: self.items[name] += amount

    def remove_thing(self, name, amount=1):
        if name in OBJECTS: self.remove_object(name, amount)
        else: self.items[name] -= amount
    
    # WATER
    def fill_water(self):
        self.water += 1
        if self.water > PLAYER_MAX_WATER: self.water = PLAYER_MAX_WATER

    def use_water(self):
        self.water -= 1
        if self.water < 0: self.water = 0

    def has_water(self): return self.water > 0

    # EVENT
    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.unicode.isdecimal():
                thing = item_shortcut(int(event.unicode))
                if thing is None:
                    self.selected_tool = ""
                    self.selected_object = ""
                elif thing in TOOLS:
                    self.selected_tool = thing; self.selected_object = ""
                elif thing in OBJECTS:
                    if self.objects[thing] > 0: self.selected_object = thing; self.selected_tool = ""
                    else: self.selected_object = ""; self.selected_tool = ""
                    
                self.player.world.ui.tab.close()
                    
            if event.key == pygame.K_BACKSLASH:
                if self.selected_object:
                    self.selected_object = ""
                    self.selected_tool = TOOLS[0]
    