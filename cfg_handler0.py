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
                    sub_dict[key] = cfg_file[section][key]
                rtn_dict[section] = sub_dict
            
        del cfg_file
        return rtn_dict
    
# def __main__():
#     cfg0 = cfg_handler()
#     test_dict = cfg0.get_dict_from_cfg('assets\\npc_dialogue_files\\npc_dialogue_txt_files\\Mars.ini')
#     print(test_dict)
    
# __main__()