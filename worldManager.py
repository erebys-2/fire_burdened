import pygame
pygame.init()
import os
from playerFile import player
from enemy32File import enemy_32wide
from particle import particle_


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

        self.lvl_data_list = [
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
    
    def clear_data(self):
        for lvl_data in self.lvl_data_list:
            lvl_data *= 0

    def process_data(self, level_data_list, the_sprite_group, screenW, screenH, level_transitions):
        self.clear_data()
        self.process_coords(level_data_list[0], screenW, screenH, self.lvl_data_list[0])
        enemy0_id = 0
        transition_index = 0
        transition_data = []
        #processing interactable layer
        for y, row in enumerate(level_data_list[2]):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = self.tileList[0][tile]
                    img_rect = img.get_rect()
                    if(tile == 17):#pass thru 1 way
                        img_rect = pygame.Rect(0, 0, 32, 16)
                    elif(tile == 10):#level transition tile
                        img = self.tileList[0][9]
                        img_rect = pygame.Rect(0, 0, level_transitions[transition_index][0], level_transitions[transition_index][1])
                        transition_data = level_transitions[transition_index][2:5] #passed to the player: next_level, next coords
                        transition_index += 1
                        
                    #if you want to resize the screen you might need to change 32 to a variable
                    img_rect.x = x * 32
                    if(tile == 15 or tile == 16 or tile == 18 or tile == 2):#if half tile
                        img_rect.y = (y * 32) + 16
                    else:
                        img_rect.y = y * 32

                    tile_data = (img, img_rect, tile, transition_data)
                    if tile != 26 and tile != 28: #if it isn't grass or a mob
                        self.solids.append(tile_data)
                    #add elifs for addition behaviors like spikes or smth
                    #russ instantiated players and enemies in here
                    elif tile == 28:
                        enemy0 = enemy_32wide(x * 32, y * 32, 2, 2, 'shooter', enemy0_id)
                        the_sprite_group.enemy0_group.add(enemy0)#for enemy-enemy collisions/ anti stacking
                        enemy0_id += 1
            
        #load bg
        for i in range(len(self.lvl_data_list) -3):
            self.process_bg(level_data_list[i+3], self.lvl_data_list[i+3], the_sprite_group)
        #load fg
        self.process_bg(level_data_list[1], self.lvl_data_list[1], the_sprite_group)


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
                        bg_particle_0 = particle_(x*32, y*32, -1, 1, 'lamp_flash', False, 0, False)
                        the_sprite_group.particle_group_bg.add(bg_particle_0)
                    # elif tile == 36:
                    #     bg_particle_0 = particle_(x*32, y*32, -1, 1, 'tree_leaves', False, 0)
                    #     the_sprite_group.particle_group_bg.add(bg_particle_0)
                    elif tile == 39:
                        bg_particle_0 = particle_(x*32, y*32, -1, 1, 'fountain', False, 0, False)
                        the_sprite_group.particle_group_bg.add(bg_particle_0)
                    
                    img_rect = img.get_rect()
                    img_rect.x = x * 32
                    img_rect.y = y * 32
                    tile_data = (img, img_rect, tile)
                    
                    rtrn_list.append(tile_data)
                    
                                       
    def draw_bg_layers(self, w_screen, scroll_X, data):
        #currently only handles x scrolling
        scroll_amnt = scroll_X
        #logic for looping bg, maximum sprite size is 480x480
        for tile in data:
            if (data == self.bg3 or data == self.bg4 or data == self.bg5 or data == self.bg6):
                #tile[1] is position, afterwards [0] = x, [1] = y
                if tile[1][0] > 960:
                    tile[1][0] -= (960+960)
                elif tile[1][0] < -960:
                    tile[1][0] += (960+960)

            tile[1][0] -= scroll_amnt
            if tile[1].x <= 640:
                w_screen.blit(tile[0], tile[1]) # (image, position)
                    
    def draw(self, w_screen, scroll_X, scroll_y):
        #change scroll rates in these calls, you need to place 3 480x480's back to back for full scrolling
        #Note: ONLY 2 PARALLAX LAYERS ARE SUPPORTED
        #the filter layer is also laggy
        
        self.draw_bg_layers(w_screen, scroll_X//3, self.bg6) #3 parallax layers screws up the game
        self.draw_bg_layers(w_screen, 4*scroll_X//7, self.bg5)
        self.draw_bg_layers(w_screen, 7*scroll_X//9, self.bg4)
        self.draw_bg_layers(w_screen, scroll_X, self.bg3)#filter layer
        self.draw_bg_layers(w_screen, scroll_X, self.bg2)#detailed 1:1 bg layer 2
        self.draw_bg_layers(w_screen, scroll_X, self.bg1)
        
        for tile in self.solids:
            #this code below basically means the first index: [1], gets the tile's rect, 
            #then the [0] right after gets the x coordinate
            #if you were to swap [0] with [1] you'd get the y coord
            tile[1][0] -= scroll_X
            w_screen.blit(tile[0], tile[1]) # (image, position)
        
        for tile in self.coords:
            tile[0][0] -= scroll_X #the coords file does not have an image
            
        self.draw_bg_layers(w_screen, scroll_X, self.fg)
            
        
            