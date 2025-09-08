import os
import datetime
from textfile_handler import textfile_formatter

class save_file_handler():
    def __init__(self):
        self.PS_str = 'player_state.txt'
        self.PID_str = 'plot_index_dict.txt'
        self.PI_str = 'player_inventory.txt'
        self.LCD_str = 'lvl_completion_dict.txt'
        self.OSD_str = 'onetime_spawn_dict.txt'
        
        self.t1 = textfile_formatter()
        
        self.ini_player_inv = []
        for inv_slot in self.t1.str_list_to_list_list(self.t1.read_text_from_file(os.path.join('assets', 'save_files', 'initial', self.PI_str))):
            self.ini_player_inv.append(['empty', 0])
    
    def save(self, slot, level, plot_index_dict, lvl_completion_dict, onetime_spawn_dict, player):
        txt_file_map = {
            self.PS_str:'',
            self.PID_str:'',
            self.PI_str:'',
            self.LCD_str:'',
            self.OSD_str:''
        }
        
        path = os.path.join('assets', 'save_files', str(slot))
        
        txt_file_map[self.PS_str] = f'level: {level}\nplayer_x: {player.x_coord}\nplayer_y: {player.rect.y - 8}\nhits_tanked: {player.hits_tanked}\nst_cap: {player.stamina_usage_cap}\nchar: {player.char_level}'
        
        str2 = ''
        for key_ in plot_index_dict:
            str2 = str2 + f'{key_}: {plot_index_dict[key_]}\n'
        str2 = str2[0:len(str2)-1]
        txt_file_map[self.PID_str] = str2
            
        str3 = ''
        for slot in player.inventory_handler.inventory:
            str3 = str3 + f'{slot[0]}, {slot[1]}\n'
        str3 = str3[0:len(str3)-1]
        txt_file_map[self.PI_str] = str3
        
        str4 = ''
        for lvl in lvl_completion_dict:
            str4 = str4 + f'{lvl}: {lvl_completion_dict[lvl]}\n'
        str4 = str4[0:len(str4)-1]
        txt_file_map[self.LCD_str] = str4
        
        txt_file_map[self.OSD_str] = self.format_listlistdict_to_str(onetime_spawn_dict)
        
        for entry in txt_file_map:
            self.t1.overwrite_file(os.path.join(path, entry), txt_file_map[entry])
            
    def check_plot_index(self, slot):
        return self.t1.read_text_from_file(os.path.join(os.path.join('assets', 'save_files', str(slot)), self.PID_str))[0] != 'empty'
    
    def get_save_time(self, slot):
        date_str = str(datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(os.path.join('assets', 'save_files', str(slot)), self.PID_str))))
        return date_str[:len(date_str)-7]
            
    def load_save(self, slot):
        saves_path = os.path.join('assets', 'save_files', str(slot))
        
        #initial values
        
        plot_index_dict = {}
        for npc in os.listdir(os.path.join('assets', 'sprites', 'npcs')):
            plot_index_dict[npc] = -1
            
        lvl_completion_dict = {0: 0}
        onetime_spawn_dict = {}
        player_new_coords = (32, 128)
        next_level = 0
        
        #fill inventory
        player_new_inv = self.t1.str_list_to_list_list(self.t1.read_text_from_file(os.path.join(saves_path, self.PI_str)))
        
        #set lvl completion dict
        lvl_completion_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(saves_path, self.LCD_str)), 'int')
        
        #set onetime_spawn_dict
        if self.t1.read_text_from_file(os.path.join(saves_path, self.OSD_str))[0] != 'empty':
            onetime_spawn_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(saves_path, self.OSD_str)), 'list_list')
        else:
            path2 = os.path.join('assets', 'config_textfiles', 'world_config')
            onetime_spawn_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path2, 'ini_onetime_spawns.txt')), 'list_list')
        
        #set plot index
        if self.t1.read_text_from_file(os.path.join(saves_path, self.PID_str))[0] != 'empty': #this way I don't have to keep adding -1 if a player loads from a new save
            #print(self.t1.read_text_from_file(os.path.join(saves_path, self.PID_str)))
            plot_index_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(saves_path, self.PID_str)), 'int')
        
        #get level and player location data
        player_state_data = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(saves_path, self.PS_str)), 'float')
        for key in player_state_data:#process non-floats into int
            if player_state_data[key] == int(player_state_data[key]):
                player_state_data[key] = int(player_state_data[key])
        
        player_new_coords = (player_state_data['player_x'], player_state_data['player_y'])
        
        #get player stats
        player_stats = {'hits_tanked': player_state_data['hits_tanked'], 
                        'st_cap': player_state_data['st_cap'], 
                        'char': player_state_data['char']
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
                
            
    def format_listlistdict_to_str(self, input_dict):#formats data structure to textfile handler readable string
        str_ = ''
        for list_ in input_dict:
            sub_str = ''
            for elmnt in input_dict[list_]:
                
                sub_str2 = ''
                for sub_elmnt in elmnt:
                    sub_str2 = sub_str2 + f'{sub_elmnt}# '
                sub_str2 = sub_str2[0:len(sub_str2)-2]
                
                sub_str = sub_str + f'{sub_str2}; '
            sub_str = sub_str[0:len(sub_str)-2]
            
            str_ = str_ + f'{list_}: {sub_str}\n'
        return str_[0:len(str_)-1]
    
        
    def reset_specific_save(self, slot):
        path = os.path.join('assets', 'save_files', str(slot))
        
        txt_file_map = {
            self.PS_str:f'level: 1\nplayer_x: 32\nplayer_y: 128\nhits_tanked: -1\nst_cap: -1\nchar: 0',
            self.PID_str:'empty',
            self.PI_str:'',
            self.LCD_str:'0: 0',
            self.OSD_str:'empty'
        }
            
        str3 = ''
        for slot in self.t1.str_list_to_list_list(self.t1.read_text_from_file(os.path.join(path, self.PI_str))):
            str3 = str3 + f'empty, 0\n'
        str3 = str3[0:len(str3)-1]
        txt_file_map[self.PI_str] = str3

        for entry in txt_file_map:
            self.t1.overwrite_file(os.path.join(path, entry), txt_file_map[entry])
            
        
    def reset_all_saves(self):
        for i in range(4):
            self.reset_specific_save(i)