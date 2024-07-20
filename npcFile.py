import pygame
import os
import csv
# from bullet import bullet_ #type: ignore
from particle import particle_ #type: ignore
from music_player import music_player #type: ignore
import random
from textManager import text_manager

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
        self.pil_update_flag = False
        
        self.character_index_dict = {'Test': 0,
                                    'Test2': 1
                                    }
        self.plot_index_list = plot_index_list
        
        self.current_dialogue_index = 0
        self.next_dialogue_index = 0
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
        
        
    #after every textbox, this is called, need to specify name so that npcs can modify the plot index's of other npcs
    def update_plot_index(self, name, new_plot_index):
        if new_plot_index != self.plot_index_list[self.character_index_dict[name]]:
            self.plot_index_list[self.character_index_dict[name]] = new_plot_index
        self.pil_update_flag = True

    def get_message(self, current_dialogue_index):
        message = self.dialogue_list[current_dialogue_index][0]
        next_dialogue_index = self.dialogue_list[current_dialogue_index][1]
        npc_expression = self.dialogue_list[current_dialogue_index][2]
        
        return (message, next_dialogue_index, npc_expression) #string, int
    
    #generally, current_dialogue_index will advance itself by following the next index in the dialogue array
    #self.get_dialogue_index() will only be triggered by specific conditions: level, plot index, current dialogue index and will be called right before
    #and will force current_dialogue_index to some other value in that moment
    def enable(self, dialogue_enable, next_dialogue, screen, font, player_rect, scrollx):
        
        if self.enabled:
            
            #dialogue_enable and next_dialogue are global signals; they might cause multiple NPC's on the same level to speak at once
            #self.display_interaction_prompt adds an additional conditional that will pass only if the player is in the collision range for this specific NPC
            message = ''
            player_collision = self.display_interaction_prompt(dialogue_enable, player_rect, screen)
            if player_collision and dialogue_enable:
                dialogue = self.get_message(self.current_dialogue_index) #returns message and index of next dialogue
                message = dialogue[0]
                expression = dialogue[2]
                
                if next_dialogue:#convert continuous signal next_dialogue into an impulse
                    if self.trigger_once != next_dialogue:
                        if not self.is_initial_index:
                            self.current_dialogue_index = dialogue[1]
                        else:
                            self.is_initial_index = False
                    self.trigger_once = True
                    message = (' ',' ')#prevents lingering text from previous textbox
                else:
                    self.trigger_once = False
            else:
                expression = 0
            
            # if message != '' and player_collision and dialogue_enable:
            #     self.display_text_box(screen, font, message)
                
        self.rect.x += ( - scrollx)
        
        return (message, player_collision, dialogue_enable, self.name, expression, self.character_index_dict[self.name])
    
    def display_interaction_prompt(self, dialogue_enable, player_rect, screen):
        is_interacting = self.rect.colliderect(player_rect)
        if is_interacting and self.name != 'invisible_prompt':
            if not dialogue_enable:
                screen.blit(self.interaction_prompt, (self.rect.x, self.rect.y - 24, 32, 32))
                
        return is_interacting
    
    def display_text_box(self, screen, font, message): #string list
        #calls text manager's display function
        #draws charcter art as well as a back drop for the text box
        #draws exit and next options (esc and enter)
        self.text_manager0.disp_text_box(screen, font, message, (0,0,0),  (200,200,200), 
                                   (0, 360, 640, 120), False, False, 'none')
        
        pass
    
    #i'm still standing
    
    def display_options(self):
        #displays options for player to pick, probably limited to lists of 2
        pass
    
    
    #draw and animate methods
    
    def draw(self, screen):
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
    
class Test(npc):
    def __init__(self, x, y, scale, direction, name, ini_vol, enabled, dialogue_list, plot_index_list, level, player_inventory):
        super().__init__(x, y, scale, direction, name, ini_vol, enabled, dialogue_list, plot_index_list)
        #get plot index 
        self.plot_index = self.plot_index_list[self.character_index_dict[self.name]]

        #self.current_dialogue_index = 0
        self.current_level = level
        self.current_p_inv = player_inventory
        
        self.get_dialogue_index(level, player_inventory, self.current_dialogue_index)

    #npc specific method called at the start of each self.enable()
    
    #using the inputs: level, plot_index, current_dialogue_index
    #set the next dialogue index or advance the plot index if specific parameters are met
    #immediately change 1 or 2 of them such as advancing plot index or switching the dialogue index
    def get_dialogue_index(self, level, player_inventory, current_dialogue_index):
        
        #set initial dialogue index
        #current_dialogue_index will always start at 0 (indicates the start of a level)
        #can be used to disable or enable an npc upon level change (using plot index)
        plot_index = self.plot_index_list[self.character_index_dict[self.name]]
        if current_dialogue_index == 0:
            if level == 1 and plot_index == -1:
                self.current_dialogue_index = 0
                #self.next_dialogue_index = 0
                
            
        #example of how to code using this system
        # elif level == 1 and plot_index == -1 and current_dialogue_index == 3:
        #     self.update_plot_index(1)
        #     current_dialogue_index = 4
        
        else:
            self.current_dialogue_index = self.current_dialogue_index
            

