import pygame
import os
from bullet import bullet_ #type: ignore
from particle import particle_ #type: ignore
from music_player import music_player #type: ignore
import random
 
#traps and puzzles and items

class player_interactable_(pygame.sprite.Sprite):
    #constructor
    def __init__(self, x, y, scale, direction, type, ini_vol, enabled, moveable):
        pygame.sprite.Sprite.__init__(self)
        self.direction = direction
        self.enabled = enabled
        self.moveable = moveable
        self.angle = 0
        self.initial_y = y
        self.initial_x = x
        self.current_x = x
        self.scale = scale
        self.already_falling = False
        
        if direction < 0:
            self.flip = False
        else:
            self.flip = True
        
        self.type = type
        
        self.frame_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.update_time2 = pygame.time.get_ticks()
        self.action = 0
        
        animation_types = {
            'spinning_blades':('spin', 'spin2'),
            'crusher_top':('crush', 'grimace'),
            'moving_plat_h':('move', 'move2'),
            'moving_plat_v':('move', 'move2')
        }
        
        for animation in animation_types[self.type]:
            temp_list = []
            frames = len(os.listdir(f'sprites/player_interactable/{self.type}/{animation}'))
        
            for i in range(frames):
                img = pygame.image.load(f'sprites/player_interactable/{self.type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.frame_list.append(temp_list)

        self.image = self.frame_list[self.action][self.frame_index]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        self.m_player = music_player(['mc_anvil.wav'], ini_vol)
        self.ini_vol = ini_vol
        
        self.dropping = False
        self.on_ground = False
        self.vel_y = 0
        self.vel_x = 0
        self.pause = False
        self.trigger_once = False
        self.do_screenshake = False
        
        self.collision_and_hostility = {
            'spinning_blades':(False, True),
            'crusher_top': (True, True),
            'moving_plat_h':(True, False),
            'moving_plat_v': (True, False)
        }
        
        # self.is_hostile = {
        #     'spinning_blades':True,
        #     'crusher_top':True,
        #     'moving_plat_h':False,
        #     'moving_plat_v':False
        # }
        self.atk_rect = pygame.Rect(0,0,0,0)
    
    def check_if_onscreen(self):
        return (self.rect.x > -self.rect.width and self.rect.x < 640)
         
    def do_tile_y_collisions(self, world_solids, dy):
        for tile in [tile for tile in world_solids 
                     if tile[1].x >= self.rect.x and tile[1].right <= self.rect.right
                     #and tile[1].y >= self.rect.y - 64 and tile[1].bottom <= self.rect.bottom + 64
                     ]:
            # if tile[1].colliderect(self.rect.x + dx, self.rect.y + 4, self.width//2, self.height - 8):

            # elif tile[1].colliderect(self.rect.x + self.width//2 + dx, self.rect.y + 4, self.width//2, self.height - 8):
                
            if tile[1].colliderect(self.rect.x + 2, self.rect.y + dy, self.width - 4, self.height//2) or self.rect.y <= self.initial_y:
                self.dropping = True
                self.on_ground = False
                
            elif tile[1].colliderect(self.rect.x + 2, self.rect.y + self.height//2 + dy, self.width - 4, self.height//2-4) or self.rect.bottom >= 480:
                if not self.pause:
                    self.trigger_once = True
                self.pause = True
                self.dropping = False
                self.on_ground = True
                self.already_falling = False

    def do_tile_x_collisions(self, world_solids, dx):
         for tile in [tile for tile in world_solids 
                      if tile[1].y >= self.rect.y and tile[1].bottom <= self.rect.bottom
                      and tile[1].x >= self.rect.x - 64 and tile[1].right <= self.rect.right + 64
                      ]:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y + 4, self.width//2, self.height - 8):
                self.direction = 1

            elif tile[1].colliderect(self.rect.x + self.width//2 + dx, self.rect.y + 4, self.width//2, self.height - 8):
                self.direction = -1
        
    def enable(self, player_rect, player_atk_rect, world_solids, scrollx, player_action, sp_group_list):
        if self.enabled:
            if self.type == 'spinning_blades':
                if self.check_if_onscreen():
                    self.animate()
                    
            elif self.type == 'moving_plat_h':
                self.do_tile_x_collisions(world_solids, self.vel_x)
                self.vel_x = 4*self.direction

            elif self.type == 'moving_plat_v' and self.check_if_onscreen():
                self.do_tile_y_collisions(world_solids, self.vel_x)

                if (self.dropping and not self.on_ground):
                    self.already_falling = True
                    self.vel_y = 5
                elif not self.dropping and self.on_ground:
                    self.vel_y = -5
                    
                self.rect.y += self.vel_y
                
            elif self.type == 'crusher_top' and self.check_if_onscreen():
                self.atk_rect = pygame.Rect(self.rect.x + 4, self.rect.bottom - 32, self.width - 8, 32)
                if pygame.time.get_ticks() - self.update_time2 > 720:
                    self.update_time2 = pygame.time.get_ticks()
                    self.pause = False
                    
                self.do_tile_y_collisions(world_solids, self.vel_y)
                
                if self.trigger_once:
                    if self.rect.x < 640 + 160 and self.rect.right >= 0 - 160:
                        self.m_player.play_sound(self.m_player.sfx[0])
                        particle = particle_(self.rect.x - (24*self.scale), self.rect.centery - (48*self.scale), -self.direction, self.scale*1.5, 'sparks', True, random.randint(0,2), False)
                        sp_group_list[5].add(particle)
                        #WE NEED SCREENSHAKE AAAAAA
                        self.do_screenshake = True
                    self.trigger_once = False
                
                if ((self.dropping and not self.on_ground 
                    and (player_rect.x > self.rect.x - 2*self.width and player_rect.x < self.rect.x + self.width + 2*self.width)
                    )
                    or self.already_falling
                    ):
                    self.already_falling = True
                    self.vel_y = 15
                    self.animate()
                elif not self.dropping and self.on_ground and not self.pause:
                    self.vel_y = -5
                    self.image = self.frame_list[0][0]
                else:
                    self.vel_y = 0
                    if self.pause:
                        #self.image = self.frame_list[self.action][random.randint(4,6)]
                        self.update_action(1)
                        self.animate()
                    else:
                        self.image = self.frame_list[0][0]
        
                #self.current_x += self.vel_y
                self.rect.y += self.vel_y
        else:
            self.mask.clear()
            self.atk_rect = pygame.Rect(0,0,0,0)
                
                
        self.rect.x += ( - scrollx) + self.vel_x
                
                
    def animate(self):
        framerates = {
            'spinning_blades': 30,
            'crusher_top': 70,
            'moving_plat_h': 100,
            'moving_plat_v': 100
        }    
        
        self.mask = pygame.mask.from_surface(self.image)
        frame_update = framerates[self.type]
        #setting the image
        self.image = self.frame_list[self.action][self.frame_index]

        if pygame.time.get_ticks() - self.update_time > frame_update and self.check_if_onscreen():
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1 

        #END OF ANIMATION FRAMES    
        if self.frame_index >= len(self.frame_list[self.action]):
            self.frame_index = 0
            if self.type == 'crusher_top' and self.action == 1:
                self.update_action(0)
            
    def update_action(self, new_action):
        #check if action has changed

        if new_action != self.action:
            #if new_action != 5:
                #self.jump_counter = 0
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    
    def draw(self, screen):
        if self.check_if_onscreen():
            screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        