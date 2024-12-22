import pygame
import os
import random
#from music_player import music_player #type: ignore
'''
x, y: location, floats
direction: for directional particles, int
scale: size of particle, int
type: type of particle, string
frame_sync: whether or not the particle's animation is synchronized with another animation, bool
frame: for frame sync, int

The particle object does not move, only scrolls w/ the screen or w/ its obj

Particles are created by other objects, like the player
'''

class particle_(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, scale, type, frame_sync, frame, bound):
        pygame.sprite.Sprite.__init__(self)
        #self.m_player = music_player(['pop2.wav', 'hit.wav'])
        #music_player_list = [] #fill this list later down the constructor and when it
        #tests for particle types, and then instantiate a music player one line down
        #play the sound at the very end of the constructor
        self.Active = True
        self.particle_type = type
        #self.action = 0
        self.bound = bound
        self.direction = direction
        self.sprite_centered = ('player_bullet_explosion', 'enemy_bullet_explosion', 'player_impact', 'player_mvmt', 'player_crit' )
        
        self.frame_sync = frame_sync
        self.forced_frame = frame
        if direction < 0:
            self.flip = False
        else:
            self.flip = True
        
        self.frame_list = []
        self.frame_index = self.forced_frame
        self.update_time = pygame.time.get_ticks()
        
        frames = len(os.listdir(f'sprites/particle/{self.particle_type}'))

        for i in range(frames):
            img = pygame.image.load(f'sprites/particle/{self.particle_type}/{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.frame_list.append(img)

        self.image = self.frame_list[self.frame_index]
        self.rect = self.image.get_rect()
        
        
        if any(self.particle_type == particle for particle in self.sprite_centered):
            self.rect.center = (x,y)
        else:
            self.rect.topleft = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
    # def bounded_mvmt(self, x, y):
        
    #     self.rect.x = x
    #     self.rect.y = y
    #     print("working")
    
    def move(self, scrollx):
        dx = 0
        dy = 0
        #if self.bound == False:

        if self.rect.x > 896 or self.rect.x < -96 or self.rect.y > 480 or self.rect.y < -32:
            self.Active = False
            self.kill()
            
        if self.particle_type == 'shooter_death':
            self.rect.y -= 4*(1/(self.frame_index+1))
            
        elif self.particle_type == 'dog_death' or  self.particle_type == 'fly_death' or  self.particle_type == 'walker_death':
            self.rect.y -= 2*(1/(self.frame_index+1))
            
        elif self.particle_type == 'player_down_strike':
            dx += -self.direction * 1
            
        elif self.particle_type == 'rain':
            self.rect.y += 4
        
        elif self.particle_type == 'dust0':
            self.rect.y -= 0.01
            self.rect.x += random.randint(-1, 1)/2

        self.rect.x += (dx - scrollx)
        
    def force_ini_position(self, scrollx):
        self.rect.x -= scrollx
        
    def animate(self):
        #adjust animation speed for different particle types here
        
        framerates = {
            'player_crit': 80, 
            'player_down_strike': 80, 
            'player_up_strike': 80, 
            'player_bullet_explosion': 60, 
            'enemy_bullet_explosion': 60,
            'shooter_death': 80,
            'dog_death': 100,
            'fly_death': 100,
            'player_mvmt': 75,
            'player_impact': 60,
            'sparks': 40,
            'grass_cut': 90,
            'walker_death': 100
        }    
        
        if self.particle_type in framerates:
            frame_update = framerates[self.particle_type]
        else:
            frame_update = 100
            
        #still frame particles
        if self.frame_sync:
            self.frame_index = self.forced_frame
            self.image = self.frame_list[self.frame_index]
            if pygame.time.get_ticks() - self.update_time > frame_update:
                self.update_time = pygame.time.get_ticks()
                self.Active = False
                self.kill()
                
        #animated particles
        else:
            #setting the image
            self.image = self.frame_list[self.frame_index]

            if pygame.time.get_ticks() - self.update_time > frame_update:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1 

            #END OF ANIMATION FRAMES    
            if self.frame_index >= len(self.frame_list):
                # if self.particle_type == 'dog_death' or self.particle_type == 'shooter_death':
                #     self.m_player.play_sound(self.m_player.sfx[0])
                self.frame_index = 0

                self.Active = False
                self.kill()
    
    def draw(self, p_screen):
        
        p_screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        
        
        
        
class group_particle():
    def __init__(self):
        pass
    
    def create_particles(self, loc, area, direction, data_):

        if data_[3] > 0:
            for i in range(data_[3]):
                particle = particle_(random.randrange(loc[0], area[0]), random.randrange(loc[1], area[1]), direction, data_[0], data_[1], False, data_[2], False)
                data_[4].add(particle)
        elif data_[3] < 0:
            if pygame.time.get_ticks()%(-data_[3]) == 0:
                particle = particle_(random.randrange(loc[0], area[0]), random.randrange(loc[1], area[1]), direction, data_[0], data_[1], False, data_[2], False)
                data_[4].add(particle)
