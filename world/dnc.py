from settings import *
from support import get_window

class DayNightCycle:
    def __init__(self, world):
        self.world = world
        self.display_surace = get_window()

        self.dnc_surf = pygame.Surface(WINDOW_SIZES)
        self.dnc_surf.fill(NIGHT_COLOR)
        self.max_alpha = NIGHT_ALPHA
        self.dnc_surf.set_alpha(0)
        self.alpha = 0
        self.is_day = True
        self.dn_start_time = pygame.time.get_ticks()
        self.alpha_dir = 0

    def update(self, dt):
        if self.is_day:
            if self.alpha_dir != 1:
                if pygame.time.get_ticks() - self.dn_start_time > DAY_TIME: self.alpha_dir = 1

            self.alpha += self.alpha_dir* NIGHT_SPEED
            if self.alpha_dir != 0: self.dnc_surf.set_alpha(int(self.alpha))

            if self.alpha > self.max_alpha:
                self.is_day, self.alpha_dir = False,0
                self.dn_start_time = pygame.time.get_ticks()
        else:
            if self.alpha_dir != -1:
                if pygame.time.get_ticks()- self.dn_start_time > NIGHT_TIME: self.alpha_dir = -1

            self.alpha += self.alpha_dir*NIGHT_SPEED
            if self.alpha_dir != 0: self.dnc_surf.set_alpha(int(self.alpha))

            if self.alpha <= 0:
                self.is_day, self.alpha_dir = True,0
                self.dn_start_time = pygame.time.get_ticks()

    def draw(self):
        if int(self.alpha) <= 0: return
        self.display_surace.blit(self.dnc_surf, (0,0))