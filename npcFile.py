import pygame
import os
import csv
# from bullet import bullet_ #type: ignore
from music_player import music_player #type: ignore
import random
#from textManager import text_manager
from textfile_handler import textfile_formatter
from ItemFile import Item

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
        #self.last_dialogue_index = 0
        self.is_initial_index = True
        
        self.m_player = music_player(['mc_anvil.mp3'], ini_vol)
        self.ini_vol = ini_vol
        
        font_path = os.path.join('assets', 'FiraCode-Regular.ttf')
        self.font = pygame.font.Font(font_path, 10)
        #self.trigger_once = False
        
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
        
        self.give_item_en = True

    #generally, current_dialogue_index will advance itself by following the next index in the dialogue array
    #self.get_dialogue_index() will only be triggered by specific conditions: level, plot index, current dialogue index and will be called right before
    #and will force current_dialogue_index to some other value in that moment
   
    def enable2(self, dialogue_enable, next_dialogue):
        #print(self.current_dialogue_index)
        str_curr_dialogue_index = str(self.current_dialogue_index) #keys in a the dictionary must be str
        message = ('','')
        name = ''
        expression = 0

        if self.enabled and self.player_collision and dialogue_enable:
            expression = int(self.dialogue_dict[str_curr_dialogue_index]['frame'])
            name = self.dialogue_dict[str_curr_dialogue_index]['name']
            next_index = self.dialogue_dict[str_curr_dialogue_index]['next'] #already an int
            message = self.dialogue_dict[str_curr_dialogue_index]['msg'] #reformat here

            #handle player choice logic
            if next_index == 'choice' and not self.player_choice_flag: #impulse signal
                self.player_choice_flag = True
                self.player_choice_key = message[0]
                next_dialogue = True

            #handle increment logic
            if next_dialogue and not self.get_dialogue_flag:
                if next_index == 'next': #auto increment
                    self.current_dialogue_index += 1
                elif next_index != 'choice': #not player choice event
                    self.current_dialogue_index = next_index
                self.get_dialogue_flag = True
                
        elif not self.enabled:
            dialogue_enable= False
            if self.rect.width > 0:#kills rect
                self.rect = pygame.rect.Rect(0,0,0,0)
        
        return {
            'data': {'name': name, 'real_name': self.name, 'msg': message, 'expression': expression},#, 'curr_index': self.current_dialogue_index},
            'logic': {'npc_en': self.enabled, 'dialogue_en': dialogue_enable, 'colliding': self.player_collision},
            'p_choice': {'flag': self.player_choice_flag, 'key': self.player_choice_key}
        }

        
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
        if self.player_collision and self.name != 'invisible_prompt' and not dialogue_enable:
            screen.blit(self.interaction_prompt, (self.rect.centerx - 18, self.rect.y - 24, 32, 32))
            screen.blit(self.font.render('[Enter]', False, (255,255,255)), (self.rect.centerx - 22, self.rect.y - 32))
                
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
            
    def give_item(self, item_name, pos, sprite_group):
        if self.give_item_en:
            sprite_group.item_group.add(Item(item_name, pos[0], pos[1], 1, True))
            self.give_item_en = False
            
        return not self.give_item_en
    
    def rst_dialogue_index(self, world):
        self.current_dialogue_index = self.plot_index_jumps_dict[world.plot_index_dict[self.name]]
