import pygame
import os
from playerFile import player #type: ignore
from enemy32File import enemy_32wide #type: ignore
from particle import particle_ #type: ignore
from player_interactable import player_interactable_
from dialogueCSVformatter import csv_extracter
from BGspritesFile import tree, fountain, lamp
import csv

from npcFile import npc, Test, Test2

class World():
    def __init__(self):
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
        

        self.enhanced_lvl_data_list = [
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
            
        #self.full_dialogue_list = self.csv_f0.get_all_npc_data('dialogue_data')
        
        # print(self.csv_f0.get_specific_npc_data('Test', full_dialogue_list))
        # print(self.csv_f0.get_specific_npc_data('Test2', full_dialogue_list))
        
        #plot index list will be a dynamic list under world for convenience since NPCs that access/modify it will be instantiated under world
        #it will be initially set when the main menu code is executed
        self.plot_index_list = []
        
        
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
                    
        return level_csv_data
    
    def get_raw_csv_data(self, level, lvl_size):
        raw_lvl_data_list = []
        for level_data_str in self.level_data_str_tuple:
            raw_lvl_data_list.append(self.read_level_csv_data(level, lvl_size[0], lvl_size[1], level_data_str))
            
        return raw_lvl_data_list
        
    
    #called in main menu where either a new game or save file is loaded

    def set_plot_index_list(self, plot_index_list):
        self.plot_index_list = plot_index_list
        
    #pil_update_flag will be set to true everytime plot index list is updated for a textprompt obj
    #useful method incase multiple npc's with plot sensitive lines are in a single level
    def update_all_plot_index_lists(self, textprompt_group):
        for obj in textprompt_group:
            if obj.pil_update_flag:
                self.plot_index_list = obj.plot_index_list
                obj.pil_update_flag = False
                #print(self.plot_index_list)
                for obj in textprompt_group:
                    obj.plot_index_list = self.plot_index_list
                    
                
    #for saving
    def get_plot_index_list(self, textprompt_group):
        self.update_all_plot_index_lists(textprompt_group)
        return self.plot_index_list
    
    def clear_data(self):
        for lvl_data in self.enhanced_lvl_data_list:
            lvl_data *= 0
            

    #loading the level
    def process_data(self, level, the_sprite_group, screenW, screenH, level_data, ini_vol):
        raw_lvl_data_list = []
        self.clear_data()

        
        raw_lvl_data_list = self.get_raw_csv_data(level, level_data[0:2])
        
        self.process_coords(raw_lvl_data_list[0], screenW, screenH, self.enhanced_lvl_data_list[0])
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
                        dialogue_list = self.csv_f0.get_specific_npc_data('Test', self.csv_f0.get_all_npc_data('dialogue_data'))
                        Testnpc = Test(x * 32, y * 32, 2, 1, 'Test', ini_vol, True, dialogue_list, self.plot_index_list, level, player_inventory= [])
                        the_sprite_group.textprompt_group.add(Testnpc)
                        
                    elif tile == 50:
                        dialogue_list = self.csv_f0.get_specific_npc_data('Test2', self.csv_f0.get_all_npc_data('dialogue_data'))
                        Testnpc2 = Test2(x * 32, y * 32, 2, 1, 'Test2', ini_vol, True, dialogue_list, self.plot_index_list, level, player_inventory= [])
                        the_sprite_group.textprompt_group.add(Testnpc2)
                        
                        
            
        #load bg
        for i in range(len(self.enhanced_lvl_data_list) -3):
            self.process_bg(raw_lvl_data_list[i+3], self.enhanced_lvl_data_list[i+3], the_sprite_group)
        #load fg
        self.process_bg(raw_lvl_data_list[1], self.enhanced_lvl_data_list[1], the_sprite_group)


    def process_coords(self, data, screenW, screenH, rtrn_list):
        x_coord = 0
        y_coord = 0
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile == -1:
                    x_coord = x * 32
                    y_coord = y * 32
                    
                    img_rect = pygame.Rect(0, 0, 32, 32)
                    img_rect.x = x_coord
                    img_rect.y = y_coord
                    
                    tile_data = (img_rect, (x_coord, y_coord))
                    #print(tile_data)
                    
                    rtrn_list.append(tile_data)
        self.world_limit = (x_coord, y_coord)
        #scroll enables
        if x_coord + 32 > screenW:
            self.x_scroll_en = True
        else:
            self.x_scroll_en = False
            
        if y_coord + 32 > screenH:
            self.y_scroll_en = True
        else:
            self.y_scroll_en = False
            
        # print(self.x_scroll_en)
        # print(self.y_scroll_en)
    
    def process_bg(self, data, rtrn_list, the_sprite_group):   
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
                    if tile != 36 and tile != 39 and tile != 31:
                        rtrn_list.append(tile_data)
                    
                                       
    def draw_bg_layers(self, screen, scroll_X, scroll_Y, data):
        #currently only handles x scrolling
        #scroll_amnt = scroll_X
        #logic for looping bg, maximum sprite size is 480x480
        for tile in data:
            if (data == self.bg3 or data == self.bg4 or data == self.bg5 or data == self.bg6):
                if tile[1][0] > 960:
                    tile[1][0] -= (960+960)
                elif tile[1][0] < -960:
                    tile[1][0] += (960+960)

            tile[1][0] -= scroll_X
            tile[1][1] -= scroll_Y
            
            if tile[1].x <= 640 and tile[1].x > -960:
                screen.blit(tile[0], tile[1]) # (image, position)
                
    def draw_filter_layer(self, screen, data):#filter layer doesn't scroll, for efficiency it should be 640x480
        for tile in data:
            screen.blit(tile[0], tile[1])
        
                    
    def draw(self, screen, scroll_X, scroll_Y):
        
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
        
        for tile in self.solids:
            #this code below basically means the first index: [1], gets the tile's rect, 
            #then the [0] right after gets the x coordinate
            #if you were to swap [0] with [1] you'd get the y coord
            tile[1][0] -= scroll_X
            tile[1][1] -= scroll_Y
            if tile[1][0] > -32 and tile[1][0] < 640 + 32:
                screen.blit(tile[0], tile[1]) # (image, position)
        
        for tile in self.coords:
            tile[0][0] -= scroll_X #the coords file does not have an image
            tile[0][1] -= scroll_Y
            
            
        self.draw_bg_layers(screen, scroll_X, scroll_Y, self.fg)
        
        return (self.coords[0][0][0], self.coords[0][0][1]) #x and y of first tile
            
        
            