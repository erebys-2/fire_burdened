from button import Button #type: ignore
from textManager import text_manager #type: ignore
from music_player import music_player #type: ignore
import os
import pygame

class ui_manager():
    
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, fontlist):
        m_player_sfx_list_main = ['roblox_oof.wav', 'hat.wav']
        self.m_player = music_player(m_player_sfx_list_main)
        
        self.text_manager0 = text_manager()
        self.generic_img = pygame.image.load('sprites/generic_btn.png').convert_alpha()
        
        self.S_W = SCREEN_WIDTH
        self.S_H = SCREEN_HEIGHT
        
        self.options_menu_enable = False
        self.trigger_once = True
        
        self.fontlist = fontlist
        self.button_list = []
        
    def show_pause_menu(self, screen):
        #print("working")
        pause_game = True
        exit_to_title = False
        #3 buttons just like the start menu
        
        
        if not self.options_menu_enable:
            if self.trigger_once:
                self.button_list *= 0
                
                rtn_button = Button(self.S_W //2 -64, self.S_H //2 +0, self.generic_img, 1)
                options_button = Button(self.S_W //2 -64, self.S_H //2 +48, self.generic_img, 1)
                esc_button = Button(self.S_W //2 -64, self.S_H //2 +96, self.generic_img, 1)
                
                self.button_list.append(rtn_button)
                self.button_list.append(options_button)
                self.button_list.append(esc_button)
                #print(esc_button.clicked)
                self.trigger_once = False
                
            text = ('','balls')
            self.text_manager0.disp_text_box(screen, self.fontlist[1], text, (0,0,0), (255,255,255), (0,0,self.S_W,self.S_H), False, False, 'none')
            
            if self.button_list[0].draw(screen):
                pause_game = False
                self.m_player.play_sound(self.m_player.sfx[1])
                self.trigger_once = True
                
            if self.button_list[1].draw(screen):
                self.options_menu_enable = True
                self.m_player.play_sound(self.m_player.sfx[1])
                self.trigger_once = True
                
            if self.button_list[2].draw(screen):
                exit_to_title = True
                pause_game = False
                self.m_player.play_sound(self.m_player.sfx[1])
                self.trigger_once = True
        else:
            #trigger options menu
            self.show_options_menu(screen)
                
        return (pause_game, exit_to_title)
    
    def show_options_menu(self, screen):
        if self.trigger_once:
            self.button_list *= 0
            self.trigger_once = False
            
        self.options_menu_enable = False
        self.trigger_once = True
        print("no options yet lol")