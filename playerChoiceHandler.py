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
    def __init__(self, fontlist, m_player_sfx_list_main, ini_vol):

        self.fontlist = fontlist
        self.next_index = -3
        self.prompt = ('','')
        
        self.t1 = textfile_formatter()
        path = 'npc_dialogue_files/player_choice_config/'
        self.player_choice_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path + 'choice_selection_dict.txt')), 'list_list')
        
        #2nd dictionary for prompts
        self.player_prompt_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path + 'prompt_dict.txt')), 'text_box')

        self.trigger_once = True
        self.button_list = []
        self.btn_img = pygame.image.load('sprites/dialogue_btn.png').convert_alpha()
        self.bg_img = pygame.image.load('sprites/pause_bg.png').convert_alpha()
        self.prompt_box_bg = pygame.image.load('sprites/dialogue_box.png').convert_alpha()
        
        self.m_player = music_player(m_player_sfx_list_main, ini_vol)
        self.text_manager0 = text_manager()
        
        self.dialogue_box_rect = (0, 0, 640, 120)
        
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
            pos_list = [(64, 360), (320, 360), (64, 408), (320, 408)]
        elif btn_count == 3:
            pos_list = [(64, 360), (320, 360), (192, 408)]
        elif btn_count == 2:
            pos_list = [(64, 384), (320, 384)]
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
                self.m_player.play_sound(self.m_player.sfx[1])
                self.next_index = player_choices[i][1]
                #self.trigger_once = True
                if key == 'save_game': # write to save file
                    #t1, slot, level, world, player
                    self.save_handler.save(self.t1, i, level, world.plot_index_dict, player)
                    
                    self.last_save_slot = i
                    self.save_indicator = True
                    self.save_time_pt = pygame.time.get_ticks()
                    
                #will need to set level, player new coords, inventory, plot index
                # make sure bosses are dead/ one time puzzles are trapped/ key items stay collected
                
            self.button_list[i].show_text(screen, self.fontlist[1], ('', player_choices[i][0]))
            
        #draw text
        self.text_manager0.disp_text_box(screen, self.fontlist[1], self.prompt, (-1,-1,-1),  (200,200,200), (64, 12, 640, 120), False, False, 'none')
        self.text_manager0.disp_text_box(screen, self.fontlist[1], ('Exit:(Escape)', ''), (-1,-1,-1),  (80,80,80), (533, 456, 32, 32), False, False, 'none')
        if self.save_indicator and self.save_time_pt + 2000 > pygame.time.get_ticks():
            self.text_manager0.disp_text_box(screen, self.fontlist[1], (f'Saved in File {self.last_save_slot}', ''), (-1,-1,-1), (200,200,200), (64, 64, 32, 32), False, False, 'none')
        else:
            self.save_indicator = False
        
        return (self.next_index, self.last_save_slot)
    
#next step is to modify the NPC file so that when the index is -3, a signal is sent to the text manager
#to call functions from this class

#in NPC file while the index is -3, current frame and index has to be frozen and the display string has to be set to ''