import configparser as cfgp
#import os

class cfg_handler():
    def __init__(self):
        pass
    
    def get_dict_from_cfg(self, path_):
        cfg_file = cfgp.ConfigParser()
        cfg_file.read(path_)
        
        rtn_dict = {}
        
        for section in cfg_file:
            if section != 'DEFAULT':
                sub_dict = {}
                for key in cfg_file[section]:
                    key2 = self.auto_string_to_number(key)
                    sub_dict[key2] = self.auto_string_to_number(cfg_file[section][key])
                rtn_dict[section] = sub_dict
            
        del cfg_file
        return rtn_dict
    
    def auto_string_to_number(self, str_):
        rtn_val = str_ #stay a string by default
        if str_ != '':
            
            is_int = True
            is_float = False
            dot_count = 0

            for i in range(0, len(str_)):
                char = str_[i]
                if char not in ('1','2','3','4','5','6','7','8','9','0','-','.'): #letter found, abort
                    is_int = False
                    is_float = False
                    break
                if char == '-' and i != 0: #minus sign must be in the front
                    is_int = False
                    is_float = False
                    break
                if char == '.': #switch to float conversion
                    is_int = False
                    is_float = True
                    dot_count += 1
                if dot_count > 1:
                    is_int = False
                    is_float = False
                    break
                
            if is_int:
                rtn_val = int(str_)
            elif is_float:
                rtn_val = float(str_)
            
        return rtn_val
    
# def __main__():
#     cfg0 = cfg_handler()
#     test_dict = cfg0.get_dict_from_cfg('assets\\npc_dialogue_files\\npc_dialogue_txt_files\\Mars.ini')
#     print(test_dict)
    
# __main__()