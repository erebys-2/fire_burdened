import pygame
import os
import button
import pickle
import csv
from textfile_handler import textfile_formatter

pygame.init()

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 480
LOWER_MARGIN = 96
SIDE_MARGIN = 320
t1 = textfile_formatter()
path = 'config_textfiles/for_level_editor/'
level_sizes_dict = t1.str_list_to_dict(t1.read_text_from_file(os.path.join(path + 'level_sizes_dict.txt')), 'list')
#print(level_sizes_dict)

#should be user entered for later
print('\nstandard level is 15 rows, 200 cols ')
print('layer 1 is the game layer, layer 2-3 is detailed BG')
print('layer 0 is FG. layer 4 is for gradient filter. layers 5+ is scrolling BG')

#level is selected
print('level input will either be loaded or a new level creation will be prompted')
input_level = int(input('enter level: '))
load_level_flag = False
direct_load = False
if input_level < 0:
    levels_must_be_greater_than_0 = 0/0

if input_level not in level_sizes_dict:
    row_str = input('enter rows: ')
    col_str = input('enter cols: ')
    ROWS = int(row_str)
    MAX_COLS = int(col_str)
    level = input_level
else:
    ROWS = level_sizes_dict[input_level][0]
    MAX_COLS = level_sizes_dict[input_level][1]
    row_str = str(ROWS)
    col_str = str(MAX_COLS)
    load_level_flag = True
    level = input_level
    direct_load = True

#the standard size of a tile should be 32
#background art might have to have a separate editor- it is a bridge we will cross later
TILE_SIZE = 32


#TILE_TYPES = 21

grid_on = False
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('editor window')

#framerate set up------------------------------------
clock = pygame.time.Clock()
FPS = 60
#ideas for bg tiles:
#lamps, fences, rocks, debris, gates, fountains, statues

#set bg rect
canvas_rect = pygame.Rect((0,0), (SCREEN_WIDTH,480))
layer = 1
#level = 0
t_set_index = 0
tile_index = 0
current_tile = 0
tile_list = []
tile_types = ['standard', 'bg_oversized']
change_once = False 


path = 'config_textfiles/world_config/'
sprite_group_tiles_dict = t1.str_list_to_dict(t1.read_text_from_file(os.path.join(path + 'sprite_group_tiles_dict.txt')), 'list')
static_bg_oversized_tiles_dict = t1.str_list_to_dict(t1.read_text_from_file(os.path.join(path + 'static_bg_oversized_tiles_dict.txt')), 'int')
special_hitbox_tiles_dict = t1.str_list_to_dict(t1.read_text_from_file(os.path.join(path + 'special_hitbox_tiles_dict.txt')), 'none')

#load tiles

for tile_set in tile_types:
    temp_list = []
    tile_count = len(os.listdir(f'sprites/tileset/{tile_set}'))

    for i in range(tile_count):
        img = pygame.image.load(f'sprites/tileset/{tile_set}/{i}.png').convert_alpha()
        temp_list.append(img)
    tile_list.append(temp_list)

tile = tile_list[t_set_index][tile_index]

save_img = pygame.image.load('sprites/save_btn.png').convert_alpha()
load_img = pygame.image.load('sprites/load_btn.png').convert_alpha()

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

#create empty tile list(s)

def empty_list_gen(data):
    for row in range(ROWS):
        row = [-1] * MAX_COLS
        data.append(row)

world_data = []#layer 1
coord_data = []#blank, cannot edit
#bg1_data = world_data.copy() #bruh this shit is wack

fg_data = []#layer 0
bg1_data = []#layer 2
bg2_data = []#layer 3
bg3_data = []#layer 4, gradient
bg4_data = []#layer 5, scrolling 
bg5_data = []#layer 6, scrolling
bg6_data = []#layer 7, scrolling 

layer_list = [
    world_data,
    coord_data,
    fg_data,
    bg1_data,
    bg2_data,
    bg3_data,
    bg4_data,
    bg5_data,
    bg6_data
]

for layer_ in layer_list:
    empty_list_gen(layer_)  
    
#create ground
for tile_ in range(0, MAX_COLS):
	world_data[ROWS - 1][tile_] = 17

#other methods--------------

def draw_grid():
	#vertical lines
	for c in range(MAX_COLS + 1):
		pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
	#horizontal lines
	for c in range(ROWS + 1):
		pygame.draw.line(screen, WHITE, (0, c * TILE_SIZE), (SCREEN_WIDTH, c * TILE_SIZE))

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def draw_bg(data, layer, ref_layer):
    
    for y, row in enumerate(data):#world data and bg data should have the same amount of data
        for x, tile_ in enumerate(row):
            if tile_ >= 0:
                
                if tile_ == 15 or tile_ == 16 or tile_ == 18:#these don't quite work??
                    #blit(source, dest, area=None, special_flags=0) -> Rect
                    screen.blit(tile_list[t_set_index][tile_], (x * TILE_SIZE - scroll, (y * TILE_SIZE)+ 16))
                    
                elif tile_ in sprite_group_tiles_dict and sprite_group_tiles_dict[tile_][3] != -1:
                    img = tile_list[1][sprite_group_tiles_dict[tile_][3]]
                    if tile_ != 46:
                        scale = 1
                    else:
                        scale = 2
                    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    screen.blit(img, (x * TILE_SIZE - scroll, (y * TILE_SIZE)))
                    
                elif tile_ in static_bg_oversized_tiles_dict:
                    img = tile_list[1][static_bg_oversized_tiles_dict[tile_]]
                    if tile_ != 46:
                        scale = 1
                    else:
                        scale = 2
                    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    screen.blit(img, (x * TILE_SIZE - scroll, (y * TILE_SIZE)))
                    
                else: 
                    screen.blit(tile_list[t_set_index][tile_], (x * TILE_SIZE - scroll, y * TILE_SIZE))
                #draw sprite text
                if layer == ref_layer:
                    draw_text(str(tile_), font2, WHITE, x*32 + 8 - scroll, y*32 + 8)

def draw_world(static_bg_oversized_tiles_dict, sprite_group_tiles_dict, layer, ref_layer):

    for y, row in enumerate(world_data):#world data and bg data should have the same amount of data
        for x, tile in enumerate(row):
            if tile >= 0:
                if tile in sprite_group_tiles_dict and sprite_group_tiles_dict[tile][3] != -1:
                    img = tile_list[1][sprite_group_tiles_dict[tile][3]]
                    if tile != 46:
                        scale = 1
                    else:
                        scale = 2
                    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    screen.blit(img, (x * TILE_SIZE - scroll, (y * TILE_SIZE)))
                    
                elif tile in static_bg_oversized_tiles_dict:
                    img = tile_list[1][static_bg_oversized_tiles_dict[tile]]
                    if tile != 46:
                        scale = 1
                    else:
                        scale = 2
                    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    screen.blit(img, (x * TILE_SIZE - scroll, (y * TILE_SIZE)))
                    
                elif tile == 15 or tile == 16 or tile == 18 or tile == 2:
                    screen.blit(tile_list[t_set_index][tile], (x * TILE_SIZE - scroll, (y * TILE_SIZE)+ 16))
 
                else: 
                    screen.blit(tile_list[t_set_index][tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))
                
                if layer == ref_layer:
                    draw_text(str(tile), font2, WHITE, x*32 + 8 - scroll, y*32 + 8)

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
        



#-------Reading and writing level data for loading---------------------------------------
def read_level_data(level, data_, data_str):
	with open(f'level_files/level{level}_{data_str}.csv', newline= '') as csvfile:
		reader = csv.reader(csvfile, delimiter= ',') #what separates values = delimiter
		for x, current_row in enumerate(reader):
			for y, tile in enumerate(current_row):
				data_[x][y] = int(tile)

def write_level_data(level, data_, data_str):
    with open(f'level_files/level{level}_{data_str}.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter = ',')
            for row in data_:
                writer.writerow(row)
                
def editing_lvl_data(data):
    
    if pygame.mouse.get_pressed()[0] == 1:
        if current_tile in sprite_group_tiles_dict and data != world_data:
            print("cannot place sprite group tile in non-game layer")
        elif data[y][x] != current_tile:
            data[y][x] = current_tile
    if pygame.mouse.get_pressed()[2] == 1:
        data[y][x] = -1

description = 'game layer'
overwrite = False

#running the editor----------------------------------------------------
if load_level_flag:
    read_level_data(level, world_data, 'data')
    read_level_data(level, coord_data, 'coord_data')
    read_level_data(level, bg1_data, 'bg1_data')
    read_level_data(level, bg2_data, 'bg2_data')
    read_level_data(level, bg3_data, 'bg3_data')
    read_level_data(level, bg4_data, 'bg4_data')
    read_level_data(level, bg5_data, 'bg5_data')
    read_level_data(level, bg6_data, 'bg6_data')
    read_level_data(level, fg_data, 'fg_data')
    
    print('~~loaded!~~')   
    load_level_flag = False



run = True
while run:
    clock.tick(FPS)
    screen.fill(black)
    screen.fill(BG_color, canvas_rect)

        
    #check overwrite
    if level != input_level and level in level_sizes_dict:
        overwrite = True
        pygame.draw.rect(screen, (255,0,0), (0, SCREEN_HEIGHT, SCREEN_WIDTH, LOWER_MARGIN))
        draw_text(f'YOU ARE IN OVERWRITE MODE. SAVING WILL OVERWRITE ANOTHER LEVEL.', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 15)   
    else:
        overwrite = False     
        
    draw_bg(bg6_data, layer, 7)
    draw_bg(bg5_data, layer, 6)
    draw_bg(bg4_data, layer, 5)
    draw_bg(bg3_data, layer, 4)
    draw_bg(bg2_data, layer, 3)
    draw_bg(bg1_data, layer, 2)
    draw_world(static_bg_oversized_tiles_dict, sprite_group_tiles_dict, layer, 1)
    draw_bg(fg_data, layer, 0)
    
    if grid_on == True:
        draw_grid()
    
    #drawing text and stuff
    draw_text(f'Level: {level}, Layer: {description}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
    draw_text('Press W or S to change level, A or D to scroll, Q to adjust scroll speed', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 75)
    draw_text(f'Current dimensions: row x col = {row_str} x {col_str}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)
    draw_text(f'Restart editor to load a level with different dimensions.', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 45)
    draw_text(f'Press X to show grid, L to change level', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 30)

    #update to accomodate multiple csv files
    #-------------------------------------------------------------------------------------------------------------------------------------
    #save and load data
    if save_button.draw(screen):
        #save level data
        write_level_data(level, world_data, 'data')
        write_level_data(level, coord_data, 'coord_data')
        write_level_data(level, bg1_data, 'bg1_data')
        write_level_data(level, bg2_data, 'bg2_data')
        write_level_data(level, bg3_data, 'bg3_data')
        write_level_data(level, bg4_data, 'bg4_data')
        write_level_data(level, bg5_data, 'bg5_data')
        write_level_data(level, bg6_data, 'bg6_data')
        write_level_data(level, fg_data, 'fg_data')
        
        print('~~Saved!~~')
        if level not in level_sizes_dict:
            t1.add_line_to_file(f'{level}: {ROWS}, {MAX_COLS}', 'config_textfiles/for_level_editor/level_sizes_dict.txt')
            level_sizes_dict = t1.str_list_to_dict(t1.read_text_from_file('config_textfiles/for_level_editor/level_sizes_dict.txt'), 'list') #update dictionary
        elif overwrite:
            print(f'You will have to edit the text file manually for the level just changed to: {level}: {ROWS}, {MAX_COLS}')

    if load_button.draw(screen):
        if not direct_load:
            #load in level data
            #reset scroll back to the start of the level
            scroll = 0
            read_level_data(level, world_data, 'data')
            read_level_data(level, coord_data, 'coord_data')
            read_level_data(level, bg1_data, 'bg1_data')
            read_level_data(level, bg2_data, 'bg2_data')
            read_level_data(level, bg3_data, 'bg3_data')
            read_level_data(level, bg4_data, 'bg4_data')
            read_level_data(level, bg5_data, 'bg5_data')
            read_level_data(level, bg6_data, 'bg6_data')
            read_level_data(level, fg_data, 'fg_data')
            
            print('~~loaded!~~')
        else:
            print('can not load if level was directly loaded')         

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

    #adding new tiles to the screen (using the program)
	#get mouse position
    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // TILE_SIZE
    y = pos[1] // TILE_SIZE

    #check that the coordinates are within the tile area
    if pos[0] < 640 and pos[1] < SCREEN_HEIGHT:
        #update tile value 
        #THIS IS ACTUALLY CHANGING THE TILE VALUES-------------------------------------------------------------------------------
        if layer == 1:
            editing_lvl_data(world_data)
        elif layer == 2:
            editing_lvl_data(bg1_data)
        elif layer == 3:
            editing_lvl_data(bg2_data)
        elif layer == 4:
            editing_lvl_data(bg3_data)
        elif layer == 5:
            editing_lvl_data(bg4_data)
        elif layer == 6:
            editing_lvl_data(bg5_data)
        elif layer == 7:
            editing_lvl_data(bg6_data)
        elif layer == 0:
            editing_lvl_data(fg_data)


    for event in pygame.event.get():
        #quit game
        if(event.type == pygame.QUIT):
            run = False

        #key press
        if(event.type == pygame.KEYDOWN):
            if event.key == pygame.K_ESCAPE:
                run = False

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
                grid_on = True
            if event.key == pygame.K_l and change_once == False:
                layer += 1
                change_once = True
                if layer > 7:
                    layer = 0
                if layer == 0:
                    description = 'foreground'
                elif layer == 1:
                    description = 'game layer'
                elif layer == 2:
                    description = 'detailed bg layer 1'
                elif layer == 3:
                    description = 'detailed bg layer 2'
                elif layer == 4:
                    description = 'filter layer'
                elif layer == 5:
                    description = 'bg layer fast'
                elif layer == 6:
                    description = 'bg layer med'
                else:
                    description = 'bg layer slow'
                
                #print(f'Current layer is: {layer}, {description}')
                

        if(event.type == pygame.KEYUP):
            if event.key == pygame.K_a:
                scroll_left = False
            if event.key == pygame.K_d:
                scroll_right = False
            if event.key == pygame.K_x:
                grid_on = False
            if event.key == pygame.K_l:
                change_once = False


    pygame.display.update()

pygame.quit()