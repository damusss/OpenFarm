from settings import *
import os, sys
from spritesheet import SingleSpritesheet, Spritesheet

# resources
def main_font(size, scale=UI_SCALE):
    return pygame.font.Font("assets/fonts/main.ttf",int(size*scale))

def load_audio(name, volume=1, ext="mp3"):
    sound = pygame.mixer.Sound(f"assets/audio/fx/{name}.{ext}")
    sound.set_volume(volume)
    return {
        "sound":sound,
        "volume":volume
    }

def file_names(path: str) -> list[str]:
    return [
        file_name.split(".")[0] for file_name in os.listdir(path) if "." in file_name
    ]


def file_names_full(path: str) -> list[str]:
    return [name for name in os.listdir(path) if "." in name]


def file_names_strict(path: str, exclude: list[str], extensions: list[str]) -> list[str]:
    files = [
        file_name.split(".")[0]
        for file_name in os.listdir(path)
        if "." in file_name and file_name.split(".")[1] in extensions
    ]
    for file in exclude:
        if file in files:
            files.remove(file)
    return files


# math
def randsign():
    return choice([1,-1])

def randoffset(max_value):
    return randint(-int(max_value), int(max_value))

def randoffsetvec(max_value):
    return vector(randint(-int(max_value), int(max_value)),randint(-int(max_value), int(max_value)))

def angle_to_vec(angle):
    return vector(math.cos(math.radians(angle)),-math.sin(math.radians(angle)))

def weighted_choice(sequence,weights):
    weightssum = sum(weights)
    chosen = randint(0,weightssum)
    cweight = 0; i = 0
    for w in weights:
        if inside_range(chosen,cweight,cweight+w): return sequence[i]
        cweight += w; i += 1
        
def weighted_choice_combined(sequence_and_weights):
    sequence = [s_a_w[0] for s_a_w in sequence_and_weights]
    weights = [saw[1] for saw in sequence_and_weights]
    weightssum = sum(weights)
    chosen = randint(0,weightssum)
    cweight = 0; i = 0
    for w in weights:
        if inside_range(chosen,cweight,cweight+w): return sequence[i]
        cweight += w; i += 1
        
def lerp(start, end, t): return t * (end - start) + start
            
def inside_range(number:float|int,rangeStart:float|int,rangeEnd:float|int)->bool:
    return number >= min(rangeStart,rangeEnd) and number <= max(rangeStart,rangeEnd)

def point_circle(point, center, radius):
    distance = (point - center).length()
    return distance <= radius

def rect_circle(rect, center, radius):
    corners = [rect.topleft, rect.bottomleft, rect.topright, rect.bottomright]
    for corner in corners:
        if point_circle(vector(corner), center, radius): return True
    return False

# utils
def generate_villager():
    name = choice(list(VILLAGERS.keys()))
    gen_data = VILLAGERS[name]
    if gen_data["trade"]:
        trade_num = randint(gen_data["trade-num"][0], gen_data["trade-num"][1])
        trades = []
        for i in range(trade_num):
            item_name = choice(list(gen_data["trades"].keys()))
            amount = randint(3,5)
            price = amount*gen_data["trades"][item_name]+randint(3,5)
            trades.append([item_name, amount, price])
        return name, {"trade": True, "trades":trades}
    else:
        dialogue = choice(gen_data["dialogues"])
        return name, {"trade":False, "dialogue": dialogue}

def list_remove_cond(iterable, condition):
    toremove = [el for el in iterable if condition(el)]
    for e in toremove: iterable.remove(e)

def quit_all():
    pygame.quit()
    sys.exit()

def get_window():
    return pygame.display.get_surface()

def set_cursor(name, assets):
    pygame.mouse.set_cursor(pygame.Cursor((0,0),assets["ui"]["mouse"][name]))

# graphics
def load(path, convert_alpha, scale=1, ext="png"):
    image = pygame.image.load(f"assets/graphics/{path}.{ext}").convert_alpha() \
        if convert_alpha else pygame.image.load(f"assets/graphics/{path}.{ext}").convert()
    if scale != 1: return pygame.transform.scale_by(image, scale)
    return image

def load_list(path, convert_alpha, scale=1, ext="png"):
    images = []
    for _, _, image_names in os.walk(f"assets/graphics/{path}"):
        for image_name in image_names:
            full_path = f"{path}/{image_name.split('.')[0]}"
            image = pygame.image.load(f"assets/graphics/{full_path}.{ext}").convert_alpha() \
                if convert_alpha else pygame.image.load(f"assets/graphics/{full_path}.{ext}").convert()
            if scale != 1: image = pygame.transform.scale_by(image, scale)
            images.append(image)
        break
    return images

def load_dict(path, convert_alpha, scale=1, ext="png"):
    images = {}
    for _, _, image_names in os.walk(f"assets/graphics/{path}"):
        for image_name in image_names:
            dict_name = image_name.split(".")[0]
            full_path = f"{path}/{dict_name}"
            image = pygame.image.load(f"assets/graphics/{full_path}.{ext}").convert_alpha() \
                if convert_alpha else pygame.image.load(f"assets/graphics/{full_path}.{ext}").convert()
            if scale != 1: image = pygame.transform.scale_by(image, scale)
            images[dict_name] = image
        break
    return images

def empty_surf(sizes, color, flags=0):
    surf = pygame.Surface(sizes,flags)
    surf.fill(color)
    return surf

def only_sprites_from_tuple(sprites): return {name:sprite for name, (sprite,_) in sprites.items()}

def radial_image(surface:pygame.Surface, erase_angle):
    erase_angle -= 180
    surface = surface.copy()
    w,h = surface.get_size()
    cx, cy = w//2, h//2
    center = vector(cx,cy)
    for x in range(w):
        for y in range(h):
            if surface.get_at((x,y)).a == 0: continue
            direction = vector(x,y)-center
            if math.degrees(math.atan2(direction.x, -direction.y)) < erase_angle: surface.set_at((x,y), (0,0,0,0))
    return surface

def single_sheet(path, convert_alpha, scale=1, ext="png", w=None, flip=False):
    return [pygame.transform.scale_by(frame, scale) for frame in 
            SingleSpritesheet(pygame.transform.flip(load(path, convert_alpha, 1, ext), flip, False), w).frames()]

def load_sheet(path, convert_alpha, scale=1, size=REAL_TILE_SIZE, ext="png"):
    return [frame for frame in Spritesheet(load(path, convert_alpha, 1, ext), size).frames(scale)]

# text
def create_outline(
    surface: pygame.Surface,
    radius: int,
    color: pygame.Color | list[int] | tuple[int, ...] = (0, 0, 0, 255),
    rounded: bool = False,
    border_inflate_x: int = 0,
    border_inflate_y: int = 0,
    mask_threshold=127,
    sharpness_passes: int = 4,
) -> pygame.Surface:
    surf_size = surface.get_size()
    backdrop_surf_size = (
        surf_size[0] + radius + border_inflate_x,
        surf_size[1] + radius + border_inflate_y,
    )

    silhouette = pygame.mask.from_surface(surface, threshold=mask_threshold).to_surface(
        setcolor=color, unsetcolor=(0, 0, 0, 0)
    )
    backdrop = pygame.Surface((backdrop_surf_size), pygame.SRCALPHA)
    blit_topleft = (
        backdrop_surf_size[0] / 2 - surf_size[0] / 2,
        backdrop_surf_size[1] / 2 - surf_size[1] / 2,
    )
    backdrop.blit(silhouette, blit_topleft)
    backdrop_blurred = (
        pygame.transform.gaussian_blur(backdrop, radius=radius)
        if rounded
        else pygame.transform.box_blur(backdrop, radius=radius)
    )
    for _ in range(sharpness_passes):
        backdrop_blurred.blit(
            backdrop_blurred, (0, 0), special_flags=pygame.BLEND_RGBA_ADD
        )

    backdrop_blurred.blit(surface, blit_topleft)
    return backdrop_blurred
