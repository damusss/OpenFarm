from settings import *

class Inventory:
    TOOLS = ["axe","hoe","water"]
    OBJECTS = ["wheat-seeds","tomato-seeds"]
    TOOLS_OBJS = TOOLS+OBJECTS
    ITEMS = ["wood","tomato","wheat","grass","apple", "berry","egg","milk"]

    def __init__(self, player):
        self.player = player

        self.coins = self.water = self.stars = 0
        self.selected_tool = "axe"
        self.selected_object = ""

        self.tools = {name:1 for name in self.TOOLS}
        self.objects = {name:1 for name in self.OBJECTS}
        self.items = {name:0 for name in self.ITEMS}

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

    # THING
    def has_thing(self, name, amount=1):
        if name in self.OBJECTS: return self.objects[name] >= amount
        else: return self.items[name] >= amount

    def add_thing(self, name, amount=1):
        if name in self.OBJECTS: self.objects[name] += amount   
        else: self.items[name] += amount

    def remove_thing(self, name, amount=1):
        if name in self.OBJECTS: self.remove_object(name, amount)
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
                if int(event.unicode) in ITEM_SHORTCUT:
                    thing = ITEM_SHORTCUT[int(event.unicode)]
                    if thing in self.TOOLS:
                        self.selected_tool = thing; self.selected_object = ""
                    elif thing in self.OBJECTS:
                        if self.objects[thing] > 0: self.selected_object = thing; self.selected_tool = ""
                        else: self.selected_object = ""; self.selected_tool = ""
                    else:
                        self.selected_tool = ""
                        self.selected_object = ""
                    self.player.world.ui.tab.close()
    