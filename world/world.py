from settings import *
from support import get_window, quit_all, file_names_strict, set_cursor
from world.zone import Zone
from world.player import Player
from world.transition import Transition
from world.ui import UI
from world.dialogue import Dialogue
from world.dnc import DayNightCycle

class World:
    def __init__(self, main, world_name):
        self.main = main
        self.assets = main.assets
        self.display_surface = get_window()
        self.name = world_name
        set_cursor("trig-1", self.assets)

        self.offset = vector()
        self.player = Player(self)
        self.ui = UI(self)
        self.transition = Transition(self)
        self.dialogue = Dialogue(self)
        self.dnc = DayNightCycle(self)

        self.zones = file_names_strict(f"data/{self.name}", ["player"], ["json"])
        self.current_zone = Zone(self, (0,0), from_file = True if "0;0" in self.zones else False)
        if not "0;0" in self.zones: self.zones.append("0;0")
        
        self.next_translate = (0,0)
        self.next_zone = None

    def change_zone(self, side):
        current_pos = self.current_zone.zone_pos
        new_pos = current_pos.copy()
        
        match side:
            case "left":
                new_pos.x -= 1
                self.next_translate = (-TILE_SIZE*4, 0)
                self.transition.start("x", -1, "Zone", self.mid_transition)
            case "right":
                new_pos.x += 1
                self.next_translate = (TILE_SIZE*4, 0)
                self.transition.start("x", 1, "Zone", self.mid_transition)
            case "top":
                new_pos.y -= 1
                self.next_translate = (0,-TILE_SIZE*4)
                self.transition.start("y", -1, "Zone", self.mid_transition)
            case "bottom":
                new_pos.y += 1
                self.next_translate = (0,TILE_SIZE*4)
                self.transition.start("y", 1, "Zone", self.mid_transition)

        string_pos = f"{int(new_pos.x)};{int(new_pos.y)}"

        if self.current_zone:
            self.current_zone.save()
            self.current_zone.unload()
            del self.current_zone
            self.current_zone = None

        if not string_pos in self.zones:
            self.next_zone = Zone(self, new_pos, from_file=False)
            self.zones.append(string_pos)
        else:
            self.next_zone = Zone(self, new_pos, from_file=True)

    def mid_transition(self):
        self.player.translate(self.next_translate)
        self.current_zone = self.next_zone

    def quit(self):
        if self.current_zone: self.current_zone.save()
        self.player.save()
        quit_all()

    def run(self, dt):
        self.player.frame_start()
        self.event_loop()

        self.offset.x = self.player.rect.centerx - H_WIDTH
        self.offset.y = self.player.rect.centery - H_HEIGHT
        self.player.update(dt)
        self.current_zone.update(dt) if self.current_zone else None
        self.transition.update(dt)
        self.ui.update(dt)
        self.dialogue.update(dt)
        self.dnc.update(dt)

        self.display_surface.fill(FOG_COLOR)
        self.current_zone.draw() if self.current_zone else None
        self.dialogue.draw()
        self.ui.draw()
        self.transition.draw()
        self.dnc.draw()
        
        self.player.selector.post()

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.quit()
            self.player.event(event)
            self.ui.event(event)
            self.dialogue.event(event)
            if self.current_zone: self.current_zone.event(event)
