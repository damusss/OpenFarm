from settings import *
from support import get_window, main_font, lerp, generate_menu, simple_outline, draw_outline

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
        
        # dnc
        bag_size = (self.bag_trect.h//1.2, self.bag_trect.h//1.2)
        self.day_img = pygame.transform.scale(self.ui_assets["sun"], bag_size)
        self.night_img = pygame.transform.scale(self.ui_assets["moon"], bag_size)
        self.dnc_rect = self.day_img.get_rect()

        self.bag = BagUI(self)
        self.tab = TabUI(self)
        self.f1 = False

    def can_interact(self):
        mpos = pygame.mouse.get_pos()
        if self.bag.is_open:
            if self.bag.bg_rect.collidepoint(mpos-self.bag.offset): return False
        return not self.sign_rect.collidepoint(mpos) and not self.tool_frame_rect.collidepoint(mpos) and not self.tab.is_open

    def draw(self):
        if self.f1:
            return
        
        # main
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
        draw_outline(self.display_surface, self.time_outline, self.time_trect, self.time_txt) # clock
        self.display_surface.blit(self.day_img if self.world.dnc.is_day else self.night_img, self.dnc_rect) # sun moon

        # water
        x = self.tool_frame_rect.left-self.bar_size-UI_OFFSET_H
        for i in range(1,PLAYER_MAX_WATER):
            image = self.empty_bar if self.inventory.water < i else self.water_bar
            self.display_surface.blit(image, (x, self.tool_frame_rect.centery))
            x -= self.bar_size
        
        # comps
        self.bag.draw()
        self.tab.draw()
        
        # selected
        if self.inventory.selected_object:
            image = self.assets["ui"]["items"][self.inventory.selected_object]
            rect = image.get_rect(center=pygame.mouse.get_pos())
            self.display_surface.blit(image, rect)
            
        self.player.selector.draw()

    def update(self, dt):
        if self.inventory.selected_tool: self.cur_tool = self.ui_assets["items"][self.inventory.selected_tool]
        elif self.inventory.selected_object: self.cur_tool = self.ui_assets["items"][self.inventory.selected_object]
        else: self.cur_tool = self.light_stop
        
        self.time_txt, self.time_outline = simple_outline(self.bag_font, self.world.dnc.str_time(), False, TEXT_DARK, TEXT_LIGHT)
        self.time_trect = self.time_txt.get_rect(midtop = self.emote_frame_rect.midbottom)
        self.dnc_rect.topleft = (self.emote_frame_rect.left+UI_OFFSET, self.emote_frame_rect.top+UI_OFFSET)
        
        self.coin_txt = self.amount_font.render(f"{self.inventory.coins}", ANTIALAS, TEXT_DARK)
        self.star_txt = self.amount_font.render(f"{self.inventory.stars}", ANTIALAS, TEXT_DARK)
        self.coin_trect = self.coin_txt.get_rect(midleft=self.coin_rect.midright)
        self.star_trect = self.star_txt.get_rect(midleft=self.star_rect.midright)
        
        self.bag.update(dt)
        self.tab.update(dt)

    def event(self, event):
        self.bag.event(event)
        self.tab.event(event)
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
            self.f1 = not self.f1

class TabUI:
    def __init__(self, ui):
        self.ui = ui
        self.ui_assets = ui.ui_assets
        self.display_surface = get_window()
        self.inventory = ui.inventory
        self.selector = self.ui.player.selector

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
        self.inv_len = len(TOOLS)
        center_i = int(self.inv_len/2)
        for i, thing_name in enumerate(TOOLS):
            offset_i = -(center_i-i) if i < center_i else i-center_i if i > center_i else 0
            start_offset = int(-frame_size//2)
            cur_offset = vector(start_offset, 0)
            end_offset = int(frame_size*offset_i-frame_size//2+UI_OFFSET*offset_i)
            self.offsets[thing_name] = {"cur":cur_offset, "open":end_offset, "close":start_offset}
            
        self.clicked = False

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
        if self.inventory.selected_object or not self.inventory.selected_tool:
            self.inventory.selected_object = ""
            self.inventory.selected_tool = TOOLS[0]
            return
        idx = TOOLS.index(self.inventory.selected_tool)
        idx += 1
        if idx >= len(TOOLS):
            idx = 0
        self.inventory.selected_tool = TOOLS[idx]

    def move_left(self):
        if not self.is_open: return
        if self.inventory.selected_object or not self.inventory.selected_tool:
            self.inventory.selected_object = ""
            self.inventory.selected_tool = TOOLS[0]
            return
        idx = TOOLS.index(self.inventory.selected_tool)
        idx -= 1
        if idx < 0:
            idx = len(TOOLS)-1
        self.inventory.selected_tool = TOOLS[idx]
        
    def tool_click(self, name):
        self.inventory.selected_tool = name
        self.inventory.selected_object = ""

    def draw(self):
        if not self.can_render: return

        for thing_name in self.inventory.tools:
            offset = self.offsets[thing_name]["cur"]
            frame_rect = self.frame_img.get_rect(topleft=self.center+offset)
            item_img = self.ui_assets["items"][thing_name]
            item_rect = item_img.get_rect(center=frame_rect.center)
            self.display_surface.blit(self.frame_img, frame_rect)
            self.display_surface.blit(item_img, item_rect)
            
            if frame_rect.collidepoint(pygame.mouse.get_pos()):
                self.selector.interact_rect = frame_rect
                self.selector.is_ui = True
                if not self.clicked and pygame.mouse.get_pressed()[0]:
                    self.clicked = True
                    self.tool_click(thing_name)
                    
            if not pygame.mouse.get_pressed()[0]:
                self.clicked = False

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
        self.selector = self.ui.player.selector

        self.bg_img = generate_menu(self.ui_assets["original-menu"], self.ui_assets["menu"].get_width(), self.ui_assets["menu"].get_height()*1.4)
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
    
        self.clicked = False

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
        
    def object_click(self, name, amount):
        if amount <= 0: return
        self.inventory.selected_object = name
        self.inventory.selected_tool = ""

    def draw(self):
        self.display_surface.blit(self.bg_img, self.bg_rect.topleft+self.offset)
        self.display_surface.blit(self.title_txt, self.title_trect.topleft+self.offset)
        
        object_tools = self.inventory.objects.copy()
        object_tools.update(self.inventory.items)

        y = self.title_trect.bottom+UI_OFFSET
        stage = "left"
        was_obj = False
        for item_name, item_amount in object_tools.items():
            
            is_obj = item_name in OBJECTS
            x = self.left_x if stage == "left" else self.right_x
            if not is_obj and was_obj:
                y += self.square_img.get_height()//3
                pygame.draw.line(self.display_surface, TEXT_DARK, 
                                 (self.left_x, y-self.square_img.get_height()//6+self.offset.y-UI_SCALE_B//2), 
                                 (self.right_x+self.square_img.get_width(), y-self.square_img.get_height()//6+self.offset.y-UI_SCALE_B//2), 
                                 int(UI_SCALE_B))
                
            square_rect = self.square_img.get_rect(topleft=(x,y))
            click_rect = square_rect.copy()
            click_rect.center += self.offset
            
            if is_obj:
                if click_rect.collidepoint(pygame.mouse.get_pos()):
                    self.selector.interact_rect = click_rect
                    self.selector.is_ui = True
                    if not self.clicked and pygame.mouse.get_pressed()[0]:
                        self.clicked = True
                        self.object_click(item_name, item_amount)
            if not pygame.mouse.get_pressed()[0]:
                self.clicked = False
            
            item_img = self.ui_assets["items-small"][item_name]
            amount_txt = self.ui.amount_font.render(f"x{item_amount}", ANTIALAS, TEXT_DARK)
            item_rect = item_img.get_rect(center = (square_rect.centerx-square_rect.w//4,square_rect.centery))
            amount_trect = amount_txt.get_rect(midleft = item_rect.midright)
            
            self.display_surface.blit(self.square_img, square_rect.topleft+self.offset)
            self.display_surface.blit(item_img, item_rect.topleft+self.offset)
            self.display_surface.blit(amount_txt, amount_trect.topleft+self.offset)
            
            if stage == "left": stage = "right"
            else: stage = "left"; y += square_rect.height+UI_OFFSET
            was_obj = is_obj

    def update(self, dt):
        self.offset.y = lerp(self.offset.y, self.dest_offset, dt*BAG_SPEED)
        
        if not self.is_open and self.ui.sign_rect.collidepoint(pygame.mouse.get_pos()):
            self.selector.interact_rect = self.ui.sign_rect
            self.selector.is_ui = True
