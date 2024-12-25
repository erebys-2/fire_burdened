import pygame
pygame.init()
import os

class StatusBars():
    def __init__(self):
        self.on = True
        scale = 1.2
        self.scale = scale

        placement_y = 480 - int(scale*32)
        
        #load bar template
        self.bar_length = 128 * scale
        self.bar_height = 8 * scale
        self.bar_disp = 32 * scale
        self.bar_ydisp2 = 20 * scale
        self.bar_ydisp1 = self.bar_ydisp2//5
        
        self.image = pygame.image.load('sprites/UI/statusbars/0.png')
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * scale), int(self.image.get_height() * scale)))
        
        self.image2 = pygame.image.load('sprites/UI/statusbars/1.png')
        self.image2 = pygame.transform.scale(self.image2, (int(self.image2.get_width() * scale), int(self.image2.get_height() * scale)))
        
        self.img3 = pygame.image.load('sprites/UI/melee_count/0.png')
        self.img4 = pygame.image.load('sprites/UI/melee_count/1.png')
        self.img5 = pygame.image.load('sprites/UI/melee_count/2.png')
        self.rect_list = []
        self.rect_list_states = [0,0,0,0]
        for i in range(4):
            self.rect_list.append(pygame.rect.Rect(40 + i*32, placement_y - 18, 16, 16))
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (0,placement_y)
        self.warning = False
        
        
        
    def draw_text(self, text, font, text_col, x, y, screen):
        img = font.render(text, True, text_col)
        screen.blit(img, (x, y))
        
    def draw2(self, screen, stat_list, key_values):
        
        for i in range(len(stat_list)):
            if stat_list[i] in key_values:
                self.rect_list_states[i] = 1
                screen.blit(self.img4, self.rect_list[i])
            else:
                self.rect_list_states[i] = 0
                screen.blit(self.img3, self.rect_list[i])
        
        if all(self.rect_list_states):
            for rect_ in self.rect_list:
                if pygame.time.get_ticks()%4 == 0:
                    screen.blit(self.img5, rect_)
        
    def draw(self, screen, stat_data, font):
        hp_color = (105,31,46)
        stam_color = (30,70,18)
        charge_color = (255,0,86)
        WHITE = (240,240,240)
        RED = (255,0,0)
        
        text_color = WHITE

        hp_ = self.bar_length * stat_data[0]
        stam_ = self.bar_length * stat_data[1]
        charge_ = self.bar_length * stat_data[2]
        hp_w = self.float_to_int(hp_)
        stam_w = self.float_to_int(stam_)
        charge_w = self.float_to_int(charge_)
        
        hp_rect = (self.rect.x + self.bar_disp, self.rect.y + self.bar_ydisp1, hp_w, self.bar_height)
        stam_rect = (self.rect.x + self.bar_disp, self.rect.y + self.bar_ydisp2, stam_w, self.bar_height)
        charge_rect = (self.rect.x + self.bar_disp, self.rect.y + self.bar_ydisp2, charge_w, self.bar_height)
        
        if self.on == True:
            pygame.draw.rect(screen, hp_color, hp_rect)
            if stat_data[2] > 0:
                if pygame.time.get_ticks()%2 == 0:
                    pygame.draw.rect(screen, charge_color, charge_rect)
            pygame.draw.rect(screen, stam_color, stam_rect)
            screen.blit(self.image, self.rect)
            
            if self.warning == True:
                screen.blit(self.image2, self.rect)
                text_color = RED
            
            self.draw_text(f'HP: {int(100*stat_data[0])}%/ ST: {int(100*stat_data[1])}%', 
                           font, text_color, self.rect.right + 12*self.scale, self.rect.y + 16*self.scale, screen)
            
    def float_to_int(self, B):
        if B - int(B) > 0.5:
            B = int(B) + 1
        else:
            B = int(B)
        return B