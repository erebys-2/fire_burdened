import os
import datetime
from textfile_handler import textfile_formatter
from cfg_handler0 import yaml_handler

class save_file_handler():
    def __init__(self):
        self.PS_str = 'player_state.txt'
        self.PID_str = 'plot_index_dict.txt'
        self.PI_str = 'player_inventory.txt'
        self.LCD_str = 'lvl_completion_dict.txt'
        self.OSD_str = 'onetime_spawn_dict.txt'
        
        self.t1 = textfile_formatter()
        self.y1 = yaml_handler()
        
        self.ini_player_inv = []
        for inv_slot in self.y1.get_data(os.path.join('assets', 'save_files', 'initial.yaml'))['player_inventory']:#self.t1.str_list_to_list_list(self.t1.read_text_from_file(os.path.join('assets', 'save_files', 'initial', self.PI_str))):
            self.ini_player_inv.append(['empty', 0])
    
    def save(self, slot, level, plot_index_dict, lvl_completion_dict, onetime_spawn_dict, player):
        save_data_dict = {}
        save_data_dict['player_state'] = {
            'level': level,
            'player_x': player.x_coord,
            'player_y': player.rect.y - 8,
            'hits_tanked': player.hits_tanked,
            'st_cap': player.stamina_usage_cap,
            'char': player.char_level,
            'lvls_visited': player.lvls_visited
        }
        save_data_dict['plot_index_dict'] = plot_index_dict
        save_data_dict['player_inventory'] = player.inventory_handler.inventory
        save_data_dict['lvl_completion_dict'] = lvl_completion_dict
        save_data_dict['onetime_spawn_dict'] = onetime_spawn_dict
        
        self.y1.write_full_data(save_data_dict, os.path.join('assets', 'save_files', f'{slot}.yaml'))
        
            
    def check_plot_index(self, slot):
        #return self.t1.read_text_from_file(os.path.join(os.path.join('assets', 'save_files', str(slot)), self.PID_str))[0] != 'empty'
        return self.y1.get_data(os.path.join('assets', 'save_files', f'{slot}.yaml'))['plot_index_dict'] != 'empty'
    
    def get_save_time(self, slot):
        date_str = str(datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(os.path.join('assets', 'save_files', f'{slot}.yaml')))))
        return date_str[:len(date_str)-7]
            
    def load_save(self, slot):
        #saves_path = os.path.join('assets', 'save_files', str(slot))
        save_file_dict = self.y1.get_data(os.path.join('assets', 'save_files', f'{slot}.yaml'))
        
        #initial values
        plot_index_dict = {}
        for npc in os.listdir(os.path.join('assets', 'sprites', 'npcs')):
            plot_index_dict[npc] = -1
            
        lvl_completion_dict = {0: 0}
        onetime_spawn_dict = {}
        player_new_coords = (32, 128)
        next_level = 0
        
        #fill inventory
        player_new_inv = save_file_dict['player_inventory']
        
        #set lvl completion dict
        lvl_completion_dict = save_file_dict['lvl_completion_dict']
        
        #set onetime_spawn_dict
        if save_file_dict['onetime_spawn_dict'] != 'empty':
            onetime_spawn_dict = save_file_dict['onetime_spawn_dict']
        else:
            path2 = os.path.join('assets', 'config_textfiles', 'world_config')
            onetime_spawn_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path2, 'ini_onetime_spawns.txt')), 'list_list')
        
        #set plot index
        if save_file_dict['plot_index_dict'] != 'empty':
            plot_index_dict = save_file_dict['plot_index_dict']
        
        #get level and player location data        
        player_state_data = save_file_dict['player_state']
        
        player_new_coords = (player_state_data['player_x'], player_state_data['player_y'])
        
        #get player stats
        player_stats = {'hits_tanked': player_state_data['hits_tanked'], 
                        'st_cap': player_state_data['st_cap'], 
                        'char': player_state_data['char'],
                        'lvls_visited': player_state_data['lvls_visited']
                        }
        
        #set the new level
        next_level = player_state_data['level']
        
        rtn_dict = {
            'PNI': player_new_inv,
            'LCD': lvl_completion_dict,
            'OSD': onetime_spawn_dict,
            'PID': plot_index_dict,
            'PNC': player_new_coords,
            'NL': next_level,
            'PS': player_stats
        }
        
        return rtn_dict
    
    def reset_specific_save2(self, slot):
        default_data = self.y1.get_data(os.path.join('assets', 'save_files', 'initial.yaml'))
        self.y1.write_full_data(default_data, os.path.join('assets', 'save_files', f'{slot}.yaml'))
        
    def reset_all_saves(self):
        for i in range(4):
            self.reset_specific_save2(i)