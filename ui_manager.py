from button import Button #type: ignore
from textManager import text_manager #type: ignore
from music_player import music_player #type: ignore
import os
import pygame
import csv

class ui_manager():
    
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, fontlist, ini_vol, fs_size):
        m_player_sfx_list_main = ['roblox_oof.wav', 'hat.wav']
        self.m_player = music_player(m_player_sfx_list_main, ini_vol)
        
        self.text_manager0 = text_manager()
        #self.ctrls_list = ['w','a','s','d','i','o','p','right alt']
        
        self.generic_img = pygame.image.load('sprites/generic_btn.png').convert_alpha()
        self.pause_img = pygame.image.load('sprites/pause_bg.png').convert_alpha()
        
        self.S_W = SCREEN_WIDTH
        self.S_H = SCREEN_HEIGHT
        
        self.std_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.fs_size = fs_size
        
        self.options_menu_enable = False
        self.ctrl_menu_enable = False
        self.vol_menu_enable = False
        self.saves_menu_enable = False
        
        self.trigger_once = True
        
        self.fontlist = fontlist
        self.button_list = []
        
        self.disp_flags = pygame.SHOWN

        self.stop = False
        self.btn_selected = 0
        
        self.disp_str_list = [
            ['','empty'],
            ['','empty'],
            ['','empty'],
            ['','empty'],
            ['','empty'],
            ['','empty'],
            ['','empty'],
            ['','empty']
        ]
        
        self.ctrls_list = [-1,-1,-1,-1,-1,-1,-1,-1]
        self.ctrls_updated = False
        self.run_game = True
        
        self.title_screen = pygame.image.load('sprites/title_screen.png').convert_alpha()
        self.ts_rect = self.title_screen.get_rect()
        self.ts_rect.center = (self.S_W//2, self.S_H//2 +32)
        
        self.vol_lvl = ini_vol
        self.lower_volume = False
        self.raise_volume = False
        
        
    def read_csv_data(self, data_name):
        temp_list = []
        with open(f'dynamic_CSVs/{data_name}.csv', newline= '') as csvfile:
            reader = csv.reader(csvfile, delimiter= ',') #what separates values = delimiter
            for row in reader:
                for entry in row:
                    temp_list.append(int(entry))
                    
        return temp_list
        
    def write_csv_data(self, data_name, data):
        with open(f'dynamic_CSVs/{data_name}.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter = ',')
            writer.writerow(data)

#-----------------------------------------------------------main menu----------------------------------------------------------
    def show_main_menu(self, screen):
        next_level = 0
        plot_index_list = [-1, -1]
        
        if not self.options_menu_enable and not self.saves_menu_enable and next_level == 0:
            if self.trigger_once:
                self.run_game = True
                self.button_list *= 0

                for i in range(4):
                    self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 +64 +36*i, self.generic_img, 1))
                self.trigger_once = False
                
            screen.blit(self.title_screen, self.ts_rect)
            
            if self.button_list[0].draw(screen):
                self.m_player.play_sound(self.m_player.sfx[1])
                self.trigger_once = True
                self.run_game = True
                #sets plot index list to 0
                plot_index_list = [-1,-1]
                next_level = 1
            self.button_list[0].show_text(screen, self.fontlist[1], ('','New Game'))
            
            if self.button_list[1].draw(screen):
                self.m_player.play_sound(self.m_player.sfx[1])
                self.saves_menu_enable = True
                self.trigger_once = True
            self.button_list[1].show_text(screen, self.fontlist[1], ('','Load File')) 
            
            if self.button_list[2].draw(screen):
                self.options_menu_enable = True
                self.m_player.play_sound(self.m_player.sfx[1])
                self.trigger_once = True
            self.button_list[2].show_text(screen, self.fontlist[1], ('','Options')) 
            
            if self.button_list[3].draw(screen):
                self.run_game = False
                self.m_player.play_sound(self.m_player.sfx[1])
            self.button_list[3].show_text(screen, self.fontlist[1], ('','Quit')) 
            
        elif self.options_menu_enable and not self.saves_menu_enable:
            self.show_options_menu(screen)
            
        elif not self.options_menu_enable and self.saves_menu_enable:
            print("load files not implemented yet")
            #will have to load the plot index list when a save is loaded
            plot_index_list = self.read_csv_data('plot_data')
            print(plot_index_list)
            
            self.saves_menu_enable = False
            
        return (next_level, self.run_game, plot_index_list)

#-----------------------------------------------------------pause menu---------------------------------------------------------
    def show_pause_menu(self, screen):
        pause_game = True
        exit_to_title = False
        
        #drawing pause text
        screen.blit(self.pause_img, (0,0))
        self.text_manager0.disp_text_box(screen, self.fontlist[2], ('','Game Paused'), (-1,-1,-1), (200,200,200), 
                                         (188, self.S_H//2 - 96,self.S_W,self.S_H), False, False, 'none')
        
        #3 buttons just like the start menu
        #possibly an inventory button too
        
        if not self.options_menu_enable:
            if self.trigger_once:
                self.button_list *= 0
                for i in range(3):
                    self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 +48*i, self.generic_img, 1))
                
                self.trigger_once = False

            if self.button_list[0].draw(screen):
                pause_game = False
                self.m_player.play_sound(self.m_player.sfx[1])
                self.trigger_once = True
                pygame.mixer.unpause()
            self.button_list[0].show_text(screen, self.fontlist[1], ('','Resume (ENT)')) 
                
            if self.button_list[1].draw(screen):
                self.options_menu_enable = True
                self.m_player.play_sound(self.m_player.sfx[1])
                self.trigger_once = True
            self.button_list[1].show_text(screen, self.fontlist[1], ('','Options')) 
                
            if self.button_list[2].draw(screen):
                exit_to_title = True
                pause_game = False
                self.trigger_once = True  
                pygame.mixer.unpause()
                pygame.mixer.stop()
                self.m_player.play_sound(self.m_player.sfx[1])
            self.button_list[2].show_text(screen, self.fontlist[1], ('','Title (ESC)'))  
            
        else:
            #trigger options menu
            self.show_options_menu(screen)
                
        return (pause_game, exit_to_title)
    
    
#-----------------------------------------------------------Options sub menu-----------------------------------------------------------    
    def show_options_menu(self, screen):
        pygame.draw.rect(screen, (0,0,0), (0,0,self.S_W,self.S_H))
        
        if not self.ctrl_menu_enable and not self.vol_menu_enable:
            if self.trigger_once:
                self.button_list *= 0
                for i in range(4):
                    self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 -48 +48*i, self.generic_img, 1))
                
                self.trigger_once = False
                
            if self.button_list[0].draw(screen):
                self.ctrl_menu_enable = True
                self.m_player.play_sound(self.m_player.sfx[1])
                self.trigger_once = True
            self.button_list[0].show_text(screen, self.fontlist[1], ('','Controls')) 
                
            if self.button_list[1].draw(screen):
                self.vol_menu_enable = True
                self.m_player.play_sound(self.m_player.sfx[1])
                self.trigger_once = True
            self.button_list[1].show_text(screen, self.fontlist[1], ('','Volume')) 
            
            if self.button_list[2].draw(screen):
                self.m_player.play_sound(self.m_player.sfx[1])
                if self.disp_flags == pygame.SHOWN: #windowed mode
                    self.disp_flags = pygame.DOUBLEBUF|pygame.FULLSCREEN|pygame.SHOWN #full screen mode
                    screen = pygame.display.set_mode(self.std_size, self.disp_flags)
                elif self.disp_flags == pygame.DOUBLEBUF|pygame.FULLSCREEN|pygame.SHOWN:
                    self.disp_flags = pygame.SHOWN
                    screen = pygame.display.set_mode(self.std_size, self.disp_flags)
            self.button_list[2].show_text(screen, self.fontlist[1], ('','Screen Toggle')) 
                
            if self.button_list[3].draw(screen):
                self.options_menu_enable = False
                self.m_player.play_sound(self.m_player.sfx[1])
                self.trigger_once = True
            self.button_list[3].show_text(screen, self.fontlist[1], ('','Back'))  
            
        elif self.ctrl_menu_enable and not self.vol_menu_enable:
            self.show_ctrl_menu(screen)
            
        else:
            self.show_vol_menu(screen)
            
#---------------------------------------------------------Controls sub menu---------------------------                
    def show_ctrl_menu(self, screen):
        if self.trigger_once:
            self.stop = False
            self.button_list *= 0
            
            #load current control scheme from csv file into ctrls_list
            self.ctrls_list = self.read_csv_data('ctrls_data')
            #set up disp_str_list
            for i in range(len(self.disp_str_list)):
                self.disp_str_list[i][1] = pygame.key.name(self.ctrls_list[i])
            #load buttons
            for i in range(8):
                self.button_list.append(Button(self.S_W//2 -128, self.S_H//2 -160 + 32*i, self.generic_img, 1))
                
            self.button_list.append(Button(self.S_W//2 -144, self.S_H /2 +144, self.generic_img, 1))
            self.button_list.append(Button(self.S_W//2 + 16, self.S_H /2 +144, self.generic_img, 1))
            
            for i in range(8): #done for formatting (these are dummy buttons)
                self.button_list.append(Button(self.S_W//2 -0, self.S_H//2 -160 + 32*i, self.generic_img, 1))
            
            self.trigger_once = False
        
        
        self.text_manager0.disp_text_box(screen, self.fontlist[1], ('','Click a button to re-map then press the desired key'), (-1,-1,-1), (200,200,200), 
                                         (112, self.S_H//2 - 216,self.S_W,self.S_H), False, False, 'none')
        self.text_manager0.disp_text_box(screen, self.fontlist[1], ('','UI buttons ESCAPE and ENTER cannot be re-mapped'), (-1,-1,-1), (200,200,200), 
                                         (128, self.S_H//2 + 96,self.S_W,self.S_H), False, False, 'none')
        
        ctrls_btn_dict = {
            0:('','Jump'),
            1:('','Left'),
            2:('','Roll'),
            3:('','Right'),
            4:('','Melee'),
            5:('','Shoot'),
            6:('','Special'),
            7:('','Sprint'),
        }
        
        
        for i in range(8):
            if self.button_list[i].draw(screen):
                self.m_player.play_sound(self.m_player.sfx[1])
                self.btn_selected = i
                
            self.button_list[i].show_text(screen, self.fontlist[1], ctrls_btn_dict[i])
            self.button_list[i+10].show_text(screen, self.fontlist[1], self.disp_str_list[i])
                
        #pressing default button
        if self.button_list[8].draw(screen):
            self.m_player.play_sound(self.m_player.sfx[1])
            self.ctrls_list = [119, 97, 115, 100, 105, 111, 112, 1073742054]
            for i in range(len(self.disp_str_list)):
                self.disp_str_list[i][1] = pygame.key.name(self.ctrls_list[i])
        self.button_list[8].show_text(screen, self.fontlist[1], ('','Default'))  
        
        #pressing save button
        if self.button_list[9].draw(screen):
            self.ctrl_menu_enable = False
            self.m_player.play_sound(self.m_player.sfx[1])
            self.trigger_once = True  
            self.ctrls_updated = True
            #print(self.ctrls_list)
            self.write_csv_data('ctrls_data', self.ctrls_list)
        self.button_list[9].show_text(screen, self.fontlist[1], ('','Save'))  
        
        if not self.stop:
            for event in pygame.event.get():
                if(event.type == pygame.KEYDOWN):
                    if event.key != pygame.K_ESCAPE and event.key != pygame.K_RETURN:
                        self.disp_str_list[self.btn_selected][1] = pygame.key.name(event.key)
                        self.ctrls_list[self.btn_selected] = event.key
                    
                if(event.type == pygame.QUIT):
                    self.stop = True
                    
#------------------------------------------------------Volume sub menu-------------------------------
        
    def show_vol_menu(self, screen):
        #kinda cursed rn, need to code a slider eventually
        self.vol_lvl = self.read_csv_data('vol_data')
        string = f'    {10*self.vol_lvl[0]}%'
        self.text_manager0.disp_text_box(screen, self.fontlist[1], ('','Volume Level', string), (-1,-1,-1), (200,200,200), 
                                    (272, self.S_H//2 - 64,self.S_W,self.S_H), False, False, 'none')

        if self.trigger_once:
            self.button_list *= 0
            for i in range(3):
                self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 +48*i, self.generic_img, 1))
                
            self.trigger_once = False

        if self.button_list[0].draw(screen):
            
            if self.vol_lvl[0] < 10:
                self.vol_lvl[0] += 1
            
            self.raise_volume = True
            self.write_csv_data('vol_data', self.vol_lvl)
            self.m_player.set_vol_all_sounds(self.vol_lvl)
            self.m_player.play_sound(self.m_player.sfx[1])
        else:
            self.raise_volume = False
        self.button_list[0].show_text(screen, self.fontlist[1], ('','Louder')) 
            
        if self.button_list[1].draw(screen):
            
            if self.vol_lvl[0] > 0:
                self.vol_lvl[0] -= 1
                
            self.lower_volume = True
            self.write_csv_data('vol_data', self.vol_lvl)
            self.m_player.set_vol_all_sounds(self.vol_lvl)
            self.m_player.play_sound(self.m_player.sfx[1])
        else:
            self.lower_volume = False
        self.button_list[1].show_text(screen, self.fontlist[1], ('','Quieter')) 
            
        if self.button_list[2].draw(screen):
            self.vol_menu_enable = False
            self.m_player.play_sound(self.m_player.sfx[1])
            self.trigger_once = True
        self.button_list[2].show_text(screen, self.fontlist[1], ('','Back'))  
        
#-------------------------------------------Death Menu---------------------------------------------

    def show_death_menu(self, screen):
        exit_to_title = False
        
        #drawing pause text
        screen.blit(self.pause_img, (0,0))
        self.text_manager0.disp_text_box(screen, self.fontlist[1], ('','You Died'), (-1,-1,-1), (200,200,200), 
                                         (288, self.S_H//2 - 32,self.S_W,self.S_H), False, False, 'none')
        
        if self.trigger_once:
            self.run_game = True
            self.button_list *= 0

            for i in range(2):
                self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 +32 +36*i, self.generic_img, 1))
            self.trigger_once = False

        if not self.saves_menu_enable:
            if self.button_list[0].draw(screen):
                self.m_player.play_sound(self.m_player.sfx[1])
                self.saves_menu_enable = True
                self.trigger_once = True
            self.button_list[0].show_text(screen, self.fontlist[1], ('','Last Save')) 
            
            if self.button_list[1].draw(screen):
                exit_to_title = True
                self.trigger_once = True  
                pygame.mixer.stop()
                self.m_player.play_sound(self.m_player.sfx[1])
            self.button_list[1].show_text(screen, self.fontlist[1], ('','Title (ESC)'))  
        
        elif self.saves_menu_enable:
            print("load files not implemented yet")
            self.saves_menu_enable = False
        
        return exit_to_title