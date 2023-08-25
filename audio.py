from pygame import mixer_music as mm
from settings import *
from support import load_audio
import json, os

class Audio:
    def __init__(self):
        self.fx_volume = 1
        self.music_volume = 0.5
        self.volume_step = 0.1
        self.music_volumes = {
            "world":0.5,
        }
        self.cur_music = None
        self.fx = {
            }
        self.load_data()

    def load_data(self):
        if not os.path.exists("data/audio.json"): self.save_data()
        with open("data/audio.json","r") as file:
            data = json.load(file)
            self.change_music_volume(data["music-volume"])
            self.change_fx_volume(data["sound-volume"])

    def save_data(self):
        with open("data/audio.json","w") as file:
            data = {
                "music-volume":self.music_volume,
                "sound-volume":self.fx_volume,
            }
            json.dump(data, file)

    def update_music_volume(self, amount):
        self.change_music_volume(self.music_volume+amount)

    def step_music_volume(self, sign):
        self.update_music_volume(self.volume_step*sign)

    def change_music_volume(self, volume):
        self.music_volume = volume
        self.music_volume = pygame.math.clamp(self.music_volume,0.0,1.0)
        self.refresh_volumes()

    def update_fx_volume(self, amount):
        self.change_fx_volume(self.fx_volume+amount)

    def step_fx_volume(self, sign):
        self.update_fx_volume(self.volume_step*sign)

    def change_fx_volume(self, volume):
        self.fx_volume = volume
        self.fx_volume = pygame.math.clamp(self.fx_volume,0.0,1.0)
        self.refresh_volumes()

    def refresh_volumes(self):
        if self.cur_music: mm.set_volume(self.music_volume * self.music_volumes[self.cur_music])
        for fx in self.fx.values(): fx["sound"].set_volume(self.fx_volume*fx["volume"])

    def play_music(self, name, ext="mp3", fade_ms = 100):
        mm.stop(); mm.unload()
        mm.load(f"assets/audio/music/{name}.{ext}")
        self.cur_music = name
        self.refresh_volumes()
        mm.play(-1, fade_ms=fade_ms)
    
    def stop_music(self): mm.stop()
    def pause_music(self): mm.pause()
    def resume_music(self): mm.unpause()
         
    def play_fx(self, name, loops=0): self.fx[name]["sound"].play(loops)
    def stop_fx(self, name): self.fx[name]["sound"].stop()
    def play_fx_single(self, name, loops=0):
        self.fx[name]["sound"].stop()
        self.fx[name]["sound"].play(loops)
