from button import Button #type: ignore
from textManager import text_manager #type: ignore
from music_player import music_player #type: ignore
from textfile_handler import textfile_formatter
from saveHandler import save_file_handler
import os
import pygame
import csv

class ui_manager(): #Helper class for displaying and operating non-game UI (menus and sub menus)
    
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, fontlist, ini_vol, fs_size):
        m_player_sfx_list_main = ['roblox_oof.wav', 'hat.wav']
        self.m_player = music_player(m_player_sfx_list_main, ini_vol)
        self.t1 = textfile_formatter()
        self.text_manager0 = text_manager()
        self.save_handler = save_file_handler()
        
        self.generic_img = pygame.image.load('sprites/generic_btn.png').convert_alpha()
        self.invisible_img = pygame.image.load('sprites/invisible_btn.png').convert_alpha()
        self.pause_img = pygame.image.load('sprites/pause_bg.png').convert_alpha()
        
        self.S_W = SCREEN_WIDTH
        self.S_H = SCREEN_HEIGHT
        
        self.std_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.fs_size = fs_size
        
        self.options_menu_enable = False
        self.ctrl_menu_enable = False
        self.vol_menu_enable = False
        self.saves_menu_enable = False
        self.saves_menu2_enable = False
        
        self.trigger_once = True
        
        self.fontlist = fontlist
        self.button_list = []
        
        self.disp_flags = pygame.DOUBLEBUF|pygame.SHOWN

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
            ['','empty'],
            ['','empty'],
            ['','empty']
        ]
        
        self.ctrls_list = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
        self.ctrls_updated = False
        self.run_game = True
        
        self.title_screen = pygame.image.load('sprites/title_screen.png').convert_alpha()
        self.ts_rect = self.title_screen.get_rect()
        self.ts_rect.center = (self.S_W//2, self.S_H//2 +32)
        
        self.vol_lvl = ini_vol
        self.lower_volume = False
        self.raise_volume = False
        
        self.set_player_location = False
        self.player_new_coords = (32, 128)
        
        self.set_player_inv = False
        self.player_new_inv = [
            ['a', 1],
            ['b', 1],
            ['c', 1],
            ['d', 1],
            ['e', 1],
            ['f', 1],
            ['g', 1],
            ['h', 1],
            ['i', 1],
            ['a', 1]
        ]
        
        #filler value, selected slot will always be set by clicking a slot before loading a game
        self.selected_slot = -1
        
        self.controller_connected = False
        
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
            
#this is essentially methods calling other methods
#menus are methods and they're drawn by the impulse signal trigger_once
#the last menu will be restored when the current sub menu kills its own enable signal
#-----------------------------------------------------------main menu----------------------------------------------------------
    def show_main_menu(self, screen):
        next_level = 0
        
        #sets plot index list to 0
        plot_index_dict = {} #populate plot index for each npc
        for npc in os.listdir('sprites/npcs'):
            plot_index_dict[npc] = -1
        
        if not self.options_menu_enable and not self.saves_menu_enable and not self.saves_menu2_enable and next_level == 0:
            if self.trigger_once:
                #self.run_game = True
                self.button_list *= 0

                for i in range(4):
                    self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 +64 +36*i, self.generic_img, 1))
                self.trigger_once = False
                
            screen.blit(self.title_screen, self.ts_rect)
            
            if self.button_list[0].draw(screen):
                self.m_player.play_sound(self.m_player.sfx[1])
                self.saves_menu2_enable = True
                self.trigger_once = True
                # self.run_game = True
                # next_level = 1
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
            
        elif self.options_menu_enable and not self.saves_menu_enable and not self.saves_menu2_enable:
            self.show_options_menu(screen)
            
        elif not self.options_menu_enable and self.saves_menu_enable and not self.saves_menu2_enable:
            self.show_saves_menu(screen)
            
        elif not self.options_menu_enable and not self.saves_menu_enable and self.saves_menu2_enable:
            self.show_saves_menu2(screen)
            
        return (next_level, self.run_game, plot_index_dict)

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
            self.button_list[0].show_text(screen, self.fontlist[1], ('','Resume')) 
                
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
            self.button_list[2].show_text(screen, self.fontlist[1], ('','Main Menu'))  
            
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
                if self.disp_flags == pygame.DOUBLEBUF|pygame.SHOWN: #windowed mode
                    self.disp_flags = pygame.DOUBLEBUF|pygame.FULLSCREEN|pygame.SHOWN #full screen mode
                    screen = pygame.display.set_mode(self.std_size, self.disp_flags)
                elif self.disp_flags == pygame.DOUBLEBUF|pygame.FULLSCREEN|pygame.SHOWN:
                    self.disp_flags = pygame.DOUBLEBUF|pygame.SHOWN
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
            
#---------------------------------------------------------Save select sub menu, new game--------------------------------
    def show_saves_menu2(self, screen):
        #doesn't actually load data, it makes the player choose a file that can be autosaved to before a new game is started
        pygame.draw.rect(screen, (0,0,0), (0,0,self.S_W,self.S_H))
        next_level = 0
        #sets plot index list to 0
        plot_index_dict = {} #populate plot index for each npc
        for npc in os.listdir('sprites/npcs'):
            plot_index_dict[npc] = -1
        
        
        if self.trigger_once: #deploy buttons
            self.button_list *= 0
            for i in range(5):
                self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 -48 +40*i, self.generic_img, 1))
            
            self.trigger_once = False
        
        for i in range(4):
            if self.button_list[i].draw(screen): #Save file buttons
                #reset specific slot and set global variable
                self.save_handler.reset_specific_save(i, self.t1)
                self.selected_slot = i
                
                #set the new level
                self.run_game = True    
                next_level = 1
                
                #get out of the sub menu
                self.saves_menu2_enable = False
                self.m_player.play_sound(self.m_player.sfx[1])
                self.trigger_once = True
                
            self.button_list[i].show_text(screen, self.fontlist[1], ('',f'File {i}')) 
        
        #back button
        if self.button_list[4].draw(screen):
            self.saves_menu2_enable = False
            self.m_player.play_sound(self.m_player.sfx[1])
            self.trigger_once = True
        self.button_list[4].show_text(screen, self.fontlist[1], ('','Main Menu'))  
        
        self.text_manager0.disp_text_box(screen, self.fontlist[1], ('', '  Choose a file to load.', 'Prior data will be erased.'), (-1,-1,-1), (200,200,200), 
                                         (self.S_W//2 - 100, self.S_H//2 - 128,self.S_W,self.S_H), False, False, 'none')
        
     
        return (next_level, self.run_game, plot_index_dict)

            
#---------------------------------------------------------Save select sub menu-----------------------------------
    def show_saves_menu(self, screen):
        pygame.draw.rect(screen, (0,0,0), (0,0,self.S_W,self.S_H))
        next_level = 0
        #sets plot index list to 0
        plot_index_dict = {} #populate plot index for each npc
        for npc in os.listdir('sprites/npcs'):
            plot_index_dict[npc] = -1
        
        
        if self.trigger_once: #deploy buttons
            self.button_list *= 0
            for i in range(5):
                self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 -48 +40*i, self.generic_img, 1))
            self.button_list.append(Button(self.S_W - 88, self.S_H - 32, self.invisible_img, 1))
            
            if self.selected_slot != -1:
                self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 - 88, self.generic_img, 1))
            
            self.trigger_once = False
            
        for i in range(4):
            if self.button_list[i].draw(screen): #Save file buttons
                #set selected slot
                self.selected_slot = i
                
                #fill inventory
                path = f'save_files/{i}'
                self.player_new_inv = self.t1.str_list_to_list_list(self.t1.read_text_from_file(os.path.join(path, 'player_inventory.txt')))
                self.set_player_inv = True
                
                #set plot index
                if self.t1.read_text_from_file(os.path.join(path, 'plot_index_dict.txt'))[0] != 'empty': #this way I don't have to keep adding -1 if a player loads from a new save
                    #print(self.t1.read_text_from_file(os.path.join(path, 'plot_index_dict.txt')))
                    plot_index_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path, 'plot_index_dict.txt')), 'int')
                
                #get level and player location data
                new_lvl_and_player_dat = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path, 'level_and_player_coords.txt')), 'int')
                self.player_new_coords = (new_lvl_and_player_dat['player_x'], new_lvl_and_player_dat['player_y'])
                self.set_player_location = True
                
                #set the new level
                self.run_game = True    
                next_level = new_lvl_and_player_dat['level']
                
                #get out of the sub menu
                self.saves_menu_enable = False
                self.m_player.play_sound(self.m_player.sfx[1])
                self.trigger_once = True
                
            self.button_list[i].show_text(screen, self.fontlist[1], ('',f'File {i}')) 
        
        #back button
        if self.button_list[4].draw(screen):
            self.saves_menu_enable = False
            self.m_player.play_sound(self.m_player.sfx[1])
            self.trigger_once = True
        self.button_list[4].show_text(screen, self.fontlist[1], ('','Main Menu'))  
        
        #reset all button
        if self.button_list[5].draw(screen):
            self.m_player.play_sound(self.m_player.sfx[1])
            self.save_handler.reset_all_saves(self.t1)
        self.button_list[5].show_text(screen, self.fontlist[1], ('','Reset All'))  
        
        if self.selected_slot != -1 and len(self.button_list) == 7:
            if self.button_list[6].draw(screen):
                #fill inventory
                path = f'save_files/{self.selected_slot}'
                self.player_new_inv = self.t1.str_list_to_list_list(self.t1.read_text_from_file(os.path.join(path, 'player_inventory.txt')))
                self.set_player_inv = True
                
                #set plot index
                if self.t1.read_text_from_file(os.path.join(path, 'plot_index_dict.txt'))[0] != 'empty': #this way I don't have to keep adding -1 if a player loads from a new save
                    #print(self.t1.read_text_from_file(os.path.join(path, 'plot_index_dict.txt')))
                    plot_index_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path, 'plot_index_dict.txt')), 'int')
                
                #get level and player location data
                new_lvl_and_player_dat = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path, 'level_and_player_coords.txt')), 'int')
                self.player_new_coords = (new_lvl_and_player_dat['player_x'], new_lvl_and_player_dat['player_y'])
                self.set_player_location = True
                
                #set the new level
                self.run_game = True    
                next_level = new_lvl_and_player_dat['level']
                
                #get out of the sub menu
                self.saves_menu_enable = False
                self.m_player.play_sound(self.m_player.sfx[1])
                self.trigger_once = True
            self.button_list[6].show_text(screen, self.fontlist[1], ('','Current File'))
            
     
        return (next_level, self.run_game, plot_index_dict)

            
#---------------------------------------------------------Controls sub menu---------------------------                
    def show_ctrl_menu(self, screen):
        if self.trigger_once:
            self.stop = False
            self.button_list *= 0
            
            #load current control scheme from csv file into ctrls_list
            self.ctrls_list = self.read_csv_data('ctrls_data')
            #set up disp_str_list
            for i in range(len(self.disp_str_list)):
                if not self.controller_connected:
                    self.disp_str_list[i][1] = pygame.key.name(self.ctrls_list[i])
                else:
                    self.disp_str_list[i][1] = str(self.ctrls_list[i])
            #load buttons
            for i in range(10):
                self.button_list.append(Button(self.S_W//2 -192, self.S_H//2 -186 + 32*i, self.generic_img, 1))
            
            for i in range(10): #done for formatting (these are dummy buttons)
                self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 -186 + 32*i, self.generic_img, 1))
                
            #save button
            self.button_list.append(Button(self.S_W//2 - 64, self.S_H /2 +172, self.generic_img, 1))
            
            #save and load control scheme buttons
            self.button_list.append(Button(self.S_W//2 + 64, self.S_H /2 -186, self.generic_img, 1))
            self.button_list.append(Button(self.S_W//2 + 64, self.S_H /2 -186 + 32, self.generic_img, 1))
            
            self.button_list.append(Button(self.S_W//2 + 64, self.S_H /2 -186 + 96, self.generic_img, 1))
            self.button_list.append(Button(self.S_W//2 + 64, self.S_H /2 -186 + 128, self.generic_img, 1))
            
            self.button_list.append(Button(self.S_W//2 + 64, self.S_H /2 -186 + 192, self.generic_img, 1))
            
            self.trigger_once = False
        
        
        self.text_manager0.disp_text_box(screen, self.fontlist[1], ('','Click a button to re-map then press the desired key'), (-1,-1,-1), (200,200,200), 
                                         (112, self.S_H//2 - 232,self.S_W,self.S_H), False, False, 'none')
        self.text_manager0.disp_text_box(screen, self.fontlist[1], ('','UI buttons ESCAPE and ENTER cannot be re-mapped'), (-1,-1,-1), (200,200,200), 
                                         (128, self.S_H//2 + 128,self.S_W,self.S_H), False, False, 'none')
        
        ctrls_btn_dict = {
            0:('','Jump'),
            1:('','Left'),
            2:('','Roll'),
            3:('','Right'),
            4:('','Melee'),
            5:('','Shoot'),
            6:('','Special'),
            7:('','Sprint'),
            8:('','Inventory'),
            9:('','Use Item')
        }
        
        
        for i in range(10):
            if self.button_list[i].draw(screen):
                self.m_player.play_sound(self.m_player.sfx[1])
                self.btn_selected = i
                
            self.button_list[i].show_text(screen, self.fontlist[1], ctrls_btn_dict[i])
            self.button_list[i+10].show_text(screen, self.fontlist[1], self.disp_str_list[i])
        
        #pressing save button
        if self.button_list[20].draw(screen):
            self.ctrl_menu_enable = False
            self.m_player.play_sound(self.m_player.sfx[1])
            self.trigger_once = True  
            self.ctrls_updated = True
            #print(self.ctrls_list)
            self.write_csv_data('ctrls_data', self.ctrls_list)
        self.button_list[20].show_text(screen, self.fontlist[1], ('','Save'))  
        
        #load scheme 1
        if self.button_list[21].draw(screen):
            self.m_player.play_sound(self.m_player.sfx[1])
            self.ctrls_list = self.read_csv_data('ctrl_scheme_1')
            for i in range(len(self.disp_str_list)):
                self.disp_str_list[i][1] = pygame.key.name(self.ctrls_list[i])
        self.button_list[21].show_text(screen, self.fontlist[1], ('','Load Ctrls 1'))  
        
        #save scheme 1
        if self.button_list[22].draw(screen):
            self.m_player.play_sound(self.m_player.sfx[1])
            self.write_csv_data('ctrl_scheme_1', self.ctrls_list)
        self.button_list[22].show_text(screen, self.fontlist[1], ('','Save Ctrls 1'))  
        
        #load scheme 2
        if self.button_list[23].draw(screen):
            self.m_player.play_sound(self.m_player.sfx[1])
            self.ctrls_list = self.read_csv_data('ctrl_scheme_2')
            for i in range(len(self.disp_str_list)):
                self.disp_str_list[i][1] = pygame.key.name(self.ctrls_list[i])
        self.button_list[23].show_text(screen, self.fontlist[1], ('','Load Ctrls 2'))  
        
        #save scheme 2
        if self.button_list[24].draw(screen):
            self.m_player.play_sound(self.m_player.sfx[1])
            self.write_csv_data('ctrl_scheme_2', self.ctrls_list)
        self.button_list[24].show_text(screen, self.fontlist[1], ('','Save Ctrls 2'))  
        
        #pressing default button
        if self.button_list[25].draw(screen):
            self.m_player.play_sound(self.m_player.sfx[1])
            self.ctrls_list = [119, 97, 115, 100, 105, 111, 112, 1073742054, 121, 117]
            for i in range(len(self.disp_str_list)):
                self.disp_str_list[i][1] = pygame.key.name(self.ctrls_list[i])
        self.button_list[25].show_text(screen, self.fontlist[1], ('','Default'))  
        
        if not self.stop:
            for event in pygame.event.get():
                if(event.type == pygame.KEYDOWN):
                    if event.key != pygame.K_ESCAPE and event.key != pygame.K_RETURN:
                        self.disp_str_list[self.btn_selected][1] = pygame.key.name(event.key)
                        self.ctrls_list[self.btn_selected] = event.key
                    elif event.key == pygame.K_ESCAPE:
                        self.stop = True
                        
                if(event.type == pygame.JOYBUTTONDOWN):
                    
                    self.disp_str_list[self.btn_selected][1] = str(event.button)
                    self.ctrls_list[self.btn_selected] = event.button

                    
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
   
        if not self.saves_menu_enable:
            if self.trigger_once:
                self.run_game = True
                self.button_list *= 0

                for i in range(2):
                    self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 +32 +36*i, self.generic_img, 1))
                self.trigger_once = False
            
            if self.button_list[0].draw(screen):
                self.trigger_once = True
                self.saves_menu_enable = True
                exit_to_title = True
                pygame.mixer.stop()
                self.m_player.play_sound(self.m_player.sfx[1])
            self.button_list[0].show_text(screen, self.fontlist[1], ('','Load File')) 
            
            if self.button_list[1].draw(screen):
                exit_to_title = True
                self.trigger_once = True  
                pygame.mixer.stop()
                self.m_player.play_sound(self.m_player.sfx[1])
            self.button_list[1].show_text(screen, self.fontlist[1], ('','Main Menu'))  
        
        elif self.saves_menu_enable:
            self.show_saves_menu(screen)
        
        return exit_to_title
    
    # def reset_all_saves(self):
    #     for i in range(4):
    #         path = f'save_files/{i}'
    #         str1 = f'level: 1\nplayer_x: 32\nplayer_y: -64'
            
    #         str2 = 'empty'
                
    #         str3 = ''
    #         for slot in self.t1.str_list_to_list_list(self.t1.read_text_from_file(os.path.join(path, 'player_inventory.txt'))):
    #             str3 = str3 + f'empty, 0\n'
    #         str3 = str3[0:len(str3)-1]
            
    #         self.t1.overwrite_file(os.path.join(path, 'level_and_player_coords.txt'), str1)
    #         self.t1.overwrite_file(os.path.join(path, 'plot_index_dict.txt'), str2)
    #         self.t1.overwrite_file(os.path.join(path, 'player_inventory.txt'), str3)