import pygame
from npcFile import npc

class opening_scene(npc):
    def __init__(self, x, y, scale, direction, name, ini_vol, enabled, dialogue_list, plot_index_dict, current_dialogue_list, level, player_inventory):
        super().__init__(x, y, scale, direction, name, ini_vol, enabled, dialogue_list, plot_index_dict)
        #get plot index
        self.plot_index = self.plot_index_dict[self.name]
        if enabled:
            self.rect = self.resize_rect((0, -64, 640, 480))
        else:
            self.rect = self.resize_rect((0, 0, 0, 0))#have to make sure the rect is destroyed immediately in the constructor

        self.current_level = level
        self.current_p_inv = player_inventory
        
        
        self.is_cutscene = True
        self.is_initial_index = False #IMPORTANT IF YOU DON'T WANT THE FIRST MESSAGE REPEATED
        

    def get_dialogue_index(self, level, player_inventory, current_dialogue_index, plot_index_dict, current_dialogue_list):
        plot_index = plot_index_dict[self.name]
            
        if self.player_collision and self.get_dialogue_flag:
            #example of how to code using this system
            # elif level == 1 and plot_index == -1 and current_dialogue_index == 3:
            #     self.update_plot_index(1)
            #     current_dialogue_index = 4
            if self.current_dialogue_index == 12:# and self.last_dialogue_index == 2:
                plot_index_dict[self.name] = -4
                self.enabled = False
            else:
                self.current_dialogue_index = self.current_dialogue_index
            self.get_dialogue_flag = False
        else:
            self.get_dialogue_flag = False
            

