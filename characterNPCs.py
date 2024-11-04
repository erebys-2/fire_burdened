from npcFile import npc
#file for character type NPCs
    
class Test(npc):
    def __init__(self, x, y, scale, direction, name, ini_vol, enabled, dialogue_list, plot_index_dict, current_dialogue_list, level, player_inventory):
        super().__init__(x, y, scale, direction, name, ini_vol, enabled, dialogue_list, plot_index_dict)
        #get plot index
        self.plot_index = self.plot_index_dict[self.name]

        #self.current_dialogue_index = 0
        self.current_level = level
        self.current_p_inv = player_inventory
        self.is_npc = True
        
        #self.get_dialogue_index(level, player_inventory, self.current_dialogue_index, plot_index_dict, current_dialogue_list)

    #npc specific method called at the start of each self.enable()
    
    #using the inputs: level, plot_index, current_dialogue_index
    #set the next dialogue index or advance the plot index if specific parameters are met
    #immediately change 1 or 2 of them such as advancing plot index or switching the dialogue index
    def get_dialogue_index(self, level, player_inventory, current_dialogue_index, plot_index_dict, current_dialogue_list):
        plot_index = plot_index_dict[self.name]
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
            if current_dialogue_index == 0 and level == 1 and plot_index == -1:
                self.current_dialogue_index = 0
                    #self.next_dialogue_index = 0
                    
                
            #example of how to code using this system
            # elif level == 1 and plot_index == -1 and current_dialogue_index == 3:
            #     self.update_plot_index(1)
            #     current_dialogue_index = 4
            elif level == 1 and current_dialogue_index == 3:# and self.plot_index_dict[1] == -1:
                plot_index_dict['Test2'] = 1
                #self.pil_update_flag = True
            
            else:
                self.current_dialogue_index = self.current_dialogue_index
            self.get_dialogue_flag = False
        else:
            self.get_dialogue_flag = False
            

class Test2(npc):
    def __init__(self, x, y, scale, direction, name, ini_vol, enabled, dialogue_list, plot_index_dict, current_dialogue_list, level, player_inventory):
        super().__init__(x, y, scale, direction, name, ini_vol, enabled, dialogue_list, plot_index_dict)
        #get plot index 
        self.plot_index = self.plot_index_dict[self.name]

        #self.current_dialogue_index = 0
        self.current_level = level
        self.current_p_inv = player_inventory
        
        self.get_dialogue_index(level, player_inventory, self.current_dialogue_index, plot_index_dict, current_dialogue_list)

    #idea for turning these into textfiles:
    #use a dictionary with list as a key, 
    #value will be another list as well, [current_index, plot_index_w_en, plot_index_value, target_character_index]
    #might not be possible... might have to implement some kind of iteraction for writing to plot index
    def get_dialogue_index(self, level, player_inventory, current_dialogue_index, plot_index_dict, current_dialogue_list):
        plot_index = plot_index_dict[self.name]
        if plot_index != -1:
            self.current_dialogue_index = self.plot_index_jumps_dict[plot_index]
            self.is_initial_index = False
        
        
        if self.is_initial_index:
            if level == 1 and plot_index == -1:
                self.current_dialogue_index = 0
                
            
        if self.player_collision and self.get_dialogue_flag:
            if current_dialogue_index == 0 and level == 1 and plot_index == -1:
                self.current_dialogue_index = 0
                    #self.next_dialogue_index = 0
                    
                
            #example of how to code using this system
            # elif level == 1 and plot_index == -1 and current_dialogue_index == 3:
            #     self.update_plot_index(1)
            #     current_dialogue_index = 4
            elif self.current_dialogue_index == 3:# and self.last_dialogue_index == 2:
                plot_index_dict[self.name] = -1
                
                #self.pil_update_flag = True

            
            else:
                self.current_dialogue_index = self.current_dialogue_index
            self.get_dialogue_flag = False
        else:
            self.get_dialogue_flag = False
            

