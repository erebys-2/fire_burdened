import pygame
import os
from enemy32File import enemy_32wide
from BGspritesFile import tree, fountain, lamp
from player_interactable import player_interactable_
from characterNPCs import Test, Test2, Mars
from objectNPCs import save_pt, read_only_obj
from cutsceneNPCs import opening_scene
from ItemFile import Item
from music_player import music_player

#Helper class for world, for instantiating special tiles in game layer as sprites.
#During level loading, when world.process_data is called, this reads data from 
# fire_burdened\config_textfiles\world_config\sprite_group_tiles_dict.txt,
#then adds sprites into sprite groups in the_sprite_group 

class sprite_instantiator():
    def __init__(self):
        print('loading sprite instantiator')
        base_path = 'assets/sprites/'
        self.bg_sprite_img_dict = self.load_img_dict(os.path.join(base_path, 'bg_sprites'))
        self.enemy_img_dict = self.load_img_dict2(os.path.join(base_path, 'enemies'), 2)
        self.p_int_img_dict = self.load_img_dict2(os.path.join(base_path, 'player_interactable'), 1)
        
        sfx_path = 'assets/sfx'
        self.master_sfx_list = []
        self.sfx_index_dict = {}
        i = 0
        for sound in os.listdir(sfx_path):
            self.sfx_index_dict[sound] = i
            self.master_sfx_list.append(pygame.mixer.Sound(f'{sfx_path}/{sound}'))
            i += 1
            
        self.ini_vol = 0
        self.m_player = music_player(None, self.ini_vol)
        self.m_player.sfx = self.master_sfx_list
        print('sprite instantiator loaded!')
        
    
    def load_img_dict2(self, asset_path, scale):
        img_dict = {}
        for subdir in os.listdir(asset_path):
            frame_list = []
            subdir_path = f'{asset_path}/{subdir}'
            for subdir2 in os.listdir(subdir_path):
                temp_list = []
                for i in range(len(os.listdir(f'{subdir_path}/{subdir2}'))):
                    loaded_img = pygame.image.load(f'{subdir_path}/{subdir2}/{i}.png').convert_alpha()
                    loaded_img = pygame.transform.scale(loaded_img, (int(loaded_img.get_width() * scale), int(loaded_img.get_height() * scale)))
                    if asset_path == 'assets/sprites/enemies' and f'{subdir2}' == '2':#enemy spaghetti code :(
                        if i < 2:
                            loaded_img = pygame.transform.scale(loaded_img, (int(loaded_img.get_width() * 0.8), int(loaded_img.get_height() * 1.1)))
                        elif i == 2:
                            loaded_img = pygame.transform.scale(loaded_img, (int(loaded_img.get_width() * 1.1), int(loaded_img.get_height() * 0.9)))

                    temp_list.append(loaded_img)
                frame_list.append(temp_list)
            img_dict[subdir] = frame_list
            
        return img_dict
    
    def load_img_dict(self, asset_path):#2 layer deep
        img_dict = {}
        for subdir in os.listdir(asset_path):
            temp_list = []
            for i in range(len(os.listdir(f'{asset_path}/{subdir}'))):
                loaded_img = pygame.image.load(f'{asset_path}/{subdir}/{i}.png').convert_alpha()
                temp_list.append(loaded_img)
            img_dict[subdir] = temp_list
            
        return img_dict
    
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
                    world.enemy0_order_id += 1#for enemy-enemy collisions/ anti stacking
                elif sprite_id == 'shooter':
                    enemy0 = enemy_32wide(x * 32, y * 32, 2, 2, 'shooter', world.enemy0_order_id, ini_vol, self.enemy_img_dict[sprite_id],
                                          self.get_sfx_list(['bassdrop2.mp3', 'hit.mp3', 'roblox2.mp3', 'shoot.mp3', 'step2soft.mp3', 'hit2.mp3']))
                    the_sprite_group.enemy0_group.add(enemy0)
                    world.enemy0_order_id += 1
                elif sprite_id == 'fly':
                    enemy0 = enemy_32wide(x * 32, y * 32, 2, 2, 'fly', world.enemy0_order_id, ini_vol, self.enemy_img_dict[sprite_id],
                                          self.get_sfx_list(['bassdrop2.mp3', 'hit.mp3', 'bee_hurt.mp3', 'bee.mp3', 'step2soft.mp3', 'hit2.mp3']))
                    the_sprite_group.enemy0_group.add(enemy0)
                    world.enemy0_order_id += 1
                elif sprite_id == 'walker':
                    enemy0 = enemy_32wide(x * 32, y * 32, 2, 2, 'walker', world.enemy0_order_id, ini_vol, self.enemy_img_dict[sprite_id],
                                          self.get_sfx_list(['bassdrop2.mp3', 'hit.mp3', 'cough.mp3', 'bite.mp3', 'step2soft.mp3', 'hit2.mp3']))
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
                        Testnpc = Test(x * 32, y * 32, 2, 1, sprite_id, ini_vol, True, world, level, player_inventory= [])
                        the_sprite_group.textprompt_group.add(Testnpc)
                    elif sprite_id == 'Test2':
                        Testnpc2 = Test2(x * 32, y * 32, 2, 1, sprite_id, ini_vol, True, world, level, player_inventory= [])
                        the_sprite_group.textprompt_group.add(Testnpc2)
                    elif sprite_id == 'Mars':
                        Mars_npc = Mars(x * 32 - 32, y * 32, 2, 1, sprite_id, ini_vol, True, world, level, player_inventory= [])
                        the_sprite_group.textprompt_group.add(Mars_npc)
                        
                elif sprite_subcategory == 'object':
                    if sprite_id == 'save_pt':
                        save_pt_obj = save_pt(x * 32, y * 32, 1, 1, sprite_id, ini_vol, True, world, level, player_inventory= [])
                        the_sprite_group.textprompt_group.add(save_pt_obj)
                    elif sprite_id == 'read_only_obj':
                        read_only_obj_ = read_only_obj(x * 32, y * 32, 1, 1, sprite_id, ini_vol, True, world, level, player_inventory= [])
                        the_sprite_group.textprompt_group.add(read_only_obj_)
                        
                elif sprite_subcategory == 'cutscene':
                    if sprite_id == 'opening_scene':
                        opening_scene_ = opening_scene(x * 32, y * 32, 1, 1, sprite_id, ini_vol, True, world, level, player_inventory= [])
                        the_sprite_group.textprompt_group.add(opening_scene_)
                        
            

