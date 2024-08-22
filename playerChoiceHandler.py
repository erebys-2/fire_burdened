import pygame
import os
from button import Button
from music_player import music_player
from textManager import text_manager

#addon class for the subclass dialogue box under text manager
#it will overlay buttons over a blank text box and return the next index

class player_choice_handler():
    def __init__(self, choice_list, prompt_list, fontlist, m_player_sfx_list_main, ini_vol):
        self.choice_list = choice_list
        self.prompt_list = prompt_list
        self.fontlist = fontlist
        self.next_index = -3
        self.prompt = ('','')
        
        #a diectionary is going to be easier to modify and track choices than a pure list where I'd need to keep track of indices
        self.player_choice_dict = {
            # number of tuples in outer tuple = number of options, 
            # inner tuple = (message list index, next dialogue index) for the NPC waiting on the player choice
            'test_greeting' : ((2,2),(3,0)) 
        }    
        
        #2nd dictionary for prompts
        self.player_prompt_dict = { #list of lists, each inner list being a message
            'test_greeting' : self.prompt_list[0]
        }    
        
        self.trigger_once = True
        self.button_list = []
        self.btn_img = pygame.image.load('sprites/dialogue_btn.png').convert_alpha()
        self.bg_img = pygame.image.load('sprites/pause_bg.png').convert_alpha()
        
        self.m_player = music_player(m_player_sfx_list_main, ini_vol)
        self.text_manager0 = text_manager()
        
        self.dialogue_box_rect = (0, 0, 640, 120)
        
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

        
    def deploy_buttons(self, key, screen):
        screen.blit(pygame.transform.flip(self.bg_img, False, False), screen.get_rect())
        pygame.draw.rect(screen, (0,0,0), self.dialogue_box_rect)#draw box
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
                
            self.button_list[i].show_text(screen, self.fontlist[1], ('', self.choice_list[player_choices[i][0]]))
            
        #draw text
        self.text_manager0.disp_text_box(screen, self.fontlist[1], self.prompt, (-1,-1,-1),  (200,200,200), (64, 12, 640, 120), False, False, 'none')
        self.text_manager0.disp_text_box(screen, self.fontlist[1], ('Exit:(Escape)', ''), (-1,-1,-1),  (80,80,80), (533, 456, 32, 32), False, False, 'none')
        

        
        return self.next_index
    
#next step is to modify the NPC file so that when the index is -3, a signal is sent to the text manager
#to call functions from this class

#in NPC file while the index is -3, current frame and index has to be frozen and the display string has to be set to ''