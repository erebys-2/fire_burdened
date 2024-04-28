import pygame
pygame.init()

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
        self.rect.centerx = screenW//2 - 32
        self.rect.centery = screenH//2
    
    def get_pos_data(self, player_rect, world_coords):
        for tile in world_coords:
            if tile[0].colliderect(self.rect.x + 30, self.rect.y, 1, 1):
                x_coord = tile[1][0]
                if self.x_coord != x_coord:
                    self.x_coord = x_coord
            if tile[0].colliderect(self.rect.x - 30, self.rect.y, 1, 1):
                x_coord = tile[1][0]
                if self.x_coord2 != x_coord:
                    self.x_coord2 = x_coord
                    #print(self.x_coord2)
            if tile[0].colliderect(player_rect.x, player_rect.y, 1, 1):
                x_coord = tile[1][0]
                if self.Px_coord != x_coord:
                    self.Px_coord = x_coord
                    
    def auto_correct(self, player_rect, world_coords, world_limit, screenW, screenH):
        self.scrollx = 0
        
        self.get_pos_data(player_rect, world_coords)
                
        #basically an edge case detector for when the player goes to the ends of the level
        #when the player is at the left end of the level
        if player_rect.x < self.rect.x and self.x_coord > screenW//2 -64 and player_rect.right < world_limit[0] - (screenW//2 +64): 
            player_rect.x += 1
            self.scrollx -= 1
        #when the player is at the right end
        elif player_rect.right > self.rect.right and self.x_coord2 < world_limit[0] - (screenW//2 + 64) and player_rect.right < self.x_coord2 + screenW//2: 
            player_rect.x -= 1
            self.scrollx += 1
            
            
        #I am delirious, but the player can be loaded into any part of the level now and the camera will immediately autocorrect
        #and center itself on the player's location, except in the edge cases of being at half screen widths from the start and end
        #of a level
        #holy shit kms
        
        if player_rect.x > screenW//2 and (player_rect.x - self.x_coord > 0) and self.set_ini_pos: 
            #tests if the player is beyond the first screen half of the level and if the initial position needs to be set, middle boolean is a limiter
            
            dx = player_rect.x - self.x_coord #adjustment for if the player is not on the right edge
            dx2 = dx -  (screenW//2 + 32) #adjustment for if the player is on the right edge
            
            if self.on_r_edge == False: #idk why this is faster?? the camera will lag without this boolean
                temp_x = player_rect.x #probably has to do with this statement
            else:
                temp_x = self.Px_coord
            
            if player_rect.x < world_limit[0] - screenW//2 and self.on_r_edge == False:
                self.scrollx += dx
                player_rect.x -= dx
            elif world_limit[0]-temp_x < screenW//2 + 32:
                self.on_r_edge = True
                player_rect.x -= (dx2 + world_limit[0]-temp_x - 2)
                self.scrollx += (dx2 + world_limit[0]-temp_x - 2)
                
            self.set_ini_pos = False
        else:
            self.set_ini_pos = False
            self.on_r_edge = False
                
        
    def draw(self, p_screen):
        #for debugging (the camera is basically a column that checks relative position of the player)
        pygame.draw.rect(p_screen, (128,0,255), self.rect)
