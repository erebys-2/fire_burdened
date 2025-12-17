from cfg_handler0 import yaml_handler
import os
import csv
import pygame

class map_gen():
    def __init__(self, path_):
        self.y1 = yaml_handler()
        self.level_dict = self.y1.get_data(path_)
        self.levels_added = []
        self.direction = None
        self.x_pos = None
        self.base_lvl = None
        self.pos_dict = {}
        
        
    def check_trans_orientation(self, transition, l_length):
        direction = ''
        if transition['x'] == 0 and transition['h'] == 480:
            direction = 'left'
        elif transition['x'] > l_length - 20 and transition['h'] == 480:
            direction = 'right'
        elif transition['y'] == 0 and transition['h'] == 2:
            direction = 'up'
        elif transition['y'] == 14 and transition['h'] == 2:
            direction = 'down'
            
        return (direction, transition['x'])
    
        
    def recursive_trace(self, level):#fills a dictionary with positions and lengths
        if level in self.level_dict:
            self.levels_added.append(level)
            data = self.level_dict[level]
            l_length = data['size'][1]
            l = data['size'][1]//10
            # print(f'level: {level}, length: {l}')
            # print(self.base_lvl)
            
            if self.direction != None:
                base_pos = self.pos_dict[self.base_lvl]['pos']
            if self.direction == None:
                self.pos_dict[level] = {'pos': [0,0], 'len': l}
            elif self.direction == 'left':
                self.pos_dict[level] = {'pos': [base_pos[0], base_pos[1]-l], 'len': l}
            elif self.direction == 'right':
                self.pos_dict[level] = {'pos': [base_pos[0], base_pos[1]+self.pos_dict[self.base_lvl]['len']], 'len': l}
            elif self.direction == 'down':
                self.pos_dict[level] = {'pos': [base_pos[0]+1, base_pos[1]+self.x_pos//10], 'len': l}
            elif self.direction == 'up':
                self.pos_dict[level] = {'pos': [base_pos[0]-1, base_pos[1]+self.x_pos//10], 'len': l}
            else:
                self.pos_dict[level] = [-99999999999999999999,-99999999999999999999]
                
                
            for transition in data['trans_data']:
                if transition['n_lvl'] not in self.levels_added:
                    self.direction, self.x_pos = self.check_trans_orientation(transition, l_length)
                    self.base_lvl = level
                    #call again
                    self.recursive_trace(transition['n_lvl'])
        
                
    def normalize_positions(self, level):
        leftest_lvl = level
        topmost_lvl = level
        #find x_shift_amnt and y_shift_amnt
        len_x = 0
        len_y = 0
        for lvl in self.pos_dict:
            if self.pos_dict[lvl]['pos'][1] < self.pos_dict[leftest_lvl]['pos'][1]:
                leftest_lvl = lvl
            if self.pos_dict[lvl]['pos'][0] < self.pos_dict[topmost_lvl]['pos'][0]:
                topmost_lvl = lvl
                
        x_shift_amnt = -self.pos_dict[leftest_lvl]['pos'][1]
        y_shift_amnt = -self.pos_dict[topmost_lvl]['pos'][0]
        
        #normalize positions and find the max dimensions of the map
        for lvl in self.pos_dict:
            self.pos_dict[lvl]['pos'][1] += x_shift_amnt
            self.pos_dict[lvl]['pos'][0] += y_shift_amnt
            
            if self.pos_dict[lvl]['pos'][1] + self.pos_dict[lvl]['len'] > len_x:
                len_x = self.pos_dict[lvl]['pos'][1] + self.pos_dict[lvl]['len']
            if self.pos_dict[lvl]['pos'][0] > len_y:
                len_y = self.pos_dict[lvl]['pos'][0]
            
        return(len_x , len_y + 1)
    
    def generate_map_list(self, level):
        map_arr = []
        self.recursive_trace(level)
        len_x, len_y = self.normalize_positions(1)
        #populate map with -1
        for i in range(len_y):
            temp_list = []
            for j in range(len_x):
                temp_list.append(-1)
            map_arr.append(temp_list)
            
        #polulate levels into map
        for lvl in self.pos_dict:
            coord = self.pos_dict[lvl]['pos']
            l = self.pos_dict[lvl]['len']
            for i in range(l):#just need to draw horizontal lines from the start positions for each level
                map_arr[coord[0]][coord[1]+i] = lvl
                
        return map_arr
    
    def save_map(self, data_, path_):
        with open(os.path.join(path_, 'map_data.csv'), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter = ',')
            for row in data_:
                writer.writerow(row)
        print(f"map saved in {os.path.join(path_, 'map_data.csv')}")
        
class map_handler():
    def __init__(self, path_, screenW, screenH):
        #self.map_enable = False
        self.map_arr = self.read_map_data(path_)
        self.screen_sz = (screenW, screenH)
        self.map_surf = pygame.surface.Surface((screenW, screenH), flags=pygame.SRCALPHA)
        self.bg = pygame.surface.Surface((screenW, screenH), flags=pygame.SRCALPHA)
        pygame.draw.rect(self.bg, (0,0,0,180), pygame.rect.Rect(0,0,screenW, screenH))
        self.fg = pygame.image.load('assets/sprites/misc_art/aria/1.png').convert_alpha()
        self.map_pos = [0,0]
        self.last_mouse_pos = (0,0)
        self.dx = 0
        self.dy = 0
        self.offsetx = 0
        self.offsety = 0
        self.W = screenW
        self.H = screenH
        self.scale_xy = (4,8)
        
        self.enable_once = True
        self.click_rel_en = False
        self.render_enable = False
        self.font = pygame.font.Font(os.path.join('assets', 'FiraCode-Regular.ttf'), 14)
    
    def read_map_data(level, path_):
        rtn_list = []
        with open(os.path.join(path_, 'map_data.csv'), newline= '') as csvfile:
            reader = csv.reader(csvfile, delimiter= ',') 
            for x, current_row in enumerate(reader):
                row_list = []
                for y, tile in enumerate(current_row):
                    row_list.append(int(tile))
                rtn_list.append(row_list)

        return rtn_list
    
    def center_map(self, level):
        #translate a coord in map_surf to center
        map_disp = None
        #find coord in map
        for y in range(len(self.map_arr)):
            if map_disp != None:
                break
            for x in range(len(self.map_arr[0])):
                if self.map_arr[y][x] == level:
                    map_disp = (x,y)
                    break
                
        dx = map_disp[0]*self.scale_xy[0]
        dy = map_disp[1]*self.scale_xy[1]
        self.map_pos = [self.W//4, self.H//2]
        self.map_pos[0] -= dx
        self.map_pos[1] -= dy
        self.offsetx = self.map_pos[0]
        self.offsety = self.map_pos[1]
        
    
    def draw_map(self, level, p_visit_set=None):
        self.map_surf = pygame.surface.Surface(self.screen_sz, flags=pygame.SRCALPHA)
        for y in range(len(self.map_arr)):
            for x in range(len(self.map_arr[0])):
                if p_visit_set == None and self.map_arr[y][x] != -1:
                    pygame.draw.rect(self.map_surf, (58, 58, 78), pygame.rect.Rect(x,y,1,1))
                elif p_visit_set != None and self.map_arr[y][x] != -1:#only render visited levels if p_visit_set != None
                    if self.map_arr[y][x] in p_visit_set:
                        pygame.draw.rect(self.map_surf, (58, 58, 78), pygame.rect.Rect(x,y,1,1))
                    else:
                        pygame.draw.rect(self.map_surf, (38, 38, 58), pygame.rect.Rect(x,y,1,1))
                if self.map_arr[y][x] == level:
                    pygame.draw.rect(self.map_surf, (244, 67, 54), pygame.rect.Rect(x,y,1,1))
        self.map_surf = pygame.transform.scale_by(self.map_surf, self.scale_xy)
        self.map_surf.convert_alpha()
        
    def render_map(self, screen, level, p_visit_set=None):
        if self.render_enable:
            if self.enable_once:
                self.draw_map(level, p_visit_set)
                self.center_map(level)
                self.enable_once = False
            screen.blit(self.bg, (0,0))
            screen.blit(self.map_surf, self.map_pos)
            screen.blit(self.fg, (0,0))
            pygame.draw.rect(screen, (0,0,0), pygame.rect.Rect(0, 0, self.screen_sz[0], 64))
            
            screen.blit(self.font.render('Left Click and Drag to Move; Right Click to re-center\nTab or ESC to exit', False, (200,200,200)), (16, 16))
            

            #move with mouse
            if pygame.mouse.get_pressed()[0] == 0:#release left click
                self.last_mouse_pos = pygame.mouse.get_pos()
                if not self.click_rel_en:
                    self.offsetx += self.dx
                    self.offsety += self.dy
                    self.click_rel_en = True
            elif pygame.mouse.get_pressed()[0] == 1:#left click
                self.click_rel_en = False
                self.dx = pygame.mouse.get_pos()[0] - self.last_mouse_pos[0]
                self.dy = pygame.mouse.get_pos()[1] - self.last_mouse_pos[1]
                self.map_pos = [self.offsetx + self.dx, self.offsety + self.dy]
                #print((dx,dy))
            if pygame.mouse.get_pressed()[2] == 1:#right click
                self.center_map(level)
                self.dx = 0
                self.dy = 0
        else:
            self.enable_once = True
            
        
#this is completely isolated from the rest of the game code, ingerate with level editor later
# m1 = map_gen(os.path.join("assets", "config_textfiles", "world_config", "level_dict.yaml"))
# map_arr = m1.generate_map_list(1)
# m1.save_map(map_arr, os.path.join('assets', 'config_textfiles', 'world_config'))
   
# pygame.init()
# screen = pygame.display.set_mode((640, 480))
# clock = pygame.time.Clock()
# running = True

# mh1 = map_handler(os.path.join("assets", "config_textfiles", "world_config"), 640, 480)
# mh1.render_enable = True
            
# while running:
#     # poll for events
#     # pygame.QUIT event means the user clicked X to close your window
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     # fill the screen with a color to wipe away anything from last frame
#     screen.fill("black")
#     #screen.blit(map_surf, (0,0))
#     mh1.render_map(screen, 1)

#     # RENDER YOUR GAME HERE

#     # flip() the display to put your work on screen
#     pygame.display.flip()

#     clock.tick(60)  # limits FPS to 60

# pygame.quit()