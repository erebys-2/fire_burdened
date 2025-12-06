import configparser as cfgp
import yaml
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
    
class yaml_handler():
    def __init__(self):
        pass
    
    def get_data(self, path):
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return data
    
    def write_full_data(self, data, path, sort=False):
        with open(path, 'w') as f:
            yaml.dump(data, f, indent=4, sort_keys=sort)
            
    def write_value(self, path, key, value, sort=False):
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            
        data[key] = value
        
        with open(path, 'w') as f:
            yaml.dump(data, f, indent=4, sort_keys=sort)
                
    def format_complex_str(self, str_, force_none=False):
        if force_none:
            self.filter_word(str_, 'None', '~')
        
        return yaml.safe_load(str_)
    
    def filter_word(self, str_, word, replacement):
        index_ = str_.find(word)
        while index_ != -1:
            #print('hit')
            str_ = str_[0:index_] + replacement + str_[index_ + len(word):len(str_)]
            index_ = str_.find(word)
        
        return str_
    
# def __main__():
#     cfg0 = cfg_handler()
#     test_dict = cfg0.get_dict_from_cfg('assets\\npc_dialogue_files\\npc_dialogue_txt_files\\Mars.ini')
#     print(test_dict)
    
# __main__()