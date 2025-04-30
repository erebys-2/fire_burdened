from button import Button #type: ignore
from textManager import text_manager #type: ignore
from music_player import music_player #type: ignore
from textfile_handler import textfile_formatter
from saveHandler import save_file_handler
import os
import pygame
import csv

class ui_manager(): #Helper class for displaying and operating non-game UI (menus and sub menus)
    
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, ts, fontlist, ini_vol, fs_size):
        m_player_sfx_list_main = ['roblox_oof.mp3', 'hat.mp3']
        self.m_player = music_player(m_player_sfx_list_main, ini_vol)
        self.t1 = textfile_formatter()
        self.text_manager0 = text_manager(SCREEN_WIDTH, SCREEN_HEIGHT, ts)
        self.save_handler = save_file_handler()
        
        self.generic_img = pygame.image.load('assets/sprites/generic_btn.png').convert_alpha()
        self.generic_img2 = pygame.image.load('assets/sprites/generic_btn2.png').convert_alpha()
        self.invisible_img = pygame.image.load('assets/sprites/invisible_btn.png').convert_alpha()
        self.pause_img = pygame.image.load('assets/sprites/pause_bg.png').convert_alpha()
        
        self.S_W = SCREEN_WIDTH
        self.S_H = SCREEN_HEIGHT
        self.ts = ts
        
        self.std_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.fs_size = fs_size
        
        self.in_fullscreen = False
        
        self.options_menu_enable = False
        self.ctrl_menu_enable = False
        self.vol_menu_enable = False
        self.saves_menu_enable = False
        self.saves_menu2_enable = False
        self.main_menu_enable = False
        
        self.trigger_once = True
        
        self.fontlist = fontlist
        self.button_list = []
        
        self.disp_flags = pygame.DOUBLEBUF|pygame.SHOWN

        self.stop = False
        self.btn_selected = 0
        
        self.disp_str_list = []
        for i in range(10):
            self.disp_str_list.append(['','empty'])
        
        self.ctrls_list = [-1]*10
        self.ctrls_updated = False

        self.title_screen = pygame.image.load('assets/sprites/title_screen.png').convert_alpha()
        self.ts_rect = self.title_screen.get_rect()
        self.ts_rect.center = (self.S_W//2, self.S_H//2 +self.ts)
        
        self.vol_lvl = ini_vol
        self.lower_volume = False
        self.raise_volume = False
        
        self.set_player_location = False

        #filler value, selected slot will always be set by clicking a slot before loading a game
        self.selected_slot = -1
        self.reset_all_slots = False
        self.controller_connected = False
        
        self.help_open = False
        self.help_btn_str = '[Open Tips]'
        
        path = 'assets/game_settings'
        self.toggle_settings_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path, 'toggle_settings.txt')), 'int')
        
        self.came_from_death_menu = False
        
        self.rtn_dict = self.reset_rtn_dict()
        self.kbd_new_game = False
        
        self.btn_click_counter = []
        self.joysticks = {}
        
    def reset_rtn_dict(self):
        rtn_dict = {
            'RG': True,
            'PNI': self.save_handler.ini_player_inv,
            'LCD': {0: 0},
            'OSD': {},
            'PID': {},
            'PNC': (self.ts,128),
            'NL': 0,
            'PS': {}
        }  
        
        plot_index_dict = {} #populate plot index for each npc
        for npc in os.listdir('assets/sprites/npcs'):
            plot_index_dict[npc] = -1
        rtn_dict['PID'] = plot_index_dict
        
        return rtn_dict  
    
    def read_csv_data(self, data_name):
        temp_list = []
        with open(f'assets/game_settings/{data_name}.csv', newline= '') as csvfile:
            reader = csv.reader(csvfile, delimiter= ',') #what separates values = delimiter
            for row in reader:
                for entry in row:
                    temp_list.append(int(entry))
     
        return temp_list
        
    def write_csv_data(self, data_name, data):
        with open(f'assets/game_settings/{data_name}.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter = ',')
            writer.writerow(data)
            
    def do_btn_logic(self, screen, btn, btn_name, update_trig1, font_list_index):
        btn_pressed = btn.draw(screen)
        if btn_pressed:
            self.m_player.play_sound(self.m_player.sfx[1], None)
            self.trigger_once = update_trig1
        btn.show_text(screen, self.fontlist[font_list_index], ('', btn_name))
        
        return btn_pressed
        
#this is essentially methods calling other methods
#menus are methods and they're drawn by the impulse signal trigger_once
#the last menu will be restored when the current sub menu kills its own enable signal
#-----------------------------------------------------------main menu----------------------------------------------------------
    def show_main_menu(self, screen):
        
        if not self.options_menu_enable and not self.saves_menu_enable and not self.saves_menu2_enable and self.rtn_dict['NL'] == 0:
            if self.trigger_once:
                self.button_list *= 0

                for i in range(4):
                    self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 +64 +36*i, self.generic_img, 1))
                self.trigger_once = False
                
                self.main_menu_enable = True
                self.came_from_death_menu = False
                self.rtn_dict = self.reset_rtn_dict()
                
            screen.blit(self.title_screen, self.ts_rect)
            
            if self.do_btn_logic(screen, self.button_list[0], 'New Game', True, 1) or self.kbd_new_game:
                self.saves_menu2_enable = True
                if self.kbd_new_game:
                    self.trigger_once = True
            
            if self.do_btn_logic(screen, self.button_list[1], 'Load File', True, 1):
                self.saves_menu_enable = True
                self.main_menu_enable = False
            
            if self.do_btn_logic(screen, self.button_list[2], 'Options', True, 1):
                self.options_menu_enable = True
                self.main_menu_enable = False
            
            if self.do_btn_logic(screen, self.button_list[3], 'Quit', False, 1):
                self.rtn_dict['RG'] = False

            
        elif self.options_menu_enable and not self.saves_menu_enable and not self.saves_menu2_enable:
            self.show_options_menu(screen)
            
        elif not self.options_menu_enable and self.saves_menu_enable and not self.saves_menu2_enable:
            self.show_saves_menu(screen)
            
        elif not self.options_menu_enable and not self.saves_menu_enable and self.saves_menu2_enable:
            self.show_saves_menu2(screen)

        return self.rtn_dict

#-----------------------------------------------------------pause menu---------------------------------------------------------
    def show_pause_menu(self, screen):
        pause_game = True
        exit_to_title = False
        
        #drawing pause text
        screen.blit(self.pause_img, (0,0))
        self.text_manager0.disp_text_box(screen, self.fontlist[2], ('','Game Paused'), (-1,-1,-1), (200,200,200), 
                                         (188, self.S_H//2 - 96,self.S_W,self.S_H), False, False, 'none')
        self.text_manager0.disp_text_box(screen, self.fontlist[1], ('[Shift] + [ESC] to Exit',), (-1,-1,-1), (200,200,200), 
                                         (5, 5,self.S_W,self.S_H), False, False, 'none')
        
        if not self.options_menu_enable:
            if self.trigger_once:
                self.button_list *= 0
                for i in range(3):
                    self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 +48*i, self.generic_img, 1))
                
                self.trigger_once = False

            if self.do_btn_logic(screen, self.button_list[0], 'Resume', True, 1):
                pause_game = False
                pygame.mixer.unpause()
            
            if self.do_btn_logic(screen, self.button_list[1], 'Options', True, 1):
                self.options_menu_enable = True
            
            if self.do_btn_logic(screen, self.button_list[2], 'Main Menu', True, 1):
                self.rtn_dict = self.reset_rtn_dict()
                exit_to_title = True
                pause_game = False
                pygame.mixer.unpause()
                pygame.mixer.stop()
                self.m_player.play_sound(self.m_player.sfx[1], None) #logic mix up
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
                for i in range(5):
                    self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 -80 +48*i, self.generic_img, 1))
                
                self.trigger_once = False
                
            if self.do_btn_logic(screen, self.button_list[0], 'Controls', True, 1):
                self.ctrl_menu_enable = True
            
            if self.do_btn_logic(screen, self.button_list[1], 'Volume', True, 1):
                self.vol_menu_enable = True
            
            if self.do_btn_logic(screen, self.button_list[2], 'Full Screen', False, 1):
                pygame.display.toggle_fullscreen()
                self.in_fullscreen = not self.in_fullscreen
            self.text_manager0.disp_text_box(screen, self.fontlist[1], (f'[{str(self.in_fullscreen)}]',''),
                                    (-1,-1,-1), (200,200,200), (self.button_list[2].rect.right + 10, self.button_list[2].rect.y + 8, 0, 0), False, False, 'none')
            
            if self.do_btn_logic(screen, self.button_list[3], 'Skip Death Screen', False, 0):
                self.toggle_settings_dict['skip_death_screen'] *= -1
                str2 = ''
                for key_ in self.toggle_settings_dict:
                    str2 = str2 + f'{key_}: {self.toggle_settings_dict[key_]}\n'
                str2 = str2[0:len(str2)-1]
                self.t1.overwrite_file('assets/game_settings/toggle_settings.txt', str2)
            self.text_manager0.disp_text_box(screen, self.fontlist[1], (f'[{str(self.toggle_settings_dict['skip_death_screen'] > 0)}]',''),
                                    (-1,-1,-1), (200,200,200), (self.button_list[3].rect.right + 10, self.button_list[3].rect.y + 8, 0, 0), False, False, 'none')
                
            if self.do_btn_logic(screen, self.button_list[4], 'Back', True, 1):
                self.options_menu_enable = False
            
        elif self.ctrl_menu_enable and not self.vol_menu_enable:
            self.show_ctrl_menu(screen)
            
        else:
            self.show_vol_menu(screen)
            
#---------------------------------------------------------Save select sub menu, new game--------------------------------
    def show_saves_menu2(self, screen):
        #doesn't actually load data, it makes the player choose a file that can be autosaved to before a new game is started
        pygame.draw.rect(screen, (0,0,0), (0,0,self.S_W,self.S_H))
        save_files_ct = 4
        if self.trigger_once: #deploy buttons
            self.button_list *= 0
            
            for i in range(save_files_ct+1):
                if i < 4:
                    img = self.generic_img2
                else:
                    img = self.generic_img
                self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 -48 +40*i, img, 1))
                self.button_list[i].rect.centerx = self.S_W//2#center buttons
                if i < save_files_ct and len(self.btn_click_counter) <= save_files_ct:
                    self.btn_click_counter.append(0)
            
            self.rtn_dict = self.reset_rtn_dict()
            self.trigger_once = False
        
        for i in range(save_files_ct):
            file_status = 'Empty'
            if self.save_handler.check_plot_index(i):
                file_status = self.save_handler.get_save_time(i)#'Used'

            btn_str = f'File {i}: {file_status}'
            if self.btn_click_counter[i] > 0:
                btn_str = 'Confirm Reset?'
                
            if self.do_btn_logic(screen, self.button_list[i], btn_str, True, 1) or self.kbd_new_game:
                #reset specific slot and set global variable
                if self.kbd_new_game and self.btn_click_counter == [0]*save_files_ct:
                    index = 0
                elif self.kbd_new_game and 1 in self.btn_click_counter:
                    index = self.btn_click_counter.index(1)
                    self.trigger_once = True
                else:
                    index = i
                self.kbd_new_game = False
                
                if self.btn_click_counter[index] > 0:  
                    self.save_handler.reset_specific_save(index)
                    self.selected_slot = index
                    
                    #set the new level
                    self.rtn_dict['NL'] = 1
                    
                    #populate onetime_spawn_dict with default values
                    path2 = 'assets/config_textfiles/world_config/'
                    self.rtn_dict['OSD'] = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path2, 'ini_onetime_spawns.txt')), 'list_list') #onetime_spawn_dict
                    
                    #set flag
                    self.saves_menu2_enable = False
                    self.btn_click_counter = [0]*save_files_ct
                else:
                    ini_value = self.btn_click_counter[index]
                    self.btn_click_counter = [0]*save_files_ct
                    self.btn_click_counter[index] += ini_value + 1
                    
                #print(self.btn_click_counter)
                    
        
        #back button        
        if self.do_btn_logic(screen, self.button_list[4], 'Main Menu', True, 1):
            self.btn_click_counter = [0]*save_files_ct
            self.saves_menu2_enable = False
        
        self.text_manager0.disp_text_box(screen, self.fontlist[1], ('', '  Choose a file to load.', 'Prior data will be erased.'), (-1,-1,-1), (200,200,200), 
                                         (self.S_W//2 - 100, self.S_H//2 - 128,self.S_W,self.S_H), False, False, 'none')

        return self.rtn_dict

            
#---------------------------------------------------------Save select sub menu-----------------------------------
    def show_saves_menu(self, screen):
        pygame.draw.rect(screen, (0,0,0), (0,0,self.S_W,self.S_H))
        
        if self.trigger_once: #deploy buttons
            self.button_list *= 0
            for i in range(5):
                if i < 4:
                    img = self.generic_img2
                else:
                    img = self.generic_img
                self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 -48 +40*i, img, 1))
                self.button_list[i].rect.centerx = self.S_W//2#center buttons
            self.button_list.append(Button(self.S_W - 112, self.S_H - self.ts, self.invisible_img, 1))
            
            if self.selected_slot != -1:
                self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 - 88, self.generic_img, 1))
            
            self.rtn_dict = self.reset_rtn_dict()
            self.trigger_once = False
            
        for i in range(4):
            if self.save_handler.check_plot_index(i):
                file_status = self.save_handler.get_save_time(i)#'Used'
            else:
                file_status = 'Empty'
            if self.do_btn_logic(screen, self.button_list[i], f'File {i}: {file_status}', True, 1):
                #set selected slot
                self.selected_slot = i

                loaded_data = self.save_handler.load_save(self.selected_slot)
                for entry in loaded_data:#update rtn dict
                    self.rtn_dict[entry] = loaded_data[entry]
                
                #get out of the sub menu and send control signals
                self.set_player_location = True
                self.saves_menu_enable = False

        #back button
        if self.do_btn_logic(screen, self.button_list[4], 'Main Menu', True, 1):
            self.saves_menu_enable = False
        
        #reset all button
        if self.do_btn_logic(screen, self.button_list[5], '[Reset All]', False, 1):
            self.save_handler.reset_all_saves()
            self.reset_all_slots = True
            self.selected_slot = -1
        
        #select current slot
        if self.selected_slot != -1 and len(self.button_list) >= 7:
            if self.do_btn_logic(screen, self.button_list[6], f'Last File: {self.selected_slot}', True, 1) or (self.came_from_death_menu and self.toggle_settings_dict['skip_death_screen'] > 0):
                loaded_data = self.save_handler.load_save(self.selected_slot)
                
                for entry in loaded_data:#update rtn dict
                    self.rtn_dict[entry] = loaded_data[entry]
                
                #get out of the sub menu, set control signals
                self.set_player_location = True
                self.saves_menu_enable = False
                self.trigger_once = True

            if self.came_from_death_menu and self.toggle_settings_dict['skip_death_screen'] > 0:
                pygame.draw.rect(screen, (0,0,0), pygame.rect.Rect(0,0,self.S_W,self.S_H))
     
        return self.rtn_dict

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
                self.button_list.append(Button(self.S_W//2 -192, self.S_H//2 -186 + self.ts*i, self.generic_img, 1))
            
            for i in range(10): #done for formatting (these are dummy buttons)
                self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 -186 + self.ts*i, self.generic_img, 1))
                
            #save button
            self.button_list.append(Button(self.S_W//2 - 64, self.S_H//2 +172, self.generic_img, 1))
            
            #save and load control scheme buttons
            self.button_list.append(Button(self.S_W//2 + 64, self.S_H//2 -186, self.generic_img, 1))
            self.button_list.append(Button(self.S_W//2 + 64, self.S_H /2 -186 + self.ts, self.generic_img, 1))
            
            self.button_list.append(Button(self.S_W//2 + 64, self.S_H//2 -186 + 96, self.generic_img, 1))
            self.button_list.append(Button(self.S_W//2 + 64, self.S_H//2 -186 + 128, self.generic_img, 1))
            
            self.button_list.append(Button(self.S_W//2 + 64, self.S_H//2 -186 + 192, self.generic_img, 1))
            
            self.button_list.append(Button(self.S_W//2 + 64, self.S_H//2 -186 + 256, self.generic_img, 1))
            
            #tips button
            self.button_list.append(Button(0, self.S_H - self.ts, self.invisible_img, 1))
            
            self.trigger_once = False
        
        
        self.text_manager0.disp_text_box(screen, self.fontlist[1], ('','Click a button to re-map then press the desired key'), (-1,-1,-1), (200,200,200), 
                                         (112, self.S_H//2 - 232, self.S_W, self.S_H), False, False, 'none')
        self.text_manager0.disp_text_box(screen, self.fontlist[1], ('','UI buttons ESCAPE and ENTER cannot be re-mapped'), (-1,-1,-1), (200,200,200), 
                                         (128, self.S_H//2 + 128, self.S_W, self.S_H), False, False, 'none')
        
        ctrs_btn_list = [
            'Jump',
            'Left',
            'Roll',
            'Right',
            'Melee',
            'Shoot',
            'Special',
            'Sprint',
            'Inventory',
            'Use Item'
        ]
        
        if  not self.help_open:
            ref_rect = self.button_list[self.btn_selected].rect
            pygame.draw.rect(screen, (255,255,255), pygame.rect.Rect(ref_rect.x, ref_rect.y, 2*ref_rect.width, ref_rect.height), 1)
            for i in range(10):
                if self.do_btn_logic(screen, self.button_list[i], ctrs_btn_list[i], False, 1):
                    self.btn_selected = i

                self.button_list[i+10].show_text(screen, self.fontlist[1], self.disp_str_list[i])
            
            #pressing save button
            if self.do_btn_logic(screen, self.button_list[20], 'Save', True, 1):
                self.ctrl_menu_enable = False
                self.ctrls_updated = True
                self.write_csv_data('ctrls_data', self.ctrls_list)

            #load/save control schemes
            for j in range(2):
                #load scheme
                if self.do_btn_logic(screen, self.button_list[21 + 2*j], f'Load Ctrls {j+1}', False, 1):
                    self.ctrls_list = self.read_csv_data(f'ctrl_scheme_{j+1}')
                    for k in range(len(self.disp_str_list)):
                        if self.controller_connected:
                            self.disp_str_list[k][1] = str(self.ctrls_list[k])
                        else:
                            self.disp_str_list[k][1] = pygame.key.name(self.ctrls_list[k])
                
                #save scheme
                if self.do_btn_logic(screen, self.button_list[22 + 2*j], f'Save Ctrls {j+1}', False, 1):
                    self.write_csv_data(f'ctrl_scheme_{j+1}', self.ctrls_list)
            
            #pressing default button
            if self.do_btn_logic(screen, self.button_list[25], 'Default', False, 1):
                self.ctrls_list = [119, 97, 115, 100, 105, 111, 112, 1073742054, 121, 117]
                for i in range(len(self.disp_str_list)):
                    self.disp_str_list[i][1] = pygame.key.name(self.ctrls_list[i])
                    
            if self.do_btn_logic(screen, self.button_list[26], 'Default2', False, 1):
                self.ctrls_list = [1073741906, 1073741904, 1073741905, 1073741903, 101, 119, 113, 1073742049, 121, 117]#https://www.ascii-code.com/
                for i in range(len(self.disp_str_list)):
                    self.disp_str_list[i][1] = pygame.key.name(self.ctrls_list[i])
            
        else:
            pygame.draw.rect(screen, (0,0,0), (0, 0, self.S_W, self.S_H))
            ctrl_listk = []
            for key in self.ctrls_list:
                ctrl_listk.append(pygame.key.name(key))
            ctrl_tips = (
                'Melee Attacking:',
                f'   -Pressing [{ctrl_listk[4]}] while mid air will amplify your vertical velocity.',
                f'   -Pressing [{ctrl_listk[4]}] while rolling will trigger a large dash attack, which will do more damage.',
                '   -You are invulnerable during melee animation.',
                '   -Your melee doubles as a small forward dash.',
                f'       -Pressing either [{ctrl_listk[1]}] or [{ctrl_listk[3]}] will increase dash distance.',
                '   -Spamming melee for more than 4 times in a row will cause you to enter heavy attack mode.',
                f'       -Exit heavy attack mode by doing some other action: [{ctrl_listk[0]}, {ctrl_listk[2]}, {ctrl_listk[9]}, {ctrl_listk[5]}, etc].',
                '       -Or wait a full animation cycle to exit.',
                f'   -Melee animation can be canceled by rolling [{ctrl_listk[2]}] or moving in the opposite direction.',
                '',
                'Rolling:',
                '   -You are invulnerable during roll animation.',
                f'   -Rolling can be canceled by jumping [{ctrl_listk[0]}] or rolling [{ctrl_listk[2]}].',
                '',
                'Shooting:',
                '   -You need items that can serve as ammunition to shoot.',
                f'   -Hold [{ctrl_listk[5]}] to charge a shot.',
                '',
                'Sprinting:',
                f'   -Holding down [{ctrl_listk[7]}] will enable sprint; lifting the key will disable it.',
                '   -Stamina regeneration is lowered while sprint is enabled.',
                '   -All animations will slightly speed up while sprint is enabled.'
            )
            
            self.text_manager0.disp_text_box(screen, self.fontlist[0], ctrl_tips,
                                        (-1,-1,-1), (200,200,200), (self.ts, self.ts, 630, 480), False, False, 'none')
            
        
        #pressing tips button
        if self.do_btn_logic(screen, self.button_list[27], self.help_btn_str, False, 1):
            self.help_open = not self.help_open
            if self.help_open:
                self.help_btn_str = '[Close Tips]'
            else:
                self.help_btn_str = '[Open Tips]'
              
        if not self.stop:
            if self.controller_connected:
                for joystick in self.joysticks.values():
                    btns = [joystick.get_button(b) for b in range(joystick.get_numbuttons())]
                    axiis = [joystick.get_axis(a) for a in range(joystick.get_numaxes())]
                    #if pygame.time.get_ticks()%20 ==0:
                    # print(btns)
                    # print(axiis)
                    for b in range(joystick.get_numbuttons()):
                        if joystick.get_button(b):
                            self.disp_str_list[self.btn_selected][1] = str(b)
                            self.ctrls_list[self.btn_selected] = b
                    for a in range(joystick.get_numaxes()-2):
                        if abs(joystick.get_axis(a)) > 0.9:
                            #print(a + joystick.get_numbuttons() - 1)
                            self.disp_str_list[self.btn_selected][1] = str(a + joystick.get_numbuttons() - 1)
                            self.ctrls_list[self.btn_selected] = a
                    
                    
                    # self.disp_str_list[self.btn_selected][1] = str(btns[])
                    # self.ctrls_list[self.btn_selected] = event.button

                    
                
            for event in pygame.event.get():
                    
                
                if(event.type == pygame.KEYDOWN):
                    if event.key != pygame.K_ESCAPE and event.key != pygame.K_RETURN:
                        self.disp_str_list[self.btn_selected][1] = pygame.key.name(event.key)
                        self.ctrls_list[self.btn_selected] = event.key
                    elif event.key == pygame.K_ESCAPE:
                        self.stop = True
                        
                # if(event.type == pygame.JOYBUTTONDOWN):
                #     self.disp_str_list[self.btn_selected][1] = str(event.button)
                #     self.ctrls_list[self.btn_selected] = event.button
                    
                if(event.type == pygame.QUIT):
                    self.stop = True
                    
#------------------------------------------------------Volume sub menu-------------------------------
        
    def show_vol_menu(self, screen):
        #kinda cursed rn, need to code a slider eventually
        self.vol_lvl = self.read_csv_data('vol_data')[0]
        string = f'    {10*self.vol_lvl}%'
        self.text_manager0.disp_text_box(screen, self.fontlist[1], ('','Volume Level', string), (-1,-1,-1), (200,200,200), 
                                    (272, self.S_H//2 - 64,self.S_W,self.S_H), False, False, 'none')

        if self.trigger_once:
            self.button_list *= 0
            for i in range(3):
                self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 +48*i, self.generic_img, 1))
                
            self.trigger_once = False

        #not using do_btn_logic since this will play the btn click sound after the volume is adjusted
        if self.button_list[0].draw(screen):
            
            if self.vol_lvl < 10:
                self.vol_lvl += 1
            
            self.raise_volume = True
            self.write_csv_data('vol_data', (self.vol_lvl, 10))
            self.m_player.set_vol_all_sounds(self.vol_lvl)
            self.m_player.play_sound(self.m_player.sfx[1], None)
        else:
            self.raise_volume = False
        self.button_list[0].show_text(screen, self.fontlist[1], ('','Louder')) 
            
        if self.button_list[1].draw(screen):
            
            if self.vol_lvl > 0:
                self.vol_lvl -= 1
                
            self.lower_volume = True
            self.write_csv_data('vol_data', (self.vol_lvl, 10))
            self.m_player.set_vol_all_sounds(self.vol_lvl)
            self.m_player.play_sound(self.m_player.sfx[1], None)
        else:
            self.lower_volume = False
        self.button_list[1].show_text(screen, self.fontlist[1], ('','Quieter')) 
            
        if self.do_btn_logic(screen, self.button_list[2], 'Back', True, 1):
            self.vol_menu_enable = False
        
#-------------------------------------------Death Menu---------------------------------------------

    def show_death_menu(self, screen):
        exit_to_title = False
        
        #drawing pause text
        screen.blit(self.pause_img, (0,0))
        self.text_manager0.disp_text_box(screen, self.fontlist[1], ('','You Died'), (-1,-1,-1), (200,200,200), 
                                         (288, self.S_H//2 - self.ts,self.S_W,self.S_H), False, False, 'none')
   
        if not self.saves_menu_enable:
            if self.trigger_once:
                self.button_list *= 0

                for i in range(2):
                    self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 +self.ts +36*i, self.generic_img, 1))
                self.trigger_once = False
                
                self.came_from_death_menu = True
            
            if self.do_btn_logic(screen, self.button_list[0], 'Load File', True, 1) or self.toggle_settings_dict['skip_death_screen'] > 0:
                self.trigger_once = True #self.toggle_settings_dict['skip_death_screen'] > 0: does not set it to True
                self.saves_menu_enable = True
                exit_to_title = True
                pygame.mixer.stop()
                self.m_player.play_sound(self.m_player.sfx[1], None)
            
            if self.do_btn_logic(screen, self.button_list[1], 'Main Menu', True, 1):
                self.rtn_dict = self.reset_rtn_dict()
                exit_to_title = True
                pygame.mixer.stop()
                self.m_player.play_sound(self.m_player.sfx[1], None)

        if self.toggle_settings_dict['skip_death_screen'] > 0:
            pygame.draw.rect(screen, (0,0,0), pygame.rect.Rect(0,0,self.S_W,self.S_H))
        
        elif self.saves_menu_enable:
            self.show_saves_menu(screen)
        
        return exit_to_title
    