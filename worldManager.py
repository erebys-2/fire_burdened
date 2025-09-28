import pygame
import os
import random
from spriteInstantiator import sprite_instantiator

from textfile_handler import textfile_formatter

import csv

#Class responsible for handling level related functions 
#including: loading level, instantiating sprites, drawing level, scrolling level.
#
#Stores persistent data across levels such as plot index or death counters per level.
#Is only instantiated once on game start up.

class World():
    def __init__(self, screen_w, screen_h):
        print('loading world')
        self.rect = pygame.rect.Rect(0,0,1,1)
        self.coords = []
        self.fg = []
        self.fg_1 = []
        self.solids = []
        self.bg1 = []
        self.bg2 = []
        self.bg2_1 = []
        self.bg3 = []
        self.bg4 = []
        self.bg5 = []
        self.bg6 = []
        
       
        self.detailed_lvl_data_dict = {
            'coord_data': self.coords,
            'fg_data': self.fg,
            'fg_1_data': self.fg_1,
            'data': self.solids,
            'bg1_data': self.bg1,
            'bg2_data': self.bg2,
            'bg2_1_data': self.bg2_1,
            'bg3_data': self.bg3,
            'bg4_data': self.bg4,
            'bg5_data': self.bg5,
            'bg6_data': self.bg6
        }
        
        self.tileList = []
        self.t_set_index = 0
        tile_set_types = ['standard', 'bg_oversized']
        
        #self.horiz_scrolling = False
        #self.vert_scrolling = False
        
        #self.scroll_y = 0
        #self.scroll = 0
        #self.ref_pt = pygame.Rect((0,0),(32,32))

        #load tiles/images
        #if screen_w > 0:
        for tile_set in tile_set_types:
            temp_list = []
            tset_path = os.path.join('assets', 'sprites', 'tileset', tile_set)
            tile_count = len(os.listdir(tset_path))#f'assets/sprites/tileset/{tile_set}'))

            for i in range(tile_count):
                tile_img = pygame.image.load(os.path.join(tset_path, f'{i}.png')).convert_alpha()#f'assets/sprites/tileset/{tile_set}/{i}.png'
                temp_list.append(tile_img)
            self.tileList.append(temp_list)
        
            
        self.t1 = textfile_formatter()
        
        #create dicitonary from special tiles text file
        path = os.path.join('assets', 'config_textfiles', 'world_config')#'assets/config_textfiles/world_config/'
        self.sprite_group_tiles_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path, 'sprite_group_tiles_dict.txt')), 'list')
        self.static_bg_oversized_tiles_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path, 'static_bg_oversized_tiles_dict.txt')), 'int')
        self.special_hitbox_tiles_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path, 'special_hitbox_tiles_dict.txt')), 'none')
        self.slightly_oversized_tiles_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path, 'slightly_oversized_tiles_dict.txt')), 'float')
        
        path2 = os.path.join('assets', 'config_textfiles', 'level_config')#'assets/config_textfiles/level_config/'
        self.level_sizes_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path2, 'level_sizes_dict.txt')), 'list')

        #load onetime_spawn_dict whenever a save file is selected
        #this will be saved as a textfile, used for items and chests
        #level: item: enabled, item2: enabled
        
        #for a given level, sprite instantiator will instantiate sprites in the 1 time spawn dict if their output == True
        #the dictionary will be modified by a method that will check if the specific sprite was removed from their respective sprite group
        #note might have to do some enemy_id type thing to specify generic sprites like chests
        self.onetime_spawn_dict = {}
        self.ots_id = 0
        self.read_only_obj_id = 0
        self.sp_groups_to_check = []
        
        self.plot_index_dict = {}
        
        #===============================================create surface dict from layers
        self.surface_map_dict = self.get_lvl_map_dict()
            
        self.slice_width = 1 #tiles
        self.slice_height = 15
        self.num_slices = 0
        
        self.screen_w = screen_w
        self.screen_h = screen_h
        
        self.enemy0_order_id = 0
        self.transition_index = 0
        
        # self.wall_hitting_time = pygame.time.get_ticks()
        # self.hitting_wall_status = False
        
        if screen_w > 0:
            self.world_map_non_parallax = pygame.Surface((32,32), pygame.SRCALPHA)
            self.world_map_non_parallax.fill(pygame.Color(0,0,0,0))
            self.world_map_non_parallax.convert_alpha()
            
            self.world_map_non_parallax_fg = pygame.Surface((32,32), pygame.SRCALPHA)
            self.world_map_non_parallax_fg.fill(pygame.Color(0,0,0,0))
            self.world_map_non_parallax_fg.convert_alpha()
        
            self.sp_ini = sprite_instantiator()
        
        #resets per instance
        self.death_counters_dict = {} #player deaths per level
        self.lvl_completion_dict = {0:0} #if all enemies are killed in a level
        self.lvl_completed = False
        print('world loaded!')
        
    def scale_tile(self, img, pos):
        return(pygame.transform.scale(img, (36, 36)), (pos[0]-2, pos[1]-2))
    
    def get_lvl_map_dict(self):
        surface_map_dict = {}
        ini_path = os.path.join('assets', 'sprites', 'world_maps')
        for lvl_subdir in os.listdir(ini_path):#will get level folders
            map_subdir = os.path.join(ini_path, lvl_subdir, 'drawn_maps')
            temp_dict = {}
            for img_name in os.listdir(map_subdir):#gets img names
                temp_dict[img_name] = pygame.image.load(os.path.join(map_subdir, img_name)).convert_alpha()

            #combine maps
            non_paralax_map = self.combine_surfaces([temp_dict[f'{name}.PNG'] for name in ('filtered_layers', 'filter_layer', 'non_filtered_layers')]).convert_alpha()
            true_fg_map = temp_dict['true_fg.PNG']

            surface_map_dict[lvl_subdir] = {'non_parallax': non_paralax_map, 'true_fg': true_fg_map}

        return surface_map_dict
            
    # Rabbid76's game map method, modified, from https://stackoverflow.com/questions/66781952/
    def create_map(self, size, level_tile_lists): #apply to all 1:1 layers
        #print(size[1])
        game_map = pygame.Surface((size[1] * 32, size[0] * 32), pygame.SRCALPHA)#create a surface the size of the whole level
        game_map.fill(pygame.Color(0,0,0,0))
        for layer in range(len(level_tile_lists)):
            for tile in level_tile_lists[len(level_tile_lists)-1-layer]:
                x_pixel = tile[1][0]
                y_pixel = tile[1][1]
                img = tile[0].convert_alpha()
                # if layer != 3 and 2 == random.randint(0,4):
                #     img_tup = self.scale_tile(img, (x_pixel, y_pixel))
                # else:
                img_tup = (img, (x_pixel, y_pixel))
                game_map.blit(img_tup[0], img_tup[1])
        return game_map
    
    def update_lvl_completion(self, level, enemy_death_count, player_alive, passive_effects):#called on level change
        #player_alive is true when the next_level isn't the menu level, when the player dies they are sent to this level
        #so if the player kills all the enemies in a level then dies or exits to the main menu, the dict will not be updated
        if passive_effects['salted_earth'] and player_alive and self.enemy0_order_id != 0 and self.enemy0_order_id == enemy_death_count:
            self.lvl_completion_dict[level] = 4#how many times a level will be loaded without enemies
                
    def get_death_count(self, level):#death counts are a dictionary with levels as keys, it is reset everytime a mew slot is selected or the game is restarted
        death_count = 0
        if level in self.death_counters_dict:
            death_count = self.death_counters_dict[level]
            
        return death_count
    
    def set_death_count(self, level, count):
        if level in self.death_counters_dict:
            self.death_counters_dict[level] = count
        
    def read_level_csv_data(self, level, rows, cols, csv_data_name):
        
        #populate a rows x cols sized list with -1
        level_csv_data = []
        for current_row in range(rows):
            r = [-1] * cols
            level_csv_data.append(r)

        #change list with values from CSV file
        with open(os.path.join('assets', 'level_files', f'level{level}', f'level{level}_{csv_data_name}.csv'), newline= '') as csvfile:#f'assets/level_files/level{level}/level{level}_{csv_data_name}.csv'
            reader = csv.reader(csvfile, delimiter= ',') 
            for x, current_row in enumerate(reader):
                for y, tile in enumerate(current_row):
                    level_csv_data[x][y] = int(tile)
                    
        return level_csv_data #returns 2d array
    
    def get_raw_csv_data(self, level, lvl_size):
        raw_lvl_data_dict = {}
        for level_data_str in self.detailed_lvl_data_dict:
            raw_lvl_data_dict[level_data_str] = (self.read_level_csv_data(level, lvl_size[0], lvl_size[1], level_data_str))
            
        return raw_lvl_data_dict
        
    
    #called in main menu where either a new game or save file is loaded

    def set_plot_index_dict(self, plot_index_dict):
        self.plot_index_dict = plot_index_dict
        
    #for saving
    def get_plot_index_dict(self):
        return self.plot_index_dict
    
            
   
    #=======================================  SET HITBOXES FOR SPECIAL TILES =================================
    
    def set_hitbox_for_special_tile(self, tile, x, y, lvl_data_trans_list):
        tile_type = self.special_hitbox_tiles_dict[tile]
        
        transition_data = []
        img = self.tileList[0][tile].convert_alpha()
        img_rect = img.get_rect()
        
        #modify the shape of a rect
        if tile_type == 'one_way_pass':#pass thru 1 way
            img_rect = pygame.Rect(0, 0, 32, 16)
        elif lvl_data_trans_list != None and tile_type == 'lvl_transition':#level transition tile
            img = self.tileList[0][9]
            
            # img = pygame.Surface((lvl_data_trans_list[self.transition_index][0], lvl_data_trans_list[self.transition_index][1]))
            # img.fill((255,0,0))        
            img_rect = pygame.Rect(0, 0, lvl_data_trans_list[self.transition_index][0], lvl_data_trans_list[self.transition_index][1])
            transition_data = list(lvl_data_trans_list[self.transition_index][2:6]) #passed to the player: next_level, player new x, player new y, bound index
            transition_data.append((x*32,y*32))
            #print(transition_data)
            self.transition_index += 1
        
        #modify placement of the rect
        img_rect.x = x * 32
        if tile_type == 'lower_half':#if lower half tile
            img_rect.y = (y * 32) + 16
        else:
            img_rect.y = y * 32
            
        if tile_type == 'lvl_transition' and y > 0:
            img_rect.y += 30
        
        if lvl_data_trans_list != None and tile == 10:
            tile_data = (img, img_rect, tile, transition_data)
        else:
            tile_data = (img, img_rect, tile)
        
        return tile_data
    
    #check onetime spawn dict
    def check_onetime_spawn_dict(self, level): #called before sprite groups are purged during level change
        if level != 0 and level in self.onetime_spawn_dict:
            for i in range(len(self.onetime_spawn_dict[level])):
                found = False
                for sp_group in self.sp_groups_to_check:
                    for sprite in sp_group:
                        if sprite.id == self.onetime_spawn_dict[level][i][1]:#bottleneck: ots sprites need an id
                            found = True
                            break
                    if found:
                        break
                #print(f'world check: {found}')
                self.onetime_spawn_dict[level][i][2] = str(found)
                
            self.sp_groups_to_check *= 0


        

    #======================================================= loading the level ============================================
    
    def process_data(self, level, the_sprite_group, screenW, screenH, lvl_data_trans_list, ini_vol):
        #clear old data
        raw_lvl_data_dict = {}
        for lvl_data in self.detailed_lvl_data_dict:
            self.detailed_lvl_data_dict[lvl_data] *= 0
            
        self.rect = pygame.rect.Rect(0,0,1,1)
        
        #get level size
        lvl_size = self.level_sizes_dict[level]
        
        #bind the world's rect
        # if y == 0 and x == 0: 
        #     self.rect.x = x
        #     self.rect.y = y
        # self.rect.y = 0
        # self.rect.x = 0
        
        #populate raw_lvl_data_list with lists of int values from level csv files
        raw_lvl_data_dict = self.get_raw_csv_data(level, lvl_size)

        self.enemy0_order_id = 0
        self.ots_id = 0
        self.read_only_obj_id = 0
        self.transition_index = 0
        
        #check world lvl completion dict
        self.lvl_completed = False
        if level != 0 and level in self.lvl_completion_dict:
            if self.lvl_completion_dict[level] > 0:
                self.lvl_completed = True
                self.lvl_completion_dict[level] -= 1 #reset the completion status of the level
        
        #processing interactable layer
        for y, row in enumerate(raw_lvl_data_dict['data']):
            for x, tile in enumerate(row):
                # #bind the world's rect
                # if y == 0 and x == 0: 
                #     self.rect.x = x
                #     self.rect.y = y
                
                #process tiles into detailed game layer list
                if tile >= 0:
                    if tile in self.sprite_group_tiles_dict:
                        self.sp_ini.instantiate_sprites_from_tiles(tile, x, y, the_sprite_group, ini_vol, level, [], self)
                    elif tile in self.special_hitbox_tiles_dict:
                        tile_data = self.set_hitbox_for_special_tile(tile, x, y, lvl_data_trans_list)
                        self.solids.append(tile_data)
                    else:
                        if tile in self.static_bg_oversized_tiles_dict:
                            img = self.tileList[1][self.static_bg_oversized_tiles_dict[tile]]
                        else:
                            img = self.tileList[0][tile]
                        img_rect = img.get_rect()
                        
                        img_rect.x = x * 32
                        img_rect.y = y * 32
                        
                        tile_data = (img, img_rect, tile, [])
                        
                        self.solids.append(tile_data)
        #self.solids, x, y = self.process_game_layer(raw_lvl_data_dict['data'], False, the_sprite_group, ini_vol, level, lvl_data_trans_list)
                        
        #set world limits as width/height of the world's rect
        self.rect.width = x * 32
        self.rect.height = y * 32
        
        #set scroll en        
        if self.rect.width + 32 > screenW:
            self.x_scroll_en = True
        else:
            self.x_scroll_en = False
            
        self.y_scroll_en = False
        
        #===========================================================Loading Lvl maps=============================================
        # #can clear lists by iterating through dictionary but cannot set lists
        # self.bg1 = self.process_bg(raw_lvl_data_dict['bg1_data'], False)
        # self.bg2 = self.process_bg(raw_lvl_data_dict['bg2_data'], True)
        # self.bg2_1 = self.process_bg(raw_lvl_data_dict['bg2_1_data'], True)
        # self.bg3 = self.process_bg(raw_lvl_data_dict['bg3_data'], False)
        self.bg4 = self.process_bg(raw_lvl_data_dict['bg4_data'], False)
        self.bg5 = self.process_bg(raw_lvl_data_dict['bg5_data'], False)
        self.bg6 = self.process_bg(raw_lvl_data_dict['bg6_data'], False)
        
            
        # #process filter layer
        # #if self.bg3 != []:
        # self.bg3 = self.post_process_filter_layer(self.bg3, lvl_size[1]*32)
                
        # #load fg and fg_1
        # self.fg = self.process_bg(raw_lvl_data_dict['fg_data'], False)
        # self.fg_1 = self.process_bg(raw_lvl_data_dict['fg_1_data'], False)
        
        # #create maps
        # # layer_list = [self.fg_1, self.solids, self.bg1, self.bg3, self.bg2, self.bg2_1]
        # # self.world_map_non_parallax = self.create_map(lvl_size, layer_list).convert_alpha()
        
        # filtered_layers = self.create_map(lvl_size, [self.bg2, self.bg2_1])#.convert_alpha()
        # filter_layer = self.create_map(lvl_size, [self.bg3,])#.convert_alpha()
        # non_filtered_layers = self.create_map(lvl_size, [self.fg_1, self.solids, self.bg1])#.convert_alpha()
        
        # self.world_map_non_parallax = self.combine_surfaces((filtered_layers, filter_layer, non_filtered_layers)).convert_alpha()
        
        
        # layer_list2 = [self.fg,]
        # self.world_map_non_parallax_fg = self.create_map(lvl_size, layer_list2).convert_alpha() 
        self.world_map_non_parallax = self.surface_map_dict[f'level{level}_maps']['non_parallax'].convert_alpha()
        self.world_map_non_parallax_fg = self.surface_map_dict[f'level{level}_maps']['true_fg'].convert_alpha()
        #==========================================================================================================

        #add another death counter
        if level not in self.death_counters_dict:
            self.death_counters_dict[level] = 0
            
        
    def combine_surfaces(self, surface_list):
        rtn_surface = pygame.surface.Surface(surface_list[0].get_size(), pygame.SRCALPHA)
        for surface in surface_list:
            rtn_surface.blit(surface)
        #rtn_surface.blits([(surface, (0,0)) for surface in surface_list])
        return rtn_surface
            
   
    def post_process_filter_layer(self, filter_layer, level_size_pixels): #for filter layer that contains one very large tile that gets repeated across the level
        temp_list = []
        if filter_layer != []:
            filter_width = filter_layer[0][1].width
            filter_height = filter_layer[0][1].height
            
            img = filter_layer[0][0]
            tile = filter_layer[0][2]
            
            x = 0
            while (x-1)*filter_width < level_size_pixels:
                img_rect = pygame.rect.Rect(x*filter_width, 0, filter_width, filter_height)
                tile_data = (img, img_rect, tile)
                temp_list.append(tile_data)
                x+= 1
        
        return temp_list
    
    def process_game_layer_map(self, data):
        rtn_list = []
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
 
                #process tiles into detailed game layer list
                if tile in self.special_hitbox_tiles_dict and tile != 10:
                    tile_data = self.set_hitbox_for_special_tile(tile, x, y, None)
                    rtn_list.append(tile_data)
                elif tile >= 0 and tile != 10 and tile not in self.sprite_group_tiles_dict:# and tile not in self.special_hitbox_tiles_dict:
                    if tile in self.static_bg_oversized_tiles_dict:
                        img = self.tileList[1][self.static_bg_oversized_tiles_dict[tile]]
                    else:
                        img = self.tileList[0][tile]
                    img_rect = img.get_rect()
                    
                    img_rect.x = x * 32
                    img_rect.y = y * 32
                    
                    tile_data = (img, img_rect, tile)
                    
                    rtn_list.append(tile_data)
                        
        return rtn_list
            
        
    def process_bg(self, data, is_detailed_bg):   
        rtrn_list = []
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    scale = 1
                    disp = 0
                    # if tile in self.sprite_group_tiles_dict: #avoid key errors
                    #     self.sp_ini.instantiate_sprites_from_tiles(tile, x, y, the_sprite_group, 0, 0, [], self)
                        
                    if tile in self.special_hitbox_tiles_dict:
                        tile_data = self.set_hitbox_for_special_tile(tile, x, y, None)
                        rtrn_list.append(tile_data)

                    else:
                        if tile in self.static_bg_oversized_tiles_dict:
                            img = self.tileList[1][self.static_bg_oversized_tiles_dict[tile]]
                        else:
                            img = self.tileList[0][tile]
                            
                        if is_detailed_bg and tile not in (8,57,58):
                            img = pygame.transform.hsl(img, -0.75, -0.75, -0.75)
                            
                        if tile in self.slightly_oversized_tiles_dict:
                            scale = self.slightly_oversized_tiles_dict[tile]
                            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale )))
                    
                        if scale != 1:
                            disp = int((scale - 1)*32/2)
                        
                        img_rect = img.get_rect()
                        img_rect.x = x * 32 - disp
                        img_rect.y = y * 32 - disp

                        tile_data = (img, img_rect, tile)
                        

                        
                        if tile != 36 and tile != 39 and tile != 31:
                            rtrn_list.append(tile_data)
        return rtrn_list
                                 
    def draw_parallax_layers(self, screen, scroll_X, scroll_Y, data, player_hitting_wall):
        for tile in data:
            #cycling through image
            if tile[1][0] > tile[1].width:
                tile[1][0] -= (2 * tile[1].width)
            elif tile[1][0] < -tile[1].width:
                tile[1][0] += (2 * tile[1].width)
                
            if not player_hitting_wall:#scrolling
                tile[1][0] -= scroll_X

            #drawing
            if tile[1].x <= self.screen_w and tile[1].x > -tile[1].width:
                screen.blit(tile[0], tile[1]) # (image, position)
            
                    
        
    def update_tiles(self, tile, screen, scroll_X, scroll_Y):
        tile[1][0] -= scroll_X
        tile[1][1] -= scroll_Y
        if tile[1][0] > -32 and tile[1][0] < 640 + 32:
            screen.blit(tile[0], tile[1]) # (image, position)
                    
    def draw(self, screen, scroll_X, scroll_Y, player_hitting_wall): #MOVE sliceS HERE

        #parallax layers
        if scroll_X > 0:
            correction = 1
        else:
            correction = 0
        
        self.draw_parallax_layers(screen, (scroll_X + correction)//3, 0, self.bg6, player_hitting_wall)
        self.draw_parallax_layers(screen, 4*(scroll_X + correction)//7, 0, self.bg5, player_hitting_wall)
        self.draw_parallax_layers(screen, 7*(scroll_X + correction)//9, 0, self.bg4, player_hitting_wall)
        
        
        #these scroll every tile in a layer
        
        for tile in self.solids:
            #this code below basically means the first index: [1], gets the tile's rect, 
            #then the [0] right after gets the x coordinate
            #if you were to swap [0] with [1] you'd get the y coord
            
            tile[1][0] -= scroll_X
            tile[1][1] -= scroll_Y
            

        #scroll the world's rect
        self.rect.x -= scroll_X
        self.rect.y -= scroll_Y
            
            
    
    def draw_foreground(self, screen):
        for tile in self.fg:
            if tile[1].x <= self.screen_w and tile[1].x > -self.screen_w//2:
                screen.blit(tile[0], tile[1]) # (image, position)
            
            