import pygame
import os
from button import Button
from music_player import music_player
from textManager import text_manager
from textfile_handler import textfile_formatter
from saveHandler import save_file_handler

#addon class for the subclass dialogue box under text manager
#it will overlay buttons over a blank text box and return the next index

class player_choice_handler():
    def __init__(self, fontlist, m_player_sfx_list_main, ini_vol, SW, SH, TS):

        self.fontlist = fontlist
        self.next_index = -3
        self.prompt = ('','')
        self.SH = SH
        self.SW = SW
        self.ts = TS
        
        self.t1 = textfile_formatter()
        path = 'assets/npc_dialogue_files/player_choice_config/'
        self.player_choice_dict = {}
        player_choice_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path + 'choice_selection_dict.txt')), 'list_list')
        for entry in player_choice_dict:
            self.player_choice_dict[entry] = tuple(player_choice_dict[entry])
        
        #2nd dictionary for prompts
        self.player_prompt_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path + 'prompt_dict.txt')), 'text_box')

        self.trigger_once = True
        self.button_list = []
        self.btn_img = pygame.image.load('assets/sprites/dialogue_btn.png').convert_alpha()
        self.bg_img = pygame.image.load('assets/sprites/pause_bg.png').convert_alpha()
        self.prompt_box_bg = pygame.image.load('assets/sprites/dialogue_box.png').convert_alpha()
        
        self.m_player = music_player(m_player_sfx_list_main, ini_vol)
        self.text_manager0 = text_manager(SW, SH, TS)
        
        self.dialogue_box_rect = (0, 0, self.SW, self.SH//4)
        
        self.save_indicator = False
        self.last_save_slot = 0
        self.save_time_pt = pygame.time.get_ticks()
        
        self.save_handler = save_file_handler()
        
    def disable(self):
        self.next_index = -3
        self.button_list *= 0
        self.trigger_once = True
        
    def get_button_locations(self, btn_count):
        
        if btn_count == 4:
            pos_list = [(2*self.ts, 1.125*self.SW//2), (self.SW//2, 1.125*self.SW//2), (2*self.ts, 0.85*self.SH), (self.SW//2, 0.85*self.SH)]
        elif btn_count == 3:
            pos_list = [(2*self.ts, 1.125*self.SW//2), (self.SW//2, 1.125*self.SW//2), (192, 0.85*self.SH)]
        elif btn_count == 2:
            pos_list = [(2*self.ts, self.SW//2 + 2*self.ts), (self.SW//2, self.SW//2 + 2*self.ts)]
        else:
            pos_list = []
        
        return pos_list

        
    def deploy_buttons(self, key, screen, player, level, world):
        screen.blit(pygame.transform.flip(self.bg_img, False, False), screen.get_rect())
        #pygame.draw.rect(screen, (0,0,0), self.dialogue_box_rect)#draw box
        screen.blit(self.prompt_box_bg, self.dialogue_box_rect)
        player_choices = self.player_choice_dict[key] #get relevant data

        if self.trigger_once:#instantiate buttons
            self.prompt = self.player_prompt_dict[key]#get prmpt
            self.next_index = -3
            self.button_list *= 0
            btn_count = len(player_choices)
            pos_list = self.get_button_locations(btn_count)
            
            for i in range(btn_count):
                self.button_list.append(Button(pos_list[i][0], pos_list[i][1], self.btn_img, 1))

            self.trigger_once = False
            
        for i in range(len(self.button_list)):#button behvior, the buttons should be aligned with the player_choices list
            if self.button_list[i].draw(screen):
                self.next_index = player_choices[i][1]
                #self.trigger_once = True
                if key == 'save_game': # write to save file
                    #t1, slot, level, world, player
                    world.check_onetime_spawn_dict(level)
                    self.save_handler.save(i, level, world.plot_index_dict, world.lvl_completion_dict, world.onetime_spawn_dict, player)
                    
                    self.last_save_slot = i
                    self.save_indicator = True
                    self.save_time_pt = pygame.time.get_ticks()
                    
                #will need to set level, player new coords, inventory, plot index
                # make sure bosses are dead/ one time puzzles are trapped/ key items stay collected
            txt = ''
            if key == 'save_game':
                txt = ': Empty'
                if self.save_handler.check_plot_index(i):
                    txt = f': {self.save_handler.get_save_time(i)}'
                
            self.button_list[i].show_text(screen, self.fontlist[1], ('', player_choices[i][0] + txt))
            
        #draw text
        self.text_manager0.disp_text_box(screen, self.fontlist[1], self.prompt, (-1,-1,-1),  (200,200,200), (2*self.ts, 12, self.SW, self.SH//4), False, False, 'none')
        self.text_manager0.disp_text_box(screen, self.fontlist[1], ('Exit:(Escape)', ''), (-1,-1,-1),  (80,80,80), (0.8328125*self.SW, 0.95*self.SH, self.ts, self.ts), False, False, 'none')
        if self.save_indicator and self.save_time_pt + 2000 > pygame.time.get_ticks():
            self.text_manager0.disp_text_box(screen, self.fontlist[1], (f'Saved in File {self.last_save_slot}', ''), (-1,-1,-1), (200,200,200), (2*self.ts, 2*self.ts, self.ts, self.ts), False, False, 'none')
        else:
            self.save_indicator = False
        
        return (self.next_index, self.last_save_slot)
    
#next step is to modify the NPC file so that when the index is -3, a signal is sent to the text manager
#to call functions from this class

#in NPC file while the index is -3, current frame and index has to be frozen and the display string has to be set to ''