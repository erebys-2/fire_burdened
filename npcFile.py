import pygame
import os
import csv
# from bullet import bullet_ #type: ignore
from particle import particle_ #type: ignore
from music_player import music_player #type: ignore
import random
from textManager import text_manager
from textfile_handler import textfile_formatter

#NPC class used for sprites with access to text and player choice ui

class npc(pygame.sprite.Sprite):
    #constructor
    def __init__(self, x, y, scale, direction, name, ini_vol, enabled, world):#plot index is passed from game_window, to world, then here
        pygame.sprite.Sprite.__init__(self)
        self.direction = direction
        self.enabled = enabled
        self.scale = scale
        
        self.name = name
        
        self.cutscene_rect = pygame.rect.Rect(0,0,0,0)
        self.is_cutscene = False
        self.is_npc = False
        self.is_obj = False
        self.flip = False

        self.npc_index_id = (os.listdir('sprites/npcs')).index(name)

        self.plot_index_dict = world.plot_index_dict
        
        self.current_dialogue_index = 0
        self.last_dialogue_index = 0
        self.is_initial_index = True
        
        self.m_player = music_player(['mc_anvil.wav'], ini_vol)
        self.ini_vol = ini_vol
        
        self.trigger_once = False
        
        self.frame_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        
        #action_types = ('idle', 'wave', 'sit', 'shock')
        for action in range(len(os.listdir(f'sprites/npcs/{self.name}'))):
            temp_list = []
            frames = len(os.listdir(f'sprites/npcs/{self.name}/{action}'))

            for i in range(frames):
                img = pygame.image.load(f'sprites/npcs/{self.name}/{action}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
                
            self.frame_list.append(temp_list)
        

        self.image = self.frame_list[self.action][self.frame_index]
        self.mask = pygame.mask.from_surface(self.image)
        
        self.rect = self.image.get_rect()
        self.img_rect = self.image.get_rect()
        
        self.rect.topleft = (x,y)
        self.img_rect.topleft = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        self.interaction_prompt = pygame.image.load('sprites/interaction_prompt.png').convert_alpha()
        self.interaction_prompt_rect = self.interaction_prompt.get_rect()
        
        self.text_manager0 = text_manager()
        self.player_collision = False
        self.get_dialogue_flag = False
        
        self.player_choice_flag = False #signal
        self.player_choice_key = '' #key
        
        self.collisions_disabled = False
        
        self.t1 = textfile_formatter()
        #plot index, dialogue index to jump to
        self.plot_index_jumps_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file('npc_dialogue_files/npc_plot_index_config/' + self.name + '.txt'), 'int')
        #print(self.plot_index_jumps_dict)
        self.dialogue_list = self.get_specific_npc_dialogue(self.name)
        
    
    def get_npc_index_id(self, name):
        return (os.listdir('sprites/npcs')).index(name)
    
    def get_specific_npc_dialogue(self, name):
        path = 'npc_dialogue_files/npc_dialogue_txt_files/'
        rtn_list = self.t1.str_list_to_dialogue_list(self.t1.read_text_from_file(path + name + '.txt'), 60, self.t1.endcase_char)
        
        return rtn_list
    
    def get_message(self, current_dialogue_index):
        name = self.dialogue_list[current_dialogue_index][0]
        message = self.dialogue_list[current_dialogue_index][1]
        next_dialogue_index = self.dialogue_list[current_dialogue_index][2]
        npc_expression = self.dialogue_list[current_dialogue_index][3]
        
        return (name, message, next_dialogue_index, npc_expression) #string, int
    
    #generally, current_dialogue_index will advance itself by following the next index in the dialogue array
    #self.get_dialogue_index() will only be triggered by specific conditions: level, plot index, current dialogue index and will be called right before
    #and will force current_dialogue_index to some other value in that moment
    def enable(self, dialogue_enable, next_dialogue, current_dialogue_list):
        if self.enabled:
            
            #dialogue_enable and next_dialogue are global booleans in the game window file
            message = ''
            name = ''
            if self.player_collision and dialogue_enable:
                dialogue = self.get_message(self.current_dialogue_index) #returns message and index of next dialogue
                expression = dialogue[3]
                name = dialogue[0]
                
                if not self.player_choice_flag:
                    message = dialogue[1] #reformat here
                else:
                    message = ('','')
                
                if dialogue[2] == -3 and not self.player_choice_flag: #impulse signal
                    self.player_choice_flag = True
                    self.player_choice_key = message[0]
                    next_dialogue = True
                    #print(message)
                else:
                    current_dialogue_list[self.npc_index_id] = dialogue[3]
                
                if next_dialogue:#convert continuous signal next_dialogue into an impulse

                    if self.trigger_once != next_dialogue and not self.get_dialogue_flag:

                        if dialogue[2] == -3: #if the index is -3, then a player choice is in progress.
                            #do not change variables and set player_choice_flag to true
                            #self.current_dialogue_index = 0
                            message = ('','')
                            self.get_dialogue_flag = True
                        elif not self.is_initial_index: 
                            #updates to next dialogue index
                            self.last_dialogue_index = self.current_dialogue_index
                            self.current_dialogue_index = dialogue[2]
                            
                            self.get_dialogue_flag = True
                            
                        elif self.is_initial_index: #skips changing index for first dialogue box
                            self.is_initial_index = False
                            
                        
                            
                    
                    self.trigger_once = True
                    message = (' ',' ')#prevents lingering text from previous textbox
                else:
                    self.trigger_once = False
            else:
                expression = 0
        else:
            message = ''
            name = ''
            dialogue_enable= False
            expression = 0
            if self.rect.width > 0:#kills rect
                self.rect = pygame.rect.Rect(0,0,0,0)
        
        return (message, 
                self.player_collision, 
                dialogue_enable, 
                name, 
                expression, 
                self.npc_index_id, 
                (self.player_choice_flag, self.player_choice_key),
                self.enabled)
        
    def force_ini_position(self, scrollx):
        self.rect.x -= scrollx
        self.img_rect.x -= scrollx
    
    
    def force_dialogue_index(self, new_index):
        
        self.player_choice_flag = False
        self.player_choice_key = ''
        self.current_dialogue_index = new_index
        
    
    def display_interaction_prompt(self, dialogue_enable, player_rect, screen):
        if not self.collisions_disabled:
            self.player_collision = self.rect.colliderect(player_rect)
        else:
            self.player_collision = False
        if self.player_collision and self.name != 'invisible_prompt':
            if not dialogue_enable:
                screen.blit(self.interaction_prompt, (self.rect.x, self.rect.y - 24, 32, 32))
        
    def scroll_along(self, scrollx):
        self.rect.x += ( - scrollx)
        self.img_rect.x += ( - scrollx)

    def disable(self):
        if self.enabled:
            self.enabled = False
            self.rect = pygame.Rect.rect(0,0,0,0)
        else:
            pass
    
    def resize_rect(self, new_rect):
        return pygame.rect.Rect(new_rect)
    
    #draw and animate methods
    
    def draw(self, screen):
        if self.enabled and self.rect.x > -self.width and self.rect.x < 640 + self.width:
            screen.blit(pygame.transform.flip(self.image, self.flip, False), self.img_rect)
            #pygame.draw.rect(screen, (255,0,0), self.rect)
        
    def animate(self, sprite_group):
        self.mask = pygame.mask.from_surface(self.image)
        
        framerates = (
            180,
            100,
            100,
            100
        )

        frame_update = framerates[self.action]

        #setting the image
        self.image = self.frame_list[self.action][self.frame_index]
        
        #change frame index---------------------------------------------------------------
        if pygame.time.get_ticks() - self.update_time > frame_update:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1 

        #END OF ANIMATION FRAMES    
        if self.frame_index >= len(self.frame_list[self.action]):
            self.frame_index = 0
    
    #npc sub classes take plot index and current level to decide the dialogue index
    
#each level, NPC's dialogue indexes are reset

