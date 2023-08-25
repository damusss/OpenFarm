from settings import *
from assetloader import AssetLoader
from audio import Audio
from world.world import World
import os

class Main:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode(WINDOW_SIZES,pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.assets = AssetLoader()
        self.audio = Audio()

        #for file in os.listdir("data/test_world"):
        #    os.remove(f"data/test_world/{file}")

        self.world = World(self, "test_world")
        self.in_world = True
        
    def run(self):
        while True:
            dt = self.clock.tick(WINDOW_FPS)*0.001
            if self.in_world: self.world.run(dt)
            pygame.display.update()
            pygame.display.set_caption(f"{self.clock.get_fps():.0f}")

if __name__ == "__main__": Main().run()