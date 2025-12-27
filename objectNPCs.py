from npcFile import npc

#helper file containing object type NPCs for instantiation

class save_pt(npc):
    def __init__(self, x, y, scale, direction, name, ini_vol, enabled, world, dialogue_dict, level, player_inventory):
        super().__init__(x, y, scale, direction, name, ini_vol, enabled, world, dialogue_dict)
        self.plot_index = 0
        self.current_level = level
        self.current_p_inv = player_inventory
        self.is_obj = True
        
    def get_dialogue_index(self, player, current_dialogue_index, world, sp_group, selected_slot):
        pass
    
    # def display_interaction_prompt(self, dialogue_enable, player_rect, screen):
    #     self.player_collision = self.rect.colliderect(player_rect)
    #     if self.player_collision and self.name != 'invisible_prompt':
    #         if not dialogue_enable:
    #             #screen.blit(self.interaction_prompt, (self.rect.x + 32, self.rect.y + 32, 32, 32))
    #             screen.blit(self.interaction_prompt, (self.rect.left - 8, self.rect.y - 16))
                

class read_only_obj(npc):
    def __init__(self, x, y, scale, direction, name, ini_vol, enabled, world, dialogue_dict, level, player_inventory):
        super().__init__(x, y, scale, direction, name, ini_vol, enabled, world, dialogue_dict)
        #get plot index 
        #self.plot_index = self.plot_index_dict[self.name]
        self.current_level = level
        self.current_p_inv = player_inventory
        # if level == 1:
        #     self.current_dialogue_index = 0
        self.order_id = world.read_only_obj_id

    #idea for turning these into textfiles:
    #use a dictionary with list as a key, 
    #value will be another list as well, [current_index, plot_index_w_en, plot_index_value, target_character_index]
    #might not be possible... might have to implement some kind of iteraction for writing to plot index
    def get_dialogue_index(self, player, current_dialogue_index, world, sp_group, selected_slot):
        plot_index = world.plot_index_dict[self.name]
        if plot_index > 0:
            self.current_dialogue_index = self.plot_index_jumps_dict[plot_index]
            self.is_initial_index = False
        
        if self.is_initial_index:
            if self.current_level == 1:
                if self.order_id == 0:#256 air jump
                    self.current_dialogue_index = 2
                elif self.order_id == 1:#288
                    self.current_dialogue_index = 3
                elif self.order_id == 2:#288 
                    self.current_dialogue_index = 4
                elif self.order_id == 3:#288 
                    self.current_dialogue_index = 5
            
            elif self.current_level == 4:
                if self.order_id == 1:
                    self.current_dialogue_index = 9
                elif self.order_id == 0:
                    self.current_dialogue_index = 10
                    
            elif self.current_level == 5:
                if self.order_id == 1:
                    self.current_dialogue_index = 6
                elif self.order_id == 2:
                    self.current_dialogue_index = 7
                elif self.order_id == 0:
                    self.current_dialogue_index = 8

        if self.player_collision and self.get_dialogue_flag:
            # if current_dialogue_index == 0 and self.current_level == 1 and plot_index == 0:
            #     self.current_dialogue_index = 0
  
                
            # #example of how to code using this system
            # # elif level == 1 and plot_index == 0 and current_dialogue_index == 3:
            # #     self.update_plot_index(1)
            # #     current_dialogue_index = 4
            # elif self.current_dialogue_index == 3:# and self.last_dialogue_index == 2:
            #     world.plot_index_dict[self.name] = -1

            #else:
            self.current_dialogue_index = self.current_dialogue_index
            self.get_dialogue_flag = False
        else:
            self.get_dialogue_flag = False