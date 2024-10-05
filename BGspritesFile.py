import pygame
import os

class animated_bg_sprite(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, flip, name):
        pygame.sprite.Sprite.__init__(self)
        
        #load the BG frames by name
        self.name = name
        self.flip = flip
        
        self.frame_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        
        frames = len(os.listdir(f'sprites/bg_sprites/{self.name}'))

        for i in range(frames):
            img = pygame.image.load(f'sprites/bg_sprites/{self.name}/{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.frame_list.append(img)

        self.image = self.frame_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def check_if_onscreen(self):
        return (self.rect.x > -self.rect.width and self.rect.x < 640)
    
    def force_ini_position(self, scrollx):
        self.rect.x -= scrollx

    #only draws and animates if the sprite is on screen
    def animate(self, frame_rate):
        self.image = self.frame_list[self.frame_index]

        if self.check_if_onscreen() and pygame.time.get_ticks() - self.update_time > frame_rate:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1 

        if self.frame_index >= len(self.frame_list):
            self.frame_index = 0
        
    def draw(self, screen):
        if self.check_if_onscreen():
            screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
            
            
class tree(animated_bg_sprite):
    def __init__(self, x, y, scale, flip, name):
        super().__init__(x, y, scale, flip, name)
        
        self.frame_rate = 300
    
    #this will be specialized per sub class
    def enable(self, scrollx, player_hitbox_rect, player_atk_rect_scaled, particle_group):
        self.rect.x -= scrollx
        
class fountain(animated_bg_sprite):
    def __init__(self, x, y, scale, flip, name):
        super().__init__(x, y, scale, flip, name)
        
        self.frame_rate = 300
        
    def enable(self, scrollx, player_hitbox_rect, player_atk_rect_scaled, particle_group):
        self.rect.x -= scrollx
        
class lamp(animated_bg_sprite):
    def __init__(self, x, y, scale, flip, name):
        super().__init__(x, y, scale, flip, name)
        
        self.frame_rate = 300
        
    def enable(self, scrollx, player_hitbox_rect, player_atk_rect_scaled, particle_group):
        self.rect.x -= scrollx