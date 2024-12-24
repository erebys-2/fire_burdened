
from enemy32File import enemy_32wide
from BGspritesFile import tree, fountain, lamp
from player_interactable import player_interactable_
from characterNPCs import Test, Test2, Mars
from objectNPCs import save_pt
from cutsceneNPCs import opening_scene

#Helper class for world, for instantiating special tiles in game layer as sprites.
#During level loading, when world.process_data is called, this reads data from 
# fire_burdened\config_textfiles\world_config\sprite_group_tiles_dict.txt,
#then adds sprites into sprite groups in the_sprite_group 

class sprite_instantiator():
    def __init__(self):
        pass

    def instantiate_sprites_from_tiles(self, tile, x, y, the_sprite_group, ini_vol, level, player_inventory, world):
        
        sprite_info = world.sprite_group_tiles_dict[tile]
        sprite_category = sprite_info[0]
        sprite_subcategory = sprite_info[2]
        sprite_id = sprite_info[1]

        #enemies and player interactables/obstacles
        if sprite_category == 'enemy':
            if sprite_id == 'dog':
                enemy0 = enemy_32wide(x * 32, y * 32, 3, 2, 'dog', world.enemy0_id, ini_vol)
                the_sprite_group.enemy0_group.add(enemy0)
                world.enemy0_id += 1#for enemy-enemy collisions/ anti stacking
            elif sprite_id == 'shooter':
                enemy0 = enemy_32wide(x * 32, y * 32, 2, 2, 'shooter', world.enemy0_id, ini_vol)
                the_sprite_group.enemy0_group.add(enemy0)
                world.enemy0_id += 1
            elif sprite_id == 'fly':
                enemy0 = enemy_32wide(x * 32, y * 32, 2, 2, 'fly', world.enemy0_id, ini_vol)
                the_sprite_group.enemy0_group.add(enemy0)
                world.enemy0_id += 1
            elif sprite_id == 'walker':
                enemy0 = enemy_32wide(x * 32, y * 32, 2, 2, 'walker', world.enemy0_id, ini_vol)
                the_sprite_group.enemy0_group.add(enemy0)
                world.enemy0_id += 1
                
        elif sprite_category == 'p_int':
            if sprite_id == 'crusher_top':
                p_int = player_interactable_(x * 32, y * 32, 1, 1, 'crusher_top', ini_vol, True, False, True)
                the_sprite_group.p_int_group.add(p_int)
            elif sprite_id == 'spinning_blades':
                p_int2 = player_interactable_(x * 32, y * 32, 2, 1, 'spinning_blades', ini_vol, True, False, False)
                the_sprite_group.p_int_group2.add(p_int2)
            elif sprite_id == 'moving_plat_h':
                p_int = player_interactable_(x * 32, y * 32, 1, 1, 'moving_plat_h', ini_vol, True, False, True)
                the_sprite_group.p_int_group.add(p_int)
            elif sprite_id == 'moving_plat_v':
                p_int = player_interactable_(x * 32, y * 32, 1, 1, 'moving_plat_v', ini_vol, True, False, True)
                the_sprite_group.p_int_group.add(p_int)
            elif sprite_id == 'grass':
                p_int = player_interactable_(x * 32, y * 32, 1, 1, 'grass', ini_vol, True, False, False)
                the_sprite_group.p_int_group.add(p_int)
            elif sprite_id == 'breakable_brick1':
                p_int = player_interactable_(x * 32, y * 32, 1, 1, 'breakable_brick1', ini_vol, True, False, False)
                the_sprite_group.p_int_group.add(p_int)
            elif sprite_id == 'flame_pillar':
                p_int = player_interactable_(x * 32, y * 32, 1, 1, 'flame_pillar', ini_vol, True, False, False)
                the_sprite_group.p_int_group.add(p_int)
            
        #bg type sprites
        elif sprite_category == 'bg_sprite':
            if sprite_id == 'lamp':
                bg_sprite = lamp(x*32, y*32, 1, False, 'lamp')
                the_sprite_group.bg_sprite_group.add(bg_sprite)
            elif sprite_id == 'tree':
                bg_sprite = tree(x*32, y*32, 1, False, 'tree')
                the_sprite_group.bg_sprite_group.add(bg_sprite)
            elif sprite_id == 'fountain':        
                bg_sprite = fountain(x*32, y*32, 1, False, 'fountain')
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
                    
            elif sprite_subcategory == 'cutscene':
                if sprite_id == 'opening_scene':
                    opening_scene_ = opening_scene(x * 32, y * 32, 1, 1, sprite_id, ini_vol, True, world, level, player_inventory= [])
                    the_sprite_group.textprompt_group.add(opening_scene_)

