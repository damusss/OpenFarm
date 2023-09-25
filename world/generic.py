from settings import *
from support import get_window
from pygame.sprite import Sprite, Group

class Generic(Sprite):
    def __init__(self, pos, image, groups, zone, pos_center):
        super().__init__(groups)
        self.image, self.zone = image, zone
        self.world = self.zone.world if self.zone else zone
        self.rect = self.image.get_rect(center=pos) if pos_center else self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.copy()
        self.pos = vector(pos)
        self.animator: StatusAnimator|Animator = None
        self.kinematic = False

    def add_animator(self, frames, speed_mul=1, loop=True, on_finish=None):
        self.animator = Animator(self, frames, speed_mul, loop, on_finish)

    def add_status_animator(self, animations, status, speed_mul=1, loop=True, on_finish=None):
        self.animator = StatusAnimator(self, animations, status, speed_mul, loop, on_finish)

class BorderTreePack:
    def __init__(self, side, zone):
        self.zone, self.side = zone, side
        self.trees = []
        self.display_surface = get_window()
        zone.border_trees.append(self)

    def register(self, tree):
        self.trees.append(tree)

    def build(self):
        min_x = min_y = max_x = max_y = None
        self.trees = sorted(self.trees, key=lambda t: t.rect.centery)

        for tree in self.trees:
            if not min_x or tree.rect.x < min_x: min_x = tree.rect.x
            if not max_x or tree.rect.right > max_x: max_x = tree.rect.right
            if not min_y or tree.rect.y < min_y: min_y = tree.rect.y
            if not max_y or tree.rect.bottom > max_y: max_y = tree.rect.bottom
        self.hitbox = pygame.Rect(min_x,min_y,max_x-min_x,max_y-min_y)
        self.rect = self.hitbox

        self.image = pygame.Surface(self.hitbox.size, pygame.SRCALPHA); self.image.fill(0)
        for tree in self.trees: self.image.blit(tree.image, tree.rect.topleft-vector(self.hitbox.topleft))

    def kill(self):
        for sprite in self.trees: sprite.kill()
        self.trees.clear()
        del self

    def draw(self):
        self.display_surface.blit(self.image, self.hitbox.topleft-self.zone.world.offset)

    def screenshot(self, screenshot):
        screenshot.blit(self.image, self.hitbox.topleft-self.zone.pixel_topleft)

class HouseGeneric(Sprite):
    def __init__(self, pos, image, groups, house, pos_center):
        super().__init__(groups)
        self.image, self.house = image, house
        self.rect = self.image.get_rect(center=pos) if pos_center else self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.copy()
        self.pos = vector(pos)
        self.animator: StatusAnimator|Animator = None
        self.kinematic, self.can_save = False, True

    def add_animator(self, frames, speed_mul=1, loop=True, on_finish=None):
        self.animator = Animator(self, frames, speed_mul, loop, on_finish)

    def add_status_animator(self, animations, status, speed_mul=1, loop=True, on_finish=None):
        self.animator = StatusAnimator(self, animations, status, speed_mul, loop, on_finish)

class CameraGroup(Group):
    def __init__(self, world):
        super().__init__()
        self.world = world
        self.display_surface = get_window()
        self.sorted_cache = []
        self.super = super()
    
    def custom_draw(self):
        for sprite in sorted(self.spritedict, key=lambda sprite: sprite.pos.y):
            self.display_surface.blit(sprite.image,sprite.rect.topleft-self.world.offset)

    def screenshot(self, screenshot, house=None):
        offset = house.topleft if house else self.world.current_zone.pixel_topleft
        for sprite in sorted(self.spritedict, key=lambda sprite: sprite.pos.y):
            screenshot.blit(sprite.image, sprite.rect.topleft-offset)

class Animator:
    def __init__(self, parent, frames, speed_mul=1, loop=True, on_finish=None):
        self.parent, self.frames = parent, frames
        self.animation_speed = ANIMATION_SPEED*speed_mul
        self.frame_index = 0
        self.loop = loop
        self.finished = self.flippedx = self.flippedy = False
        self.on_finish = on_finish

    def update(self, dt):
        self.frame_index += self.animation_speed*dt * (not self.finished)
        if int(self.frame_index) > len(self.frames)-1:
            if self.loop: self.frame_index = 0
            else:
                self.finished = True
                self.frame_index = 0
                if self.on_finish: self.on_finish()
                else: self.parent.kill()
        self.parent.image = pygame.transform.flip(self.frames[int(self.frame_index)], self.flippedx, self.flippedy)

    def stop_loop(self, on_finish=None):
        self.loop = False
        self.on_finish = on_finish

    def resume_loop(self):
        self.loop = True
        self.on_finish = None
        self.finished = False

class StatusAnimator(Animator):
    def __init__(self, parent, animations, status, speed_mul=1, loop=True, on_finish=None):
        super().__init__(parent, animations[status], speed_mul, loop, on_finish)
        self.animations, self.status = animations, status

    def set_status(self, status):
        if self.status != status:
            self.status = status
            self.frames = self.animations[self.status]
            self.frame_index = 0
