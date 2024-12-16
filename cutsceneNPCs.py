import pygame
from npcFile import npc
from saveHandler import save_file_handler
from textfile_handler import textfile_formatter

#helper file containing cutscene type NPCs for instantiation
#has access to save game infrastructure

cutscene_autosave = save_file_handler()
custscene_t1 = textfile_formatter()

class opening_scene(npc):
    def __init__(self, x, y, scale, direction, name, ini_vol, enabled, world, level, player_inventory):
        super().__init__(x, y, scale, direction, name, ini_vol, enabled, world)
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
        

    def get_dialogue_index(self, player, current_dialogue_index, world, selected_slot):
            
        if self.player_collision and self.get_dialogue_flag:
            #example of how to code using this system
            # elif level == 1 and plot_index == -1 and current_dialogue_index == 3:
            #     self.update_plot_index(1)
            #     current_dialogue_index = 4
            if self.current_dialogue_index == 13:# and self.last_dialogue_index == 2:
                world.plot_index_dict[self.name] = -4
                self.enabled = False
                cutscene_autosave.save(custscene_t1, selected_slot, self.current_level, world.plot_index_dict, player)
            else:
                self.current_dialogue_index = self.current_dialogue_index
            self.get_dialogue_flag = False
        else:
            self.get_dialogue_flag = False
            

