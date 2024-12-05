import pygame

class Camera():
    #rudimentary camera, but it works
    #can possibly implement screenshake here
    def __init__(self, screenW, screenH, camera_offset):
        
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

        self.camera_offset = camera_offset
        self.curr_direction = 0
        self.shift_dist = 1
        self.max_shift_dist = self.camera_offset//8
        
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
            self.cycle = 0
            
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
        
        if (not self.set_ini_pos #level is not being loaded
            and self.camera_offset >= 8
            and self.curr_direction != player_direction #player changes direction 
            and self.x_coord > self.half_screen - 48 and self.x_coord2 < world_limit[0] - (self.half_screen - 48) #within scrollable part of level
            ):
            self.shift_dist = self.max_shift_dist
            self.curr_direction = player_direction
                    
    def auto_correct(self, player_rect, player_direction, player_x_coord, world_coords, world_tile0_coord, world_limit, screenW, screenH):
        self.scrollx = 0
        self.get_pos_data(world_coords)
        
        #============================================= MAIN AUTOCORRECTING LOGIC ==============================================
        displacement = self.camera_offset * player_direction
        
        #gets how much the autocorrect should adjust given the camera displacement value
        #should set shift_dist = 1 by default if camera disp is small or if there's no level scrolling
        self.get_shift_dist(player_direction, world_limit, screenW)
        #aligns player to a vertical axis when the player is traversing level rightwards
        if (player_rect.right - self.rect.right > 16 - displacement
              #and player_rect.right - 16 < self.x_coord2 + self.half_screen
              and self.x_coord2 < world_limit[0] - (self.half_screen + 32) #prevents from over scrolling on the rightmost edge
              ): 
            player_rect.x -= self.shift_dist
            self.scrollx += self.shift_dist    
        
        #aligns player to a vertical axis screen when the player is traversing level leftwards
        elif (self.rect.x - player_rect.x > 16 + displacement
              and world_tile0_coord[0] < 0
              and self.x_coord >= self.half_screen 
              ): #prevents from over scrolling on the leftmost edge
            player_rect.x += self.shift_dist
            self.scrollx -= self.shift_dist
            
        #========================================= OVERSCROLL CORRECTION AT LEVEL EDGES ====================================    
            
        # #when the player is on the left half screen of the level, I think it prevents underscrolling
        elif ((player_rect.x + 32 < self.rect.x #basic check that previous conditionals didn't occur
             and self.x_coord < screenW - 32 #make sure false positives don't occur
             and world_tile0_coord[0] > 0) #fine adjustment
            ):
            player_rect.x -= world_tile0_coord[0]
            self.scrollx += world_tile0_coord[0] 
 
        #prevents over scroll at the right edge of a level
        elif (  player_rect.x > self.rect.x #basic check that previous conditionals didn't occur
                and self.x_coord > world_limit[0] - (self.half_screen + 32 ) #make sure false positives don't occur
                and world_tile0_coord[0] < -(world_limit[0] - 608) #fine adjustment
                ):
            player_rect.x += 1
            self.scrollx -= 1
        
        else:
            self.scrollx = 0
            
        #not sure why, but level changing is most stable when this function is integrated with auto_correct and this happens after 
        #a level change is complete
        #if this is called during level change or even just by itself, there is a chance that aggressively changing levels will 
        #send the player somewhere off the level or off screen
        
        #Everything is already loaded when this occurs, but it's so fast the player doesn't notice zooming across the level
        #update: made it so that a black box is drawn over the screen and sprite logic is surpressed
        if self.set_ini_pos:
            self.set_initial_position(player_rect, player_x_coord, world_limit)
        
    def set_initial_position(self, player_rect, player_x_coord, world_limit):
        self.scrollx = 0
        #==================================== SETTING INITIAL POSITION ON LEVEL LOAD ===============================

        #During a level transition player_rect.x is set to a real coordinate, NOT relative to the screen
        #The camera doesn't move during level transition, its self.rect.x will always be set to relative to the screen at its center line 320 pixels
        #so if player's new position is out of the camera's range, the camera will need to be moved-  
        #basically if the NEW location of the player is beyond the first half screen 
        
        #tests if the player is beyond the first screen half of the level
        if self.set_ini_pos and player_rect.x > self.half_screen: 
            
            #don't ask how I got these formulas
            dx = player_rect.x - self.x_coord #adjustment for if the player is not on the right edge
            dx2 = dx - self.half_screen #adjustment for if the player is on the right edge

            #new player coord not on r edge, but somewhere in the middle of the level
            if not self.on_r_edge and player_rect.x < world_limit[0] - self.half_screen:
                self.scrollx += dx
                player_rect.x -= dx
                
            #new player coord on right edge of level
            elif world_limit[0] - player_rect.x < self.half_screen + 32:
                self.on_r_edge = True
                temp_x = player_rect.x
                player_rect.x -= (dx2 + world_limit[0]- player_rect.x - 2)
                self.scrollx += (dx2 + world_limit[0]- temp_x - 2)
                
            self.set_ini_pos = False
        else:#no logic required if player is being loaded on the left edge
            self.set_ini_pos = False
            self.on_r_edge = False
                
        
    def draw(self, p_screen):
        #for debugging (the camera is basically a column that checks relative position of the player)
        #pygame.draw.rect(p_screen, (0,0,128), (self.Px_coord, 0, 10,10))
        pygame.draw.rect(p_screen, (128,0,255), self.rect)