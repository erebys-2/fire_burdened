import os

class save_file_handler():
    def __init__(self) -> None:
        pass
    
    def save(self, t1, slot, level, plot_index_dict, lvl_completion_dict, onetime_spawn_dict, player):
        txt_file_map = {
            'level_and_player_coords.txt':'',
            'plot_index_dict.txt':'',
            'player_inventory.txt':'',
            'lvl_completion_dict.txt':'',
            'onetime_spawn_dict.txt':''
        }
        
        path = f'save_files/{slot}'
        
        txt_file_map['level_and_player_coords.txt'] = f'level: {level}\nplayer_x: {player.x_coord}\nplayer_y: {player.rect.y - 8}'
        
        str2 = ''
        for key_ in plot_index_dict:
            str2 = str2 + f'{key_}: {plot_index_dict[key_]}\n'
        str2 = str2[0:len(str2)-1]
        txt_file_map['plot_index_dict.txt'] = str2
            
        str3 = ''
        for slot in player.inventory_handler.inventory:
            str3 = str3 + f'{slot[0]}, {slot[1]}\n'
        str3 = str3[0:len(str3)-1]
        txt_file_map['player_inventory.txt'] = str3
        
        str4 = ''
        for lvl in lvl_completion_dict:
            str4 = str4 + f'{lvl}: {lvl_completion_dict[lvl]}\n'
        str4 = str4[0:len(str4)-1]
        txt_file_map['lvl_completion_dict.txt'] = str4
        
        txt_file_map['onetime_spawn_dict.txt'] = self.format_listlistdict_to_str(onetime_spawn_dict)
        
        for entry in txt_file_map:
            t1.overwrite_file(os.path.join(path, entry), txt_file_map[entry])
            
    def format_listlistdict_to_str(self, input_dict):
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
        
    def reset_specific_save(self, slot, t1):
        path = f'save_files/{slot}'
        
        txt_file_map = {
            'level_and_player_coords.txt':f'level: 1\nplayer_x: 32\nplayer_y: 128',
            'plot_index_dict.txt':'empty',
            'player_inventory.txt':'',
            'lvl_completion_dict.txt':'0: 0',
            'onetime_spawn_dict.txt':'empty'
        }
            
        str3 = ''
        for slot in t1.str_list_to_list_list(t1.read_text_from_file(os.path.join(path, 'player_inventory.txt'))):
            str3 = str3 + f'empty, 0\n'
        str3 = str3[0:len(str3)-1]
        txt_file_map['player_inventory.txt'] = str3

        for entry in txt_file_map:
            t1.overwrite_file(os.path.join(path, entry), txt_file_map[entry])
            
        
    def reset_all_saves(self, t1):
        for i in range(4):
            self.reset_specific_save(i, t1)