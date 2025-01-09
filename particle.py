import pygame
import os
import random

class particle_2(pygame.sprite.Sprite):
    def __init__(self, particle_img_dict):
        #load every frame for every particle into lists of a dict
        pygame.sprite.Sprite.__init__(self)
        self.Active = True
 
        if particle_img_dict == None:
            particle_path = 'sprites/particle'
            self.particle_img_dict = {}
            for subdir in os.listdir(particle_path):
                temp_list = []
                for i in range(len(os.listdir(f'{particle_path}/{subdir}'))):
                    loaded_img = pygame.image.load(f'{particle_path}/{subdir}/{i}.png').convert_alpha()
                    temp_list.append(loaded_img)
                self.particle_img_dict[subdir] = temp_list
        else:
            self.particle_img_dict = particle_img_dict
            
        self.particle_list = []
        
        self.framerates = {
            'player_crit': 80, 
            'player_down_strike': 80, 
            'player_up_strike': 80, 
            'player_bullet_explosion': 60, 
            'enemy_bullet_explosion': 60,
            'shooter_death': 80,
            'player_mvmt': 75,
            'player_impact': 60,
            'sparks': 40,
            'grass_cut': 90,
            'player_atk1_trail':150
        }    
            
        #print(self.particle_img_dict)
        
    def add_particle(self, name, x, y, direction, scale, frame_sync, frame):
        
        base_name = name
        if scale != 1:
            #modify name if scale != 1
            name = name + str(scale)
            
            #add new resized frames if not already in particle_img_dict
            if name not in self.particle_img_dict:
                temp_list = []
                for img in self.particle_img_dict[base_name]:
                    temp_list.append(pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale))))
                self.particle_img_dict[name] = temp_list
                
        
        #shift x,y if centered
        if base_name in ('player_bullet_explosion', 'enemy_bullet_explosion', 'player_impact', 'player_mvmt', 'player_crit', 'bloom',
                    'player_atk1_trail'
                    ):#centered particles
            x -= (self.particle_img_dict[base_name][0].get_width()//2)*scale
            y -= (self.particle_img_dict[base_name][0].get_height()//2)*scale
            
        #set update_time
        update_time = pygame.time.get_ticks()
        
        #set frame_update
        if name in self.framerates:
            frame_update = self.framerates[name]
        else:
            frame_update = 100
            
        #set flip
        if direction < 0:
            flip = True
        else:
            flip = False
            
        #set img
        frame_img = self.particle_img_dict[name][frame]
        
        self.particle_list.append([name,        #0
                                   x,           #1
                                   y,           #2
                                   direction,   #3 
                                   flip,        #4
                                   scale,       #5
                                   frame_sync,  #6 
                                   frame,       #7
                                   frame_img,   #8
                                   update_time, #9
                                   frame_update,#10
                                   base_name    #11
                                   ])
    def empty_list(self):
        for particle0 in self.particle_list:
            particle0 *= 0
        
        self.particle_list *= 0
        
    def move(self, scrollx):
        for particle0 in self.particle_list:
            # if self.rect.x > 896 or self.rect.x < -96 or self.rect.y > 480 or self.rect.y < -32:
            #     self.Active = False
            #     self.kill()
                
            if particle0[11] == 'shooter_death':
                particle0[2] -= 0.75*(1/(particle0[6]+1))
                
            if particle0[11] in ('dog_death', 'fly_death', 'walker_death'):
                particle0[2] -= (1/(particle0[6]+1))
                
            elif particle0[11] == 'player_down_strike':
                particle0[1] += -particle0[3] * 1
                
            elif particle0[11] == 'rain':
                particle0[2] += 4
            
            elif particle0[11] == 'dust0':# or self.particle_type == 'player_atk1_trail':
                particle0[2] -= 1
                particle0[1] += random.randint(-1, 1)/2

            particle0[1] -= scrollx
            
    def force_ini_position(self, scrollx):
        for particle0 in self.particle_list:
            particle0[1] -= scrollx
            
           
    def animate(self): 
     #still frame particles, IMPORTANT: given frame index cannot exceed the particle frame count
        for particle0 in self.particle_list:
            if particle0[6]: #frame_synch enable
                if pygame.time.get_ticks() - particle0[9] > particle0[10]:
                    particle0[9] = pygame.time.get_ticks()
                    self.particle_list.pop(self.particle_list.index(particle0))
                    
            #animated particles
            else:
                #setting the image
                particle0[8] = self.particle_img_dict[particle0[0]][particle0[7]]

                if pygame.time.get_ticks() - particle0[9] > particle0[10]:
                    particle0[9] = pygame.time.get_ticks()
                    particle0[7] += 1

                #END OF ANIMATION FRAMES    
                if particle0[7] >= len(self.particle_img_dict[particle0[0]]):
                    self.particle_list.pop(self.particle_list.index(particle0))
        
    def draw(self, screen):
        for particle0 in self.particle_list:
            rect = pygame.rect.Rect(particle0[1], particle0[2], 1, 1)
            screen.blit(pygame.transform.flip(particle0[8], particle0[4], False), rect)
        
          
class group_particle2():
    def __init__(self):
        pass
    
    def create_particles(self, loc, area, direction, data_): #data_ = scale, p_type, frame, density, sprite_group

        if data_[3] > 0:
            for i in range(data_[3]):
                data_[4].sprite.add_particle(data_[1], random.randrange(loc[0], area[0]), random.randrange(loc[1], area[1]), direction, data_[0], False, data_[2])
                    
        elif data_[3] < 0:
            if pygame.time.get_ticks()%(-data_[3]) == 0:
                data_[4].sprite.add_particle(data_[1], random.randrange(loc[0], area[0]), random.randrange(loc[1], area[1]), direction, data_[0], False, data_[2])
