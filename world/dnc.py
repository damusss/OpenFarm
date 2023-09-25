from settings import *
from support import get_window
import datetime

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
        
        self.time = DAY_START
        
    def str_time(self):
        td = datetime.timedelta(seconds=self.time)
        return ":".join(str(td).split(":")[:2])
        
    def update(self, dt):
        self.time += TIME_SPEED
        if self.time >= MIDNIGHT_TIME:
            self.time = 0
        
        # day
        if DAY_START < self.time < SUNSET_TIME:
            self.alpha = 0
            self.is_day = True
            
        if SUNSET_TIME < self.time < DAY_END:
            # cur_time-start_time : end_time-start_time = cur_alpha : max_alpha
            self.alpha = ((self.time-SUNSET_TIME) * NIGHT_ALPHA) / (DAY_END-SUNSET_TIME)
            self.is_day = True
        
        # night
        if self.time < SUNRISE_TIME or self.time > DAY_END:
            self.alpha = NIGHT_ALPHA
            self.is_day = False
            
        if SUNRISE_TIME < self.time < DAY_START:
            # cur_time-start_time : end_time-start_time = cur_alpha : max_alpha
            self.alpha = NIGHT_ALPHA - ((self.time-SUNRISE_TIME) * NIGHT_ALPHA) / (DAY_START-SUNRISE_TIME)
            self.is_day = False
            
        self.dnc_surf.set_alpha(self.alpha)

    def draw(self):
        if int(self.alpha) <= 0: return
        self.display_surace.blit(self.dnc_surf, (0,0))