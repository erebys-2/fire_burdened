import pygame

class Camera():
    #rudimentary camera, but it works
    #can possibly implement screenshake here
    def __init__(self, screenW, screenH, camera_displacement):
        
        self.scrollx = 0
        self.half_screen = screenW//2
        self.x_coord = self.half_screen - 32
        self.x_coord2 = self.half_screen + 32
        self.on_r_edge = False
        self.Px_coord = 0
        self.set_ini_pos = True

        self.rect = pygame.Rect(0, 0, 64, screenH)
        self.rect.centerx = self.half_screen #- 32
        self.rect.centery = screenH//2

        self.camera_displacement = camera_displacement
        self.curr_direction = 0
        self.shift_dist = 1
        self.max_shift_dist = self.camera_displacement//8
        
        self.on_right_edge = False
        
        self.cycle = 0
        self.is_visible = False
        
        
        
    def screen_shake(self, profile, trigger):
        intensity_x = profile[0]
        intensity_y = profile[1]
        cycle_limit = profile[2] * 2

        if trigger:
            if self.cycle < cycle_limit:
                if self.cycle %2 == 0:
                    #player_mvmt_x, scroll_x, player_mvmt_y, scroll_y
                    mvmt_output = (-intensity_x, intensity_x, -intensity_y, intensity_y)
                else:
                    mvmt_output = (intensity_x, -intensity_x, intensity_y, -intensity_y)
                    
                self.cycle += 1
            else:
                mvmt_output = (0,0,0,0)
                self.cycle = 0
                trigger = False
        else:
            mvmt_output = (0,0,0,0)
            
        return (trigger, mvmt_output)
            
        
    
    def get_pos_data(self, world_coords):
        for loaded_tile in [tile for tile in world_coords if tile[1].x >= self.rect.x - 64 and tile[1].right <= self.rect.right + 64]:
            #print(loaded_tile)
            if loaded_tile[1].colliderect(self.rect.x + 30, self.rect.y, 1, 1):
                x_coord = loaded_tile[2][0]
                if self.x_coord != x_coord:
                    self.x_coord = x_coord
            if loaded_tile[1].colliderect(self.rect.x - 30, self.rect.y, 1, 1):
                x_coord = loaded_tile[2][0]
                if self.x_coord2 != x_coord:
                    self.x_coord2 = x_coord
                    #print(self.x_coord2)
            # if tile[1].colliderect(player_rect.x, player_rect.y, 1, 1):
            #     x_coord = tile[2][0]
            #     if self.Px_coord != x_coord:
            #         self.Px_coord = x_coord
            
    def get_shift_dist(self, player_direction, world_limit, screenW):
        if self.shift_dist > 1:
            self.shift_dist -= 1
        
        if (self.camera_displacement >= 8
            and self.curr_direction != player_direction #player changes direction
            and not self.set_ini_pos #level is not being loaded
            and self.x_coord > self.half_screen - 48 and self.x_coord2 < world_limit[0] - (self.half_screen - 48) #within scrollable part of level
            ):
            self.shift_dist = self.max_shift_dist
            self.curr_direction = player_direction
                    
    def auto_correct(self, player_rect, player_direction, player_scrollx, world_coords, world_tile0_coord, world_limit, screenW, screenH):
        self.scrollx = 0
        self.get_pos_data(world_coords)
        
        #============================================= MAIN AUTOCORRECTING LOGIC ==============================================
        displacement = self.camera_displacement * player_direction
        
        #gets how much the autocorrect should adjust given the camera displacement value
        #should set shift_dist = 1 by default if camera disp is small or if there's no level scrolling
        self.get_shift_dist(player_direction, world_limit, screenW)

        #aligns player to a vertical axis when the player is traversing level rightwards
        if ((player_rect.right - self.rect.right > 16 - displacement
              and player_rect.right - 16 < self.x_coord2 + self.half_screen - 32)
              and self.x_coord2 < world_limit[0] - (self.half_screen + 32) #prevents from over scrolling on the rightmost edge
              ): 
            player_rect.x -= self.shift_dist
            self.scrollx += self.shift_dist
            # if pygame.time.get_ticks() %10 == 0:
            #     print("b")    
        
        #aligns player to a vertical axis screen when the player is traversing level leftwards
        elif (self.rect.x - player_rect.x > 16 + displacement
              and self.x_coord >= self.half_screen 
              and self.x_coord < world_limit[0] - (self.half_screen)): #prevents from over scrolling on the leftmost edge
            player_rect.x += self.shift_dist
            self.scrollx -= self.shift_dist
            # if pygame.time.get_ticks() %10 == 0:
            #     print("a")
            
        #========================================= OVERSCROLL CORRECTION AT LEVEL EDGES ====================================    
            
        #when the player is on the left half screen of the level, I think it prevents underscrolling
        elif ((player_rect.x + 32 < self.rect.x 
             and self.x_coord < screenW - 32 
             and world_tile0_coord[0] > 0)
            ):
            player_rect.x -= world_tile0_coord[0]
            self.scrollx += world_tile0_coord[0]
            # if pygame.time.get_ticks() %10 == 0:
            #     print("a")   
 
        #prevents over scroll at the right edge of a level
        elif (  player_rect.right - 16 < self.rect.right
                and world_tile0_coord[0] < -(world_limit[0] - 640)
                ):
            player_rect.x += 1
            self.scrollx -= 1
            # if pygame.time.get_ticks() %10 == 0:
            #     print("c")
        
        else:
            self.scrollx = 0
            
        #I am delirious, but the player can be loaded into any part of the level now and the camera will immediately autocorrect
        #and center itself on the player's location, except in the edge cases of being at half screen widths from the start and end
        #of a level
        #holy shit kms
        if self.set_ini_pos:
            self.set_initial_position(player_rect, world_coords, world_limit, screenW, screenH)
        
    def set_initial_position(self, player_rect, world_coords, world_limit, screenW, screenH):
        self.shift_dist = 1
        self.scrollx = 0
        #self.get_pos_data(world_coords)
        #==================================== SETTING INITIAL POSITION ON LEVEL LOAD ===============================
        
        if self.set_ini_pos and player_rect.x > self.half_screen and (player_rect.x - self.x_coord > 0): 
            #tests if the player is beyond the first screen half of the level and if the initial position needs to be set, middle boolean is a limiter
            
            dx = player_rect.x - self.x_coord #adjustment for if the player is not on the right edge
            dx2 = dx - (self.half_screen ) #adjustment for if the player is on the right edge
            
            # if self.on_r_edge == False: #idk why this is faster?? the camera will lag without this boolean
            #     temp_x = player_rect.x #probably has to do with this statement
            # else:
            temp_x = player_rect.x
            
            if player_rect.x < world_limit[0] - self.half_screen and self.on_r_edge == False:
                self.scrollx += dx
                player_rect.x -= dx
               
            elif world_limit[0] - temp_x < self.half_screen + 32:
                self.on_r_edge = True
                player_rect.x -= (dx2 + world_limit[0]-temp_x - 2)
                self.scrollx += (dx2 + world_limit[0]-temp_x - 2)
               
                
            self.set_ini_pos = False
        else:
            self.set_ini_pos = False
            self.on_r_edge = False
                
        
    def draw(self, p_screen):
        #for debugging (the camera is basically a column that checks relative position of the player)
        #pygame.draw.rect(p_screen, (0,0,128), (self.Px_coord, 0, 10,10))
        pygame.draw.rect(p_screen, (128,0,255), self.rect)