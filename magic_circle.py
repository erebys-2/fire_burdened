import pygame
import math as m
from geometry import geometry

class magic_circle():
    def __init__(self, center, radius, color):
        self.center = center
        self.color = color
        self.radius = radius
        self.g1 = geometry()
        
        self.pt_list = self.g1.get_radial_pts(self.radius, self.center, 3, 0)
        self.pt_list2 = self.g1.get_radial_pts(self.radius, self.center, 3, 0)
        self.char_pos_list = self.g1.get_radial_pts(self.radius*0.85, self.center, 12, 0.1)
        
        self.radius += 1
        self.tick_ct = pygame.time.get_ticks()
        self.update_time = 140
        
    def move(self, scrollx):
        self.center[0] -= scrollx
    
    def force_ini_position(self, scrollx):
        self.center[0] -= scrollx
        
    def draw(self, screen, sp_group_list, pause_game):
        pygame.draw.circle(screen, self.color, self.center, self.radius, 2)
        pygame.draw.polygon(screen, self.color, self.pt_list, 1)
        pygame.draw.polygon(screen, self.color, self.pt_list2, 1)
        pygame.draw.circle(screen, self.color, self.center, self.radius*0.6, 1)
        pygame.draw.circle(screen, self.color, self.center, self.radius/2, 1)
        pygame.draw.circle(screen, self.color, self.center, 4, 6)
        pygame.draw.circle(screen, self.color, self.pt_list[0], self.radius/2, 1)
        for pt in self.pt_list2:
            pygame.draw.circle(screen, self.color, pt, self.radius/4, 1)
        
        inc = self.g1.get_periodic_radians(90, 1)
        self.pt_list = self.g1.get_radial_pts(self.radius, self.center, 3, inc)
        self.pt_list2 = self.g1.get_radial_pts(self.radius, self.center, 3, -2*inc)
        self.char_pos_list = self.g1.get_radial_pts(self.radius*0.85, self.center, 12, inc/2)
        
        if not pause_game and pygame.time.get_ticks() - self.update_time > self.tick_ct:
            for pt in self.char_pos_list:
                sp_group_list[4].sprite.add_particle('char_pink', pt[0], pt[1], 1, 1, True, -1)
                
            self.tick_ct = pygame.time.get_ticks()