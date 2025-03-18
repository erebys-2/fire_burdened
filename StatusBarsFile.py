import pygame
pygame.init()
import os

class StatusBars():
    def __init__(self, screen_w, screen_h, tile_size):
        self.on = True
        scale = 1.2
        self.scale = scale
        self.SC_WIDTH = screen_w
        self.HALF_SC_WIDTH = screen_w//2
        self.SC_HEIGHT = screen_h
        self.t_size = tile_size

        placement_y = 480 - int(scale*self.t_size)
        
        #load assets
        self.bar_length = 128 * scale
        self.bar_height = 8 * scale
        self.bar_disp = 32 * scale
        self.bar_ydisp2 = 20 * scale
        self.bar_ydisp1 = self.bar_ydisp2//5
        
        self.image = pygame.image.load('sprites/UI/statusbars/0.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * scale), int(self.image.get_height() * scale)))
        
        self.image2 = pygame.image.load('sprites/UI/statusbars/1.png').convert_alpha()
        self.image2 = pygame.transform.scale(self.image2, (int(self.image2.get_width() * scale), int(self.image2.get_height() * scale)))
        
        self.img3 = pygame.image.load('sprites/UI/melee_count/0.png').convert_alpha()
        self.img4 = pygame.image.load('sprites/UI/melee_count/1.png').convert_alpha()
        self.img5 = pygame.image.load('sprites/UI/melee_count/2.png').convert_alpha()
        self.rect_list = []
        
        self.status_icon_imglist = []
        self.status_enable_dict = {}
        path_ = 'sprites/UI/status_icons'
        for i in range(len(os.listdir(path_))):
            self.status_icon_imglist.append(pygame.image.load(os.path.join(path_+f'/{i}.png')).convert_alpha())
            self.status_enable_dict[i] = False
        self.status_fx_list = []
        
        self.direction_img_list = []
        path_ = 'sprites/UI/directions'
        for i in range(len(os.listdir(path_))):
            self.direction_img_list.append(pygame.image.load(os.path.join(path_+f'/{i}.png')).convert_alpha())
        
        for i in range(4):
            self.rect_list.append(pygame.rect.Rect(40 + i*32, placement_y - 18, 16, 16))
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (0,placement_y)
        self.warning = False
        self.very_charred = False
        self.is_exhausted = False
        self.color = (0,0,0)
       
    def draw_tutorial_cues(self, screen, player, enemies_nearby, ctrls_list, font):
        txt = ''
        x_disp = 0
        if self.is_exhausted:
            txt = f'[{pygame.key.name(ctrls_list[0])}] or [{pygame.key.name(ctrls_list[2])}]'
            x_disp = player.direction*4 - player.rect.width//2
            if player.action in (1,0):
                countdown = str(len(player.frame_list[player.action]) - player.frame_index)
                self.draw_text(f'({countdown})', 
                         font, (255,255,255), self.rect.right + 48*self.scale, self.rect.y - 15*self.scale, screen)
                
        elif not self.is_exhausted and enemies_nearby:
            txt = f'[{pygame.key.name(ctrls_list[4])}] or [{pygame.key.name(ctrls_list[2])}]'
            x_disp = player.direction*4 - player.rect.width//2
            
        if txt != '':
            self.draw_text(txt, font, (255,255,255), player.rect.centerx + x_disp, player.rect.y - 32, screen)
            
        #should make a txt file for ini player config values
        if abs(player.vel_y) > 2:
            p_jump_val = 10
            numerator = player.vel_y
            
            if player.vel_y > p_jump_val:
                numerator = p_jump_val
            elif player.vel_y < -p_jump_val:
                numerator= -p_jump_val
                
            vel_y_ratio = numerator/p_jump_val
   

            if vel_y_ratio < 0:
                index = 1
                # if player.atk1:
                #     index = 3
            else:
                index = 0
                # if player.atk1:
                #     index = 2
                    
            screen.blit(self.direction_img_list[index],#pygame.transform.hsl(self.direction_img_list[index], 0, vel_y_ratio, 1-abs(vel_y_ratio)), 
                        (player.rect.centerx - self.t_size//2,# - player.direction*self.t_size, 
                         player.rect.y - self.t_size)
                         #player.rect.y + self.t_size//4)
                        )
            
    
    
    def update_status_list(self, conditions_met, fx_id):
        check_active = fx_id in self.status_fx_list
        if conditions_met and not check_active:
            self.status_fx_list.append(fx_id)
        elif not conditions_met and check_active:
            self.status_fx_list.pop(self.status_fx_list.index(fx_id))
        
    def draw_status_icons(self, screen, player, font):#NOT independent from other draw functions
        
        #set conditions met
        self.status_enable_dict[0] = (player.vel_y > 1 and player.action == 1 and player.coyote_ratio > 0)
        self.status_enable_dict[1] = self.color == (140,130,80)
        self.status_enable_dict[2] = self.is_exhausted
        self.status_enable_dict[3] = self.very_charred

        #update status fx list
        for status in self.status_enable_dict:
            self.update_status_list(self.status_enable_dict[status], status)
            
        #draw
        #0+self.t_size*i%3, 2+self.t_size*i//3
        num_fx = len(self.status_fx_list)
        for i in range(num_fx):
            if num_fx != 0:
                screen.blit(self.status_icon_imglist[self.status_fx_list[i]], (self.HALF_SC_WIDTH+self.t_size*i, self.SC_HEIGHT-self.t_size))
                
                if self.status_fx_list[i] == 0:
                    num = int(255*(1-player.coyote_ratio))
                    pygame.draw.rect(screen, (num,num,num), 
                                    pygame.rect.Rect(self.HALF_SC_WIDTH+self.t_size*i,
                                                    self.SC_HEIGHT-self.t_size, 
                                                    self.t_size*(1-player.coyote_ratio), 
                                                    2)
                                    )
        
    def draw_text(self, text, font, text_col, x, y, screen):
        screen.blit(font.render(text, True, text_col), (x, y))
        
    def draw2(self, screen, stat_list, key_values, font):
        rect_list_bitstr = ''#set default values
        len_ = len(stat_list)
        atk_ct = 0
        
        for i in range(len_):#convert action history to binary string
            rect_list_bitstr = str(int(stat_list[len_-1-i] in key_values)) + rect_list_bitstr
            screen.blit(self.img4, self.rect_list[i])#draw pink
        #key = int(rect_list_bitstr, 2)#convert binary string to int
        for j in range(len_):#checks if the key can be masked to 1, 11, 111, 1111, etc
            bit_mask = 2**(j+1) - 1
            if int(rect_list_bitstr, 2) & bit_mask == bit_mask:
                atk_ct = j+1
                #consecutive_atk = bit_mask != 1
        
        self.is_exhausted = atk_ct == len_
        for rect_ in self.rect_list[0:atk_ct]:
            screen.blit(self.img3, rect_)#draw black
            if self.is_exhausted:
                self.draw_text(f'EXHAUSTED', 
                         font, (255,255,255), self.rect.right - 22*self.scale, self.rect.y - 15*self.scale, screen)
                if pygame.time.get_ticks()%4 == 0:
                    screen.blit(self.img5, rect_)#draw white
            
        
    def draw(self, screen, stat_data, player_action, key_values, font, flicker):
        hp_color = (105,31,46)
        #hp_color2 = (55,20,45)
        hp_color2 = (140,130,80)
        stam_color = (0,80,28)
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
            if self.very_charred:
                if pygame.time.get_ticks()%10 == 0:
                    self.color = (255,255,255)
                else:
                    self.color = (255,0,86)
            else:
                self.color = hp_color
                
            if player_action in key_values:
                self.color = hp_color2
                
            pygame.draw.rect(screen, self.color, hp_rect)
            if stat_data[2] > 0:
                if pygame.time.get_ticks()%2 == 0:
                    pygame.draw.rect(screen, charge_color, charge_rect)
            if not flicker:
                pygame.draw.rect(screen, stam_color, stam_rect)
            else:
                pygame.draw.rect(screen, (255,255,255), stam_rect)
            screen.blit(self.image, self.rect)
            
            if self.warning == True:
                screen.blit(self.image2, self.rect)
                text_color = RED
            
            self.draw_text(f'HP: {int(100*stat_data[0])}%/ ST: {int(100*stat_data[1])}%', 
                           font, text_color, self.rect.right + 12*self.scale, self.rect.y + 16*self.scale, screen)
            
            if self.very_charred:
                self.draw_text(f'HEAVILY CHARRED', 
                           font, text_color, self.rect.x + 1.2*self.bar_disp, self.rect.y + 0.5*self.bar_ydisp1, screen)
            
    def float_to_int(self, B):
        if B - int(B) > 0.5:
            B = int(B) + 1
        else:
            B = int(B)
        return B
    
