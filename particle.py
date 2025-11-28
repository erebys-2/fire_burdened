import pygame
import os
import random

class particle_2(pygame.sprite.Sprite):
    def __init__(self, particle_img_dict, centered_dict):
        #load every frame for every particle into lists of a dict
        pygame.sprite.Sprite.__init__(self)
        self.Active = True
        self.centered_dict = centered_dict
 
        if particle_img_dict == None:
            particle_path = os.path.join('assets', 'sprites', 'particle')#'assets/sprites/particle'
            self.particle_img_dict = {}
            for subdir in os.listdir(particle_path):
                temp_list = []
                for i in range(len(os.listdir(os.path.join(particle_path, subdir)))):#f'{particle_path}/{subdir}'
                    loaded_img = pygame.image.load(os.path.join(particle_path, subdir, f'{i}.png')).convert_alpha()#f'{particle_path}/{subdir}/{i}.png'
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
        
    def add_particle(self, name, x, y, direction, scale, frame_sync, frame, update_time=-1):
        
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
        if self.centered_dict[base_name]:#centered particles
            x -= (self.particle_img_dict[base_name][0].get_width()//2)*scale
            y -= (self.particle_img_dict[base_name][0].get_height()//2)*scale
            
        #set update_time
        if update_time == -1:
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
        if frame == -1:
            frame = random.randrange(0, len(self.particle_img_dict[name]))
        frame_img = self.particle_img_dict[name][frame]
        
        
        self.particle_list.append({'name': name,        
                                   'basename': base_name,
                                   'x': x,
                                   'y': y,
                                   'direction': direction,
                                   'flip': flip,
                                   #'scale': scale,
                                   'frame_sync': frame_sync,
                                   'frame': frame,
                                   'frame_img': frame_img,
                                   'update_time': update_time,
                                   'frame_update': frame_update
                                   })
        
    def empty_list(self):
        for particle0 in self.particle_list:
            del particle0
        
        self.particle_list *= 0
        
    def move(self, scrollx):
        for particle0 in self.particle_list:
            # if self.rect.x > 896 or self.rect.x < -96 or self.rect.y > 480 or self.rect.y < -32:
            #     self.Active = False
            #     self.kill()
            basename = particle0['basename']
            if  basename == 'shooter_death':
                particle0['y'] -= 0.75*(1/(particle0['frame_sync']+1))
                
            if basename in ('dog_death', 'fly_death', 'walker_death', 'worm_death'):
                particle0['y'] -= (1/(particle0['frame_sync']+1))
                
            elif basename == 'player_down_strike':
                particle0['x'] += -particle0['direction'] * 1
                
            elif basename == 'rain':
                particle0['y'] += 4
            
            elif basename == 'dust0':# or self.particle_type == 'player_atk1_trail':
                particle0['y'] -= 1
                particle0['x'] += random.randint(-1, 1)/2
                
            elif 'bloom' in basename:# or self.particle_type == 'player_atk1_trail':
                r = 5
                particle0['y'] += random.randint(-r, r)
                particle0['x'] += random.randint(-r, r)

            particle0['x'] -= scrollx
            
    def force_ini_position(self, scrollx):
        for particle0 in self.particle_list:
            particle0['x'] -= scrollx
            
           
    def animate(self): 
     #still frame particles, IMPORTANT: given frame index cannot exceed the particle frame count
        for particle0 in self.particle_list:
            if particle0['frame_sync']: #frame_synch enable
                if pygame.time.get_ticks() - particle0['update_time'] > particle0['frame_update']:
                    #particle0['update_time'] = pygame.time.get_ticks()
                    self.particle_list.pop(self.particle_list.index(particle0))
                    
            #animated particles
            else:
                #setting the image
                particle0['frame_img'] = self.particle_img_dict[particle0['name']][particle0['frame']]

                if pygame.time.get_ticks() - particle0['update_time'] > particle0['frame_update']:
                    particle0['update_time'] = pygame.time.get_ticks()
                    particle0['frame'] += 1

                #END OF ANIMATION FRAMES    
                if particle0['frame'] >= len(self.particle_img_dict[particle0['name']]):
                    self.particle_list.pop(self.particle_list.index(particle0))
        
    def draw(self, screen):
        for particle0 in self.particle_list:
            rect = pygame.rect.Rect(particle0['x'], particle0['y'], 1, 1)
            screen.blit(pygame.transform.flip(particle0['frame_img'], particle0['flip'], False), rect)
        
          
class group_particle2():
    def __init__(self):
        self.counter = 0
    
    def create_particles(self, loc, area, direction, data_): #data_ = scale, p_type, frame, density, sprite_group

        if data_[3] > 0:
            update_time = pygame.time.get_ticks()
            for i in range(data_[3]):
                data_[4].sprite.add_particle(data_[1], random.randrange(loc[0], area[0]), random.randrange(loc[1], area[1]), direction, data_[0], False, data_[2], update_time)
                    
        elif data_[3] < 0:
            self.counter += 1
            if self.counter >= -data_[3]:#pygame.time.get_ticks()%(-data_[3]) == 0:
                data_[4].sprite.add_particle(data_[1], random.randrange(loc[0], area[0]), random.randrange(loc[1], area[1]), direction, data_[0], False, data_[2])
                self.counter = 0
