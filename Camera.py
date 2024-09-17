import pygame

class Camera():
    #rudimentary camera, but it works
    #can possibly implement screenshake here
    def __init__(self, screenW, screenH):
        
        self.scrollx = 0
        self.x_coord = screenW//2 - 32
        self.x_coord2 = screenW//2 + 32
        self.on_r_edge = False
        self.Px_coord = 0
        self.set_ini_pos = True

        self.rect = pygame.Rect(0, 0, 64, screenH)
        self.rect.centerx = screenW//2 #- 32
        self.rect.centery = screenH//2

        self.on_right_edge = False
        
        self.cycle = 0
        
        
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
            
        
    
    def get_pos_data(self, player_rect, world_coords):
        for loaded_tile in [tile for tile in world_coords if tile[1].x > -32 and tile[1].x < 640]:
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
                    
    def auto_correct(self, player_rect, world_coords, world_tile0_coord, world_limit, screenW, screenH):
        self.scrollx = 0
        self.get_pos_data(player_rect, world_coords)
                
        #when the player is on the left half screen of the level
        if player_rect.x + 32 < self.rect.x and self.x_coord < screenW - 32 and world_tile0_coord[0] > 0:
            player_rect.x -= world_tile0_coord[0]
            self.scrollx += world_tile0_coord[0]
            
        #when the player on the right half screen of the level
        elif player_rect.right - 16 > self.rect.right and self.x_coord2 < world_limit[0] - (screenW//2 + 32) and player_rect.right - 16 < self.x_coord2 + screenW//2 - 32: 
            player_rect.x -= 1
            self.scrollx += 1
            #self.on_right_edge = True
            #print("working")
    
        else:
            #set player to center screen
            #self.on_right_edge = False
            if self.rect.x - player_rect.x > 16  and self.x_coord >= screenW//2 and self.x_coord < world_limit[0] - (screenW//2):
                player_rect.x += 1
                self.scrollx -= 1
            # elif self.x_coord < screenW//2 - 32:
            #     print(self.x_coord)
            #     print(screenW//2)
            #     player_rect.x -= 1
            #     self.scrollx += 1
            else:
                self.scrollx = 0
            
        #I am delirious, but the player can be loaded into any part of the level now and the camera will immediately autocorrect
        #and center itself on the player's location, except in the edge cases of being at half screen widths from the start and end
        #of a level
        #holy shit kms
        
        if player_rect.x > screenW//2 and (player_rect.x - self.x_coord > 0) and self.set_ini_pos: 
            #tests if the player is beyond the first screen half of the level and if the initial position needs to be set, middle boolean is a limiter
            
            dx = player_rect.x - self.x_coord #adjustment for if the player is not on the right edge
            dx2 = dx - (screenW//2 ) #adjustment for if the player is on the right edge
            
            # if self.on_r_edge == False: #idk why this is faster?? the camera will lag without this boolean
            #     temp_x = player_rect.x #probably has to do with this statement
            # else:
            temp_x = player_rect.x
            
            if player_rect.x < world_limit[0] - screenW//2 and self.on_r_edge == False:
                self.scrollx += dx
                player_rect.x -= dx
               
            elif world_limit[0] - temp_x < screenW//2 + 32:
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