import pygame
from npcFile import npc
from saveHandler import save_file_handler
from textfile_handler import textfile_formatter

#helper file containing cutscene type NPCs for instantiation
#has access to save game infrastructure

cutscene_autosave = save_file_handler()

class opening_scene(npc):
    def __init__(self, x, y, scale, direction, name, ini_vol, enabled, world, dialogue_dict, frame_dict, level, player_inventory):
        super().__init__(x, y, scale, direction, name, ini_vol, enabled, world, dialogue_dict, frame_dict)
        #get plot index
        #self.plot_index = self.plot_index_dict[self.name]
        # if level == 1 and world.plot_index_dict[self.name] >= 10:
        #     enabled = False
        #     #print("?")
        # elif level == 4 and world.plot_index_dict[self.name] >= 20:
        #     enabled = False
        # elif level == 6 and world.plot_index_dict[self.name] >= 30:
        #     enabled = False
        enabled = level in self.enable_dict[world.plot_index_dict[self.name]]

        if enabled:
            self.rect = self.resize_rect((self.rect.x, -64, 640, 480))
        else:
            self.rect = self.resize_rect((0, 0, 0, 0))#have to make sure the rect is destroyed immediately in the constructor
        self.enabled = enabled
        self.autosaved = False
        
        self.current_level = level
        self.current_p_inv = player_inventory
        # print(world.plot_index_dict[self.name])
        # print(self.enabled)
        # print(self.current_dialogue_index)
        
        self.is_cutscene = True
        self.is_initial_index = False #IMPORTANT IF YOU DON'T WANT THE FIRST MESSAGE REPEATED
        self.current_dialogue_index = self.plot_index_jumps_dict[world.plot_index_dict[self.name]]
            

    def get_dialogue_index(self, player, current_dialogue_index, world, sp_group, selected_slot):
        
        if self.player_collision and self.get_dialogue_flag:
            #example of how to code using this system
            # elif level == 1 and plot_index == -1 and current_dialogue_index == 3:
            #     self.update_plot_index(1)
            #     current_dialogue_index = 4
            self.enabled = not self.autosaved
            
            if self.current_dialogue_index == 13:# and self.last_dialogue_index == 2:
                world.plot_index_dict[self.name] = 10
                world.check_onetime_spawn_dict(self.current_level)
                cutscene_autosave.save(selected_slot, self.current_level, world.plot_index_dict, world.lvl_completion_dict, world.onetime_spawn_dict, player)
                self.autosaved = True
            elif self.current_dialogue_index == 33:
                world.plot_index_dict[self.name] = 20
                world.plot_index_dict['Mars'] = 10
                world.check_onetime_spawn_dict(self.current_level)
                cutscene_autosave.save(selected_slot, self.current_level, world.plot_index_dict, world.lvl_completion_dict, world.onetime_spawn_dict, player)
                self.autosaved = True
            elif self.current_dialogue_index == 20:
                self.give_item_en = True
                world.plot_index_dict[self.name] = 30
                world.plot_index_dict['Mars'] = 20
                world.check_onetime_spawn_dict(self.current_level)
                cutscene_autosave.save(selected_slot, self.current_level, world.plot_index_dict, world.lvl_completion_dict, world.onetime_spawn_dict, player)
                self.autosaved = True
            elif self.current_dialogue_index == 36:
                self.give_item('Worn Knee Socks', (player.rect.centerx, player.rect.centery), sp_group)
                #need to reset self.give_item_en some pt after
            else:
                self.current_dialogue_index = self.current_dialogue_index
            self.get_dialogue_flag = False
        else:
            self.get_dialogue_flag = False
            

