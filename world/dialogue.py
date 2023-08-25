from settings import *
from support import get_window, main_font, lerp

class Dialogue:
    def __init__(self, world):
        self.world = world
        self.assets = world.assets
        self.player = world.player
        self.inventory = self.player.inventory
        self.display_surface = get_window()
        self.ui_assets = self.assets["ui"]
        # fonts
        self.name_font = main_font(18)
        self.dialogue_font = main_font(10)
        self.amount_font = main_font(16)
        # images
        self.dialogue_bg = self.ui_assets["dialogue"]["full-big"]
        self.dialogue_rect = self.dialogue_bg.get_rect(topleft=(UI_OFFSET,HEIGHT))
        self.trade_bg = pygame.transform.scale_by(self.ui_assets["menu"], 1.5)
        self.trade_rect = self.trade_bg.get_rect(topleft=(UI_OFFSET,HEIGHT))
        self.double_arrow_img = self.ui_assets["double-arrow"]
        # offsets
        self.offset = vector(0,0)
        self.closed_offset = 0
        self.dest_offset = self.closed_offset
        self.trade_open_offset = -self.trade_rect.h-UI_OFFSET
        self.dialogue_open_offset = -self.dialogue_rect.h-UI_OFFSET
        # data
        self.can_render = self.do_trade = self.active = False
        self.pfp = self.name = self.data = None

    def start(self, pfp, name, data):
        self.active= self.can_render = True
        self.pfp, self.name, self.data = pfp, name, data
        self.build()

    def build(self):
        self.do_trade = self.data["trade"]
        self.dest_offset = self.trade_open_offset if self.do_trade else self.dialogue_open_offset
        self.name_txt = self.name_font.render(f"{self.name}", ANTIALAS, TEXT_DARK)
        # TRADE
        if self.do_trade:
            self.name_trect = self.name_txt.get_rect(midtop=(self.trade_rect.centerx,self.trade_rect.top+UI_OFFSET))
            self.trade_btns, self.double_arrows = [],[]

            y = self.name_trect.bottom+UI_OFFSET*2
            for item_name, item_amount, price in self.data["trades"]:
                left_btn = DialogueTradeButton(self.ui_assets, item_amount, False, item_name, self.amount_font)
                right_btn = DialogueTradeButton(self.ui_assets, price, True, None, self.amount_font)

                left_btn.bg_rect = left_btn.bg.get_rect(topright=(self.trade_rect.centerx-UI_OFFSET*4, y))
                right_btn.bg_rect = right_btn.bg.get_rect(topleft=(self.trade_rect.centerx+UI_OFFSET*4, y))
                
                left_btn.finish(right_btn,  self.trade_open_offset); right_btn.finish(left_btn,  self.trade_open_offset)
                self.trade_btns.append(left_btn); self.trade_btns.append(right_btn)

                y += left_btn.bg_rect.h + UI_OFFSET
                self.double_arrows.append([self.double_arrow_img, self.double_arrow_img.get_rect(center=(self.trade_rect.centerx, left_btn.bg_rect.centery))])
        
        # DIALOGUE
        else:
            self.pfp_rect = self.pfp.get_rect(center=(self.dialogue_rect.left+self.dialogue_rect.h//2, self.dialogue_rect.centery))
            self.name_trect = self.name_txt.get_rect(topleft=(self.dialogue_rect.left+self.dialogue_rect.h+UI_OFFSET,self.dialogue_rect.top+UI_OFFSET))
            self.dialogue_text = self.data["dialogue"]
            self.dialogue_chars = len(self.dialogue_text)
            self.char_idx = 0

    def quit(self):
        self.active = False
        self.dest_offset = self.closed_offset

    def update(self, dt):
        self.offset.y = lerp(self.offset.y, self.dest_offset, dt*DIALOGUE_SPEED)
        if not self.active and abs(self.dest_offset-self.offset.y) <= 1: self.can_render = False
        if not self.active: return

        if not self.do_trade:
            self.char_idx += dt*TEXT_SPEED
            if self.char_idx >= self.dialogue_chars: self.char_idx = self.dialogue_chars
            cut_text = self.dialogue_text[0:int(self.char_idx)]
            self.speech_txt = self.dialogue_font.render(f"{cut_text}", ANTIALAS, TEXT_DARK)
            self.speech_trect = self.speech_txt.get_rect(midleft=(self.dialogue_rect.left+self.dialogue_rect.h+UI_OFFSET*2, self.dialogue_rect.top+self.dialogue_rect.h//2+UI_OFFSET))
        else:
            for btn in self.trade_btns: btn.update(self.player.selector)

    def draw(self):
        if not self.can_render: return
        if self.do_trade:
            self.display_surface.blit(self.trade_bg, self.trade_rect.topleft+self.offset)
            for btn in self.trade_btns: btn.draw(self.display_surface, self.offset)
            for img, rect in self.double_arrows: self.display_surface.blit(img, rect.topleft+self.offset)
        else:
            self.display_surface.blit(self.dialogue_bg, self.dialogue_rect.topleft+self.offset)
            self.display_surface.blit(self.pfp, self.pfp_rect.topleft+self.offset)
            self.display_surface.blit(self.speech_txt, self.speech_trect.topleft+self.offset)
        self.display_surface.blit(self.name_txt, self.name_trect.topleft+self.offset)

    def trade_clicked(self, btn):
        if btn.is_coin:
            item_name, amount = btn.side_btn.item_name, btn.side_btn.amount
            if self.inventory.has_thing(item_name, amount):
                self.inventory.add_money(btn.amount)
                self.inventory.remove_thing(item_name, amount)
        else:
            price = btn.side_btn.amount
            if self.inventory.has_money(price):
                self.inventory.add_thing(btn.item_name, btn.amount)
                self.inventory.remove_money(price)

    def event(self, event):
        if not self.active: return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self.quit()
        if self.do_trade:
            for btn in self.trade_btns:
                clicked = btn.event(event)
                if clicked: self.trade_clicked(btn)

class DialogueTradeButton:
    def __init__(self, ui_assets, amount, is_coin, item_name, font):
        self.bg = ui_assets["btn"]
        self.ui_assets, self.amount, self.is_coin, self.item_name, self.font = ui_assets, amount, is_coin, item_name, font
        self.bg_rect: pygame.Rect = None

    def finish(self, side_btn, open_offset):
        self.side_btn = side_btn
        if self.is_coin: self.item_img = pygame.transform.scale_by(self.ui_assets["icons"]["special"][13],0.8)
        else: self.item_img = self.ui_assets["items-small"][self.item_name]
        self.item_rect = self.item_img.get_rect(midleft=(self.bg_rect.left+UI_OFFSET_H, self.bg_rect.centery))
        self.amount_txt = self.font.render(f"x{self.amount}", ANTIALAS, TEXT_DARK)
        self.amount_trect = self.amount_txt.get_rect(midleft=self.item_rect.midright)
        self.click_rect = self.bg_rect.copy()
        self.click_rect.y += open_offset

    def event(self, event):
        if self.hovering:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: return True
        return False
    
    def update(self, selector):
        self.hovering = self.click_rect.collidepoint(pygame.mouse.get_pos())
        if self.hovering:
            selector.interact_rect = self.click_rect
            selector.is_ui = True

    def draw(self, display_surface, offset):
        display_surface.blit(self.bg,self.bg_rect.topleft+offset)
        display_surface.blit(self.item_img, self.item_rect.topleft+offset)
        display_surface.blit(self.amount_txt, self.amount_trect.topleft+offset)