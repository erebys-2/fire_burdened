import pygame
import os
import csv
# from bullet import bullet_ #type: ignore
from music_player import music_player #type: ignore
import random
#from textManager import text_manager
from textfile_handler import textfile_formatter
#from cfg_handler0 import cfg_handler

#NPC class used for sprites with access to text and player choice ui

class npc(pygame.sprite.Sprite):
    #constructor
    def __init__(self, x, y, scale, direction, name, ini_vol, enabled, world, dialogue_dict):#plot index is passed from game_window, to world, then here
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

        self.base_path = os.path.join('assets', 'sprites', 'npcs')
        self.npc_index_id = (os.listdir(self.base_path)).index(name)

        self.plot_index_dict = world.plot_index_dict
        self.old_plot_index = -1
        
        self.current_dialogue_index = 0
        self.last_dialogue_index = 0
        self.is_initial_index = True
        
        self.m_player = music_player(['mc_anvil.mp3'], ini_vol)
        self.ini_vol = ini_vol
        
        self.trigger_once = False
        
        self.frame_list = []
        self.frame_dict = {}
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        
        #action_types = ('idle', 'wave', 'sit', 'shock')
        for action in range(len(os.listdir(os.path.join(self.base_path, self.name)))):#f'assets/sprites/npcs/{self.name}'
            temp_list = []
            frames = len(os.listdir(os.path.join(self.base_path, self.name, str(action))))#f'assets/sprites/npcs/{self.name}/{action}'

            for i in range(frames):
                img = pygame.image.load(os.path.join(self.base_path, self.name, str(action), f'{i}.png')).convert_alpha()#f'assets/sprites/npcs/{self.name}/{action}/{i}.png'
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
                
            #self.frame_list.append(temp_list)
            self.frame_dict[action] = temp_list
        

        self.image = self.frame_dict[self.action][self.frame_index]#frame_list
        self.mask = pygame.mask.from_surface(self.image)
        
        self.rect = self.image.get_rect()
        self.img_rect = self.image.get_rect()
        
        self.rect.topleft = (x,y)
        self.img_rect.topleft = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        self.interaction_prompt = pygame.image.load(os.path.join('assets', 'sprites', 'interaction_prompt.png')).convert_alpha()
        self.interaction_prompt_rect = self.interaction_prompt.get_rect()
        
        #self.text_manager0 = text_manager(0,0,32)
        self.player_collision = False
        self.get_dialogue_flag = False
        
        self.player_choice_flag = False #signal
        self.player_choice_key = '' #key
        
        self.collisions_disabled = False
        #self.dx = 0
        self.ini_coord = [x,y]
        self.speed = 3
        self.dist = 0
        self.direction_set = []#action, distance
        self.frame_rate = 200
        self.ini_frame_rate = 200
        
        self.t1 = textfile_formatter()

        self.dialogue_dict = dialogue_dict
        self.plot_index_jumps_dict = self.dialogue_dict['plot_index_jumps']

    #generally, current_dialogue_index will advance itself by following the next index in the dialogue array
    #self.get_dialogue_index() will only be triggered by specific conditions: level, plot index, current dialogue index and will be called right before
    #and will force current_dialogue_index to some other value in that moment
   
    def enable2(self, dialogue_enable, next_dialogue):
        #print(self.current_dialogue_index)
        str_curr_dialogue_index = str(self.current_dialogue_index)
        message = ''
        name = ''
        expression = 0
        if self.enabled:
            #dialogue_enable and next_dialogue are global booleans in the game window file
  
            if self.player_collision and dialogue_enable:
                expression = int(self.dialogue_dict[str_curr_dialogue_index]['frame'])
                name = self.dialogue_dict[str_curr_dialogue_index]['name']
                
                if not self.player_choice_flag:
                    message = self.dialogue_dict[str_curr_dialogue_index]['msg'] #reformat here
                else:
                    message = ('','')
                
                if self.dialogue_dict[str_curr_dialogue_index]['next'] == -3 and not self.player_choice_flag: #impulse signal
                    self.player_choice_flag = True
                    self.player_choice_key = message[0]
                    next_dialogue = True
                    #print(message)
                # else:
                #     current_dialogue_list[self.npc_index_id] = dialogue[3]
                
                if next_dialogue:#convert continuous signal next_dialogue into an impulse
                    if self.trigger_once != next_dialogue and not self.get_dialogue_flag:

                        if self.dialogue_dict[str_curr_dialogue_index]['next'] == -3: #if the index is -3, then a player choice is in progress.
                            #do not change variables and set player_choice_flag to true
                            #self.current_dialogue_index = 0
                            message = ('','')
                            self.get_dialogue_flag = True
                        elif not self.is_initial_index and self.dialogue_dict[str_curr_dialogue_index]['next'] != -3: #2nd condition is important!!!
                            #updates to next dialogue index
                            self.last_dialogue_index = self.current_dialogue_index
                            self.current_dialogue_index = self.dialogue_dict[str_curr_dialogue_index]['next']
                            self.get_dialogue_flag = True
                            
                        elif self.is_initial_index: #skips changing index for first dialogue box
                            self.is_initial_index = False

                    self.trigger_once = True
                    message = (' ',' ')#prevents lingering text from previous textbox
                else:
                    self.trigger_once = False
        else:
            dialogue_enable= False
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
        if not self.collisions_disabled and self.action in (0,):
            self.player_collision = self.rect.colliderect(player_rect)
            if self.rect.height == 480:
                self.player_collision = self.rect.colliderect(player_rect.scale_by(2, 2))
        else:
            self.player_collision = False
        if self.player_collision and self.name != 'invisible_prompt':
            if not dialogue_enable:
                screen.blit(self.interaction_prompt, (self.rect.x, self.rect.y - 24, 32, 32))
                
    def finish_action(self):
        self.direction_set.pop(0)
        self.dist = 0
        self.frame_rate = self.ini_frame_rate
        
    def scroll_along(self, world_0_coord, scrollx):
        dx = 0
        self.action = 0
        self.dist = 0
        if self.direction_set != []: #set action and distance as the first tuple in direction set (1,123)
            self.action = self.direction_set[0][0]
            self.dist = self.direction_set[0][1]
            self.frame_rate = self.direction_set[0][2]
            
        if self.action == 1:
            if self.dist != 0:
                dx = self.move_x(world_0_coord, self.dist, self.speed)
        
        self.rect.x += (dx - scrollx)
        self.img_rect.x += (dx - scrollx)
        
    def move_x(self, world_0_coord, dist, speed):
        curr_coord = self.rect.x - world_0_coord
        target_coord = dist + self.ini_coord[0]
        
        if curr_coord != target_coord:
            #self.action = 1
            # print(target_coord)
            # print(curr_coord)
            
            if dist >= 0:
                self.direction = 1
            else:
                self.direction = -1
                
            if (curr_coord > target_coord and self.direction > 0) or (curr_coord < target_coord and self.direction < 0):
                dx = target_coord - curr_coord
            else:
                dx = speed * self.direction
        else:
            self.ini_coord[0] += self.dist
            #self.action = 0
            dx = 0
            # self.dist = 0
            # self.direction_set.pop(0)
            self.finish_action()
            
            
        return dx
            

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
        self.flip = self.direction < 0
        
        if self.enabled and self.rect.x > -self.width and self.rect.x < 640 + self.width:
            screen.blit(pygame.transform.flip(self.image, self.flip, False), self.img_rect)
            #pygame.draw.rect(screen, (255,0,0), self.rect)
        
    def animate(self, sprite_group):
        self.mask = pygame.mask.from_surface(self.image)
        

        frame_update = self.frame_rate

        #setting the image
        self.image = self.frame_dict[self.action][self.frame_index]#frame_list
        
        #change frame index---------------------------------------------------------------
        if pygame.time.get_ticks() - self.update_time > frame_update:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1 

        #END OF ANIMATION FRAMES    
        if self.frame_index >= len(self.frame_dict[self.action]):#frame_list
            self.frame_index = 0
    
    #npc sub classes take plot index and current level to decide the dialogue index
    
#each level, NPC's dialogue indexes are reset

