from settings import *
from world.generic import Generic
from support import get_window
from world.inventory import Inventory
import os, json

class Player(Generic):
    def __init__(self, world):
        super().__init__((0,0), world.assets["player"]["down"][0], [], None, True)
        self.add_status_animator(world.assets["player"], "down", 1, True, None)

        self.world = world
        self.assets = world.assets
        self.display_surface = get_window()

        self.direction = vector()
        self.hitbox = self.rect.scale_by(0.33,0.15)
        self.hitbox_offset = int(30*SCALE)
        self.using_item = False
        self.speed = PLAYER_SPEED

        self.inventory = Inventory(self)
        self.selector = InteractSelector(self)
        self.load()

    def save(self):
        data = {
            "coins": self.inventory.coins,
            "stars": self.inventory.stars,
            "water": self.inventory.water,
            "tools": self.inventory.tools,
            "objects": self.inventory.objects,
            "items": self.inventory.items,
            "sel-object": self.inventory.selected_object,
            "sel-tool": self.inventory.selected_tool
        }
        with open(f"data/{self.world.name}/player.json", "w") as save_file:
            json.dump(data, save_file)

    def load(self):
        if not os.path.exists(f"data/{self.world.name}/player.json"): self.save()
        with open(f"data/{self.world.name}/player.json", "r") as save_file:
            data = json.load(save_file)
            self.inventory.coins = data["coins"]
            self.inventory.stars = data["stars"]
            self.inventory.water = data["water"]
            self.inventory.tools = data["tools"]
            self.inventory.objects = data["objects"]
            self.inventory.items = data["items"]
            self.inventory.selected_object = data["sel-object"]
            self.inventory.selected_tool = data["sel-tool"]

    def input(self):
        keys = pygame.key.get_pressed()
        status = self.animator.status.split("_")[0]
        old_status = status

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.direction.y = -1
            status = "up"
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.direction.y = 1
            status = "down"
        else: self.direction.y = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.direction.x = -1
            status = "left"
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.direction.x = 1
            status = "right"
        else: self.direction.x = 0
        
        if self.world.ui.tab.is_open or self.world.dialogue.active:
            self.direction = vector()
            status = old_status
        if self.direction.length() != 0: self.direction.normalize_ip()
        self.update_status(status)

    def update_status(self, base_status):
        if not self.using_item:
            if self.direction.length()==0 and not "idle" in base_status: base_status += "_idle"
        else:
            if (self.inventory.selected_tool) and (self.inventory.selected_tool not in base_status): base_status += f"_{self.inventory.selected_tool}"
        self.animator.set_status(base_status)

    def movement(self, dt):
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = round(self.pos.x)
        self.hitbox.centerx = self.rect.centerx
        self.collidable_collisions("horizontal")
        
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = round(self.pos.y)
        self.hitbox.centery = self.rect.centery+self.hitbox_offset
        self.collidable_collisions("vertical")

    def update(self, dt):
        if self.world.current_zone is None: return
        self.border_collisions()
        if self.world.current_zone is None: return
        self.door_collisions()
        self.collectable_collisions()
        self.chicken_collisions()
        self.input()
        self.movement(dt)
        self.animator.update(dt)
        self.update_interaction()

    def frame_start(self):
        self.selector.just_pressed = self.selector.is_ui = False
        self.selector.interact_rect = None

    def update_interaction(self):
        if not self.world.ui.can_interact(): return
        if self.world.dialogue.active: return

        if self.selector.just_pressed:
            self.using_item = True
            self.animator.stop_loop(self.interact_finish)
            self.animator.frame_index = 0

        mouse_offset = vector(pygame.mouse.get_pos())-WINDOW_CENTER
        if mouse_offset.length() > INTERACT_RADIUS: return
        interact_point = self.pos + mouse_offset

        interact_rect = pygame.Rect((0,0), (TILE_SIZE,TILE_SIZE))
        interact_rect.center = interact_point
        interacted_once = False

        if not self.world.current_zone.in_house:
            for sprite in self.world.current_zone.interactable:
                if sprite.hitbox.colliderect(interact_rect):
                    if sprite.can_interact(self.inventory.selected_tool, self.inventory.selected_object):
                        self.selector.interact_rect = sprite.hitbox
                    if self.selector.just_pressed:
                        interacted = sprite.interact(self.inventory.selected_tool, self.inventory.selected_object)
                        interacted_once = interacted
                        if interacted: break
                    if self.selector.interact_rect:
                        interacted_once = True
                        break
        
            if not interacted_once:
                if (hitbox:=self.world.current_zone.soil.can_interact(self.inventory.selected_tool, self.inventory.selected_object, interact_point)):
                    self.selector.interact_rect = hitbox
                if self.selector.just_pressed:
                    self.world.current_zone.soil.interact(self.inventory.selected_tool, self.inventory.selected_object, interact_point)
        else:
            for villager in self.world.current_zone.current_house.interior.villagers:
                if villager.hitbox.colliderect(interact_rect):
                    self.selector.interact_rect = villager.hitbox
                    if self.selector.just_pressed:
                        self.world.dialogue.start(villager.pfp, villager.name, villager.data)

    def interact_finish(self):
        self.using_item = False
        self.animator.resume_loop()

    def face_mouse(self):
        mouse_pos = vector(pygame.mouse.get_pos())
        angle = (mouse_pos-WINDOW_CENTER).as_polar()[1]
        topright_a = (vector(WIDTH,0)-WINDOW_CENTER).as_polar()[1]
        topleft_a = (vector(0,0)-WINDOW_CENTER).as_polar()[1]
        bottomright_a = (vector(WIDTH,HEIGHT)-WINDOW_CENTER).as_polar()[1]
        bottomleft_a = (vector(0,HEIGHT)-WINDOW_CENTER).as_polar()[1]
        if angle < 0:
            status = "up"
            if angle > topright_a: status = "right"
            elif angle < topleft_a: status = "left"
        else:
            status = "down"
            if angle > bottomleft_a: status = "left"
            elif angle < bottomright_a: status = "right"
        self.update_status(status)

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.face_mouse()
                self.selector.just_pressed = True
        self.inventory.event(event)

    def border_collisions(self):
        for tree in self.world.current_zone.border_trees:
            if tree.hitbox.colliderect(self.hitbox) and not self.world.transition.active: self.world.change_zone(tree.side)

    def collidable_collisions(self, direction):
        group = self.world.current_zone.collidable if not self.world.current_zone.in_house else self.world.current_zone.current_house.interior.collidable
        for sprite in group:
            if sprite.kinematic: continue
            if sprite.hitbox.colliderect(self.hitbox):
                if direction == "horizontal":
                    self.hitbox.right = sprite.hitbox.left if self.direction.x > 0 else self.hitbox.right
                    self.hitbox.left = sprite.hitbox.right if self.direction.x < 0 else self.hitbox.left
                    self.rect.centerx, self.pos.x = self.hitbox.centerx, self.hitbox.centerx
                    self.direction.x = 0
                else:
                    self.hitbox.top = sprite.hitbox.bottom if self.direction.y < 0 else self.hitbox.top
                    self.hitbox.bottom = sprite.hitbox.top if self.direction.y > 0 else self.hitbox.bottom
                    self.rect.centery = self.hitbox.centery - self.hitbox_offset
                    self.pos.y = self.rect.centery
                    self.direction.y = 0

    def door_collisions(self):
        if self.world.transition.active: return
        hitbox = self.hitbox.scale_by(1.5,1.5)
        if not self.world.current_zone.in_house:
            for door in self.world.current_zone.village_doors:
                if door.hitbox.colliderect(hitbox):
                    house = None
                    for h in self.world.current_zone.village_houses:
                        dist = (h.exterior.exit_loc-vector(door.pos)).length()
                        if dist < TILE_SIZE*3: house = h; break
                    self.world.current_zone.enter_house(house)
                    return
            return
        for door in self.world.current_zone.current_house.interior.doors:
            if door.hitbox.colliderect(hitbox):
                self.world.current_zone.exit_house()
                return
            
    def collectable_collisions(self):
        for sprite in self.world.current_zone.collectable:
            if sprite.hitbox.colliderect(self.hitbox): sprite.collect()

    def chicken_collisions(self):
        for rect, chicken_house in self.world.current_zone.chicken_zones:
            if rect.colliderect(self.hitbox): chicken_house.image = chicken_house.low_alpha
            else: chicken_house.image = chicken_house.normal_alpha

    def teleport(self, position):
        self.pos = vector(position)
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        self.hitbox.center = (self.rect.centerx, self.rect.centery+self.hitbox_offset)

    def translate(self, offset):
        self.teleport(self.pos+vector(offset))

    def draw(self, screenshot=None):
        if self.inventory.selected_object:
            image = self.assets["items"][self.inventory.selected_object]
            rect = image.get_rect(midbottom=self.hitbox.midbottom-self.world.offset)
            if not screenshot: self.display_surface.blit(image, rect)
            else: screenshot.blit(image, rect.topleft-self.world.current_zone.pixel_topleft)
        self.selector.draw()

class InteractSelector:
    def __init__(self, player:Player):
        self.player = player
        self.selector_images = player.world.assets["ui"]["selector"]
        self.display_surface = player.display_surface

        self.interact_rect = None
        self.is_ui = self.just_pressed = False
        self.selector_size = self.selector_images[0].get_width()//2
        self.selector_offset = vector(-self.selector_size,-self.selector_size)

    def draw(self, UI=False):
        if self.interact_rect and (not self.is_ui or UI):
            offset = self.player.world.offset if not self.is_ui else vector()
            self.display_surface.blit(self.selector_images[0], self.interact_rect.topleft+self.selector_offset-offset)
            self.display_surface.blit(self.selector_images[1], self.interact_rect.topright+self.selector_offset-offset)
            self.display_surface.blit(self.selector_images[2], self.interact_rect.bottomleft+self.selector_offset-offset)
            self.display_surface.blit(self.selector_images[3], self.interact_rect.bottomright+self.selector_offset-offset)

