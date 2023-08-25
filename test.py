import pygame
import pygame._sdl2 as pys

pygame.init()
pygame.display.set_mode((640, 480))
window = pys.Window("Test", (640, 480), fullscreen=False)
renderer = pys.Renderer(window,accelerated=True)

surf = pygame.image.load("assets/graphics/house/house.png").convert_alpha()
texture = pys.Texture.from_surface(renderer, surf)
rect = surf.get_rect(topleft=(0,0))

while True:
    for e in pygame.event.get():
        if e.type== pygame.QUIT: pygame.quit()

    renderer.draw_color = (0,0,20,0)
    renderer.clear()

    texture.draw(dstrect=rect)

    renderer.present()