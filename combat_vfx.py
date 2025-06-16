import pygame
import math as m

class combat_vfx():#class for vfx for combat
    def __init__(self, size):
        self.w = size[0]
        self.h = size[1]
        self.rect = pygame.rect.Rect(0,0,self.w,self.h)
        self.rect.topleft = (-size[0],-size[1])
        self.dist = [1000,1000]
        self.appr_vfx_en = False
        
    
    #positional functions
    
    #checks distance between 2 points, returns true if decreasing
    def get_approaching_1d(self, dimemsion, pos0, pos1):
        approaching = 0
        dist = abs(pos0 - pos1)
        if abs(pos0 - pos1) < self.dist[dimemsion]:
            approaching = 2
            self.dist[dimemsion] = dist
            
        elif abs(pos0 - pos1) == self.dist[dimemsion]:
            approaching = 1
            
        print(approaching)
        return approaching
    
    def enable_appr_vfx(self, player_rect):#makes sure player is in a range
        en = False
        if self.rect.colliderect(player_rect):
            en = self.get_approaching_1d(0, self.rect.center[0], player_rect.center[0]) + self.get_approaching_1d(1, self.rect.center[1], player_rect.center[1]) > 2
        else:
            self.dist = [1000,1000]#reset distances
        self.appr_vfx_en = en
    
    #drawing function
    
    def draw_appr_vfx(self, screen):
        pygame.draw.rect(screen, (255,0,0), self.rect, 1)
        if self.appr_vfx_en:
            pygame.draw.line(screen, (255,255,255), (self.rect.x, self.rect.centery), (self.rect.right, self.rect.centery), 1)
            pygame.draw.line(screen, (255,255,255), (self.rect.centerx, self.rect.y), (self.rect.centerx, self.rect.bottom), 1)
    