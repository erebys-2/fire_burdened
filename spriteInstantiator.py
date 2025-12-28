import pygame
import os
from enemy32File import enemy_32wide
from articulated_enemy import ms_enemy
from pecker_enemy import pecker
from BGspritesFile import tree, fountain, lamp
from player_interactable import player_interactable_
from characterNPCs import Test, Test2, Mars
from objectNPCs import save_pt, read_only_obj
from cutsceneNPCs import opening_scene
from ItemFile import Item
from music_player import music_player
from cfg_handler0 import yaml_handler
from textfile_handler import textfile_formatter

#Helper class for world, for instantiating special tiles in game layer as sprites.
#During level loading, when world.process_data is called, this reads data from 
# fire_burdened\config_textfiles\world_config\sprite_group_tiles_dict.txt,
#then adds sprites into sprite groups in the_sprite_group 

class sprite_instantiator():
    def __init__(self):
        print('loading sprite instantiator')
        base_path = os.path.join('assets', 'sprites')
        self.bg_sprite_img_dict = self.load_img_dict(os.path.join(base_path, 'bg_sprites'))
        self.enemy_img_dict = self.load_img_dict2(os.path.join(base_path, 'enemies'), 2)
        self.enemy_img_dict_x1 = self.load_img_dict2(os.path.join(base_path, 'enemies'), 1)
        self.p_int_img_dict = self.load_img_dict2(os.path.join(base_path, 'player_interactable'), 1)
        self.npc_img_dict = self.load_img_dict2(os.path.join(base_path, 'npcs'), 2)
        self.npc_img_dict_small = self.load_img_dict2(os.path.join(base_path, 'npcs'), 1, dir_filter=('read_only_obj', 'save_pt', 'opening_scene'))
        
        sfx_path = os.path.join('assets', 'sfx')
        self.master_sfx_list = []
        self.sfx_index_dict = {}
        i = 0
        for sound in os.listdir(sfx_path):
            self.sfx_index_dict[sound] = i
            self.master_sfx_list.append(pygame.mixer.Sound(os.path.join(sfx_path, sound)))#f'{sfx_path}/{sound}'
            i += 1
            
        self.ini_vol = 0
        self.m_player = music_player(None, self.ini_vol)
        self.m_player.sfx = self.master_sfx_list
        
        #loading dialogue dicts
        # cfgp0 = cfg_handler()
        # self.all_dialogue_dict = {}
        # npc_path = os.path.join('assets', 'npc_dialogue_files', 'npc_dialogue_txt_files')
        # for file in os.listdir(npc_path):
        #     if file[-4:] == '.ini':
        #         self.all_dialogue_dict[file[:-4]] = cfgp0.get_dict_from_cfg(os.path.join(npc_path, file))
                
        yh1 = yaml_handler()
        self.all_dialogue_dict = {}
        npc_path = os.path.join('assets', 'npc_dialogue_files', 'npc_dialogue_txt_files')
        for file in os.listdir(npc_path):
            if file[-5:] == '.yaml':
                self.all_dialogue_dict[file[:-5]] = yh1.get_data(os.path.join(npc_path, file))
                
        #this is gonna be so slow... post processing npc dialogue to dialogue lists
        t1 = textfile_formatter()
        for npc_dict in self.all_dialogue_dict:
            for line in self.all_dialogue_dict[npc_dict]:
                for key in self.all_dialogue_dict[npc_dict][line]:
                    if key == 'msg':
                        tmp_str = self.all_dialogue_dict[npc_dict][line][key]
                        self.all_dialogue_dict[npc_dict][line][key] = t1.split_string2(tmp_str, 60)#, t1.endcase_char)
                        
        config_path = os.path.join('assets', 'config_textfiles', 'world_config', 'particle_alignment_dict.txt')
        self.particle_alignment_dict = t1.str_list_to_dict(t1.read_text_from_file(config_path), 'bool')
                        
        #self.plot_index_jump_dict =  os.path.join('assets', 'npc_dialogue_files', 'npc_plot_index_config')
                
        print('sprite instantiator loaded!')
        
    
    def load_img_dict2(self, asset_path, scale, dir_filter=None):#3 layers deep
        img_dict = {}
        if dir_filter == None:
            l = os.listdir(asset_path)
        else:
            l = [dir_ for dir_ in os.listdir(asset_path) if dir_ in dir_filter]
        for subdir in l:
            frame_dict = {}
            #print(subdir)
            subdir_path = os.path.join(asset_path, subdir)#f'{asset_path}/{subdir}'
            subdir2_ct = 0
            for subdir2 in os.listdir(subdir_path):
                #print('     '+subdir2)
                temp_list = []
                for i in range(len(os.listdir(os.path.join(subdir_path, subdir2)))):#f'{subdir_path}/{subdir2}'
                    #print('             ' + 'frame: ' + str(i))
                    loaded_img = pygame.image.load(os.path.join(subdir_path, subdir2, f'{i}.png')).convert_alpha()#f'{subdir_path}/{subdir2}/{i}.png'
                    loaded_img = pygame.transform.scale(loaded_img, (int(loaded_img.get_width() * scale), int(loaded_img.get_height() * scale)))
                    enemy_path = os.path.join('assets', 'sprites', 'enemies')
                    if asset_path == enemy_path and f'{subdir2}' == '2' and subdir != 'worm':#enemy spaghetti code :(
                        if i < 2:
                            loaded_img = pygame.transform.scale(loaded_img, (int(loaded_img.get_width() * 0.8), int(loaded_img.get_height() * 1.1)))
                        elif i == 2:
                            loaded_img = pygame.transform.scale(loaded_img, (int(loaded_img.get_width() * 1.1), int(loaded_img.get_height() * 0.9)))
                    elif asset_path == enemy_path and subdir == 'worm':#and int(subdir2) in (0,3)
                        if int(subdir2) in (0,3):
                            scale2 = 1.5
                        else:
                            scale2 = 1.2
                        loaded_img = pygame.transform.scale(loaded_img, (int(loaded_img.get_width() * scale2), int(loaded_img.get_height() * scale2)))
                            

                    temp_list.append(loaded_img)

                try:
                    key = int(subdir2)
                except:
                    key = subdir2_ct
                subdir2_ct += 1
                frame_dict[key] = temp_list
            img_dict[subdir] = frame_dict
            
        return img_dict
    
    def load_img_dict(self, asset_path):#2 layer deep
        img_dict = {}
        for subdir in os.listdir(asset_path):
            temp_list = []
            for i in range(len(os.listdir(os.path.join(asset_path, subdir)))):#f'{asset_path}/{subdir}'
                loaded_img = pygame.image.load(os.path.join(asset_path, subdir, f'{i}.png')).convert_alpha()#f'{asset_path}/{subdir}/{i}.png'
                temp_list.append(loaded_img)
            img_dict[subdir] = temp_list
            
        return img_dict
    
    def add_hsl_particles(self, img_dict, centered_dict, name_list):
        for data_tuple in name_list:
            name = data_tuple[0]
            
            if name in img_dict:
                new_name = data_tuple[1]
                h = data_tuple[2]
                s = data_tuple[3]
                l = data_tuple[4]
                temp_list = []
                for img in img_dict[name]:
                    temp_list.append(pygame.transform.hsl(img, h, s, l))
                img_dict[new_name] = temp_list
                
                if centered_dict[name]:
                    centered_dict[new_name] = True
        
        return img_dict, centered_dict
    
    def add_text_particles(self, img_dict, centered_dict, font_, new_name, color, str_):
        img_list = []
        for char_ in str_:
            img_list.append(font_.render(char_, False, color))
        img_dict[new_name] = img_list
        centered_dict[new_name] = True
        
        return img_dict, centered_dict
    
    def get_sfx_list(self, str_list):
        sfx_list = []
        for str_ in str_list:
            sfx_list.append(self.master_sfx_list[self.sfx_index_dict[str_]])
            
        return sfx_list

    def instantiate_sprites_from_tiles(self, tile, x, y, the_sprite_group, ini_vol, level, player_inventory, world):
        if self.ini_vol != ini_vol:
            self.m_player.set_vol_all_sounds(ini_vol)
            self.ini_vol = ini_vol
        
        if tile == 74:
            #Note that tile order priority is row then column
            onetime_sprite_info = world.onetime_spawn_dict[level][world.ots_id]
            ot_category = onetime_sprite_info[0]
            ot_sprite_id = onetime_sprite_info[1]
            ot_sprite_en = onetime_sprite_info[2] == 'True' #the bool() function in python returns bool('False') = True FUCK
            #print(f'sp inst: {ot_sprite_en}')
            if ot_sprite_en:
                if ot_category == 'item':
                    the_sprite_group.item_group.add(Item(ot_sprite_id, x*32 + 16, y*32 + 16, 1, True))
                    
                    if the_sprite_group.item_group not in world.sp_groups_to_check:
                        world.sp_groups_to_check.append(the_sprite_group.item_group)
            
            
            world.ots_id += 1
            
        else:
            
            sprite_info = world.sprite_group_tiles_dict[tile]
            sprite_category = sprite_info[0]
            sprite_subcategory = sprite_info[2]
            sprite_id = sprite_info[1]

            #enemies and player interactables/obstacles
            if not world.lvl_completed and sprite_category == 'enemy':
                if sprite_id == 'dog':
                    enemy0 = enemy_32wide(x * 32, y * 32, 3, 2, 'dog', world.enemy0_order_id, ini_vol, self.enemy_img_dict[sprite_id], 
                                          self.get_sfx_list(['bassdrop2.mp3', 'hit.mp3', 'dog_hurt.mp3', 'woof.mp3', 'step2soft.mp3', 'hit2.mp3']))
                    the_sprite_group.enemy0_group.add(enemy0)
                    #world.enemy0_order_id += 1#for enemy-enemy collisions/ anti stacking
                elif sprite_id == 'shooter':
                    enemy0 = enemy_32wide(x * 32, y * 32, 2, 2, 'shooter', world.enemy0_order_id, ini_vol, self.enemy_img_dict[sprite_id],
                                          self.get_sfx_list(['bassdrop2.mp3', 'hit.mp3', 'roblox2.mp3', 'shoot.mp3', 'step2soft.mp3', 'hit2.mp3']))
                    the_sprite_group.enemy0_group.add(enemy0)
                    #world.enemy0_order_id += 1
                elif sprite_id == 'fly':
                    enemy0 = enemy_32wide(x * 32, y * 32, 3, 2, 'fly', world.enemy0_order_id, ini_vol, self.enemy_img_dict[sprite_id],
                                          self.get_sfx_list(['bassdrop2.mp3', 'hit.mp3', 'bee_hurt.mp3', 'bee.mp3', 'step2soft.mp3', 'hit2.mp3', 'shoot.mp3']))
                    the_sprite_group.enemy0_group.add(enemy0)
                    #world.enemy0_order_id += 1
                elif sprite_id == 'walker':
                    enemy0 = enemy_32wide(x * 32, y * 32, 2, 2, 'walker', world.enemy0_order_id, ini_vol, self.enemy_img_dict[sprite_id],
                                          self.get_sfx_list(['bassdrop2.mp3', 'hit.mp3', 'cough.mp3', 'bite.mp3', 'step2soft.mp3', 'hit2.mp3']))
                    the_sprite_group.enemy0_group.add(enemy0)
                    #world.enemy0_order_id += 1
                elif sprite_id == 'walker_v2':
                    enemy0 = enemy_32wide(x * 32, y * 32, 2, 2, 'walker_v2', world.enemy0_order_id, ini_vol, self.enemy_img_dict['walker'],
                                          self.get_sfx_list(['bassdrop2.mp3', 'hit.mp3', 'cough.mp3', 'bite.mp3', 'step2soft.mp3', 'hit2.mp3', 'mc_anvil.mp3']))
                    the_sprite_group.enemy0_group.add(enemy0)
                    #world.enemy0_order_id += 1
                elif sprite_id == 'worm':
                    enemy0 = ms_enemy(x * 32, y * 32, 2, 2, 'worm', world.enemy0_order_id, ini_vol, self.enemy_img_dict_x1[sprite_id],
                                          self.get_sfx_list(['bassdrop2.mp3', 'hit.mp3', 'cough.mp3', 'dog_hurt.mp3', 'boonk.mp3', 'hit2.mp3', 'woof.mp3', 'mc_anvil.mp3', 'glass_break.mp3', 'bite.mp3']))
                    the_sprite_group.enemy0_group.add(enemy0)
                    #world.enemy0_order_id += 1
                elif sprite_id == 'pecker':
                    enemy0 = pecker(x * 32, y * 32, 4, 2, 'pecker', world.enemy0_order_id, ini_vol, self.enemy_img_dict_x1[sprite_id],
                                          self.get_sfx_list(['bassdrop2.mp3', 'hit.mp3', 'cough.mp3', 'dog_hurt.mp3', 'boonk.mp3', 'hit2.mp3', 'woof.mp3', 'mc_anvil.mp3', 'glass_break.mp3', 'bite.mp3']))
                    the_sprite_group.enemy0_group.add(enemy0)
                world.enemy0_order_id += 1
                    
            elif sprite_category == 'p_int':
                sfx_list_ext = self.get_sfx_list(['mc_anvil.mp3', 'step2soft.mp3', 'pop3.mp3'])
                if sprite_id == 'spinning_blades':
                    the_sprite_group.p_int_group2.add(player_interactable_(x * 32, y * 32, 2, 1, 'spinning_blades', ini_vol, True, None, sfx_list_ext))
                else:
                    the_sprite_group.p_int_group.add(player_interactable_(x * 32, y * 32, 1, 1, sprite_id, ini_vol, True, self.p_int_img_dict[sprite_id], sfx_list_ext))
                
               
                
            #bg type sprites
            elif sprite_category == 'bg_sprite': #always scaled at 1
                if sprite_id == 'lamp':
                    bg_sprite = lamp(x*32, y*32, False, 'lamp', self.bg_sprite_img_dict[sprite_id])
                elif sprite_id == 'tree':
                    bg_sprite = tree(x*32, y*32, False, 'tree', self.bg_sprite_img_dict[sprite_id])
                elif sprite_id == 'fountain':        
                    bg_sprite = fountain(x*32, y*32, False, 'fountain', self.bg_sprite_img_dict[sprite_id])
                the_sprite_group.bg_sprite_group.add(bg_sprite)
            
            #npcs
            elif sprite_category == 'npc':
                if sprite_subcategory == 'character':
                    if sprite_id == 'Test':
                        Testnpc = Test(x * 32, y * 32, 2, 1, sprite_id, ini_vol, True, world, self.all_dialogue_dict[sprite_id], self.npc_img_dict_s[sprite_id], level, player_inventory= [])
                        the_sprite_group.textprompt_group.add(Testnpc)
                    elif sprite_id == 'Test2':
                        Testnpc2 = Test2(x * 32, y * 32, 2, 1, sprite_id, ini_vol, True, world, self.all_dialogue_dict[sprite_id], self.npc_img_dict[sprite_id], level, player_inventory= [])
                        the_sprite_group.textprompt_group.add(Testnpc2)
                    elif sprite_id == 'Mars':
                        Mars_npc = Mars(x * 32 - 32, y * 32, 2, 1, sprite_id, ini_vol, True, world, self.all_dialogue_dict[sprite_id], self.npc_img_dict[sprite_id], level, player_inventory= [])
                        the_sprite_group.textprompt_group.add(Mars_npc)
                        
                elif sprite_subcategory == 'object':
                    if sprite_id == 'save_pt':
                        save_pt_obj = save_pt(x * 32, y * 32, 1, 1, sprite_id, ini_vol, True, world, self.all_dialogue_dict[sprite_id], self.npc_img_dict_small[sprite_id], level, player_inventory= [])
                        the_sprite_group.textprompt_group.add(save_pt_obj)
                    elif sprite_id == 'read_only_obj':
                        read_only_obj_ = read_only_obj(x * 32, y * 32, 1, 1, sprite_id, ini_vol, True, world, self.all_dialogue_dict[sprite_id], self.npc_img_dict_small[sprite_id], level, player_inventory= [])
                        the_sprite_group.textprompt_group.add(read_only_obj_)
                        world.read_only_obj_id += 1
                        
                elif sprite_subcategory == 'cutscene':
                    if sprite_id == 'opening_scene':
                        opening_scene_ = opening_scene(x * 32, y * 32, 1, 1, sprite_id, ini_vol, True, world, self.all_dialogue_dict[sprite_id], self.npc_img_dict_small[sprite_id], level, player_inventory= [])
                        the_sprite_group.textprompt_group.add(opening_scene_)
                        
            

