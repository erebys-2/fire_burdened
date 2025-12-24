import math as m
import random
import sys
import pygame

class geometry():
    def __init__(self, orbit_ct = 3):
        self.zero = sys.float_info.min
        # self.tick_ct = pygame.time.get_ticks()
        # self.radians = 0
        
        self.orbital_list = [#used for periodic things, default is 3, add more as necessary
            {'tick_ct': pygame.time.get_ticks(), 'deg': 0} for i in range(orbit_ct)
        ]
        
        pass
    
    def get_angle_from_pts(self, pt0, pt1):#not completely reliable
        len_x = pt1[0] - pt0[0]
        len_y = pt1[1] - pt0[1]
        theta = m.atan((len_y)/(len_x+self.zero))
        if len_x < 0:
            theta += m.pi
        return theta
        
    def translate(self, x, y, pt_list):
        for pt in pt_list:
            pt[0] += x
            pt[1] += y
            
    def get_dist(self, pt0, pt1):
        return m.sqrt((pt1[0]-pt0[0])**2 + (pt1[1]-pt0[1])**2)
    
    def get_radial_pts(self, r, center, ct, phi=0, rand_disp=0):
        x = center[0]
        y = center[1]
        
        pt_list = []

        theta = 2*m.pi/ct
        for i in range(ct):
            pt_list.append([x + r*m.cos(i*(theta+rand_disp)+phi), y + r*m.sin(i*(theta+rand_disp)+phi)])
            
        return pt_list
    
    def get_periodic_radians(self, div, dt, orbit_index = 0):
        inc = m.pi/div
        if pygame.time.get_ticks() > self.orbital_list[orbit_index]['tick_ct'] + dt:
            self.orbital_list[orbit_index]['deg'] += inc
            self.orbital_list[orbit_index]['tick_ct'] = pygame.time.get_ticks()
            
        if self.orbital_list[orbit_index]['deg'] >= 2*m.pi:
            self.orbital_list[orbit_index]['deg'] = 0

        return self.orbital_list[orbit_index]['deg']

    
    
    
# # Example file showing a basic pygame "game loop"
# import pygame

# # pygame setup
# pygame.init()
# screen = pygame.display.set_mode((640, 480))
# clock = pygame.time.Clock()
# running = True

# g = geometry()

# pt0 = (320, 240)
# r = 256
# arc_rect = pygame.rect.Rect(0,0,r,r)
# arc_rect.center = pt0

# obj_rect = pygame.rect.Rect(0,0,5,5)
# obj_rect.center = pt0

# orbital_rect = pygame.rect.Rect(0,0,3,3)

# font0 = pygame.font.SysFont('SimSun', 12)

# dx = 150
# dy = 150

# while running:
#     clock.tick(60)  # limits FPS to 60
#     # poll for events
#     # pygame.QUIT event means the user clicked X to close your window
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     # fill the screen with a color to wipe away anything from last frame
    
#     screen.fill("black")
    
#     pt0 = pygame.mouse.get_pos()

#     #obj_rect.center = pt0
#     pygame.draw.rect(screen, (255,0,0), obj_rect)
    
#     theta = g.get_periodic_radians(100, 1)
#     epsilon = g.get_periodic_radians(100, 1, orbit_index=1)
    
    
#     orbital_rect.centerx = dx*m.cos(theta) + obj_rect.centerx
#     orbital_rect.centery = dy*m.sin(theta) + obj_rect.centery
#     pygame.draw.rect(screen, (255,0,0), orbital_rect)
    
#     # RENDER YOUR GAME HERE

#     # flip() the display to put your work on screen
#     pygame.display.flip()

    
#     pygame.display.set_caption(f" @ {clock.get_fps():.1f} FPS")

# pygame.quit()
            