import pygame
import os
import button
import csv
from textfile_handler import textfile_formatter
from worldManager import World

pygame.init()
from profilehooks import profile
#@profile

def main():
    SCREEN_WIDTH = 960
    SCREEN_HEIGHT = 480
    LOWER_MARGIN = 96
    SIDE_MARGIN = 320
    
    t1 = textfile_formatter()
    path = 'assets/config_textfiles/level_config/'
    level_sizes_dict = t1.str_list_to_dict(t1.read_text_from_file(os.path.join(path + 'level_sizes_dict.txt')), 'list')
    #print(level_sizes_dict)
    
    layer_desc_dict = {
        0:'true foreground',
        1:'foreground',
        2:'game layer',
        3:'game layer filler',
        4:'filter',
        5:'detailed bg1',
        6:'detailed bg2',
        7:'parallax fast',
        8:'parallax med',
        9:'parallax slow'
    }
    
    layer_name_dict = {
        0:'coord_data',
        1:'fg_data',
        2:'fg_1_data',
        3:'data',
        4:'bg1_data',
        5:'bg3_data',
        6:'bg2_data',
        7:'bg2_1_data',
        8:'bg4_data',
        9:'bg5_data',
        10:'bg6_data'
    }
    
    world_layer_index = [key for key in layer_name_dict if layer_name_dict[key] == 'data'][0]-1
    filter_layer_index = [key for key in layer_name_dict if layer_name_dict[key] == 'bg3_data'][0]-1
    
    layer_list = []
    
    
    path = 'assets/config_textfiles/world_config/'
    path2 = 'assets/config_textfiles/level_config/'
    sprite_group_tiles_dict = t1.str_list_to_dict(t1.read_text_from_file(os.path.join(path + 'sprite_group_tiles_dict.txt')), 'list')
    static_bg_oversized_tiles_dict = t1.str_list_to_dict(t1.read_text_from_file(os.path.join(path + 'static_bg_oversized_tiles_dict.txt')), 'int')
    special_hitbox_tiles_dict = t1.str_list_to_dict(t1.read_text_from_file(os.path.join(path + 'special_hitbox_tiles_dict.txt')), 'none')
    
    #should be user entered for later
    print('\nstandard level is 15 rows, 200 cols ')

    #level is selected
    print('level input will either be loaded or a new level creation will be prompted')
    input_level = int(input('enter level: '))
  
    if input_level < 0:
        levels_must_be_greater_than_0 = 0/0

    if input_level not in level_sizes_dict:
        row_str = input('enter rows: ')
        col_str = input('enter cols: ')
        ROWS = int(row_str)
        MAX_COLS = int(col_str)
        level = input_level
        direct_load = False

    else:
        ROWS = level_sizes_dict[input_level][0]
        MAX_COLS = level_sizes_dict[input_level][1]
        row_str = str(ROWS)
        col_str = str(MAX_COLS)
        level = input_level
        direct_load = True

    #create surfaces
    tile_id_map_dict = {}
    map_dict = {}
    for i in range(len(layer_name_dict)-1):
        map_dict[i] = pygame.Surface((MAX_COLS * 32, ROWS * 32), pygame.SRCALPHA).fill(pygame.Color(0,0,0,0))
        tile_id_map_dict[i] = pygame.Surface((MAX_COLS * 32, ROWS * 32), pygame.SRCALPHA).fill(pygame.Color(0,0,0,0))
        

    #the standard size of a tile should be 32
    #background art might have to have a separate editor- it is a bridge we will cross later
    TILE_SIZE = 32

    isolate_layer = False

    grid_on = False
    scroll_left = False
    scroll_right = False
    scroll = 0
    scroll_speed = 1

    screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN), 0, 32)
    pygame.display.set_caption('editor window')
    w = World(-1,-1)

    #framerate set up------------------------------------
    clock = pygame.time.Clock()
    FPS = 60
    #ideas for bg tiles:
    #lamps, fences, rocks, debris, gates, fountains, statues

    #set bg rect
    canvas_rect = pygame.Rect((0,0), (SCREEN_WIDTH,480))
    curr_layer = world_layer_index

    #level = 0
    t_set_index = 0
    tile_index = 0
    current_tile = 0
    tile_list = []
    tile_types = ['standard', 'bg_oversized']
    change_once = False 

    eraser_mode = False
    insert_mode = False
    select_mode = False
    insert_pos = 0
    shift = False
    ctrl = False
    ini_scroll = 0
    copied_chunk = []

    #load tiles

    for tile_set in tile_types:
        temp_list = []
        tile_count = len(os.listdir(f'assets/sprites/tileset/{tile_set}'))

        for i in range(tile_count):
            img = pygame.image.load(f'assets/sprites/tileset/{tile_set}/{i}.png').convert_alpha()
            temp_list.append(img)
        tile_list.append(temp_list)


    save_img = pygame.image.load('assets/sprites/save_btn.png').convert_alpha()
    load_img = pygame.image.load('assets/sprites/load_btn.png').convert_alpha()

    '''
    good bg colors
    20, 40, 80
    20, 30, 80
    15, 13, 40
    7, 6, 28

    '''


    WHITE = (210, 210, 210)
    BG_color = (200,143,167)
    black = (0,0,0)
    RED = (255, 128, 128)
    BG_color2 = (50,50,50)

    #define font
    font = pygame.font.SysFont('SimSun', 12)
    font2 = pygame.font.SysFont('SimSun', 16)
    
     #button stuff
    save_button = button.Button(SCREEN_WIDTH // 3 + 150, SCREEN_HEIGHT + LOWER_MARGIN - 50, save_img, 1)
    load_button = button.Button(SCREEN_WIDTH // 3 + 235, SCREEN_HEIGHT + LOWER_MARGIN - 50, load_img, 1)
                        

    #populate buttons
    button_list = []
    button_col = 0
    button_row = 0
    temp_dist = 0
    
    
    for i in range(len(tile_list[t_set_index])):
        if i == 15 or i == 16 or i  == 18:#these are the half tiles
            temp_dist = 20
        else:
            temp_dist = 4
        tile_button = button.Button(640 + (40 * button_col) + 4, (40 * button_row) + temp_dist, tile_list[t_set_index][i], 1)
        button_list.append(tile_button)
        button_col += 1
        if button_col == 16:
            button_row += 1
            button_col = 0
            
    description = 'game layer'

    reload_map = False
    reload_all_maps = False
    
    is_loading = False
    is_saving = False

    #create empty tile list(s)

    def empty_list_gen():
        rtn_list = []
        for row in range(ROWS):
            row = [-1] * MAX_COLS
            rtn_list.append(row)
            
        return rtn_list
    #other methods--------------

    def check_onscreen(x):
        return (x >= 0 and x < 640)

    def draw_grid():
        #vertical lines
        for c in range(MAX_COLS + 1):
            if TILE_SIZE*c in range(scroll, scroll+640):
                pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
                if c%10 == 0:
                    pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT), 3)
                screen.blit(font.render(str(c*32), False, (255,255,255)), (c*32 - scroll, 0))
        #horizontal lines
        for c in range(ROWS + 1):
            #if TILE_SIZE*c in range(scroll, scroll+640):
            pygame.draw.line(screen, WHITE, (0, c * TILE_SIZE), (SCREEN_WIDTH, c * TILE_SIZE))
            screen.blit(font.render(str(c*32), False, (255,255,255)), (0, c*32))

    def draw_text(surface, text, font, text_col, x, y):
        img = font.render(text, False, text_col)#.convert_alpha()
        surface.blit(img, (x, y))
        
    def get_tile_img_bg(tile, sprite_group_tiles_dict, static_bg_oversized_tiles_dict):
        img = None
        y_disp = 0
        if tile in sprite_group_tiles_dict and sprite_group_tiles_dict[tile][3] != -1:
            img = tile_list[1][sprite_group_tiles_dict[tile][3]]
            if tile != 46:
                scale = 1
            else:
                scale = 2
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))

        elif tile in static_bg_oversized_tiles_dict:
            img = tile_list[1][static_bg_oversized_tiles_dict[tile]]
            if tile != 46:
                scale = 1
            else:
                scale = 2
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))

        elif tile in (15,16,18,2,60):
            img = tile_list[t_set_index][tile]
            y_disp = 16
        else: 
            img = tile_list[t_set_index][tile]
            
        return (img, y_disp, img.get_size())

    def draw_bg(data, layer_index, static_bg_oversized_tiles_dict, sprite_group_tiles_dict):
        map_ = pygame.Surface((MAX_COLS * 32, ROWS * 32), pygame.SRCALPHA)
        tile_id_map = pygame.Surface((MAX_COLS * 32, ROWS * 32), pygame.SRCALPHA)

        for y, row in enumerate(data):#world data and bg data should have the same amount of data
            for x, tile_ in enumerate(row):
                if tile_ >= 0:
                    (img, y_disp, size) = get_tile_img_bg(tile_, sprite_group_tiles_dict, static_bg_oversized_tiles_dict)
                    
                    if layer_index == filter_layer_index:
                        for i in range((MAX_COLS*32)//img.get_width() + 1):
                            map_.blit(img, (i * img.get_width(), (y * TILE_SIZE)+y_disp))
                    else:
                        map_.blit(img, (x * TILE_SIZE, (y * TILE_SIZE)+y_disp))

                    draw_text(tile_id_map, str(tile_), font2, WHITE, x*32 + 8, y*32 + 8)
                    
        return (map_.convert_alpha(), tile_id_map.convert_alpha())

    def draw_world(data, static_bg_oversized_tiles_dict, sprite_group_tiles_dict):
        map_ = pygame.Surface((MAX_COLS * 32, ROWS * 32), pygame.SRCALPHA)
        tile_id_map = pygame.Surface((MAX_COLS * 32, ROWS * 32), pygame.SRCALPHA)

        for y, row in enumerate(data):#world data and bg data should have the same amount of data
            for x, tile in enumerate(row):
                if tile >= 0:
                    (img, y_disp, size) = get_tile_img_bg(tile, sprite_group_tiles_dict, static_bg_oversized_tiles_dict)
                 
                    map_.blit(img, (x * TILE_SIZE, (y * TILE_SIZE) + y_disp))
                    draw_text(tile_id_map, str(tile), font2, WHITE, x*32 + 8, y*32 + 8)
        return (map_.convert_alpha(), tile_id_map.convert_alpha())

   

    #-------Reading and writing level data for loading---------------------------------------
    def read_level_data(level, data_str):
        rtn_list = []
        with open(f'assets/level_files/level{level}/level{level}_{data_str}.csv', newline= '') as csvfile:
            reader = csv.reader(csvfile, delimiter= ',') #what separates values = delimiter
            for x, current_row in enumerate(reader):
                row_list = []
                for y, tile in enumerate(current_row):
                    row_list.append(int(tile))
                rtn_list.append(row_list)

        return rtn_list

    def write_level_data(level, level_sizes_dict, data_, data_str):
        if f'level{level}' not in os.listdir('assets/level_files'):
            os.mkdir(f'assets/level_files/level{level}')
        with open(f'assets/level_files/level{level}/level{level}_{data_str}.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter = ',')
            for row in data_:
                writer.writerow(row)
                    
    def editing_lvl_data(x, y, current_tile, data, data_index, world_layer_index, eraser_mode):
        reload_map = False
        rtn_data = data
        if pygame.mouse.get_pressed()[0] == 1 and not eraser_mode:
            if current_tile in sprite_group_tiles_dict and data_index != world_layer_index:
                print("cannot place sprite group tile in non-game layer")
            elif rtn_data[y][x] != current_tile:
                rtn_data[y][x] = current_tile
                reload_map = True
        if pygame.mouse.get_pressed()[2] == 1 or (pygame.mouse.get_pressed()[0] == 1 and eraser_mode):
            if rtn_data[y][x] != -1:
                rtn_data[y][x] = -1
                reload_map = True
            # rtn_data[y][x] = -1
            # reload_map = True
            
        return (rtn_data, reload_map)

    
    def extend_lvl(extension, layer_list):
        rtn_layer_list = []#3d list of lists
        for layer in layer_list:#layer is 2d
            new_layer = []
            for i in range(ROWS):
                if extension > 0:
                    data_list = layer[i] + [-1]*extension
                else:
                    data_list = layer[i][:MAX_COLS+extension]
                new_layer.append(data_list)
            rtn_layer_list.append(new_layer)

        return rtn_layer_list
    
    def copy_chunk(start_pos, end_pos, layer_list):
        temp_chunk = []#3d list of lists
        for layer in layer_list:
            temp_layer = []
            for i in range(ROWS):
                temp_layer.append(layer[i][start_pos:end_pos])
            temp_chunk.append(temp_layer)
        print("chunk copied!")
        return temp_chunk        
    
    def paste_chunk(pos, chunk, layer_list):
        tiles_added = len(chunk[0][0])
        for k in range(len(layer_list)):
            for i in range(ROWS):
                for j in range(tiles_added):
                    layer_list[k][i].insert(pos, chunk[k][i][tiles_added -1 -j])
        print("chunk pasted!")
        return tiles_added
    

    #running the editor----------------------------------------------------
    
        #creating a new level
    def create_new_lvl(layer_name_dict):
        rtn_list = []
        rtn_map_dict = {}
        rtn_TIM_dict = {}
        for layer in layer_name_dict:
            rtn_list.append(empty_list_gen())
        
            #create ground
            if layer_name_dict[layer] == 'data':
                rtn_list[layer][ROWS - 1] = [17]*MAX_COLS
                
            if layer != 0:#skip coord layer for creating maps
                if layer != world_layer_index:
                    (rtn_map_dict[layer-1], rtn_TIM_dict[layer-1]) = draw_bg(rtn_list[layer], layer-1, static_bg_oversized_tiles_dict, sprite_group_tiles_dict)
                else:
                    (rtn_map_dict[layer-1], rtn_TIM_dict[layer-1]) = draw_world(rtn_list[layer], static_bg_oversized_tiles_dict, sprite_group_tiles_dict)
                    
        return (rtn_list, rtn_map_dict, rtn_TIM_dict)

    
    def load_lvl(level, layer_name_dict, world_layer_index, static_bg_oversized_tiles_dict, sprite_group_tiles_dict):
        rtn_list = []
        rtn_map_dict = {}
        rtn_TIM_dict = {}
        for layer in layer_name_dict:#load layers from csvs
            rtn_list.append(read_level_data(level, layer_name_dict[layer]))
            if layer != 0:#skip coord layer for creating maps
                if layer-1 != world_layer_index:
                    (rtn_map_dict[layer-1], rtn_TIM_dict[layer-1]) = draw_bg(rtn_list[layer], layer-1, static_bg_oversized_tiles_dict, sprite_group_tiles_dict)
                else:
                    (rtn_map_dict[layer-1], rtn_TIM_dict[layer-1]) = draw_world(rtn_list[layer], static_bg_oversized_tiles_dict, sprite_group_tiles_dict)
        
        print('~~loaded!~~')   
        return (rtn_list, rtn_map_dict, rtn_TIM_dict)
    
    if direct_load:
        (layer_list, map_dict, tile_id_map_dict) = load_lvl(level, layer_name_dict, world_layer_index, static_bg_oversized_tiles_dict, sprite_group_tiles_dict)
    else:
        (layer_list, map_dict, tile_id_map_dict) = create_new_lvl(layer_name_dict)
        
    # def save_lvl_layers(level):
        
        
    run = True
    while run:
        clock.tick(FPS)
        screen.fill(black)
        screen.fill(BG_color, canvas_rect)

            
        #check overwrite
        if level != input_level and level in level_sizes_dict:
            pygame.draw.rect(screen, (255,0,0), (0, SCREEN_HEIGHT, SCREEN_WIDTH, LOWER_MARGIN))
            draw_text(screen, f'YOU ARE IN OVERWRITE MODE. SAVING WILL OVERWRITE ANOTHER LEVEL.', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 15)   
           
            
            
        #====================================================================drawing=================================================================
        if isolate_layer:
            screen.blit(map_dict[curr_layer], (-scroll,0))#only draw map of current layer
        else:
            for i in range(len(map_dict)):#draw all data maps
                screen.blit(map_dict[len(map_dict)-1-i], (-scroll,0))
 
        #draw tile ids of current data map
        screen.blit(tile_id_map_dict[curr_layer], (-scroll,0))#only draw text of current layer
        
        
        
        #==================================================================================================================================
           
        
        if reload_map:#reload maps
            if curr_layer == world_layer_index:
                (map_dict[curr_layer], tile_id_map_dict[curr_layer]) = draw_world(layer_list[1:][curr_layer], static_bg_oversized_tiles_dict, sprite_group_tiles_dict)
            else:
                (map_dict[curr_layer], tile_id_map_dict[curr_layer]) = draw_bg(layer_list[1:][curr_layer], curr_layer, static_bg_oversized_tiles_dict, sprite_group_tiles_dict)
            reload_map = False
            
        if reload_all_maps:
            for i in range(len(layer_list)-1):
                if i == world_layer_index:
                    (map_dict[i], tile_id_map_dict[i]) = draw_world(layer_list[1:][i], static_bg_oversized_tiles_dict, sprite_group_tiles_dict)
                else:
                    (map_dict[i], tile_id_map_dict[i]) = draw_bg(layer_list[1:][i], i, static_bg_oversized_tiles_dict, sprite_group_tiles_dict)
            reload_all_maps = False
        
        if grid_on:
            draw_grid()
            
        #draw insertion box
        if insert_mode:
            pygame.draw.line(screen, (255, 254, 171), (insert_pos-scroll,0), (insert_pos-scroll,SCREEN_HEIGHT), 3)
        elif select_mode:
            pygame.draw.rect(screen, (255, 120, 120), pygame.rect.Rect(insert_pos-scroll, 0, 32*((scroll-ini_scroll)//32)+3, SCREEN_HEIGHT), 3)

        #drawing text and stuff
        draw_text(screen, f'Level: {level}, Layer: {description}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
        draw_text(screen, 'Press W or S to change level, A or D to scroll, Q to adjust scroll speed', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 75)
        draw_text(screen, f'{row_str} x {col_str}, ([,]) to change lvl size, select_mode (ctrl + click): {select_mode}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)
        draw_text(screen, f'Eraser mode (E): {eraser_mode}, insert_mode (shift + click): {insert_mode}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 45)
        draw_text(screen, f'Press X to show grid, L and K to change layer, I to isolate layer', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 30)

        #update to accomodate multiple csv files
        #-------------------------------------------------------------------------------------------------------------------------------------
        #save and load data
        if save_button.draw(screen) and not is_loading:
            is_saving = True
            surface_list = []
            #save level data
            for layer in layer_name_dict:
                write_level_data(level, level_sizes_dict, layer_list[layer], layer_name_dict[layer])
                if layer > 0:
                    if layer != 3:
                        surface_list.append(w.process_bg(layer_list[layer], (layer in (6,7))))
                    else:
                        surface_list.append(w.process_game_layer_map(layer_list[layer]))
                    
            lvl_size = (ROWS, MAX_COLS)
            
            base_path = f'assets/sprites/world_maps/level{level}_maps'
            if f'level{level}_maps' not in os.listdir('assets/sprites/world_maps'):
                os.mkdir(base_path)
            pygame.image.save(w.create_map(lvl_size, surface_list[5:7]), os.path.join(base_path, 'filtered_layers.PNG'))
            pygame.image.save(w.create_map(lvl_size, [w.post_process_filter_layer(surface_list[4], MAX_COLS*32),]), os.path.join(base_path, 'filter_layer.PNG'))
            pygame.image.save(w.create_map(lvl_size, surface_list[1:4]), os.path.join(base_path, 'non_filtered_layers.PNG'))
            pygame.image.save(w.create_map(lvl_size, [surface_list[0],]), os.path.join(base_path, 'true_fg.PNG'))
            
            print('~~Saved!~~')
            if level not in level_sizes_dict:
                t1.add_line_to_file(f'{level}: {ROWS}, {MAX_COLS}', path2 + 'level_sizes_dict.txt')
    
            str_list = list(t1.read_text_from_file((path2 + 'level_sizes_dict.txt')))
            str_list[level] = f'{level}: {ROWS}, {MAX_COLS}'
            output_str = ''
            for str_ in str_list:
                output_str = output_str + str_ + '\n'
            output_str = output_str[0:len(output_str)-1]
            t1.overwrite_file((path2 + 'level_sizes_dict.txt'), output_str)
            is_saving = False

        if load_button.draw(screen) and not is_saving:
            is_loading = True
            if level in level_sizes_dict:
                input_level = level
                scroll = 0
                ROWS = level_sizes_dict[input_level][0]
                MAX_COLS = level_sizes_dict[input_level][1]
                row_str = str(ROWS)
                col_str = str(MAX_COLS)
                (layer_list, map_dict, tile_id_map_dict) = load_lvl(level, layer_name_dict, world_layer_index, static_bg_oversized_tiles_dict, sprite_group_tiles_dict)
            else:
                print('Level does not exist')
            is_loading = False

        #-------------------------------------------------------------------------------------------------------------------------------


        
        #draw tile panel and tiles
        pygame.draw.rect(screen, BG_color2, (640, 0, 640, SCREEN_HEIGHT + LOWER_MARGIN))
        
        #choose a tile
        button_count = 0
        for button_count, i in enumerate(button_list):
            if i.draw(screen):
                current_tile = button_count

        #highlight the selected tile
        pygame.draw.rect(screen, WHITE, button_list[current_tile].rect, 1)
        
        #draw text
        for button_ in enumerate(button_list):
            button_[1].show_text(screen, font2, ('',str(button_[0])))

        if scroll_left == True and scroll > 0:
            scroll -= 5 * scroll_speed
        if scroll_right == True and scroll < (MAX_COLS * TILE_SIZE) - 640:
            scroll += 5 * scroll_speed

        if scroll > (MAX_COLS * TILE_SIZE) - 640:
            scroll -= 1
        elif scroll < 0:
            scroll += 1
        #adding new tiles to the screen (using the program)
        #get mouse position
        pos = pygame.mouse.get_pos()
        x = (pos[0] + scroll) // TILE_SIZE
        y = pos[1] // TILE_SIZE

        #check that the coordinates are within the tile area
        rtn_data = []
        if pos[0] < 640 and pos[1] < SCREEN_HEIGHT and not is_saving and not is_loading:
            #update tile value 
            #THIS IS ACTUALLY CHANGING THE TILE VALUES-------------------------------------------------------------------------------
            for i in range(len(layer_list[1:])):
                if not shift and not ctrl and curr_layer == i:
                    (rtn_data, reload_map) = editing_lvl_data(x, y, current_tile, layer_list[1:][i], i, world_layer_index, eraser_mode)
                    if reload_map:
                        layer_list[1:][i] = rtn_data#set the layer to the new values
                        break
                    
            if pygame.mouse.get_pressed()[0] == 1 and shift:
                insert_pos = x*32
                insert_mode = True
                select_mode = False
            if pygame.mouse.get_pressed()[0] == 1 and ctrl:
                insert_pos = x*32
                ini_scroll = scroll
                insert_mode = False
                select_mode = True
            elif pygame.mouse.get_pressed()[2] == 1:
                insert_mode = False
                select_mode = False
            
        for event in pygame.event.get():
            #quit game
            if(event.type == pygame.QUIT):
                run = False

            #key press
            if(event.type == pygame.KEYDOWN) and not is_loading and not is_saving:
                if event.key == pygame.K_ESCAPE:
                    #run = False
                    shift = False
                    ctrl = False
                    eraser_mode = False
                    select_mode = False
                    insert_mode = False
                    
                if event.key == pygame.K_e:
                    eraser_mode = not eraser_mode

                if event.key == pygame.K_w:
                    level += 1
                if event.key == pygame.K_s and level > 0:
                    level -= 1
                if event.key == pygame.K_a:
                    scroll_left = True
                if event.key == pygame.K_d:
                    scroll_right = True
                if event.key == pygame.K_q:
                    if scroll_speed != 5:
                        scroll_speed = 5
                    else:
                        scroll_speed = 1
                if event.key == pygame.K_x:
                    grid_on = not grid_on
                if event.key == pygame.K_l and change_once == False:
                    curr_layer += 1
                    change_once = True
                    if curr_layer > len(layer_list) - 2:
                        curr_layer = 0
                    description = layer_desc_dict[curr_layer]
                    
                if event.key == pygame.K_k and change_once == False:
                    curr_layer -= 1
                    change_once = True
                    if curr_layer < 0:
                        curr_layer = len(layer_list) - 2
                    description = layer_desc_dict[curr_layer]
                    
                    #print(f'Current layer is: {layer}, {description}')
                    
                if event.key == pygame.K_i:
                    isolate_layer = not isolate_layer
                    
                if event.key == pygame.K_LEFTBRACKET:
                    if insert_mode:
                        for layer in layer_list:
                            for i in range(ROWS):
                                layer[i].pop(insert_pos//32)
                    else:
                        layer_list = extend_lvl(-1, layer_list)
                    MAX_COLS -= 1
                    reload_all_maps = True
                    if scroll > ((MAX_COLS) * TILE_SIZE) - 640:
                        scroll -= TILE_SIZE
                    row_str = str(ROWS)
                    col_str = str(MAX_COLS)
                elif event.key == pygame.K_RIGHTBRACKET:
                    if insert_mode:
                        for layer in layer_list:
                            for i in range(ROWS):
                                layer[i].insert(insert_pos//32, -1)
                    else:
                        layer_list = extend_lvl(1, layer_list)
                    MAX_COLS += 1
                    reload_all_maps = True
                    row_str = str(ROWS)
                    col_str = str(MAX_COLS)
                    
                if event.key == pygame.K_c and select_mode:
                    copied_chunk = copy_chunk(insert_pos//32, insert_pos//32 + ((scroll-ini_scroll)//32), layer_list)
                if event.key == pygame.K_v and (select_mode or insert_mode):
                    tiles_added = 0
                    tiles_added = paste_chunk(insert_pos//32, copied_chunk, layer_list)
                    reload_all_maps = tiles_added != 0
                    MAX_COLS += tiles_added
                    col_str = str(MAX_COLS)
                    
                if event.key == pygame.K_LSHIFT:
                    shift = True
                    
                if event.key == pygame.K_LCTRL:
                    ctrl = True

            if(event.type == pygame.KEYUP):
                if event.key == pygame.K_a:
                    scroll_left = False
                if event.key == pygame.K_d:
                    scroll_right = False
                if event.key == pygame.K_l:
                    change_once = False
                if event.key == pygame.K_k:
                    change_once = False
                    
                if event.key == pygame.K_LSHIFT:
                    shift = False
                if event.key == pygame.K_LCTRL:
                    ctrl = False

        pygame.display.set_caption(f"editor window v2.0 @ {clock.get_fps():.1f} FPS")
        pygame.display.update()

    pygame.quit()
    
if __name__ == '__main__':
    main()