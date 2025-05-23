import pygame
from npcFile import npc
from saveHandler import save_file_handler
from textfile_handler import textfile_formatter

#helper file containing cutscene type NPCs for instantiation
#has access to save game infrastructure

cutscene_autosave = save_file_handler()

class opening_scene(npc):
    def __init__(self, x, y, scale, direction, name, ini_vol, enabled, world, level, player_inventory):
        super().__init__(x, y, scale, direction, name, ini_vol, enabled, world)
        #get plot index
        #self.plot_index = self.plot_index_dict[self.name]
        if level == 1 and world.plot_index_dict[self.name] <= -4:
            enabled = False
        elif level == 3 and world.plot_index_dict[self.name] <= -5:
            enabled = False

        if enabled:
            self.rect = self.resize_rect((self.rect.x, -64, 640, 480))
        else:
            self.rect = self.resize_rect((0, 0, 0, 0))#have to make sure the rect is destroyed immediately in the constructor
        self.enabled = enabled
        
        self.current_level = level
        self.current_p_inv = player_inventory
        # print(world.plot_index_dict[self.name])
        # print(self.enabled)
        # print(self.current_dialogue_index)
        
        self.is_cutscene = True
        self.is_initial_index = False #IMPORTANT IF YOU DON'T WANT THE FIRST MESSAGE REPEATED
        if world.plot_index_dict[self.name] != -1:
            self.current_dialogue_index = self.plot_index_jumps_dict[world.plot_index_dict[self.name]]
        

    def get_dialogue_index(self, player, current_dialogue_index, world, selected_slot):
        
        if self.player_collision and self.get_dialogue_flag:
            #example of how to code using this system
            # elif level == 1 and plot_index == -1 and current_dialogue_index == 3:
            #     self.update_plot_index(1)
            #     current_dialogue_index = 4
                
            if self.current_dialogue_index == 14:# and self.last_dialogue_index == 2:
                world.plot_index_dict[self.name] = -4
                self.enabled = False
                world.check_onetime_spawn_dict(self.current_level)
                cutscene_autosave.save(selected_slot, self.current_level, world.plot_index_dict, world.lvl_completion_dict, world.onetime_spawn_dict, player)
            elif self.current_dialogue_index == 21:
                world.plot_index_dict[self.name] = -5
                world.plot_index_dict['Mars'] = 1
                self.enabled = False
                world.check_onetime_spawn_dict(self.current_level)
                cutscene_autosave.save(selected_slot, self.current_level, world.plot_index_dict, world.lvl_completion_dict, world.onetime_spawn_dict, player)
            else:
                self.current_dialogue_index = self.current_dialogue_index
            self.get_dialogue_flag = False
        else:
            self.get_dialogue_flag = False
            

