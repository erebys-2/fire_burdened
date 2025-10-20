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
        
        ui_path = os.path.join('assets', 'sprites', 'UI')
        self.image = pygame.image.load(os.path.join(ui_path, 'statusbars', '0.png')).convert_alpha()#'assets/sprites/UI/statusbars/0.png'
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * scale), int(self.image.get_height() * scale)))
        
        self.image2 = pygame.image.load(os.path.join(ui_path, 'statusbars', '1.png')).convert_alpha()
        self.image2 = pygame.transform.scale(self.image2, (int(self.image2.get_width() * scale), int(self.image2.get_height() * scale)))
        
        self.img3 = pygame.image.load(os.path.join(ui_path, 'melee_count', '0.png')).convert_alpha()
        self.img4 = pygame.image.load(os.path.join(ui_path, 'melee_count', '1.png')).convert_alpha()
        self.img4_1 = pygame.transform.scale(self.img4, (int(self.img4.get_width() * scale**3), int(self.img4.get_height() * scale**3)))
        self.img5 = pygame.image.load(os.path.join(ui_path, 'melee_count', '2.png')).convert_alpha()
        self.rect_list = []
        self.rect_list2 = []
        
        self.status_icon_imglist = []
        self.status_enable_list = []
        path_ = 'assets/sprites/UI/status_icons'
        for i in range(len(os.listdir(path_))):
            self.status_icon_imglist.append(pygame.image.load(os.path.join(path_+f'/{i}.png')).convert_alpha())
            self.status_enable_list.append(False)

        self.arrow_y_disp = -999
        self.direction_img_list = []
        path_ = 'assets/sprites/UI/directions'
        for i in range(len(os.listdir(path_))):
            arrow_img = pygame.image.load(os.path.join(path_+f'/{i}.png')).convert_alpha()
            self.direction_img_list.append(pygame.transform.scale(arrow_img, (int(arrow_img.get_width() * scale), int(arrow_img.get_height() * scale))))
        
        for i in range(4):
            self.rect_list.append(pygame.rect.Rect(40 + i*32, placement_y - 18, 16, 16))
            self.rect_list2.append(pygame.rect.Rect(36 + i*32, placement_y - 18*scale, 16, 16))
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (0,placement_y)
        self.warning = False
        self.very_charred = False
        self.is_exhausted = False
        self.color = (0,0,0)
        self.full_recover = True
        self.full_recover_time = pygame.time.get_ticks()
        
       
    def draw_tutorial_cues(self, screen, player, enemies_nearby, p_int_nearby, controller_en, ctrls_list, font):
        #draw player action cues
        txt = ''
        x_disp = 0
        if self.is_exhausted:#draw exhaustion action cues
            if not controller_en:
                txt = f'[{pygame.key.name(ctrls_list[0])}] or [{pygame.key.name(ctrls_list[2])}]'
                x_disp = player.direction*3 - player.rect.width*0.6
            else:
                txt = '[Jump] or [Roll]'
                x_disp = player.direction*3 - player.rect.width*0.75
            
                
        elif not self.is_exhausted and enemies_nearby:#draw attack/ evade cues
            if not controller_en:
                txt = f'[{pygame.key.name(ctrls_list[4])}] or [{pygame.key.name(ctrls_list[2])}]'
                x_disp = player.direction*3 - player.rect.width*0.6
            else:
                txt = '[Melee] or [Roll]'
                x_disp = player.direction*3 - player.rect.width*0.75
                
        elif p_int_nearby:
            if not controller_en:
                txt = f'[{pygame.key.name(ctrls_list[2])}] >> [{pygame.key.name(ctrls_list[4])}]'
                x_disp = player.direction*3 - player.rect.width*0.6
            else:
                txt = '[Roll] >> [Melee]'
                x_disp = player.direction*3 - player.rect.width*0.75
            
        if txt != '':
            self.draw_text(txt, font, (255,255,255), player.rect.centerx + x_disp, player.rect.y - 32, screen)
            
        #should make a txt file for ini player config values
        #draw arrows for player vertical direction
        #no longer relevant
        # if abs(player.vel_y) > 1.5:
        #     p_jump_val = 10
            
        #     numerator = player.vel_y#get numerator
        #     if abs(player.vel_y) > p_jump_val:#set bounds 
        #         numerator = (abs(player.vel_y)/player.vel_y)*p_jump_val
                
        #     vel_y_ratio = numerator/p_jump_val

        #     index = 0#set img index
        #     if vel_y_ratio < 0 or (player.in_air and player.hold_jump and player.vel_y < 0.5):
        #         index = 1
            
        #     if self.arrow_y_disp != player.rect.y:#set y disp
        #         self.arrow_y_disp += 0.85*p_jump_val*vel_y_ratio
                
        #     screen.blit(self.direction_img_list[index],#pygame.transform.hsl(self.direction_img_list[index], 0, vel_y_ratio, 1-abs(vel_y_ratio)), 
        #                 (player.rect.centerx - self.scale*(self.t_size//2),# - player.direction*self.t_size, 
        #                  self.arrow_y_disp - self.t_size*self.scale)#player.rect.y + self.t_size//4)
        #                 )
        # else:
        #     self.arrow_y_disp = player.rect.y
            
        
    def draw_status_icons(self, screen, player, font):#NOT independent from other draw functions
        #draw exhaustion count down
        if self.is_exhausted:
            countdown = str(player.recovery_counter)
            self.draw_text(f'({countdown})', 
                        font, (255,255,255), self.rect.right + 48*self.scale, self.rect.y - 15*self.scale, screen)
        
        #set conditions met
        self.status_enable_list[0] = (player.vel_y > 1 and player.action == 1 and player.coyote_ratio > 0)
        self.status_enable_list[1] = self.color == (140,130,80)
        self.status_enable_list[2] = self.is_exhausted
        self.status_enable_list[3] = self.very_charred

        #update status fx list, list of ints that are fx id's
        active_status_fx_list = [fx_status[0] for fx_status in enumerate(self.status_enable_list) if fx_status[1]] #list comprehension !...
            
        #draw
        # for i in range(len(active_status_fx_list)):
        #     screen.blit(self.status_icon_imglist[active_status_fx_list[i]], (self.HALF_SC_WIDTH+self.t_size*i, self.SC_HEIGHT-self.t_size))
            
        #     if active_status_fx_list[i] == 0:
        #         num = int(255*(1-player.coyote_ratio))
        #         pygame.draw.rect(screen, (num,num,num), 
        #                         pygame.rect.Rect(self.HALF_SC_WIDTH+self.t_size*i,
        #                                         self.SC_HEIGHT-self.t_size, 
        #                                         self.t_size*(1-player.coyote_ratio), 
        #                                         2)
        #                         )
    
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

                self.full_recover = False
                self.full_recover_time = pygame.time.get_ticks()
                #consecutive_atk = bit_mask != 1
        
        self.is_exhausted = atk_ct == len_
        for rect_ in self.rect_list[:atk_ct]:
            screen.blit(self.img3, rect_)#draw black
            if self.is_exhausted:
                self.draw_text(f'EXHAUSTED', 
                         font, (255,255,255), self.rect.right - 22*self.scale, self.rect.y - 15*self.scale, screen)
                if pygame.time.get_ticks()%4 == 0:
                    screen.blit(self.img5, rect_)#draw white
                    
        if atk_ct == 0 and not self.full_recover:
            if pygame.time.get_ticks() > self.full_recover_time + 120:
                self.full_recover = True
            for i in range(len_):
                screen.blit(self.img4_1, self.rect_list2[i])
            # self.draw_text(f'ATK READY', 
            #             font, (255,255,255), self.rect.right - 22*self.scale, self.rect.y - 15*self.scale, screen)
        
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
    
