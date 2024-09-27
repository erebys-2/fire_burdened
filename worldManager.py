import pygame
import os
from playerFile import player #type: ignore
from enemy32File import enemy_32wide #type: ignore
from particle import particle_ #type: ignore
from player_interactable import player_interactable_
from dialogueCSVformatter import csv_extracter
from textfile_handler import textfile_formatter
from BGspritesFile import tree, fountain, lamp
import csv

from npcFile import npc, Test, Test2

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
        
        
        # self.active_coords = []
        # self.active_fg = []
        # self.active_solids = []
        # self.active_bg1 = []
        # self.active_bg2 = []
        
        # self.loaded_lvl_data_list = [
        #     self.active_coords,
        #     self.active_fg,
        #     self.active_solids,
        #     self.active_bg1,
        #     self.active_bg2
        # ]
        
        self.tileList = []
        self.t_set_index = 0
        tile_set_types = ['standard', 'bg_oversized']
        
        #self.horiz_scrolling = False
        #self.vert_scrolling = False
        
        #self.scroll_y = 0
        #self.scroll = 0
        #self.ref_pt = pygame.Rect((0,0),(32,32))

        #load tiles/images
        
        self.special_tiles = (
            26,
            28,
            29,
            45,
            46,
            47,
            48,
            49,
            50
        )

        for tile_set in tile_set_types:
            temp_list = []
            tile_count = len(os.listdir(f'sprites/tileset/{tile_set}'))

            for i in range(tile_count):
                tile_img = pygame.image.load(f'sprites/tileset/{tile_set}/{i}.png').convert_alpha()
                temp_list.append(tile_img)
            self.tileList.append(temp_list)
            
        self.csv_f0 = csv_extracter(60)
        self.player_choices_list = self.csv_f0.csv_nonformatted('player_choices')
        self.player_prompt_list = []
        for prompt in self.csv_f0.csv_nonformatted('player_prompts'):
            str_list = self.csv_f0.split_string(prompt, self.csv_f0.cut_off_length, self.csv_f0.endcase_char)
            self.player_prompt_list.append(str_list)
            
        self.t1 = textfile_formatter()
        #print(self.csv_f0.str_to_str_list(self.t1.str_list_to_dialogue_list(self.t1.read_text_from_file('npc_dialogue_files/npc_dialogue_txt_files/Test.txt'))))
            
        #self.full_dialogue_list = self.csv_f0.get_all_npc_data('dialogue_data')
        
        # print(self.csv_f0.get_specific_npc_data('Test', full_dialogue_list))
        # print(self.csv_f0.get_specific_npc_data('Test2', full_dialogue_list))
        
        #plot index list will be a dynamic list under world for convenience since NPCs that access/modify it will be instantiated under world
        #it will be initially set when the main menu code is executed
        self.plot_index_list = []
        self.npc_current_dialogue_list = [0,0]
        
        self.lvl_slice_lists = []
            
        self.slice_width = 1 #tiles
        self.slice_height = 15
        self.num_slices = 0
        
        self.screen_w = screen_w
        self.screen_h = screen_h
        #self.screen_rect = pygame.rect.Rect(0, 0, screen_w, screen_h)
        
        self.world_map_non_parallax = pygame.Surface((32,32), pygame.SRCALPHA).convert_alpha
        #self.world_map_non_parallax.fill(pygame.Color(0,0,0,0))
        
    def get_specific_npc_dialogue(self, name):
        path = 'npc_dialogue_files/npc_dialogue_txt_files/'
        rtn_list = tuple(self.csv_f0.str_to_str_list(self.t1.str_list_to_dialogue_list(self.t1.read_text_from_file(path + name + '.txt'))))
        
        return rtn_list
    
    def get_num_slices(self, rows):
        num_slices = rows/self.slice_width
        if num_slices > int(num_slices):
            self.num_slices = int(num_slices) + 1 #there's a partial slice at the end
        else:
            self.num_slices = int(num_slices)
            
    def clear_slice_lists(self):
        for slice_list in self.lvl_slice_lists:
            for slice in slice_list:
                slice *= 0
        self.lvl_slice_lists *= 0
            
    def initialize_slice_lists(self, rows, data_layers):
        self.clear_slice_lists()
        self.get_num_slices(rows)
        
        for i in range(data_layers):
            temp_list = []
            for slice_num in range(self.num_slices):
                slice_x_coord = slice_num * self.slice_width * 32
                slice_rect = pygame.rect.Rect(slice_x_coord, 0, self.slice_width * 32, self.slice_height * 32)
                temp_list.append([slice_rect, False, []])
            
            self.lvl_slice_lists.append(temp_list)
            
        #print(slice_coord_list)
        #print(self.lvl_slice_lists[0])
        
            
    def fill_slice_list(self, layer, tile_x_coord, tile_data):
        # [ slices for layer 0
        #   slices for layer 1
        #   etc
        # ]
        for slice_index in range(self.num_slices):
            if tile_x_coord >= slice_index * self.slice_width * 32 and tile_x_coord < (slice_index + 1) * self.slice_width * 32:
                self.lvl_slice_lists[layer][slice_index][2].append(tile_data)
                
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

    def set_plot_index_list(self, plot_index_list):
        self.plot_index_list = plot_index_list
        
    # #pil_update_flag will be set to true everytime plot index list is updated for a textprompt obj
    # #useful method incase multiple npc's with plot sensitive lines are in a single level
    # def update_all_plot_index_lists(self, textprompt_group):
    #     for obj in textprompt_group:
    #         if obj.pil_update_flag:
    #             self.plot_index_list = obj.plot_index_list
    #             obj.pil_update_flag = False
    #             #print(self.plot_index_list)
    #             for obj in textprompt_group:
    #                 obj.plot_index_list = self.plot_index_list
                    
                
    #for saving
    def get_plot_index_list(self, textprompt_group):
        self.update_all_plot_index_lists(textprompt_group)
        return self.plot_index_list
    
    def clear_data(self):
        for lvl_data in self.detailed_lvl_data_list:
            lvl_data *= 0
            

    #loading the level
    def process_data(self, level, the_sprite_group, screenW, screenH, level_data, ini_vol):
        #clear old data
        raw_lvl_data_list = []
        self.clear_data()
        
        #reset level window
        #self.screen_rect.topleft = (0,0)
        
        #populate raw_lvl_data_list with lists of int values from level csv files
        raw_lvl_data_list = self.get_raw_csv_data(level, level_data[0:2])
        
        #set up slice processing
        #self.clear_slice_lists()
        #self.initialize_slice_lists(level_data[1], len(self.level_data_str_tuple))
        
        
        
        #process int lists into detailed list
        self.process_coords_vslice(raw_lvl_data_list[0], screenW, screenH, self.detailed_lvl_data_list[0])
        enemy0_id = 0
        transition_index = 0
        transition_data = []
        
        #processing interactable layer
        for y, row in enumerate(raw_lvl_data_list[2]):
            for x, tile in enumerate(row):
                if tile >= 0:

                    img = self.tileList[0][tile]
                    img_rect = img.get_rect()
                    if(tile == 17):#pass thru 1 way
                        #img = pygame.transform.scale(img, (32,32))
                        img_rect = pygame.Rect(0, 0, 32, 16)
                    elif(tile == 10):#level transition tile
                        img = self.tileList[0][9]
                        img_rect = pygame.Rect(0, 0, level_data[2][transition_index][0], level_data[2][transition_index][1])
                        transition_data = level_data[2][transition_index][2:5] #passed to the player: next_level, next coords
                        transition_index += 1
                        
                    #if you want to resize the screen you might need to change 32 to a variable
                    img_rect.x = x * 32
                    if(tile == 15 or tile == 16 or tile == 18 or tile == 2):#if half tile
                        img_rect.y = (y * 32) + 16
                    else:
                        img_rect.y = y * 32
                    
                    tile_data = (img, img_rect, tile, transition_data)
                    
                    
                        
                    if all(tile != s_tile for s_tile in self.special_tiles):
                        self.solids.append(tile_data)
                        #self.fill_slice_list(2, img_rect.x, tile_data)
                    elif tile == 28:
                        enemy0 = enemy_32wide(x * 32, y * 32, 3, 2, 'dog', enemy0_id, ini_vol)
                        the_sprite_group.enemy0_group.add(enemy0)
                        enemy0_id += 1#for enemy-enemy collisions/ anti stacking
                    elif tile == 29:
                        enemy0 = enemy_32wide(x * 32, y * 32, 2, 2, 'shooter', enemy0_id, ini_vol)
                        the_sprite_group.enemy0_group.add(enemy0)
                        enemy0_id += 1#for enemy-enemy collisions/ anti stacking
                    elif tile == 45:
                        p_int = player_interactable_(x * 32, y * 32, 1, 1, 'crusher_top', ini_vol, True, False)
                        the_sprite_group.p_int_group.add(p_int)
                    elif tile == 46:
                        p_int2 = player_interactable_(x * 32, y * 32, 2, 1, 'spinning_blades', ini_vol, True, False)
                        the_sprite_group.p_int_group2.add(p_int2)
                    elif tile == 47:
                        p_int = player_interactable_(x * 32, y * 32, 1, 1, 'moving_plat_h', ini_vol, True, False)
                        the_sprite_group.p_int_group.add(p_int)
                    elif tile == 48:
                        p_int = player_interactable_(x * 32, y * 32, 1, 1, 'moving_plat_v', ini_vol, True, False)
                        the_sprite_group.p_int_group.add(p_int)
                    elif tile == 49:
                        dialogue_list = self.get_specific_npc_dialogue('Test')
                        Testnpc = Test(x * 32, y * 32, 2, 1, 'Test', ini_vol, True, dialogue_list, self.plot_index_list, self.npc_current_dialogue_list, level, player_inventory= [])
                        the_sprite_group.textprompt_group.add(Testnpc)
                        
                    elif tile == 50:
                        dialogue_list = self.get_specific_npc_dialogue('Test2')
                        Testnpc2 = Test2(x * 32, y * 32, 2, 1, 'Test2', ini_vol, True, dialogue_list, self.plot_index_list, self.npc_current_dialogue_list, level, player_inventory= [])
                        the_sprite_group.textprompt_group.add(Testnpc2)
                        
                        
            
        #load bg
        for i in range(len(self.detailed_lvl_data_list) -3):
            self.process_bg(raw_lvl_data_list[i+3], self.detailed_lvl_data_list[i+3], the_sprite_group, i+3)
        #load fg
        self.process_bg(raw_lvl_data_list[1], self.detailed_lvl_data_list[1], the_sprite_group, 1)
        
        
        #self.world_map_non_parallax = self.create_map(level_data[0:2], self.detailed_lvl_data_list[1:4]).convert_alpha()
        
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
            
        # print(self.x_scroll_en)
        # print(self.y_scroll_en)
        #print(self.lvl_slice_lists[0][0])
        
        
    def process_bg(self, data, rtrn_list, the_sprite_group, index_):   
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    
                    if tile < 30:
                        img = self.tileList[0][tile]
                    elif tile >= 30 and tile < 50:
                        img = self.tileList[1][tile-30]
                        
                    if tile == 31:
                        bg_sprite = lamp(x*32, y*32, 1, False, 'lamp')
                        the_sprite_group.bg_sprite_group.add(bg_sprite)
                    elif tile == 36:
                        bg_sprite = tree(x*32, y*32, 1, False, 'tree')
                        the_sprite_group.bg_sprite_group.add(bg_sprite)
                    elif tile == 39:        
                        bg_sprite = fountain(x*32, y*32, 1, False, 'fountain')
                        the_sprite_group.bg_sprite_group.add(bg_sprite)
                    
                    img_rect = img.get_rect()
                    img_rect.x = x * 32
                    img_rect.y = y * 32
                    tile_data = (img, img_rect, tile)
                    
                    # if index_ <= 4: #do not fill slices for filter and parallax layers
                    #     self.fill_slice_list(index_, img_rect.x, tile_data)
                    
                    if tile != 36 and tile != 39 and tile != 31:
                        rtrn_list.append(tile_data)
                    
    def scroll_slices_all_layers(self, scroll_x):
        for slice_list in self.lvl_slice_lists[0:5]: #cutting out filter and parallax layers
            for slice in slice_list: #slice = [rect, loaded, tile list[]]
                slice[0][0] -= scroll_x
                if slice[1]: #slice is loaded
                    for tile in slice[2]:
                        tile[1][0] = slice[0][0]
            
    def load_unload_slices(self, window_rect):
        for i in range(len(self.lvl_slice_lists[0:5])): #cutting out filter and parallax layers
            for slice in self.lvl_slice_lists[i]:
                if window_rect.colliderect(slice[0]) and not slice[1]: #load
                    
                    for tile in slice[2]:
                        self.loaded_lvl_data_list[i].append(tile)
                        
                    slice[1] = True
                elif not window_rect.colliderect(slice[0]) and slice[1]: #unload
                    for loaded_tile in self.loaded_lvl_data_list[i]:
                        for tile in slice[2]:
                            if loaded_tile == tile:
                                self.loaded_lvl_data_list[i].pop(self.loaded_lvl_data_list[i].index(loaded_tile))
                         
                    slice[1] = False
                        
            #print(i)
                        
                                       
    def draw_bg_layers(self, screen, scroll_X, scroll_Y, data):
        #currently only handles x scrolling
        #scroll_amnt = scroll_X
        #logic for looping bg, maximum sprite size is 480x480
        for tile in data:
            if (data == self.bg4 or data == self.bg5 or data == self.bg6):
                if tile[1][0] > tile[1].width:
                    tile[1][0] -= (2 * tile[1].width)
                elif tile[1][0] < -tile[1].width:
                    tile[1][0] += (2 * tile[1].width)
                tile[1][0] -= scroll_X
                if tile[1].x <= self.screen_w and tile[1].x > -tile[1].width:
                    screen.blit(tile[0], tile[1]) # (image, position)
               
            else:
                tile[1][0] -= scroll_X
                tile[1][1] -= scroll_Y
                if tile[1].x <= self.screen_w and tile[1].x > -self.screen_w//2:
                    screen.blit(tile[0], tile[1]) # (image, position)
                    
                
            
          
                
    def draw_filter_layer(self, screen, data):#filter layer doesn't scroll, for efficiency it should be 640x480
        for tile in data:
            screen.blit(tile[0], tile[1])
        
    def update_tiles(self, tile, screen, scroll_X, scroll_Y):
        tile[1][0] -= scroll_X
        tile[1][1] -= scroll_Y
        if tile[1][0] > -32 and tile[1][0] < 640 + 32:
            screen.blit(tile[0], tile[1]) # (image, position)
                    
    def draw(self, screen, scroll_X, scroll_Y): #MOVE sliceS HERE
        
        # self.load_unload_slices(self.screen_rect)
        # self.scroll_slices_all_layers(scroll_X)
        
        # self.screen_rect.x += scroll_X
        # self.screen_rect.y += scroll_Y
        
        if scroll_X > 0:
            correction = 1
        else:
            correction = 0
        
        self.draw_bg_layers(screen, (scroll_X + correction)//3, 0, self.bg6)
        self.draw_bg_layers(screen, 4*(scroll_X + correction)//7, 0, self.bg5)
        self.draw_bg_layers(screen, 7*(scroll_X + correction)//9, 0, self.bg4)
        self.draw_filter_layer(screen, self.bg3)
        self.draw_bg_layers(screen, (scroll_X), scroll_Y, self.bg2)#detailed 1:1 bg layer 2
        self.draw_bg_layers(screen, (scroll_X), scroll_Y, self.bg1)
        
        #these scroll every tile in a layer
        
        for tile in self.solids:
            #this code below basically means the first index: [1], gets the tile's rect, 
            #then the [0] right after gets the x coordinate
            #if you were to swap [0] with [1] you'd get the y coord
            
            tile[1][0] -= scroll_X
            tile[1][1] -= scroll_Y
            if tile[1][0] > -32 and tile[1][0] < 640 + 32:
                screen.blit(tile[0], tile[1]) # (image, position)
                
      
        
        for tile in self.coords:
            tile[1][0] -= scroll_X #the coords file does not have an image
            tile[1][1] -= scroll_Y
            
            
        self.draw_bg_layers(screen, scroll_X, scroll_Y, self.fg)
        
        #screen.blit(self.world_map_non_parallax, (0,0), self.screen_rect)
        
        
        return (self.coords[0][1][0], self.coords[0][1][1]) #x and y of first tile
            
        
            