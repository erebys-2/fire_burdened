import pygame
import os
from particle import particle_
from music_player import music_player
class bullet_(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, direction, scale, type, ini_vol):
        pygame.sprite.Sprite.__init__(self)
        
        self.m_player = music_player(['pop.wav', 'hit.wav'], ini_vol)
        self.Active = True
        self.scale = scale
        
        self.direction = direction
        self.speed = speed
        self.bullet_type = type
        self.exploded = False
        
        if direction < 0:
            self.flip = False
        else:
            self.flip = True
        
        self.deflected = False
        self.action = 0
        
        self.animation_types = []
        self.frame_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        
        if type == '8x8_red':
            self.animation_types = ['default']
        if type == 'player_basic':
            self.animation_types = ['default']
        if type == 'ground_impact':
            self.animation_types = ['default']
            
        for animation in self.animation_types:
            temp_list = []
            frames = len(os.listdir(f'sprites/bullet/{self.bullet_type}/{animation}'))

            for i in range(frames):
                img = pygame.image.load(f'sprites/bullet/{self.bullet_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.frame_list.append(temp_list)

        self.image = self.frame_list[self.action][self.frame_index]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        
    def move(self, player_rect, player_atk_rect, world_solids, scrollx, player_action, sp_group_list, player_direction):
        dx = 0
        dy = 0
        
        
        if self.Active == True and self.action != 1:
            dx = self.direction * self.speed
        else:
            dx = 0
        
        #player interactions
        if self.bullet_type == '8x8_red':
            if player_action != 6 and player_action != 7 and player_action != 8 and player_action != 9:
                if self.rect.colliderect(player_rect.scale_by(0.8)):
                    if self.exploded == True:
                        #self.kill()
                        self.Active = False
                        
                    if self.exploded == False:
                        self.explode(sp_group_list)
                    self.exploded = True
                    # self.Active = False
                    # #self.kill()
            elif (self.rect.colliderect(player_atk_rect)
                and player_direction != self.direction
                and self.deflected == False
                ):
                    pygame.time.wait(12)
                    if player_direction == 1:
                        self.rect.centerx = player_atk_rect.right
                    else:
                        self.rect.centerx = player_atk_rect.x
                    self.explode(sp_group_list)
                    self.m_player.play_sound(self.m_player.sfx[1])
                    self.direction = -self.direction
                    self.deflected = True
                    self.speed += 16
                    self.flip = not self.flip
                
            
        #tile collisions
        for tile in [tile for tile in world_solids if tile[1].y >= self.rect.y - 32 and tile[1].bottom <= self.rect.bottom + 32 and tile[1].x > -160 and tile[1].x < 800]:
            if self.rect.colliderect(tile[1]) and tile[2] != 10:
                self.Active = False
                self.explode(sp_group_list)
                #self.kill()
                
        for p_int in sp_group_list[8]:
            if (self.rect.colliderect(p_int.rect)):
                self.Active = False
                self.explode(sp_group_list)
        
        #enemy collisions
        
        # notes: this used to have a 1 tick collision detection, where a bullet was detected each cycle
        # but there was some glitch probably involving scrolling and spawning particles that made those
        # collisions inconsistent
        
        # this file handles the bullet killing itself (after 2 cycles), it's up to the enemy file to handle
        # taking damage
        
        # currently for player bullets, damage taken is directly incremented with time spent colliding with
        # bullets instead of how many bullets hit
        
        # a possible solution could be on the enemy end have it iterate thru the bullet list to check each bullet
        # for collisions, but I think this would be noticeably inefficient
        
        if (pygame.sprite.spritecollide(self, sp_group_list[0], False) and self.bullet_type != 'ground_impact'):
            #dx +=(self.direction)*64
            if self.exploded == True:
                #self.kill()
                self.Active = False
                
            if self.exploded == False:
                self.explode(sp_group_list)
            self.exploded = True
            #self.kill()
        
        #border collisions
        if self.rect.right > 640 + 160 or self.rect.x < -160 or self.rect.y > 480 or self.rect.y < 0:
            self.Active = False
            #self.kill()
        
        self.rect.x += (dx - scrollx)
        
    def force_ini_position(self, scrollx):
        self.rect.x -= scrollx
        
    def explode(self, sp_group_list):
        if self.frame_index % 2 == 0:
            frame = 0
        else:
            frame = 1
        if self.direction < 0:
            x_loc = self.rect.x
        else:
            x_loc = self.rect.right
        if self.bullet_type == 'player_basic':    
            particle = particle_(x_loc, self.rect.y + self.height//2, -self.direction, self.scale, 'player_bullet_explosion', True, frame, False)
            sp_group_list[5].add(particle)
            self.m_player.play_sound(self.m_player.sfx[0])
        elif self.bullet_type == '8x8_red':
            particle = particle_(x_loc, self.rect.y + self.height//2, -self.direction, self.scale, 'enemy_bullet_explosion', True, frame, False)
            sp_group_list[5].add(particle)
            self.m_player.play_sound(self.m_player.sfx[0])
        #self.kill()
        
    def animate(self):
        
        # if (pygame.sprite.spritecollide(self, the_sprite_group.enemy0_group, False)):
        #     self.Active = False
        #     #self.kill()
        if self.bullet_type == 'ground_impact':
            frame_update = 30
        else:
            frame_update = 30

        #setting the image
        self.image = self.frame_list[self.action][self.frame_index]
        self.mask = pygame.mask.from_surface(self.image)

        #update sprite dimensions
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        if pygame.time.get_ticks() - self.update_time > frame_update:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1 

        #END OF ANIMATION FRAMES    
        if self.frame_index >= len(self.frame_list[self.action]):
            if self.bullet_type != 'ground_impact':
                if self.action == 1:
                    self.frame_index = 2
                    self.Active = False
                    #self.kill()
                else:
                    self.frame_index = 0
            else:
                self.Active = False
        
    
    
    def draw(self, p_screen):
        #self.animate()
        p_screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        
    def update_action(self, new_action):
    #check if action has changed
        if new_action != self.action:
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            