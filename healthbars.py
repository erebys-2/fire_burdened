import pygame

class health_bar():
    def __init__(self, color=(237,124,117), bg_color=(51,47,47), h=2, w=32):
        self.h = h
        self.w = w
        self.color = color
        self.bg_color = bg_color
        self.hp_rect = pygame.rect.Rect(0,0,w,h)
        self.hp_bg_rect = pygame.rect.Rect(0,0,w+2,h+2)
        
    def render_bar(self, pos, hp_ratio, screen):
        self.hp_bg_rect.center = pos
        self.hp_rect.topleft = (self.hp_bg_rect.x+1, self.hp_bg_rect.y+1)
        self.hp_rect.width = int(self.w*hp_ratio)
        
        pygame.draw.rect(screen, self.bg_color, self.hp_bg_rect)
        pygame.draw.rect(screen, self.color, self.hp_rect)