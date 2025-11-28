import math as m
import random
import sys

class geometry():
    def __init__(self):
        self.zero = sys.float_info.min
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
    
    def get_radial_pts(self, r, center, ct, phi=0, rand_disp=0):
        x = center[0]
        y = center[1]
        
        pt_list = []

        theta = 2*m.pi/ct
        for i in range(ct):
            pt_list.append([x + r*m.cos(i*(theta+rand_disp)+phi), y + r*m.sin(i*(theta+rand_disp)+phi)])
            
        return pt_list
    

    
    
    
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

# obj_rect = pygame.rect.Rect(0,0,3,3)
# obj_rect.center = pt0

# font0 = pygame.font.SysFont('SimSun', 12)

# dx = 5
# dy = 5

# while running:
#     clock.tick(60)  # limits FPS to 60
#     # poll for events
#     # pygame.QUIT event means the user clicked X to close your window
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     # fill the screen with a color to wipe away anything from last frame
    
#     screen.fill("black")
    
#     pt1 = pygame.mouse.get_pos()
    
#     theta = g.get_angle_from_pts(pt0, pt1)
#     #font0.render(str((180/m.pi)*theta), False, (255, 0, 0))
#     screen.blit(font0.render(str((180/m.pi)*theta), False, (255, 0, 0)), (0, 0))
    
#     pygame.draw.line(screen, (255,0,0), (0, 240), (640, 240))
#     pygame.draw.line(screen, (255,0,0), (pt0), (pt1))    
#     pygame.draw.arc(screen, (255,0,0), arc_rect, -theta, 0)
    
    
#     obj_rect.centerx += dx
#     obj_rect.centery += dy
    
#     if obj_rect.centerx < 0 or obj_rect.centerx > 640 or  obj_rect.centery < 0 or obj_rect.centery > 480:
#         obj_rect.center = pt0
#         dx = 5*m.cos(theta)
#         dy = 5*m.sin(theta)

#     pygame.draw.rect(screen, (255,0,0), obj_rect)
    
#     # RENDER YOUR GAME HERE

#     # flip() the display to put your work on screen
#     pygame.display.flip()

    
#     pygame.display.set_caption(f" @ {clock.get_fps():.1f} FPS")

# pygame.quit()
            