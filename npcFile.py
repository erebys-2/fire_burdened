import pygame
import os
import csv
# from bullet import bullet_ #type: ignore
from particle import particle_ #type: ignore
from music_player import music_player #type: ignore
import random
from textManager import text_manager
from textfile_handler import textfile_formatter

class npc(pygame.sprite.Sprite):
    #constructor
    def __init__(self, x, y, scale, direction, name, ini_vol, enabled, dialogue_list, plot_index_list):#plot index is passed from game_window, to world, then here
        pygame.sprite.Sprite.__init__(self)
        self.direction = direction
        self.enabled = enabled
        self.scale = scale
        self.dialogue_list = dialogue_list
        self.name = name
        self.flip = False
        #self.pil_update_flag = False
        
        self.npc_index_id = (os.listdir('sprites/npcs')).index(name)

        self.plot_index_list = plot_index_list
        
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
        
        action_types = ('idle', 'wave', 'sit', 'shock')
        for action in action_types:
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
        
        self.rect.topleft = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        self.interaction_prompt = pygame.image.load('sprites/interaction_prompt.png').convert_alpha()
        self.interaction_prompt_rect = self.interaction_prompt.get_rect()
        
        self.text_manager0 = text_manager()
        self.player_collision = False
        self.get_dialogue_flag = False
        
        self.player_choice_flag = False #signal
        self.player_choice_key = '' #key
        
        t1 = textfile_formatter()
        #plot index, dialogue index to jump to
        self.plot_index_jumps_dict = t1.str_list_to_dict(t1.read_text_from_file('npc_dialogue_files/npc_plot_index_config/' + self.name + '.txt'), 'int')
        #print(self.plot_index_jumps_dict)
        
    
        
    #after every textbox, this is called, need to specify name so that npcs can modify the plot index's of other npcs
    # def update_plot_index(self, name, new_plot_index):
    #     if new_plot_index != self.plot_index_list[self.npc_index_id]:
    #         self.plot_index_list[self.npc_index_id] = new_plot_index
    #     self.pil_update_flag = True

    def get_message(self, current_dialogue_index):
        message = self.dialogue_list[current_dialogue_index][0]
        next_dialogue_index = self.dialogue_list[current_dialogue_index][1]
        npc_expression = self.dialogue_list[current_dialogue_index][2]
        
        return (message, next_dialogue_index, npc_expression) #string, int
    
    #generally, current_dialogue_index will advance itself by following the next index in the dialogue array
    #self.get_dialogue_index() will only be triggered by specific conditions: level, plot index, current dialogue index and will be called right before
    #and will force current_dialogue_index to some other value in that moment
    def enable(self, dialogue_enable, next_dialogue, current_dialogue_list):
        if self.enabled:
            
            #dialogue_enable and next_dialogue are global booleans in the game window file
            message = ''
            if self.player_collision and dialogue_enable:
                #print(self.current_dialogue_index)
                
                dialogue = self.get_message(self.current_dialogue_index) #returns message and index of next dialogue
                expression = dialogue[2]
                
                if not self.player_choice_flag:
                    message = dialogue[0] #reformat here
                else:
                    message = ('','')
                
                if dialogue[1] == -3 and not self.player_choice_flag: #impulse signal
                    self.player_choice_flag = True
                    self.player_choice_key = message[0]
                    next_dialogue = True
                    #print(message)
                else:
                    current_dialogue_list[self.npc_index_id] = dialogue[1]
                
                if next_dialogue:#convert continuous signal next_dialogue into an impulse
                    #print(self.is_initial_index)
                    if self.trigger_once != next_dialogue and not self.get_dialogue_flag:
                        #print(current_dialogue_list) the indexing is really weird
                        #print(dialogue[1])
                        if dialogue[1] == -3: #if the index is -3, then a player choice is in progress.
                            #do not change variables and set player_choice_flag to true
                            #self.current_dialogue_index = 0
                            message = ('','')
                            self.get_dialogue_flag = True
                        #doesn't do dialogue index changing if is_initial_index is true
                        #you don't want the first interaction iterate through the indexes
                        elif not self.is_initial_index: 
                            #updates to next dialogue index
                            self.last_dialogue_index = self.current_dialogue_index
                            self.current_dialogue_index = dialogue[1]
                            
                            self.get_dialogue_flag = True
                            
                        elif self.is_initial_index: #skips changing index for first dialogue box
                            self.is_initial_index = False
                            
                        
                            
                    
                    self.trigger_once = True
                    message = (' ',' ')#prevents lingering text from previous textbox
                else:
                    self.trigger_once = False
            else:
                expression = 0
        
        return (message, 
                self.player_collision, 
                dialogue_enable, 
                self.name, 
                expression, 
                self.npc_index_id, 
                (self.player_choice_flag, self.player_choice_key))
        
    def force_ini_position(self, scrollx):
        self.rect.x -= scrollx
    
    
    def force_dialogue_index(self, new_index):
        
        self.player_choice_flag = False
        self.player_choice_key = ''
        self.current_dialogue_index = new_index

        
    
    
    
    def display_interaction_prompt(self, dialogue_enable, player_rect, screen):
        self.player_collision = self.rect.colliderect(player_rect)
        if self.player_collision and self.name != 'invisible_prompt':
            if not dialogue_enable:
                screen.blit(self.interaction_prompt, (self.rect.x, self.rect.y - 24, 32, 32))
        
    def scroll_along(self, scrollx):
        self.rect.x += ( - scrollx)

    def disable(self):
        if self.enabled:
            self.enabled = False
            self.rect = (0,0,0,0)
        else:
            pass
    
    #draw and animate methods
    
    def draw(self, screen):
        if self.enabled and self.rect.x > -self.width and self.rect.x < 640 + self.width:
            screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        
    def animate(self, sp_group_list):
        self.mask = pygame.mask.from_surface(self.image)
        
        framerates = (
            100,
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
    
class Test(npc):
    def __init__(self, x, y, scale, direction, name, ini_vol, enabled, dialogue_list, plot_index_list, current_dialogue_list, level, player_inventory):
        super().__init__(x, y, scale, direction, name, ini_vol, enabled, dialogue_list, plot_index_list)
        #get plot index
        self.plot_index = self.plot_index_list[self.npc_index_id]

        #self.current_dialogue_index = 0
        self.current_level = level
        self.current_p_inv = player_inventory
        
        self.get_dialogue_index(level, player_inventory, self.current_dialogue_index, plot_index_list, current_dialogue_list)

    #npc specific method called at the start of each self.enable()
    
    #using the inputs: level, plot_index, current_dialogue_index
    #set the next dialogue index or advance the plot index if specific parameters are met
    #immediately change 1 or 2 of them such as advancing plot index or switching the dialogue index
    def get_dialogue_index(self, level, player_inventory, current_dialogue_index, plot_index_list, current_dialogue_list):
        plot_index = plot_index_list[self.npc_index_id]
        if plot_index != -1:
            self.current_dialogue_index = self.plot_index_jumps_dict[plot_index]
            self.is_initial_index = False
        
        #2ndary constructor
        if self.is_initial_index:
            if level == 1 and plot_index == -1:
                self.current_dialogue_index = 0
                #self.disable() #use this method to disable npcs
                
    
        if self.player_collision and self.get_dialogue_flag:
            #print(current_dialogue_index)
            if current_dialogue_index == 0:
                if level == 1 and plot_index == -1:
                    self.current_dialogue_index = 0
                    #self.next_dialogue_index = 0
                    
                
            #example of how to code using this system
            # elif level == 1 and plot_index == -1 and current_dialogue_index == 3:
            #     self.update_plot_index(1)
            #     current_dialogue_index = 4
            elif level == 1 and current_dialogue_index == 3:# and self.plot_index_list[1] == -1:
                plot_index_list[1] = 1
                #self.pil_update_flag = True
            
            else:
                self.current_dialogue_index = self.current_dialogue_index
            self.get_dialogue_flag = False
        else:
            self.get_dialogue_flag = False
            

class Test2(npc):
    def __init__(self, x, y, scale, direction, name, ini_vol, enabled, dialogue_list, plot_index_list, current_dialogue_list, level, player_inventory):
        super().__init__(x, y, scale, direction, name, ini_vol, enabled, dialogue_list, plot_index_list)
        #get plot index 
        self.plot_index = self.plot_index_list[self.npc_index_id]

        #self.current_dialogue_index = 0
        self.current_level = level
        self.current_p_inv = player_inventory
        
        self.get_dialogue_index(level, player_inventory, self.current_dialogue_index, plot_index_list, current_dialogue_list)

    def get_dialogue_index(self, level, player_inventory, current_dialogue_index, plot_index_list, current_dialogue_list):
        plot_index = plot_index_list[self.npc_index_id]
        if plot_index != -1:
            self.current_dialogue_index = self.plot_index_jumps_dict[plot_index]
            self.is_initial_index = False
        
        
        if self.is_initial_index:
            if level == 1 and plot_index == -1:
                self.current_dialogue_index = 0
                
            
        if self.player_collision and self.get_dialogue_flag:
            if current_dialogue_index == 0 and plot_index == -1:
                if level == 1 and plot_index == -1:
                    self.current_dialogue_index = 0
                    #self.next_dialogue_index = 0
                    
                
            #example of how to code using this system
            # elif level == 1 and plot_index == -1 and current_dialogue_index == 3:
            #     self.update_plot_index(1)
            #     current_dialogue_index = 4
            elif self.current_dialogue_index == 3:# and self.last_dialogue_index == 2:
                plot_index_list[self.npc_index_id] = -1
                
                #self.pil_update_flag = True

            
            else:
                self.current_dialogue_index = self.current_dialogue_index
            self.get_dialogue_flag = False
        else:
            self.get_dialogue_flag = False
            
