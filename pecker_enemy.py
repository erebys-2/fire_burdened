import pygame
import math as m
#from music_player import music_player
from enemy_base import general_enemy

class pecker(general_enemy):
    def __init__(self, x, y, speed, scale, id, enemy0_order_id, ini_vol, frame_list, sfx_list_ext):
        super().__init__(x, y, speed, scale, id, enemy0_order_id, ini_vol, frame_list, sfx_list_ext)
        
        
        self.image2 = self.frame_list[1][0]
        self.head_rect = self.image2.get_rect()
        self.head_rect.center = (x,y - self.width//4)
        
        self.increment = 0
        self.min_i = 0.1
        self.i_ = self.min_i
        self.max_i = 1
        self.r = 256
        self.atk_success = False
        self.idling = True
        self.target_pos = [0,0]
        self.hostile = False
        self.is_vulnerable = False
        
        self.i_frames_ref_time = pygame.time.get_ticks()
        self.i_frames_en = False
        self.i_frames_durr = 800
        
    def force_ini_position(self, scrollx):
        self.head_rect.x -= scrollx
        self.rect.x -= scrollx
        
    def move(self, player, world_solids, scrollx, sp_group_list):
        player_rect = player.hitbox_rect
        player_atk_rect = player.atk_rect_scaled
        player_action = player.action
        player_direction = player.direction
        
        
        #head_pos_ini = (self.rect.centerx, self.rect.centery )#- self.h_height)
        dx = 0
        dy = 0
        dx_h = 0
        dy_h = 0
        atk_ready = self.is_in_range(player_rect.center, self.rect.center, self.r)
        atk_done = self.is_in_range(self.target_pos, self.head_rect.center, self.speed*4) #or (self.i_ >= self.max_i and self.head_rect.colliderect(player_rect))
        self.hostile = self.i_ >= self.max_i and not atk_done
        #self.is_vulnerable = self.i_ < self.max_i or not self.idling 
        #print(self.hostile)
        
        #update i frames and vulnerability
        if self.i_frames_en:
            if self.i_frames_ref_time + self.i_frames_durr > pygame.time.get_ticks():
                self.i_frames_en = False
                
        self.is_vulnerable = not self.i_frames_en
        
        #head spinning logic
        if (self.idling and atk_ready and not atk_done#player is in atk range
            ):
            if self.i_ < self.max_i:
                self.i_ += 0.02
                self.target_pos = list(player_rect.center)
        #player is out of atk range
        #first checks if head is not in range of ini body pos
        elif not self.is_in_range(self.head_rect.center, self.rect.center, self.head_rect.width):
            self.i_ = 0.1
            self.idling = False
            self.increment = 0
        else:
            self.idling = True
            self.i_ = 0.1
        
        #sinusoidal increments
        if self.increment >= 2*m.pi:
            self.increment = 0
        else:
            self.increment += self.i_
        
        #head behavior
        if self.i_ >= self.max_i: #chasing player
            self.action = 3
            (dx_h, dy_h) = self.chase(self.head_rect.center, self.target_pos, self.speed, 4*self.speed)
        elif not self.idling: #retracting
            self.action = 2
            (dx_h, dy_h) = self.chase(self.head_rect.center, self.rect.center, self.speed, self.speed)
            self.idling = self.is_in_range(self.head_rect.center, self.rect.center, self.head_rect.width//4)
        elif self.is_in_range(self.rect.center, player_rect.center, 2*self.rect.width):#player gets too close
            self.action = 1
            self.i_ = 0.1
            self.increment = 0
            self.head_rect.center = self.rect.center
            self.is_vulnerable = False
        else:#default bobbing
            self.action = 0
            self.head_rect.center = (self.rect.centerx, self.rect.centery)
            self.head_rect.centery += 16*m.sin(self.increment)
            self.head_rect.centerx += 8*m.cos(self.increment)
            
        #player collisions
        if self.is_vulnerable and player_atk_rect.width != 0:
            if self.head_rect.colliderect(player_atk_rect):
                self.i_ = 0.1
                self.idling = False
                self.increment = 0
                self.i_frames_en = True
                self.i_frames_ref_time = pygame.time.get_ticks()
                if self.action == 2:
                    recoil = 40
                else:
                    recoil = -10
                dx_h *= recoil
                dy_h *= recoil
                print("hit")
            
        #update entity head pos
        (dx_h, dy_h) = self.normalize(dx_h, dy_h)
        self.head_rect.centery += (dy_h)
        self.head_rect.centerx += (dx_h - scrollx)
        #self.target_pos[0] -= scrollx
        
        self.atk_rect_scaled.x += (dx - scrollx)
        self.rect.centerx += (dx - scrollx)

        
    def draw_body(self, screen):
        pygame.draw.line(screen, (255,0,0), self.rect.center, self.head_rect.center, 16)
        #pygame.draw.rect(screen, (255,0,0), self.rect)
        #pygame.draw.rect(screen, (0,0,255), self.head_rect)
        screen.blit(self.image, self.rect)
        screen.blit(self.image2, self.head_rect)
        
        
    def draw(self, screen):
        if self.check_if_onscreen():
            if self.inundated and self.frame_index < 1:
                if pygame.time.get_ticks()%5 != 0:
                    self.draw_body(screen)
            else:
                self.draw_body(screen)
                
    def animate(self, sp_group_list, player_rect):
        pass