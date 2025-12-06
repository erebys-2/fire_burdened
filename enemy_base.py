import pygame
import math as m
from music_player import music_player

class general_enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, scale, id_, enemy0_order_id, ini_vol, frame_list, sfx_list_ext):
        pygame.sprite.Sprite.__init__(self)
        
        self.spawn_order_id = enemy0_order_id
        self.id_ = id_

        self.Alive = True
        self.hp = 12
        self.hits_tanked = 0
        self.action = 0
        self.scale = scale
        
        self.inundated = False
        self.speed = speed
        
        
        self.frame_list = frame_list
        self.image = self.frame_list[0][0]
        self.frame_index = 0
        
        self.flip = False
        self.v_flip = 0
        self.is_on_screen = False
        self.do_screenshake = False
        
        self.framerates = (
            (150,100),
            )
        
        
        
        #audio
        self.m_player = music_player(None, ini_vol)
        self.m_player.sfx = sfx_list_ext
        self.ini_vol = ini_vol
            
        #self.atk_rect_list = []    
        self.atk_rect = pygame.Rect(-32, -32, 0,0)
        self.atk_rect_scaled = pygame.Rect(-32, -32, 0,0)

        #main rect
        self.rect = self.image.get_rect()
        self.width = self.rect.width
        self.h_width = self.width//2
        self.q_width = self.width//4
        self.height = self.rect.height
        self.h_height = self.height//2 
        self.q_height = self.height//4
        self.rect.topleft = (x,y)
                
    def is_in_range(self, vect1, vect2, r):
        return(vect1[0] in range(vect2[0] - r, vect2[0] + r) and vect1[1] in range(vect2[1] - r, vect2[1] + r))

    def chase(self, body, target, r, speed):
        speed_x = 0
        speed_y = 0
        if body[0] < target[0] - r:
            speed_x = speed
        elif body[0] > target[0] + r:
            speed_x = -speed
            
        if body[1] < target[1] - speed:
            speed_y = speed
        elif body[1] > target[1] + speed:
            speed_y = -speed
        
        return (speed_x, speed_y)

    def normalize(self, dx, dy):
        absx = abs(dx)
        absy = abs(dy)
        if (dx != 0) and (dy != 0):
            dist = m.sqrt(absx + absy)
            dx = dx/absx * dist
            dy = dy/absy * dist
            
        return(dx, dy)
    
    def check_if_onscreen(self):
        self.is_on_screen = (self.rect.x > -320 and self.rect.x < 640 + 320)
        return self.is_on_screen
    
    def check_if_in_simulation_range(self, adjustment):
        return (self.rect.x > - (320 + adjustment) and self.rect.right < 640 + (320 + adjustment))
    
    def explode(self, sp_group_list):
        particle_name = self.id_ + '_death'
        sp_group_list[3].sprite.add_particle(particle_name, self.rect.centerx, self.rect.centery, self.direction, self.scale, False, 0)
           
    def force_ini_position(self, scrollx):
        self.rect.x -= scrollx