import pygame
import os
import button
import pickle
import csv

pygame.init()

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 480
LOWER_MARGIN = 96
SIDE_MARGIN = 320

#should be user entered for later
print('\nstandard level is 15 rows, 200 cols ')
print('layer 1 is the game layer, layer 2-3 is detailed BG')
print('layer 0 is FG. layer 4 is for gradient filter. layers 5+ is scrolling BG')
print('help me god')
row_str = input('enter rows: ')
#print('\n')
col_str = input('enter cols: ')
ROWS = int(row_str)
MAX_COLS = int(col_str)
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
level = 0
t_set_index = 0
tile_index = 0
current_tile = 0
tile_list = []
tile_types = ['standard', 'bg_oversized']
change_once = False 

#load tiles

for tile_set in tile_types:
    temp_list = []
    tile_count = len(os.listdir(f'sprites/tileset/{tile_set}'))

    for i in range(tile_count):
        img = pygame.image.load(f'sprites/tileset/{tile_set}/{i}.png')
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
BG_color2 = (255,0,86)

#define font
font = pygame.font.SysFont('SimSun', 12)

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

empty_list_gen(world_data)  
empty_list_gen(coord_data)  
empty_list_gen(fg_data)  
empty_list_gen(bg1_data)
empty_list_gen(bg2_data)
empty_list_gen(bg3_data)
empty_list_gen(bg4_data)
empty_list_gen(bg5_data)
empty_list_gen(bg6_data)


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

def draw_bg(data):
    
    for y, row in enumerate(data):#world data and bg data should have the same amount of data
        for x, tile_ in enumerate(row):
            if tile_ >= 0:
                if tile_ == 15 or tile_ == 16 or tile_ == 18:#these don't quite work??
                    #blit(source, dest, area=None, special_flags=0) -> Rect
                    screen.blit(tile_list[t_set_index][tile_], (x * TILE_SIZE - scroll, (y * TILE_SIZE)+ 16))
                elif(tile_ >= 30 and tile_ < 50):
                    bg_tile = tile_ - 30
                    screen.blit(tile_list[1][bg_tile], (x * TILE_SIZE - scroll, (y * TILE_SIZE)))
                    #marker_rect = (x * TILE_SIZE, y * TILE_SIZE, 8, 8)
                    #pygame.draw.rect(screen, RED, marker_rect)
                else: 
                    screen.blit(tile_list[t_set_index][tile_], (x * TILE_SIZE - scroll, y * TILE_SIZE))

def draw_world():
    for y, row in enumerate(world_data):#world data and bg data should have the same amount of data
        for x, tile_ in enumerate(row):
            if tile_ >= 0:
                if tile_ == 15 or tile_ == 16 or tile_ == 18 or tile_ == 2:
                    #blit(source, dest, area=None, special_flags=0) -> Rect
                    screen.blit(tile_list[t_set_index][tile_], (x * TILE_SIZE - scroll, (y * TILE_SIZE)+ 16))
                elif(tile_ == 45):
                    bg_tile = tile_ - 30
                    img = tile_list[1][bg_tile]
                    img = pygame.transform.scale(img, (int(img.get_width() * 2), int(img.get_height() * 2)))
                    screen.blit(img, (x * TILE_SIZE - scroll, (y * TILE_SIZE)))
                else: 
                    screen.blit(tile_list[t_set_index][tile_], (x * TILE_SIZE - scroll, y * TILE_SIZE))


#button stuff
save_button = button.Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT + LOWER_MARGIN - 50, save_img, 1)
load_button = button.Button(SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT + LOWER_MARGIN - 50, load_img, 1)
                    
                
button_list = []
button_col = 0
button_row = 0
temp_dist = 0
for i in range(len(tile_list[t_set_index])):
    if i == 15 or i == 16 or i  == 18:#these are the half tiles
        temp_dist = 20
    else:
        temp_dist = 4
    tile_button = button.Button(SCREEN_WIDTH + (40 * button_col) + 4, (40 * button_row) + temp_dist, tile_list[t_set_index][i], 1)
    button_list.append(tile_button)
    button_col += 1
    if button_col == 8:
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
        if data[y][x] != current_tile:
            data[y][x] = current_tile
    if pygame.mouse.get_pressed()[2] == 1:
        data[y][x] = -1

#running the editor----------------------------------------------------
run = True
while run:
    clock.tick(FPS)
    screen.fill(black)
    screen.fill(BG_color, canvas_rect)

    draw_bg(bg6_data)
    draw_bg(bg5_data)
    draw_bg(bg4_data)
    draw_bg(bg3_data)
    draw_bg(bg2_data)
    draw_bg(bg1_data)
    draw_world()
    draw_bg(fg_data)
    
    if grid_on == True:
        draw_grid()
    
    #drawing text and stuff
    draw_text(f'Level: {level}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
    draw_text('Press W or S to change level, A or D to scroll, Q or E to adjust scroll speed', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 75)
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

    if load_button.draw(screen):
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

    #-------------------------------------------------------------------------------------------------------------------------------

    #draw tile panel and tiles
    pygame.draw.rect(screen, BG_color2, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
    
    #choose a tile
    button_count = 0
    for button_count, i in enumerate(button_list):
        if i.draw(screen):
            current_tile = button_count

    #highlight the selected tile
    pygame.draw.rect(screen, WHITE, button_list[current_tile].rect, 1)

    if scroll_left == True and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right == True and scroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
        scroll += 5 * scroll_speed

    #adding new tiles to the screen (using the program)
	#get mouse position
    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // TILE_SIZE
    y = pos[1] // TILE_SIZE

    #check that the coordinates are within the tile area
    if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
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
                scroll_speed = 5
            if event.key == pygame.K_e:
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
                print(f'Current layer is: {layer}, {description}')
                

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