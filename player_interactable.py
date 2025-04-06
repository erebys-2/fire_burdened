import pygame
import os
from bullet import bullet_ #type: ignore
from music_player import music_player #type: ignore
import random
from ItemFile import Item

class player_interactable_(pygame.sprite.Sprite):#generic class for sprites that can interact with the player/have hitboxes
    #constructor
    def __init__(self, x, y, scale, direction, id, ini_vol, enabled, frame_list, sfx_list_ext):
        pygame.sprite.Sprite.__init__(self)
        self.direction = direction
        if id == 'tall_plant':
            self.direction = random.randint(0,1)
            if self.direction == 0:
                self.direction = -1
            
        self.enabled = enabled
        self.is_moving_plat = id in ('moving_plat_h', 'moving_plat_v', 'crusher_top')

        self.angle = 0
        self.initial_y = y
        self.initial_x = x
        self.current_x = x
        self.scale = scale
        self.already_falling = False
        
        if self.direction < 0:
            self.flip = False
        else:
            self.flip = True

        self.id = id
        
        self.frame_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.update_time2 = pygame.time.get_ticks()
        self.action = 0
        
        
        # if self.id == 'flame_pillar':
        #     scale2 = 3
        # else:
        #     scale2 = 1
        
        if frame_list == None:
            for animation in os.listdir(f'assets/sprites/player_interactable/{self.id}'):#order matters for these, I don't want to keep adding to dictionaries 
                temp_list = []
                frames = len(os.listdir(f'assets/sprites/player_interactable/{self.id}/{animation}'))
            
                for i in range(frames):
                    img = pygame.image.load(f'assets/sprites/player_interactable/{self.id}/{animation}/{i}.png').convert_alpha()
                    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    temp_list.append(img)
                self.frame_list.append(temp_list)
        else:
            self.frame_list = frame_list
            
            
        #generate special frames
        if self.id in ('grass', 'tall_plant'):
            temp_list = []
            for img in self.frame_list[0]:
                frame = pygame.transform.scale(img, (int(img.get_width() * 1.2), int(img.get_height() * 0.6)))
                temp_list.append(frame)
            self.frame_list.append(temp_list)
        elif self.id == 'flame_pillar':
            for animation in self.frame_list:
                for img in animation:
                    img = pygame.transform.scale(img, (int(img.get_width()), int(img.get_height() * 3)))

        self.image = self.frame_list[self.action][self.frame_index]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.img_rect = self.image.get_rect()
        self.img_rect.topleft = (x,y)
        
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        self.m_player = music_player(None, ini_vol)#['mc_anvil.mp3', 'step2soft.mp3', 'pop3.mp3']
        self.m_player.sfx = sfx_list_ext
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
            'moving_plat_v': (True, False),
            'grass':(False, False),
            'tall_plant':(False, False),
            'breakable_brick1':(True, False),
            'breakable_brick2':(True, False),
            'flame_pillar':(False, True)
        }
        
        self.has_mask_collisions = ('spinning_blades',)
        
        self.atk_rect = pygame.Rect(0,0,0,0)
        
        if self.id == 'breakable_brick1':
            self.durability = 2
        else:
            self.durability = 1
        self.durability_changed = False
        
        self.framerates = {
            'spinning_blades': 30,
            'crusher_top': 70,
            'grass': 270,
            'tall_plant':270,
            'flame_pillar': 120
        }    
        
        self.is_onscreen = False
        
    
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
                
    def do_player_atk_collisions(self, player_atk_rect):
        colliding = False
        if player_atk_rect.width != 0:
            colliding = player_atk_rect.colliderect(self.rect)
        return colliding
    
    def do_bullet_collisions(self, bullet_group_list):
        colliding = False
        for bullet_group in bullet_group_list:
            for bullet in bullet_group:
                colliding = self.rect.colliderect(bullet.edge_rect)
        return colliding
            
    
    def breakable_tile_frame_change(self):
        if self.durability > 0:
            index = len(self.frame_list[self.action]) - self.durability
        else:
            index = len(self.frame_list[self.action]) - 1
        return index
        
    def enable(self, player_rect, player_atk_rect, world_solids, scrollx, player_action, sp_group_list):
        if self.enabled:
            self.is_onscreen = self.check_if_onscreen()
            if self.is_onscreen:
                if self.id == 'spinning_blades':
                    self.animate(None)
                        
                if self.id == 'flame_pillar':
                    self.atk_rect = pygame.Rect(self.rect.x + 16, self.rect.y, self.width - 32, self.height)
                    if player_rect.colliderect(self.atk_rect):
                        for i in range(random.randrange(2,4)):
                            sp_group_list[5].sprite.add_particle('player_bullet_explosion', 
                                                                player_rect.centerx + random.randint(-self.width//2,self.width//2), 
                                                                player_rect.centery + random.randint(-self.width//2,self.width//2), 
                                                                -self.direction, random.randint(1,2), True, random.randint(0,2))
                                        
                    sp_group_list[5].sprite.add_particle('bloom', self.rect.centerx, 
                                            self.rect.centery + random.randint(-self.width//2,self.width//2), 
                                            -self.direction, 1, True, random.randint(0,2))

                    if pygame.time.get_ticks()%10 == 0:
                        sp_group_list[5].sprite.add_particle('player_bullet_explosion', 
                                                                self.rect.centerx + random.randint(-self.width//2,self.width//2), 
                                                            self.rect.centery + random.randint(-self.width//2,self.width//2), 
                                                            -self.direction, 2, True, random.randint(0,2))

                    self.rect.y -= 30
                    if self.rect.bottom < -self.rect.height//4:
                        self.rect.bottom = 480 + self.rect.height//4

                        self.animate(None)
                        
                elif self.id in ('grass', 'tall_plant'):
                    frame_update = None
                    if (self.action in (0,2) and 
                        (self.do_player_atk_collisions(player_atk_rect) or 
                            self.do_bullet_collisions((sp_group_list[1], sp_group_list[2])))
                        ):
                        #self.m_player.play_sound(self.m_player.sfx[1], (self.rect.centerx, self.rect.centery))
                        self.img_rect.y = self.rect.y
                        self.img_rect.width = self.rect.width
                        self.frame_index = 0
                        self.action = 1
                        self.rect.height = 0
                        for i in range(random.randrange(4,8)):
                            sp_group_list[5].sprite.add_particle('grass_cut', self.rect.x + random.randint(-8,8), self.rect.y + random.randint(-16,8), -self.direction, self.scale, True, random.randint(0,2))
                        if random.randint(0,15) == 0:
                            sp_group_list[12].add(Item('Mild Herb', self.rect.centerx + 2*random.randint(-5,5), self.rect.centery + 2*random.randint(-5,5), 1, False))
                            
                    if self.action != 1:#not cut down
                        if player_rect.colliderect(self.rect):#squish the plant!!
                            self.action = 2
                            self.img_rect.width = int(1.2*self.rect.width)
                            if self.img_rect.y == self.rect.y:
                                #sp_group_list[5].sprite.add_particle('grass_cut', self.rect.x + random.randint(-8,8), self.img_rect.centery + random.randint(-16,0), -self.direction, self.scale, True, 2)
                                self.img_rect.y = self.rect.y + int(0.4*self.height) + self.scale
                            frame_update = 340
                        else:#reset the plant
                            self.action = 0
                            self.img_rect.width = self.rect.width
                            self.img_rect.y = self.rect.y
                    else:#regrow when cut down after 7000 ticks
                        if pygame.time.get_ticks() - self.update_time2 > 12000:
                            self.action = 2
                            self.rect.height = 32
                            self.img_rect.y = self.rect.y + int(0.4*self.height) + self.scale
                            self.update_time2 = pygame.time.get_ticks()
                        
                        
                    self.animate(frame_update)
                    # else:
                    #     self.action = 0
                    #     self.rect.height = 32
                        
                elif self.id == 'breakable_brick1' or (self.id == 'breakable_brick2' and player_action == 10):
                    #print(self.durability)
                    if self.durability > 0:
                        if (player_action != 16 and
                            (self.do_player_atk_collisions(player_atk_rect) or 
                            self.do_bullet_collisions((sp_group_list[1], sp_group_list[2])))
                            ):
                            if not self.durability_changed:
                                #if player_action != 16:
                                self.durability -= 1
                                self.durability_changed = True
                                self.image = self.frame_list[self.action][self.breakable_tile_frame_change()]
                                self.m_player.play_sound(self.m_player.sfx[2], (self.rect.centerx, self.rect.centery, None, None))
                                    
                                sp_group_list[5].sprite.add_particle('player_bullet_explosion', self.rect.centerx + random.randint(-12,12), self.rect.centery + random.randint(-12,12), -self.direction, 1.2*self.scale, False, random.randrange(0,3))
                                
                                for i in range(3):
                                    sp_group_list[5].sprite.add_particle('stone_breaking', self.rect.x + random.randint(-16,16), self.rect.y + random.randint(-16,16), -self.direction, self.scale, True, random.randint(0,2))
                        else:
                            self.durability_changed = False
                    else:
                        #if random.randint(0,1) == 0:
                        #for i in range(3):
                        sp_group_list[12].add(Item('Rock', self.rect.centerx + 2*random.randint(-5,5), self.rect.centery + 2*random.randint(-5,5), 1, False))
                        self.rect = pygame.Rect(0,0,0,0)
                        self.kill()
                        

                elif self.id == 'moving_plat_v':
                    self.do_tile_y_collisions(world_solids, self.vel_x)

                    if (self.dropping and not self.on_ground):
                        self.already_falling = True
                        self.vel_y = 5
                    elif not self.dropping and self.on_ground:
                        self.vel_y = -5
                        
                    self.rect.y += self.vel_y
                    
                elif self.id == 'crusher_top':
                    self.atk_rect = pygame.Rect(self.rect.x + 4, self.rect.bottom - 32, self.width - 8, 32)
                    if pygame.time.get_ticks() - self.update_time2 > 720:
                        self.update_time2 = pygame.time.get_ticks()
                        self.pause = False
                        
                    self.do_tile_y_collisions(world_solids, self.vel_y)
                    
                    if self.trigger_once:
                        if self.rect.x < 640 + 128 and self.rect.right >= 0 - 128:
                            self.m_player.play_sound(self.m_player.sfx[0], (self.rect.centerx, self.rect.centery, None, None))
                            sp_group_list[5].sprite.add_particle('sparks', self.rect.x - (24*self.scale), self.rect.centery - (48*self.scale), -self.direction, self.scale*1.5, True, random.randint(0,2))
                            #WE NEED SCREENSHAKE AAAAAA
                            self.do_screenshake = True
                        self.trigger_once = False
                    
                    if ((self.dropping and not self.on_ground 
                        and (player_rect.x > self.rect.x - 1.25*self.width and player_rect.x < self.rect.x + self.width + 1.25*self.width)
                        )
                        or self.already_falling
                        ):
                        self.already_falling = True
                        self.vel_y = 15
                        self.animate(None)
                    elif not self.dropping and self.on_ground and not self.pause:
                        self.vel_y = -5
                        self.image = self.frame_list[0][0]
                    # elif self.do_player_atk_collisions(player_atk_rect):
                    #     self.vel_y = random.randint(-8,0)
                    else:
                        self.vel_y = 0
                        if self.pause:
                            #self.image = self.frame_list[self.action][random.randint(4,6)]
                            self.update_action(1)
                            self.animate(None)
                        else:
                            self.image = self.frame_list[0][0]
            
                    #self.current_x += self.vel_y
                    self.rect.y += self.vel_y
                
            #p_ints that need to function on/off screen    
            if self.id == 'moving_plat_h':
                self.do_tile_x_collisions(world_solids, self.vel_x)
                self.vel_x = 4*self.direction
            
        else:
            self.mask.clear()
            self.atk_rect = pygame.Rect(0,0,0,0)
                
        self.rect.x += ( - scrollx) + self.vel_x
        self.img_rect.centerx = self.rect.centerx
        
    def force_ini_position(self, scrollx):
        self.rect.x -= scrollx
                
                
    def animate(self, frame_update_forced):

        if self.id in self.has_mask_collisions:
            self.mask = pygame.mask.from_surface(self.image)
        
        if frame_update_forced == None:
            if self.id in self.framerates:
                frame_update = self.framerates[self.id]
            else:
                frame_update = 100
        else:
            frame_update = frame_update_forced
        #setting the image
        self.image = self.frame_list[self.action][self.frame_index]

        if pygame.time.get_ticks() - self.update_time > frame_update:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1 

        #END OF ANIMATION FRAMES    
        if self.frame_index >= len(self.frame_list[self.action]):
            self.frame_index = 0
            if self.id == 'crusher_top' and self.action == 1:
                self.update_action(0)
            
    def update_action(self, new_action):
        #check if action has changed

        if new_action != self.action:
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    
    def draw(self, screen):
        #if self.is_onscreen:
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.img_rect)
            #pygame.draw.rect(screen, (255,0,0), self.rect)
        