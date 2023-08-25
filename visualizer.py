import pygame, sys

START_PATH = "assets/graphics/"
EXT = "png"

### CONFIG ###
path = "house/fences"
tile_size = 64
scale = 2
color = "green"
font_size = 40
##############

pygame.init()
screen = pygame.display.set_mode((100,100))
surface = pygame.image.load(f"{START_PATH}{path}.{EXT}").convert_alpha()
surface = pygame.transform.scale_by(surface, scale)
screen = pygame.display.set_mode(surface.get_size(), pygame.WINDOWPOS_CENTERED)
clock = pygame.time.Clock()
pygame.display.set_caption("Easy Visualizer")
font = pygame.Font(f"assets/fonts/main.ttf", font_size)

xamount = surface.get_width()//(tile_size*scale)
yamount = surface.get_height()//(tile_size*scale)

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()

    screen.fill("black")

    screen.blit(surface, (0,0))
    
    index = 0
    for y in range(int(yamount)):
        for x in range(int(xamount)):
            rect = pygame.Rect(x*tile_size*scale, y*tile_size*scale, tile_size*scale, tile_size*scale)
            pygame.draw.rect(screen, color, rect, 1)
            text_surf = font.render(str(index), False, color)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)
            index += 1

    clock.tick(60)
    pygame.display.update()
