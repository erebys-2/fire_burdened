import pygame
import os
from music_player import music_player
import math as m

class bullet_(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, direction, scale, type, ini_vol, angle = 0, dmg = -1):
        pygame.sprite.Sprite.__init__(self)
        
        self.m_player = music_player(['pop.mp3', 'hit.mp3'], ini_vol)
        self.Active = True
        self.scale = scale
        
        x_weight = m.cos(angle)
        self.x_weight_abs = abs(x_weight)
        y_weight = m.sin(angle)
        self.y_weight_abs = abs(y_weight)
        
        if angle == 0:
            self.direction = direction
        elif x_weight > 0:
            self.direction = 1
        elif x_weight < 0:
            self.direction = -1
            
        if angle == 0:
            self.v_direction = 0
        elif y_weight > 0:
            self.v_direction = 1
        elif y_weight < 0:
            self.v_direction = -1
        
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
        self.max_cycles = -1
        self.dmg = 0
        
        if type == '8x8_red':
            self.animation_types = ['default']
            self.dmg = 3
        if type == 'player_basic':
            self.animation_types = ['default']
            self.max_cycles = 6
        if type == 'ground_impact':
            self.animation_types = ['default']
            self.dmg = 3
            
        base_path = os.path.join('assets', 'sprites', 'bullet', self.bullet_type)
        for animation in self.animation_types:
            temp_list = []
            frames = len(os.listdir(os.path.join(base_path, animation)))#f'assets/sprites/bullet/{self.bullet_type}/{animation}'))

            for i in range(frames):
                img = pygame.image.load(os.path.join(base_path, animation, f'{i}.png')).convert_alpha()#f'assets/sprites/bullet/{self.bullet_type}/{animation}/{i}.png'
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.frame_list.append(temp_list)

        self.image = self.frame_list[self.action][self.frame_index]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.deflection_rect = self.rect.scale_by(4,2)
        self.rect.topleft = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        self.edge_rect = pygame.rect.Rect(self.rect.right, self.rect.y, 2, self.rect.height)
        
        self.vel_y = 0
        self.vel_x = 0
        self.angle = angle
        if dmg != -1:
            self.dmg = dmg
        
        
        
    def move(self, player, world_solids, scrollx, sp_group_list):
        player_rect = player.hitbox_rect
        player_atk_rect = player.atk_rect_scaled
        player_action = player.action
        player_direction = player.direction
        self.deflection_rect.center = self.rect.center
        
        dx = 0
        dy = 0
        
        if self.Active == True and self.action != 1:
            if self.angle == 0:
                dx = self.direction * self.speed
            else:
                dx = self.direction * self.speed * self.x_weight_abs
                dy = self.v_direction * self.speed * self.y_weight_abs
                self.vel_x = dx
                self.vel_y = dy
        else:
            dx = 0
        
        #player interactions
        if self.bullet_type == '8x8_red':
            sp_group_list[5].sprite.add_particle('bloom_orange', self.rect.centerx, self.rect.centery, -self.direction, self.scale/8, True, -1)
            if not player.is_invulnerable[player_action] or player_action == 5:
                if self.rect.colliderect(player_rect.scale_by(0.8)):
                    if self.exploded == True:
                        #self.kill()
                        self.Active = False
                        
                    if self.exploded == False:
                        self.explode(sp_group_list)
                    self.exploded = True
                    # self.Active = False
                    # #self.kill()
            elif (player_atk_rect.colliderect(pygame.rect.Rect(self.deflection_rect.x + dx, self.deflection_rect.y + dy, self.deflection_rect.width, self.deflection_rect.height))
                and player_direction != self.direction
                and self.deflected == False
                ):
                    pygame.time.wait(12)
                    if player_direction == 1:
                        self.rect.centerx = player_atk_rect.right
                    else:
                        self.rect.centerx = player_atk_rect.x
                    self.explode(sp_group_list)
                    self.m_player.play_sound(self.m_player.sfx[1], (self.rect.centerx, self.rect.centery, None, None))
                    self.direction = -self.direction
                    self.v_direction = -self.v_direction
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
            if (p_int.collision_and_hostility[p_int.id_][0] and p_int.rect.colliderect(self.rect)):
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
        self.rect.y += dy
        
        if self.direction > 0:
            self.edge_rect.x = self.rect.right + (dx - scrollx) + 1
        else:
            self.edge_rect.x = self.rect.x - 2 + (dx - scrollx)
        
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
            sp_group_list[5].sprite.add_particle('player_bullet_explosion', x_loc, self.rect.centery, -self.direction, self.scale, True, frame)
            self.m_player.play_sound(self.m_player.sfx[0], (self.rect.centerx, self.rect.centery, None, None))
        elif self.bullet_type == '8x8_red':
            sp_group_list[5].sprite.add_particle('enemy_bullet_explosion', x_loc, self.rect.centery, -self.direction, self.scale, True, frame)
            self.m_player.play_sound(self.m_player.sfx[0], (self.rect.centerx, self.rect.centery, None, None))
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
            if self.bullet_type != 'ground_impact' and self.max_cycles < 0:
                if self.action == 1:
                    self.frame_index = 2
                    self.Active = False
                    #self.kill()
                else:
                    self.frame_index = 0
            elif self.max_cycles > 0:
                self.Active = False
            else:
                self.Active = False
        
    
    
    def draw(self, screen):
        #self.animate()
        img = pygame.transform.flip(self.image, self.flip, False)
        if abs(self.vel_y) > abs(self.vel_x):
            img = pygame.transform.rotate(self.image, 90)
            
        if self.vel_y == -1:
            img = pygame.transform.rotate(self.image, 180)
        
        #pygame.draw.rect(screen, (255,0,255), self.deflection_rect)
        screen.blit(img, self.rect)
        #pygame.draw.rect(screen, (225,0,0), self.edge_rect)
        
    def update_action(self, new_action):
    #check if action has changed
        if new_action != self.action:
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            