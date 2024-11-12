import os

class save_file_handler():
    def __init__(self) -> None:
        pass
    
    def save(self, t1, slot, level, plot_index_dict, player):
        path = f'save_files/{slot}'
        str1 = f'level: {level}\nplayer_x: {player.rect.x}\nplayer_y: {player.rect.y + 8}'
        
        str2 = ''
        for key_ in plot_index_dict:
            str2 = str2 + (f'{key_}: {plot_index_dict[key_]}\n')
        str2 = str2[0:len(str2)-1]
            
        str3 = ''
        for slot in player.inventory_handler.inventory:
            str3 = str3 + f'{slot[0]}, {slot[1]}\n'
        str3 = str3[0:len(str3)-1]
        
        t1.overwrite_file(os.path.join(path, 'level_and_player_coords.txt'), str1)
        t1.overwrite_file(os.path.join(path, 'plot_index_dict.txt'), str2)
        t1.overwrite_file(os.path.join(path, 'player_inventory.txt'), str3)
        
    def reset_specific_save(self, slot, t1):
        path = f'save_files/{slot}'
        str1 = f'level: 1\nplayer_x: 32\nplayer_y: -64'
        
        str2 = 'empty'
            
        str3 = ''
        for slot in t1.str_list_to_list_list(t1.read_text_from_file(os.path.join(path, 'player_inventory.txt'))):
            str3 = str3 + f'empty, 0\n'
        str3 = str3[0:len(str3)-1]
        
        t1.overwrite_file(os.path.join(path, 'level_and_player_coords.txt'), str1)
        t1.overwrite_file(os.path.join(path, 'plot_index_dict.txt'), str2)
        t1.overwrite_file(os.path.join(path, 'player_inventory.txt'), str3)
        
    def reset_all_saves(self, t1):
        for i in range(4):
            self.reset_specific_save(i, t1)