import pygame
import os

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
        self.coords = []
        self.fg = []
        self.solids = []
        self.bg1 = []
        self.bg2 = []
        self.bg3 = []
        self.bg4 = []
        self.bg5 = []
        self.bg6 = []
        
        self.level_data_str_tuple = ( #names of the corresponding csv files
            'coord_data',
            'fg_data',
            'data',
            'bg1_data',
            'bg2_data',
            'bg3_data',
            'bg4_data',
            'bg5_data',
            'bg6_data'
        )

        self.detailed_lvl_data_list = [
            self.coords,
            self.fg,
            self.solids,
            self.bg1,
            self.bg2,
            self.bg3,
            self.bg4,
            self.bg5,
            self.bg6
        ]
        
        
        self.tileList = []
        self.t_set_index = 0
        tile_set_types = ['standard', 'bg_oversized']
        
        #self.horiz_scrolling = False
        #self.vert_scrolling = False
        
        #self.scroll_y = 0
        #self.scroll = 0
        #self.ref_pt = pygame.Rect((0,0),(32,32))

        #load tiles/images
        
        for tile_set in tile_set_types:
            temp_list = []
            tile_count = len(os.listdir(f'sprites/tileset/{tile_set}'))

            for i in range(tile_count):
                tile_img = pygame.image.load(f'sprites/tileset/{tile_set}/{i}.png').convert_alpha()
                temp_list.append(tile_img)
            self.tileList.append(temp_list)
            
        self.t1 = textfile_formatter()
        
        #create dicitonary from special tiles text file
        path = 'config_textfiles/world_config/'
        self.sprite_group_tiles_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path + 'sprite_group_tiles_dict.txt')), 'list')
        self.static_bg_oversized_tiles_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path + 'static_bg_oversized_tiles_dict.txt')), 'int')
        self.special_hitbox_tiles_dict = self.t1.str_list_to_dict(self.t1.read_text_from_file(os.path.join(path + 'special_hitbox_tiles_dict.txt')), 'none')
        
        self.plot_index_dict = {}
        self.npc_current_dialogue_list = []
        for npc in range(len(os.listdir('sprites/npcs'))):
            self.npc_current_dialogue_list.append(0)
        
        self.lvl_slice_lists = []
            
        self.slice_width = 1 #tiles
        self.slice_height = 15
        self.num_slices = 0
        
        self.screen_w = screen_w
        self.screen_h = screen_h
        
        self.enemy0_id = 0
        self.transition_index = 0
        
        # self.wall_hitting_time = pygame.time.get_ticks()
        # self.hitting_wall_status = False
        
        self.world_map_non_parallax = pygame.Surface((32,32), pygame.SRCALPHA)
        self.world_map_non_parallax.fill(pygame.Color(0,0,0,0))
        self.world_map_non_parallax.convert_alpha()
        
        self.world_map_non_parallax_bg = pygame.Surface((32,32), pygame.SRCALPHA)
        self.world_map_non_parallax_bg.fill(pygame.Color(0,0,0,0))
        self.world_map_non_parallax_bg.convert_alpha()
        
        self.sp_ini = sprite_instantiator()
        
        self.death_counters_dict = {}
        
            
    # Rabbid76's game map method, modified, from https://stackoverflow.com/questions/66781952/
    def create_map(self, size, level_tile_lists): #apply to all 1:1 layers
        #print(size[1])
        game_map = pygame.Surface((size[1] * 32, size[0] * 32), pygame.SRCALPHA)#create a surface the size of the whole level
        game_map.fill(pygame.Color(0,0,0,0))
        for layer in range(len(level_tile_lists)):
            for tile in level_tile_lists[len(level_tile_lists)-1-layer]:
                x_pixel = tile[1][0]
                y_pixel = tile[1][1]
                game_map.blit(tile[0], (x_pixel, y_pixel))
        return game_map
                
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
        with open(f'level_files/level{level}_{csv_data_name}.csv', newline= '') as csvfile:
            reader = csv.reader(csvfile, delimiter= ',') 
            for x, current_row in enumerate(reader):
                for y, tile in enumerate(current_row):
                    level_csv_data[x][y] = int(tile)
                    
        return level_csv_data #returns 2d array
    
    def get_raw_csv_data(self, level, lvl_size):
        raw_lvl_data_list = []
        for level_data_str in self.level_data_str_tuple:
            raw_lvl_data_list.append(self.read_level_csv_data(level, lvl_size[0], lvl_size[1], level_data_str))
            
        return raw_lvl_data_list
        
    
    #called in main menu where either a new game or save file is loaded

    def set_plot_index_dict(self, plot_index_dict):
        self.plot_index_dict = plot_index_dict
        
    #for saving
    def get_plot_index_dict(self):
        return self.plot_index_dict
    
    def clear_data(self):
        for lvl_data in self.detailed_lvl_data_list:
            lvl_data *= 0
   
   
    #=======================================  SET HITBOXES FOR SPECIAL TILES =================================
    
    def set_hitbox_for_special_tile(self, tile, x, y, level_data):
        tile_type = self.special_hitbox_tiles_dict[tile]
        
        transition_data = []
        img = self.tileList[0][tile]
        img_rect = img.get_rect()
        
        #modify the shape of a rect
        if tile_type == 'one_way_pass':#pass thru 1 way
            img_rect = pygame.Rect(0, 0, 32, 16)
        elif tile_type == 'lvl_transition':#level transition tile
            img = self.tileList[0][9]
            img_rect = pygame.Rect(0, 0, level_data[2][self.transition_index][0], level_data[2][self.transition_index][1])
            transition_data = level_data[2][self.transition_index][2:5] #passed to the player: next_level, next coords
            self.transition_index += 1
        
        #modify placement of the rect
        img_rect.x = x * 32
        if tile_type == 'lower_half':#if lower half tile
            img_rect.y = (y * 32) + 16
        else:
            img_rect.y = y * 32
        
        tile_data = (img, img_rect, tile, transition_data)
        
        self.solids.append(tile_data)
        
    #IDEA: make a secondary processing function called combine rects that combines the tile rects of horizontally adjacent rects
    #can look into rect union all, breaking the rect_sequence whenever a half tile special tile is found  
    #THIS WILL ONLY WORK IF YOU COMBINE THE IMAGES OF ALL TILES INTO A SINGLE IMAGE
    #YOU WOULD ALSO HAVE TO MAKE ENEMIES AND THE PLAYER PROCESS ALL THE TILES IN THE WORLLD

    #======================================================= loading the level ============================================
    
    def process_data(self, level, the_sprite_group, screenW, screenH, level_data, ini_vol):
        #clear old data
        raw_lvl_data_list = []
        self.clear_data()
        
        #populate raw_lvl_data_list with lists of int values from level csv files
        raw_lvl_data_list = self.get_raw_csv_data(level, level_data[0:2])
        
        #process int lists into detailed list
        self.process_coords_vslice(raw_lvl_data_list[0], screenW, screenH, self.detailed_lvl_data_list[0])
        self.enemy0_id = 0
        self.transition_index = 0
        
        #processing interactable layer
        for y, row in enumerate(raw_lvl_data_list[2]):
            for x, tile in enumerate(row):
                if tile >= 0:
                    if tile in self.sprite_group_tiles_dict:
                        self.sp_ini.instantiate_sprites_from_tiles(tile, x, y, the_sprite_group, ini_vol, level, [], self)
                        #pass
                    elif tile in self.special_hitbox_tiles_dict:
                        self.set_hitbox_for_special_tile(tile, x, y, level_data)
                    else:
                        img = self.tileList[0][tile]
                        img_rect = img.get_rect()
                        
                        img_rect.x = x * 32
                        img_rect.y = y * 32
                        
                        tile_data = (img, img_rect, tile, [])
                        
                        self.solids.append(tile_data)
        #load bg
        for i in range(len(self.detailed_lvl_data_list) -3):
            self.process_bg(raw_lvl_data_list[i+3], self.detailed_lvl_data_list[i+3], the_sprite_group, i+3)
        #load fg
        self.process_bg(raw_lvl_data_list[1], self.detailed_lvl_data_list[1], the_sprite_group, 1)
        
        
        self.world_map_non_parallax = self.create_map(level_data[0:2], self.detailed_lvl_data_list[2:4]).convert_alpha()
        self.world_map_non_parallax_bg = self.create_map(level_data[0:2], self.detailed_lvl_data_list[4:5]).convert_alpha()
        
        
        if level not in self.death_counters_dict:
            self.death_counters_dict[level] = 0
        #print(self.death_counters_dict)
        
    def process_coords_hslice(self, data, screenW, screenH, rtrn_list):
        x_coord = 0
        y_coord = 0
        for y in enumerate(data):
            y_coord = y * 32
            
            img_rect = pygame.Rect(0, 0, screenW, 32)
            img_rect.x = x_coord
            img_rect.y = y_coord
            
            tile_data = (0, img_rect, (x_coord, y_coord))
            #print(tile_data)
            #self.fill_slice_list(0, x_coord, tile_data)
            
            rtrn_list.append(tile_data)

        
    def process_coords_vslice(self, data, screenW, screenH, rtrn_list):
        x_coord = 0
        y_coord = 0
        for y, row in enumerate(data):
            if y == 0:
                for x, tile in enumerate(row):
                    if tile == -1:
                        x_coord = x * 32
                        y_coord = 0
                        
                        img_rect = pygame.Rect(0, 0, 32, screenH)
                        img_rect.x = x_coord
                        img_rect.y = y_coord
                        
                        tile_data = (0, img_rect, (x_coord, y_coord))
                        #print(tile_data)
                        #self.fill_slice_list(0, x_coord, tile_data)
                        
                        rtrn_list.append(tile_data)
            else:
                break
        self.world_limit = (x_coord, screenH)
        #scroll enables
        if x_coord + 32 > screenW:
            self.x_scroll_en = True
        else:
            self.x_scroll_en = False
            
        self.y_scroll_en = False
        
        
    def process_bg(self, data, rtrn_list, the_sprite_group, index_):   
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    
                    if tile in self.sprite_group_tiles_dict: #avoid key errors
                        self.sp_ini.instantiate_sprites_from_tiles(tile, x, y, the_sprite_group, 0, 0, [], self)

                    else:
                        if tile in self.static_bg_oversized_tiles_dict:
                            img = self.tileList[1][self.static_bg_oversized_tiles_dict[tile]]
                        else:
                            img = self.tileList[0][tile]
                    
                    img_rect = img.get_rect()
                    img_rect.x = x * 32
                    img_rect.y = y * 32
                    tile_data = (img, img_rect, tile)
                    

                    
                    if tile != 36 and tile != 39 and tile != 31:
                        rtrn_list.append(tile_data)

                        
                                       
    def draw_bg_layers(self, screen, scroll_X, scroll_Y, data, player_hitting_wall):
        #currently only handles x scrolling
        #scroll_amnt = scroll_X
        #logic for looping bg, maximum sprite size is 480x480
        for tile in data:
            if (data in self.detailed_lvl_data_list[6:9]):#parallax layers
                if tile[1][0] > tile[1].width:
                    tile[1][0] -= (2 * tile[1].width)
                elif tile[1][0] < -tile[1].width:
                    tile[1][0] += (2 * tile[1].width)
                    
                if not player_hitting_wall:
                    #print(player_hitting_wall)
                    tile[1][0] -= scroll_X

                #tile[1][0] -= scroll_X
                if tile[1].x <= self.screen_w and tile[1].x > -tile[1].width:
                    screen.blit(tile[0], tile[1]) # (image, position)
               
            else:#non parallax layers
                tile[1][0] -= scroll_X
                tile[1][1] -= scroll_Y
                if tile[1].x <= self.screen_w and tile[1].x > -self.screen_w//2 and data != self.fg:
                    screen.blit(tile[0], tile[1]) # (image, position)
                    
               

                
    def draw_filter_layer(self, screen, data):#filter layer doesn't scroll, for efficiency it should be 640x480
        for tile in data:
            screen.blit(tile[0], tile[1])
        
    def update_tiles(self, tile, screen, scroll_X, scroll_Y):
        tile[1][0] -= scroll_X
        tile[1][1] -= scroll_Y
        if tile[1][0] > -32 and tile[1][0] < 640 + 32:
            screen.blit(tile[0], tile[1]) # (image, position)
                    
    def draw(self, screen, scroll_X, scroll_Y, player_hitting_wall): #MOVE sliceS HERE

        
        if scroll_X > 0:
            correction = 1
        else:
            correction = 0
        
        self.draw_bg_layers(screen, (scroll_X + correction)//3, 0, self.bg6, player_hitting_wall)
        self.draw_bg_layers(screen, 4*(scroll_X + correction)//7, 0, self.bg5, player_hitting_wall)
        self.draw_bg_layers(screen, 7*(scroll_X + correction)//9, 0, self.bg4, player_hitting_wall)
        
        #drawing game world and 1:1 bg by tile
        # self.draw_bg_layers(screen, (scroll_X), scroll_Y, self.bg2, player_hitting_wall)#detailed 1:1 bg layer 2
        # self.draw_filter_layer(screen, self.bg3)
        # self.draw_bg_layers(screen, (scroll_X), scroll_Y, self.bg1, player_hitting_wall)
        
        
        
        #these scroll every tile in a layer
        
        for tile in self.solids:
            #this code below basically means the first index: [1], gets the tile's rect, 
            #then the [0] right after gets the x coordinate
            #if you were to swap [0] with [1] you'd get the y coord
            
            tile[1][0] -= scroll_X
            tile[1][1] -= scroll_Y
            
            # if tile[1][0] > -32 and tile[1][0] < 640 + 32:
            #     screen.blit(tile[0], tile[1]) # (image, position)
                
      
        
        for tile in self.coords:
            tile[1][0] -= scroll_X #the coords file does not have an image
            tile[1][1] -= scroll_Y
            
            
        self.draw_bg_layers(screen, scroll_X, scroll_Y, self.fg, player_hitting_wall)#calling this just scrolls the fg layer
        
        #drawing tile maps instead of by tile
        # screen.blit(self.world_map_non_parallax_bg, (self.coords[0][1][0], self.coords[0][1][1]))
        # self.draw_filter_layer(screen, self.bg3)
        # screen.blit(self.world_map_non_parallax, (self.coords[0][1][0], self.coords[0][1][1]))
        
        return (self.coords[0][1][0], self.coords[0][1][1]) #x and y of first tile
            
    
    def draw_foreground(self, screen):
        for tile in self.fg:
            if tile[1].x <= self.screen_w and tile[1].x > -self.screen_w//2:
                screen.blit(tile[0], tile[1]) # (image, position)
            
            