import pygame
from npcFile import npc

#helper file containing character type NPCs for instantiation
    
class Test(npc):
    def __init__(self, x, y, scale, direction, name, ini_vol, enabled, world, level, player_inventory):
        super().__init__(x, y, scale, direction, name, ini_vol, enabled, world)
        #get plot index
        self.plot_index = self.plot_index_dict[self.name]

        self.current_level = level
        self.current_p_inv = player_inventory
        self.is_npc = True
    #npc specific method called at the start of each self.enable()
    
    #using the inputs: level, plot_index, current_dialogue_index
    #set the next dialogue index or advance the plot index if specific parameters are met
    #immediately change 1 or 2 of them such as advancing plot index or switching the dialogue index
    def get_dialogue_index(self, player, current_dialogue_index, world, selected_slot):
        plot_index = world.plot_index_dict[self.name]
        if plot_index != -1:
            self.current_dialogue_index = self.plot_index_jumps_dict[plot_index]
            self.is_initial_index = False
        
        #2ndary constructor
        if self.is_initial_index:
            if self.current_level == 1 and plot_index == -1:
                self.current_dialogue_index = 0
                #self.disable() #use this method to disable npcs
                
    
        if self.player_collision and self.get_dialogue_flag:
            #print(current_dialogue_index)
            if current_dialogue_index == 0 and self.current_level == 1 and plot_index == -1:
                self.current_dialogue_index = 0

                
            #example of how to code using this system
            # elif level == 1 and plot_index == -1 and current_dialogue_index == 3:
            #     self.update_plot_index(1)
            #     current_dialogue_index = 4
            elif self.current_level == 1 and current_dialogue_index == 3:# and self.plot_index_dict[1] == -1:
                world.plot_index_dict['Test2'] = 1

            else:
                self.current_dialogue_index = self.current_dialogue_index
            self.get_dialogue_flag = False
        else:
            self.get_dialogue_flag = False
            

class Test2(npc):
    def __init__(self, x, y, scale, direction, name, ini_vol, enabled, world, level, player_inventory):
        super().__init__(x, y, scale, direction, name, ini_vol, enabled, world)
        #get plot index 
        self.plot_index = self.plot_index_dict[self.name]
        self.current_level = level
        self.current_p_inv = player_inventory

    #idea for turning these into textfiles:
    #use a dictionary with list as a key, 
    #value will be another list as well, [current_index, plot_index_w_en, plot_index_value, target_character_index]
    #might not be possible... might have to implement some kind of iteraction for writing to plot index
    def get_dialogue_index(self, player, current_dialogue_index, world, selected_slot):
        plot_index = world.plot_index_dict[self.name]
        if plot_index != -1:
            self.current_dialogue_index = self.plot_index_jumps_dict[plot_index]
            self.is_initial_index = False
        
        
        if self.is_initial_index:
            if self.current_level == 1 and plot_index == -1:
                self.current_dialogue_index = 0
                
            
        if self.player_collision and self.get_dialogue_flag:
            if current_dialogue_index == 0 and self.current_level == 1 and plot_index == -1:
                self.current_dialogue_index = 0
  
                
            #example of how to code using this system
            # elif level == 1 and plot_index == -1 and current_dialogue_index == 3:
            #     self.update_plot_index(1)
            #     current_dialogue_index = 4
            elif self.current_dialogue_index == 3:# and self.last_dialogue_index == 2:
                world.plot_index_dict[self.name] = -1

            else:
                self.current_dialogue_index = self.current_dialogue_index
            self.get_dialogue_flag = False
        else:
            self.get_dialogue_flag = False
            

class Mars(npc):
    def __init__(self, x, y, scale, direction, name, ini_vol, enabled, world, level, player_inventory):
        super().__init__(x, y, scale, direction, name, ini_vol, enabled, world)
        #get plot index 
        self.plot_index = self.plot_index_dict[self.name]
        self.current_level = level
        self.current_p_inv = player_inventory
        
        self.rect = pygame.rect.Rect(self.rect.x + 32, self.rect.y, self.width//3, self.height)
        if level == 1 and (world.plot_index_dict[self.name] != -1 or (world.get_death_count(1) not in [0,7] and world.get_death_count(2) != 1)):
            enabled = False
            
        self.enabled = enabled
        
        #self.img_rect 
        
    def get_dialogue_index(self, player, current_dialogue_index, world, selected_slot):
        plot_index = world.plot_index_dict[self.name]
        # print(self.name)
        # print(plot_index)
        if plot_index != -1 and self.is_initial_index:
            self.current_dialogue_index = self.plot_index_jumps_dict[plot_index]
            self.is_initial_index = False
        if self.current_level == 1 and world.get_death_count(1) > 0:
            #self.current_dialogue_index = 3
            #implement smth like this later
            if world.get_death_count(1) == 7 and self.is_initial_index:
                self.current_dialogue_index = 2
        if self.current_level == 1 and world.get_death_count(2) > 0:
            if self.is_initial_index:
                self.current_dialogue_index = 5
                world.set_death_count(2, 0)
            self.is_initial_index = False
        # if self.current_level == 3:
        #     #self.rect = pygame.rect.Rect(self.rect.x, 0, self.width, 15*32)
        #     # self.is_cutscene = True
        #     # self.is_initial_index = False
        #     pass
            
        if (self.current_level == 1 and 
             self.rect.x < -self.rect.width 
            ):
            self.enabled = False
        
        if self.is_initial_index:
            if self.current_level == 1 and plot_index == -1:
                self.current_dialogue_index = 0
                

        if self.player_collision and self.get_dialogue_flag:

            if 1 == 2:
                pass
            else:
                self.current_dialogue_index = self.current_dialogue_index
            self.get_dialogue_flag = False
        else:
            self.get_dialogue_flag = False
