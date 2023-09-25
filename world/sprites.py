from settings import *
from world.generic import Generic, HouseGeneric
from support import angle_to_vec, randoffset, tint_surface

class Animal(Generic):
    def __init__(self, pos, animal_type, zone):
        super().__init__(pos, zone.assets["animals"][animal_type]["idle"][0], [zone.all, zone.visible, zone.animals, zone.updates, zone.collectable], zone, True)
        self.animal_type = animal_type
        self.bounds_rect = None
        self.add_status_animator(zone.assets["animals"][animal_type], "idle")

        self.can_wander = self.is_moving = True
        self.orientation = "right"
        self.speed = ANIMAL_SPEEDS[animal_type]
        self.direction = angle_to_vec(randint(0,360))

        self.movement_start = self.movement_stop = self.last_dir_change = 0
        self.movement_start_range = (1500,2500)
        self.dir_change_range = (1000, 2500)
        self.movement_stop_range = (3500,5000)
        self.next_movement_stop = randint(self.movement_stop_range[0],self.movement_stop_range[1])
        self.next_movement_start = randint(self.movement_start_range[0],self.movement_start_range[1])
        self.next_dir_change = randint(self.dir_change_range[0],self.dir_change_range[1])

    def wander(self, dt):
        if not self.can_wander: return
        ticks = pygame.time.get_ticks()
        if self.is_moving:
            if ticks-self.movement_start >= self.next_movement_stop:
                self.is_moving = False
                self.movement_stop = ticks
                self.next_movement_start = randint(self.movement_start_range[0],self.movement_start_range[1])

            if ticks-self.last_dir_change>= self.next_dir_change: self.new_direction()
            if self.animator.status != "walk": self.animator.set_status("walk")
        else:
            if ticks - self.movement_stop >= self.next_movement_start:
                self.is_moving = True
                self.movement_start = ticks
                self.next_movement_stop = randint(self.movement_stop_range[0],self.movement_stop_range[1])
                self.new_direction()
            if self.animator.status != "idle": self.animator.set_status("idle")

    def movement(self, dt):
        if self.orientation == "left": self.animator.flippedx = True
        else: self.animator.flippedx = False
        if not self.is_moving or not self.can_wander:
            if self.animator.status != "idle": self.animator.set_status("idle")
            return

        self.pos.x += self.direction.x * self.speed*dt
        self.rect.centerx = round(self.pos.x)
        self.hitbox.centerx = self.rect.centerx
        self.collidable_collisions("horizontal")

        self.pos.y += self.direction.y * self.speed*dt
        self.rect.centery = round(self.pos.y)
        self.hitbox.centery= self.rect.centery
        self.collidable_collisions("vertical")

    def new_direction(self):
        self.direction = angle_to_vec(randint(0,360))
        self.last_dir_change = pygame.time.get_ticks()
        self.next_dir_change = randint(self.dir_change_range[0],self.dir_change_range[1])
        if self.direction.x > 0 : self.orientation = "right"
        else: self.orientation = "left"

    def collidable_collisions(self, direction):
        for sprite in self.zone.collidable:
            if sprite.hitbox.colliderect(self.hitbox):
                if direction == "horizontal":
                    self.hitbox.right = sprite.hitbox.left if self.direction.x > 0 else self.hitbox.right
                    self.hitbox.left = sprite.hitbox.right if self.direction.x < 0 else self.hitbox.left
                    self.rect.centerx, self.pos.x = self.hitbox.centerx, self.hitbox.centerx
                    self.direction.x *= -1
                else:
                    self.hitbox.top = sprite.hitbox.bottom if self.direction.y < 0 else self.hitbox.top
                    self.hitbox.bottom = sprite.hitbox.top if self.direction.y > 0 else self.hitbox.bottom
                    self.rect.centery = self.hitbox.centery
                    self.pos.y = self.rect.centery
                    self.direction.y *= -1
    
    def base_update(self, dt):
        self.animator.update(dt)
        self.wander(dt)
        self.movement(dt)
        if self.can_wander and not self.zone.world.dnc.is_day: self.can_wander = False

    def collect(self): return False

    def update(self, dt): self.base_update(dt)

class Chicken(Animal):
    def __init__(self, pos, zone, bounds_rect):
        super().__init__(pos, "chicken", zone)
        self.bounds_rect = bounds_rect
        self.nest = ChickenNest(vector(bounds_rect.center)+vector(randoffset(bounds_rect.w//3),randoffset(bounds_rect.h//3)), zone, self)
        self.eepy_img = self.animator.animations["idle"][1]

    def update(self, dt):
        self.base_update(dt)
        if not self.zone.world.dnc.is_day: self.image = self.eepy_img

class Cow(Animal):
    def __init__(self, pos, zone):
        super().__init__(pos, "cow", zone)

        self.last_milk = pygame.time.get_ticks()
        self.can_collect = False
        self.eepy_img = self.animator.animations["idle"][1]

    def collect(self):
        if not self.can_collect: return

        self.last_milk = pygame.time.get_ticks()
        self.zone.player.inventory.add_item("milk",1)
        DestroyMask(self.rect.center, self.image, self.zone)

    def update(self, dt):
        self.base_update(dt)

        if pygame.time.get_ticks()-self.last_milk > COW_COOLDOWN: self.can_collect, self.can_wander = True, False
        else: self.can_collect, self.can_wander = False, True

        if not self.zone.world.dnc.is_day:
            self.image = self.eepy_img
            self.can_wander = False

class ChickenNest(Generic):
    def __init__(self, pos, zone, chicken):
        super().__init__(pos, zone.assets["animals"]["egg"][3], [zone.all, zone.visible, zone.updates, zone.collectable], zone, True)

        self.chicken = chicken
        self.has_egg = False
        self.egg_img = zone.assets["animals"]["egg"][2]
        self.noegg_img = zone.assets["animals"]["egg"][3]
        self.last_egg = pygame.time.get_ticks()

    def collect(self):
        if not self.has_egg: return

        self.has_egg = False
        self.last_egg = pygame.time.get_ticks()
        self.image = self.noegg_img
        self.zone.player.inventory.add_item("egg",1)
        DestroyMask(self.pos, self.zone.assets["animals"]["egg"][0], self.zone)

    def update(self, dt):
        if not self.has_egg:
            if pygame.time.get_ticks() - self.last_egg > CHICKEN_COOLDOWN:
                self.has_egg = True
                self.image = self.egg_img
            self.chicken.can_wander = True if self.zone.world.dnc.is_day else False
        else: self.chicken.can_wander = False 

class ChickenHouse(Generic):
    def __init__(self, pos, zone):
        super().__init__(pos, zone.assets["house"]["chicken-house"], [zone.all, zone.visible_top], zone, True)
        self.normal_alpha = self.image
        self.low_alpha = self.image.copy()
        self.low_alpha.set_alpha(150)     

class InvisibleVillageElementTile(pygame.sprite.Sprite):
    def __init__(self, topleft, zone):
        super().__init__([zone.invis_village_elements])
        self.hitbox = pygame.Rect(topleft, (TILE_SIZE, TILE_SIZE))
        self.rect = self.hitbox.copy()
        self.pos = vector(self.rect.center)
        self.asset_name = "invisible"

class Merchant(HouseGeneric):
    def __init__(self, center, interior, name, data):
        super().__init__(center, interior.zone.assets["animals"]["merchant"][0], [interior.all, interior.visible, interior.updates, interior.villagers], interior.house, True)
        self.add_animator(interior.zone.assets["animals"]["merchant"])
        self.can_save = False
        self.name, self.data = name, data
        self.pfp = pygame.transform.scale_by(interior.zone.assets["animals"]["merchant"][0],1.5)

    def update(self, dt):
        self.animator.update(dt)

class HouseTile(HouseGeneric):
    def __init__(self, topleft, asset_index, interior, collidable=True, door=False, floor=False, top=False):
        super().__init__(topleft, interior.house.zone.assets["house"]["house"][asset_index], [interior.all], interior.house, False)
        if collidable: interior.collidable.add(self)
        if door: interior.doors.add(self)
        if floor: interior.visible_bottom.add(self)
        else:
            interior.walls.add(self)
            if top: interior.visible_top.add(self)
            else: interior.visible.add(self)
        self.interior = interior
        self.asset_index = asset_index
        self.is_tile, self.pos_center = True, False
        self.collidable, self.door, self.floor, self.top = collidable, door, floor, top

class HouseDecoration(HouseGeneric):
    def __init__(self, pos, asset_index, interior, collidable=True, floor=False, pos_center=True):
        super().__init__(pos, interior.house.zone.assets["house"]["house-decoration"][asset_index], [interior.all, interior.decorations], interior.house, pos_center)
        if collidable: interior.collidable.add(self)
        if floor: interior.visible_bottom.add(self)
        else: interior.visible.add(self)
        self.interior = interior
        self.asset_index = asset_index
        self.collidable, self.door, self.floor, self.top, self.pos_center, self.is_tile = collidable, False, floor, False, pos_center, False

class HouseExteriorTile(Generic):
    def __init__(self, topleft, asset_index, zone, tint, hitbox_change=None, roof=True, door=False, asset_name="house", behind=False, chimney=False):
        super().__init__(topleft, zone.assets["house"][asset_name][asset_index], [zone.all, zone.village_elements], zone, False)
        self.asset_index, self.asset_name, self.hitbox_change, self.roof, self.behind, self.door, self.tint, self.chimney = \
            asset_index, asset_name, hitbox_change, roof, behind, door, tint, chimney
        if hitbox_change != "none": zone.collidable.add(self)
        if hitbox_change == "left":
            self.hitbox.scale_by_ip(scale_by=(0.25,1.0))
            self.hitbox.midleft = self.rect.midleft
        elif hitbox_change == "right":
            self.hitbox.scale_by_ip(0.25,1.0)
            self.hitbox.midright = self.rect.midright
        if roof: zone.visible_top.add(self)
        elif behind: zone.visible_bottom.add(self)
        else: zone.visible.add(self)
        if door: zone.village_doors.add(self)
        if roof and not chimney: self.image = tint_surface(self.image, tint)

class BorderTree(Generic):
    def __init__(self, pos, zone, size):
        super().__init__(pos, zone.assets["objs"][f"tree_{size}"], [], zone, True)
        self.size = size

class Stump(Generic):
    def __init__(self, tree, zone, center=None, tree_size=None, tree_rel=None):
        self.tree = tree
        self.tree_size = self.tree.size if tree else tree_size
        super().__init__((0,0), zone.assets["objs"][f"stump_{self.tree_size}"], [zone.all, zone.visible_bottom, zone.collidable, zone.interactable, zone.stumps], zone, True)
        if tree: self.rect.midbottom = (tree.rect.centerx, tree.rect.bottom-1*SCALE*4)
        else: self.rect.center = center
        self.hitbox.center = self.rect.center
        self.pos = vector(self.rect.center)
        self.tree_rel = self.tree.pos-self.pos if tree else tree_rel
        if not tree: self.tree_destroyed()

    def tree_destroyed(self):
        self.tree = None
        self.tree_killed = pygame.time.get_ticks()
        self.zone.updates.add(self)

    def spawn_tree(self):
        Tree(self.pos+self.tree_rel, self.zone, self.tree_size)

    def can_interact(self, item, object):
        return item == "axe"

    def interact(self, item, object):
        if item == "axe":
            DestroyMask(self.pos, self.image, self.zone)
            self.kill()
            self.zone.player.inventory.add_item("wood", randint(1,3))
            return True
        return False
    
    def update(self, dt):
        if pygame.time.get_ticks() - self.tree_killed > TREE_COOLDOWN:
            self.spawn_tree()
            self.kill()
    
class Berry(Generic):
    def __init__(self, pos, zone, asset_index, name, parent):
        super().__init__(pos, zone.assets["farming"][name][asset_index], [zone.all, zone.visible_top, zone.collectable], zone, True)
        self.name, self.parent = name, parent
    
    def collect(self):
        self.zone.player.inventory.add_item(self.name, 1)
        self.parent.berry_collected(self)
        DestroyMask(self.pos, self.image, self.zone, top=True)
        self.kill()

class Tree(Generic):
    def __init__(self, pos, zone, size, apple_count=None):
        super().__init__(pos, zone.assets["objs"][f"tree_{size}"], [zone.all, zone.visible, zone.trees, zone.interactable, zone.updates], zone, True)
        self.size = size
        self.stump = Stump(self, zone)
        self.apples = []
        self.max_apples = randint(1,3)
        self.last_apple = pygame.time.get_ticks()
        if apple_count is None: apple_count = self.max_apples
        if self.size == "medium":
            for i in range(apple_count): self.spawn_apple()
        else: zone.updates.remove(self)

    def spawn_apple(self):
        apple = Berry(self.pos+vector(randint(-self.rect.w//5,self.rect.w//5), randint(-self.rect.h//5, self.rect.h//10)),
               self.zone, choice([0,1]), "apple", self)
        self.apples.append(apple)

    def berry_collected(self, apple):
        self.apples.remove(apple)

    def can_interact(self, tool, object):
        return tool == "axe"

    def interact(self, item, object):
        if item == "axe":
            DestroyMask(self.pos, self.image, self.zone)
            for apple in self.apples: apple.kill()
            self.stump.tree_destroyed()
            self.zone.player.inventory.add_item("wood", randint(1,3))
            self.kill()
            return True
        return False
    
    def update(self, dt):
        if self.size == "small": return
        if pygame.time.get_ticks() - self.last_apple >= BERRY_COOLDOWN:
            self.last_apple = pygame.time.get_ticks()
            if len(self.apples) < self.max_apples: self.spawn_apple()
    
class Bush(Generic):
    def __init__(self, pos, zone, berry_count=None):
        super().__init__(pos, zone.assets["objs"]["bush"], [zone.all, zone.visible, zone.bushes, zone.interactable, zone.updates], zone, True)
        self.berries = []
        self.max_berries = randint(1,3)
        self.last_berry = pygame.time.get_ticks()
        if berry_count is None: berry_count = self.max_berries
        for i in range(berry_count): self.spawn_berry()

    def spawn_berry(self):
        berry = Berry(self.pos+vector(randint(-self.rect.w//5,self.rect.w//5), randint(-self.rect.h//5, self.rect.h//5)),
               self.zone, choice([0,1]), "berry", self)
        self.berries.append(berry)

    def berry_collected(self, berry):
        self.berries.remove(berry)

    def can_interact(self, tool, object):
        return tool == "axe"

    def interact(self, item, object):
        if item == "axe":
            DestroyMask(self.pos, self.image, self.zone)
            for berry in self.berries: berry.kill()
            self.zone.player.inventory.add_item("grass", randint(1,3))
            self.kill()
            return True
        return False
    
    def update(self, dt):
        if pygame.time.get_ticks() - self.last_berry >= BERRY_COOLDOWN:
            self.last_berry = pygame.time.get_ticks()
            if len(self.berries) < self.max_berries: self.spawn_berry()

class Water(Generic):
    def __init__(self, pos, zone):
        super().__init__(pos, zone.assets["water"][0], [zone.all, zone.visible_water, zone.updates, zone.waters, zone.collidable, zone.interactable], zone, False)
        self.add_animator(zone.assets["water"])

    def update(self, dt):
        self.animator.update(dt)

    def can_interact(self, tool, object):
        return tool == "water"

    def interact(self, item, object):
        if item == "water":
            self.zone.player.inventory.fill_water()
            return True
        return False

class Tile(Generic):
    def __init__(self, pos, image, zone, asset_name, asset_index, water_sprite=None):
        super().__init__(pos, image, [zone.all, zone.visible_behind, zone.tiles], zone, False)
        self.asset_name, self.asset_index = asset_name, asset_index
        if water_sprite: zone.collidable.remove(water_sprite)

class Decoration(Generic):
    def __init__(self, pos, image, zone, interact_item, drop_item="grass",drop_amount=1, data=""):
        super().__init__(pos, image, [zone.all, zone.visible, zone.interactable, zone.decorations], zone, True)
        self.interact_item = interact_item
        self.drop_item = drop_item
        self.drop_amount = drop_amount
        self.data = data

    def can_interact(self, tool, object):
        return tool in self.interact_item and tool

    def interact(self, item, object):
        if item in self.interact_item and item:
            DestroyMask(self.pos, self.image, self.zone)
            self.kill()
            self.zone.player.inventory.add_item(self.drop_item, self.drop_amount)
            return True
        return False

class DestroyMask(Generic):
    def __init__(self, pos, image, zone, disappear_cooldown=400, top=False):
        mask = pygame.mask.from_surface(image)
        img = mask.to_surface()
        img.set_colorkey("black")
        super().__init__(pos, img, [zone.all, zone.updates], zone, True)
        self.disappear_cooldown = disappear_cooldown
        self.born_time = pygame.time.get_ticks()
        if top: zone.visible_top.add(self)
        else: zone.visible.add(self)

    def update(self, dt):
        if pygame.time.get_ticks()-self.born_time >= self.disappear_cooldown: self.kill()

class SoilDirt(Generic):
    def __init__(self, topleft, grid_pos, name, zone):
        super().__init__(topleft, zone.assets["soil"][name], [zone.all, zone.visible_behind, zone.soil_dirts], zone, False)
        self.grid_pos = grid_pos
        self.name = name

class SoilWater(Generic):
    def __init__(self, pos, grid_pos, image, zone):
        super().__init__(pos, image, [zone.all, zone.visible_bottom, zone.soil_waters], zone, True)
        self.grid_pos = grid_pos
        self.image.set_alpha(randint(50,100))

class SoilPlant(Generic):
    def __init__(self, pos, grid_pos, zone, crop_name, soil, stage=0, grown=False):
        super().__init__(pos, zone.assets["farming"][crop_name][0], [zone.all, zone.visible, zone.updates, zone.soil_plants, zone.interactable], zone, True)
        self.grid_pos, self.stage, self.grown, self.soil, self.crop_name = grid_pos, stage, grown, soil, crop_name
        
        self.stages = zone.assets["farming"][crop_name]
        self.image = self.stages[self.stage]
        self.last_grow = pygame.time.get_ticks()
        self.cooldown = CROP_COOLDOWNS[self.crop_name]

    def can_interact(self, tool, object):
        return tool == "hoe"

    def interact(self, tool, object):
        if not self.grown: return
        if tool != "hoe": return
        self.zone.player.inventory.add_item(self.crop_name, randint(1,2))
        self.zone.player.inventory.add_object(f"{self.crop_name}-seeds",1)
        DestroyMask(self.pos, self.image, self.zone)
        self.soil.plant_collected(self)
        self.kill()

    def update(self, dt):
        if self.grown: return
        if pygame.time.get_ticks() - self.last_grow >= self.cooldown:
            if self.soil.has_water(self):
                self.stage += 1
                self.image = self.stages[self.stage]
                if self.stage >= len(self.stages)-1:
                    self.grown = True
                    self.soil.consume_water(self)
            self.last_grow = pygame.time.get_ticks()