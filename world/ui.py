from settings import *
from support import get_window, main_font, lerp

class UI:
    def __init__(self, world):
        self.world = world
        self.assets = world.assets
        self.ui_assets = self.assets["ui"]
        self.player = world.player
        self.inventory = self.player.inventory
        self.display_surface = get_window()

        # fonts
        self.bag_font = main_font(18)
        self.title_font = main_font(22)
        self.amount_font = main_font(16)

        # emote
        self.frame_big = self.ui_assets["frame-big"]
        self.cur_emote = self.ui_assets["icons"]["emotes"][0]
        self.emote_frame_rect = self.frame_big.get_rect(topleft=(UI_OFFSET,UI_OFFSET))
        self.emote_rect = self.cur_emote.get_rect(center=self.emote_frame_rect.center)

        # coins, stars
        self.double_sign = self.ui_assets["signs"]
        self.signs_rect = self.double_sign.get_rect(midleft = (self.emote_frame_rect.right+UI_OFFSET, self.emote_frame_rect.centery))
        self.coin_img = pygame.transform.scale_by(self.ui_assets["icons"]["special"][13],0.8)
        self.star_img = pygame.transform.scale_by(self.ui_assets["icons"]["special"][7],0.8)
        self.coin_rect = self.coin_img.get_rect(midleft=(self.signs_rect.left-UI_OFFSET_H, self.signs_rect.centery-self.signs_rect.h//3.5))
        self.star_rect = self.coin_img.get_rect(midleft=(self.signs_rect.left-UI_OFFSET_H, self.signs_rect.centery+self.signs_rect.h//3.5))

        # tool/object
        self.tool_frame = self.ui_assets["frame"]
        self.cur_tool = None
        self.tool_frame_rect = self.tool_frame.get_rect(topright=(WIDTH-UI_OFFSET, UI_OFFSET))
        self.tool_rect = self.ui_assets["items"]["tomato"].get_rect(center=self.tool_frame_rect.center)
        self.light_stop = self.ui_assets["icons"]["all"][47]

        # bag
        self.single_sign = self.ui_assets["sign"]
        self.sign_rect = self.single_sign.get_rect(topright=(self.tool_frame_rect.left-UI_OFFSET, 0))
        self.bag_txt = self.bag_font.render(f"Bag", ANTIALAS, TEXT_DARK)
        self.bag_trect = self.bag_txt.get_rect(midbottom=(self.sign_rect.centerx, self.sign_rect.bottom+2*UI_SCALE))

        # water
        self.empty_bar = self.ui_assets["bar"]
        self.water_bar = self.ui_assets["bar-full"]
        self.bar_size = self.empty_bar.get_width()

        self.bag = BagUI(self)
        self.tab = TabUI(self)

    def can_interact(self):
        mpos = pygame.mouse.get_pos()
        if self.bag.is_open:
            if self.bag.bg_rect.collidepoint(mpos-self.bag.offset): return False
        return not self.sign_rect.collidepoint(mpos) and not self.tool_frame_rect.collidepoint(mpos) and not self.tab.is_open

    def draw(self):
        self.display_surface.blit(self.frame_big, self.emote_frame_rect) # emote frame
        self.display_surface.blit(self.cur_emote, self.emote_rect) # emote
        self.display_surface.blit(self.double_sign, self.signs_rect) # double sign
        self.display_surface.blit(self.tool_frame, self.tool_frame_rect) # tool frame
        self.display_surface.blit(self.cur_tool, self.tool_rect) # tool
        self.display_surface.blit(self.single_sign, self.sign_rect) # sign
        self.display_surface.blit(self.bag_txt, self.bag_trect) # bag text
        self.display_surface.blit(self.coin_img, self.coin_rect) # coin icon
        self.display_surface.blit(self.star_img, self.star_rect) # star icon
        self.display_surface.blit(self.coin_txt, self.coin_trect) # coin amount
        self.display_surface.blit(self.star_txt, self.star_trect) # star amount

        # water
        x = self.tool_frame_rect.left-self.bar_size-UI_OFFSET_H
        for i in range(1,PLAYER_MAX_WATER):
            image = self.empty_bar if self.inventory.water < i else self.water_bar
            self.display_surface.blit(image, (x, self.tool_frame_rect.centery))
            x -= self.bar_size

        self.bag.draw()
        self.tab.draw()

    def update(self, dt):
        if self.inventory.selected_tool: self.cur_tool = self.ui_assets["items"][self.inventory.selected_tool]
        elif self.inventory.selected_object: self.cur_tool = self.ui_assets["items"][self.inventory.selected_object]
        else: self.cur_tool = self.light_stop
        self.coin_txt = self.amount_font.render(f"{self.inventory.coins}", ANTIALAS, TEXT_DARK)
        self.star_txt = self.amount_font.render(f"{self.inventory.stars}", ANTIALAS, TEXT_DARK)
        self.coin_trect = self.coin_txt.get_rect(midleft=self.coin_rect.midright)
        self.star_trect = self.star_txt.get_rect(midleft=self.star_rect.midright)
        self.bag.update(dt)
        self.tab.update(dt)

    def event(self, event):
        self.bag.event(event)
        self.tab.event(event)

class TabUI:
    def __init__(self, ui):
        self.ui = ui
        self.ui_assets = ui.ui_assets
        self.display_surface = get_window()
        self.inventory = ui.inventory

        self.frame_img = self.ui_assets["frame"]
        frame_size = self.frame_img.get_width()
        self.is_open = False
        self.can_render = True
        self.center = vector(H_WIDTH, UI_OFFSET*2)
        self.selector_tl = pygame.transform.scale_by(self.ui_assets["selector"][0],1)
        self.selector_tr = pygame.transform.scale_by(self.ui_assets["selector"][1],1)
        self.selector_bl = pygame.transform.scale_by(self.ui_assets["selector"][2],1)
        self.selector_br = pygame.transform.scale_by(self.ui_assets["selector"][3],1)
        self.square = self.ui_assets["square-m"]

        self.offsets = {}
        self.inv_len = len(self.inventory.TOOLS_OBJS)
        center_i = int(self.inv_len/2)
        for i, thing_name in enumerate(self.inventory.TOOLS_OBJS):
            offset_i = -(center_i-i) if i < center_i else i-center_i if i > center_i else 0
            start_offset = int(-frame_size//2)
            cur_offset = vector(start_offset, 0)
            end_offset = int(frame_size*offset_i-frame_size//2+UI_OFFSET*offset_i)
            self.offsets[thing_name] = {"cur":cur_offset, "open":end_offset, "close":start_offset}

    def open(self):
        self.is_open = True
        self.can_render = True
    
    def close(self):
        self.is_open = False

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                if self.is_open: self.close()
                else: self.open()
            elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE or event.key == pygame.K_e: self.close()
            elif event.key == pygame.K_w or event.key == pygame.K_d or event.key == pygame.K_RIGHT or event.key == pygame.K_UP:
                self.move_right()
            elif event.key == pygame.K_s or event.key == pygame.K_a or event.key == pygame.K_LEFT or event.key == pygame.K_DOWN:
                self.move_left()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.ui.tool_frame_rect.collidepoint(event.pos):
                if self.is_open: self.close()
                else: self.open()

    def move_right(self):
        if not self.is_open: return
        if self.inventory.selected_tool:
            idx = self.inventory.TOOLS.index(self.inventory.selected_tool)
            idx += 1
            if idx > len(self.inventory.TOOLS)-1:
                idx = 0
                obj = self.inventory.OBJECTS[idx]
                if self.inventory.objects[obj] > 0:
                    self.inventory.selected_tool = ""
                    self.inventory.selected_object = obj
            else: self.inventory.selected_tool = self.inventory.TOOLS[idx]
        elif self.inventory.selected_object:
            idx = self.inventory.OBJECTS.index(self.inventory.selected_object)
            idx += 1
            if idx > len(self.inventory.OBJECTS)-1:
                idx = 0
                tool = self.inventory.TOOLS[idx]
                self.inventory.selected_tool = tool
                self.inventory.selected_object = ""
            else: self.inventory.selected_object = self.inventory.OBJECTS[idx]
        else:
            self.inventory.selected_tool = self.inventory.TOOLS[0]
            self.inventory.selected_object = ""

    def move_left(self):
        if not self.is_open: return
        if self.inventory.selected_tool:
            idx = self.inventory.TOOLS.index(self.inventory.selected_tool)
            idx -= 1
            if idx < 0:
                idx = len(self.inventory.OBJECTS)-1
                obj = self.inventory.OBJECTS[idx]
                if self.inventory.objects[obj] > 0:
                    self.inventory.selected_tool = ""
                    self.inventory.selected_object = obj
            else: self.inventory.selected_tool = self.inventory.TOOLS[idx]
        elif self.inventory.selected_object:
            idx = self.inventory.OBJECTS.index(self.inventory.selected_object)
            idx -= 1
            if idx < 0:
                idx = len(self.inventory.TOOLS)-1
                tool = self.inventory.TOOLS[idx]
                self.inventory.selected_tool = tool
                self.inventory.selected_object = ""
            else: self.inventory.selected_object = self.inventory.OBJECTS[idx]
        else:
            self.inventory.selected_tool = self.inventory.TOOLS[0]
            self.inventory.selected_object = ""

    def draw(self):
        if not self.can_render: return
        tools_objs = self.inventory.tools.copy()
        tools_objs.update(self.inventory.objects)

        for thing_name, thing_amount in tools_objs.items():
            offset = self.offsets[thing_name]["cur"]
            frame_rect = self.frame_img.get_rect(topleft=self.center+offset)
            item_img = self.ui_assets["items"][thing_name]
            item_rect = item_img.get_rect(center=frame_rect.center)
            self.display_surface.blit(self.frame_img, frame_rect)
            self.display_surface.blit(item_img, item_rect)

            if thing_name in self.inventory.OBJECTS:
                square_rect = self.square.get_rect(midtop=frame_rect.midbottom)
                amount_txt = self.ui.amount_font.render(f"x{thing_amount}", ANTIALAS, TEXT_DARK)
                amount_rect = amount_txt.get_rect(center=square_rect.center)
                self.display_surface.blit(self.square, square_rect)
                self.display_surface.blit(amount_txt, amount_rect)

            if thing_name == self.inventory.selected_tool or thing_name == self.inventory.selected_object:
                stl = self.selector_tl.get_rect(center=frame_rect.topleft)
                str = self.selector_tr.get_rect(center=frame_rect.topright)
                sbl = self.selector_tr.get_rect(center=frame_rect.bottomleft)
                sbr = self.selector_tr.get_rect(center=frame_rect.bottomright)
                self.display_surface.blit(self.selector_tl, stl)
                self.display_surface.blit(self.selector_tr, str)
                self.display_surface.blit(self.selector_bl, sbl)
                self.display_surface.blit(self.selector_br, sbr)

    def update(self, dt):
        done = 0
        for offset_dict in self.offsets.values():
            if self.is_open:
                offset_dict["cur"].x = lerp(offset_dict["cur"].x, offset_dict["open"], dt*TAB_SPEED)
                if abs(offset_dict["cur"].x-offset_dict["open"]) < 2: offset_dict["cur"].x = offset_dict["open"]
            else:
                offset_dict["cur"].x = lerp(offset_dict["cur"].x, offset_dict["close"], dt*TAB_SPEED)
                if offset_dict["cur"].x < 2: done += 1
        if done >= self.inv_len: self.can_render = False

class BagUI:
    def __init__(self, ui):
        self.ui = ui
        self.ui_assets = ui.ui_assets
        self.display_surface = get_window()
        self.inventory = ui.inventory

        self.bg_img = self.ui_assets["long-menu"]
        self.bg_rect = self.bg_img.get_rect(topright=(self.ui.sign_rect.right, UI_OFFSET))
        
        self.open_offset = self.bg_rect.height+UI_OFFSET
        self.closed_offset = 0
        self.dest_offset = self.closed_offset
        self.offset = vector()
        self.bg_rect.y = -self.bg_rect.height
        self.is_open = False

        self.title_txt = self.ui.title_font.render(f"Bag", ANTIALAS, TEXT_DARK)
        self.title_trect = self.title_txt.get_rect(midtop=(self.bg_rect.centerx, self.bg_rect.top+UI_OFFSET))

        self.square_img = self.ui_assets["btn"]
        self.square_size = vector(self.square_img.get_size())
        self.left_x = self.bg_rect.centerx-self.square_size.x-UI_OFFSET_H
        self.right_x = self.bg_rect.centerx+UI_OFFSET_H

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                if self.is_open: self.close()
                else: self.open()
            elif event.key == pygame.K_ESCAPE: self.close()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.ui.sign_rect.collidepoint(event.pos):
                if not self.is_open: self.open()

    def open(self):
        self.is_open = True
        self.dest_offset = self.open_offset

    def close(self):
        self.is_open = False
        self.dest_offset = self.closed_offset

    def draw(self):
        self.display_surface.blit(self.bg_img, self.bg_rect.topleft+self.offset)
        self.display_surface.blit(self.title_txt, self.title_trect.topleft+self.offset)

        y = self.title_trect.bottom+UI_OFFSET
        stage = "left"
        for item_name, item_amount in self.inventory.items.items():
            x = self.left_x if stage == "left" else self.right_x
            square_rect = self.square_img.get_rect(topleft=(x,y))
            item_img = self.ui_assets["items-small"][item_name]
            amount_txt = self.ui.amount_font.render(f"x{item_amount}", ANTIALAS, TEXT_DARK)
            item_rect = item_img.get_rect(center = (square_rect.centerx-square_rect.w//4,square_rect.centery))
            amount_trect = amount_txt.get_rect(midleft = item_rect.midright)
            self.display_surface.blit(self.square_img, square_rect.topleft+self.offset)
            self.display_surface.blit(item_img, item_rect.topleft+self.offset)
            self.display_surface.blit(amount_txt, amount_trect.topleft+self.offset)
            if stage == "left": stage = "right"
            else: stage = "left"; y += square_rect.height+UI_OFFSET

    def update(self, dt):
        self.offset.y = lerp(self.offset.y, self.dest_offset, dt*BAG_SPEED)
