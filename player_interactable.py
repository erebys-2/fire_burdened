import pygame
import os
from bullet import bullet_ #type: ignore
from particle import particle_ #type: ignore
from music_player import music_player #type: ignore
 
#traps and puzzles and items

class player_interactable(pygame.sprite.Sprite):
    #constructor
    def __init__(self, x, y, scale, direction, type, ini_vol, enabled, moveable):
        pygame.sprite.Sprite.__init__(self)
        self.direction = direction
        self.enabled = enabled
        self.moveable = moveable
        
        if direction < 0:
            self.flip = False
        else:
            self.flip = True
        
        self.type = type
        
        self.frame_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        
        frames = len(os.listdir(f'sprites/player_interactable/{self.type}'))

        for i in range(frames):
            img = pygame.image.load(f'sprites/player_interactable/{self.type}/{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.frame_list.append(img)

        self.image = self.frame_list[self.frame_index]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        self.m_player = music_player(['bassdrop2.wav', 'hit.wav', 'roblox2.wav', 'shoot.wav'], ini_vol)
        self.ini_vol = ini_vol
        
    def activate(self, player_rect, player_atk_rect, world_solids, scrollx, player_action, sp_group_list):
        if self.enabled:
            if self.type == 'spinning_blades':
                self.animate()
            elif self.type == 'crusher_top':
                self.animate
                
    def animate(self):
        framerates = {
            'spinning_blades': 160
        }    
        frame_update = framerates[self.type]
        #setting the image
        self.image = self.frame_list[self.frame_index]
        self.mask = pygame.mask.from_surface(self.image)

        if pygame.time.get_ticks() - self.update_time > frame_update:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1 

        #END OF ANIMATION FRAMES    
        if self.frame_index >= len(self.frame_list):
            self.frame_index = 0

    
    def draw(self, p_screen):
        
        p_screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        