import math as m
import random
import pygame
import os
from music_player import music_player
from ItemFile import Item 

class ms_enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, scale, id_, enemy0_order_id, ini_vol, frame_dict, sfx_list_ext):
        pygame.sprite.Sprite.__init__(self)
        
        self.spawn_order_id = enemy0_order_id
        self.id_ = id_

        self.Alive = True
        self.hp = 12
        self.hits_tanked = 0
        self.action = 0
        self.scale = scale
        
        self.inundated = False
        self.speed = speed
        self.speed_x = 0
        self.speed_y = 0

        
        segments = 15
        
        self.update_time = pygame.time.get_ticks()
        self.update_time2 = pygame.time.get_ticks()
        self.update_time3 = pygame.time.get_ticks()
        self.i_frames_time = pygame.time.get_ticks()
        self.pos_ref_time = pygame.time.get_ticks()
        self.death_ref_time = pygame.time.get_ticks()
        
        #animations, frames, images
        # animation_types = ['0', '1', '2', '3']
        
        # if frame_dict == None:#doesn't actually work 
        #     for animation in animation_types:
        #         temp_list = []
        #         frames = len(os.listdir(f'assets/sprites/enemies/{self.id_}/{animation}'))

        #         for i in range(frames):
        #             img = pygame.image.load(f'assets/sprites/enemies/{self.id_}/{animation}/{i}.png').convert_alpha()
                    
        #             iimg = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    
        #             temp_list.append(img)
        #         self.frame_dict.append(temp_list)
        # else:
        self.frame_dict = frame_dict
            
        self.action = 0
        self.image = self.frame_dict[0][0]#head
        self.image2 = self.frame_dict[1][0]#body
        self.body_img_list = [self.frame_dict[1][x%len(self.frame_dict[1])] for x in range(segments-1)]#body
        self.image3 = self.frame_dict[2][0]#bitng head
        self.image4 = self.frame_dict[4][0]#cracks
        self.frame_index = 0
        self.frame_index2 = 0
        self.frame_index3 = 0
        self.frame_index4 = 0
        self.flip = False
        self.v_flip = 0
        self.is_on_screen = False
        self.do_screenshake = False
        
        self.framerates = (
            (150,100,200),
            )
            
        #audio
        self.m_player = music_player(None, ini_vol)
        self.m_player.sfx = sfx_list_ext
        self.ini_vol = ini_vol
            
        #self.atk_rect_list = []    
        self.atk_rect = pygame.Rect(-32, -32, 0,0)
        self.atk_rect_scaled = pygame.Rect(-32, -32, 0,0)

        #will have a head sprite and body sprites, will use directories in tuples like (0,1) and (2,3)
        self.rect = self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height
        
        body_rect = self.image2.get_rect()
        self.body_dimensions = (0,0,body_rect.width,body_rect.height)
        self.rect.topleft = (x,y)
        self.head_img_rect = self.image.get_rect()
        self.head_img_rect.scale_by(1.5,1.5)
        self.hitbox_dim = (0,0,int(body_rect.width/1.2),int(body_rect.height/1.2))
        self.tail_hitbox_rect = pygame.rect.Rect(self.hitbox_dim)
        self.head_hitbox_rect = pygame.rect.Rect(self.hitbox_dim)
        
        self.pos_list = [list(self.rect.center)]*segments
        self.pos_list2 = []
        
        self.moving = False
        self.colliding = True
        self.rand_mvmt_ct = 0
        self.pathlist = [[self.rect.centerx + 4*random.randint(-self.width, self.width), self.rect.centery + 4*random.randint(-self.height, self.height)] for x in range(3)]
        self.angular_increment = 0
        
        self.hostile = False
        self.trig_once = False
        self.trig_once2 = False
        self.i_frames_en = False
        
        self.dying = False
        self.death_phase = 0
        
        self.shielded = False
        
        
    def check_if_onscreen(self):
        self.is_on_screen = (self.rect.x > -320 and self.rect.x < 640 + 320)
        return self.is_on_screen
    
    def check_if_in_simulation_range(self, adjustment):
        return (self.rect.x > - (320 + adjustment) and self.rect.right < 640 + (320 + adjustment))
        
    def update_pos_list(self, speed):
        if self.moving and pygame.time.get_ticks() > self.pos_ref_time + 60 - speed:
            self.pos_list.append([self.rect.centerx + int(m.cos(self.angular_increment)*self.height//4), self.rect.centery + int(m.sin(self.angular_increment)*self.height//4)])
            self.pos_list.pop(0)
            self.pos_ref_time = pygame.time.get_ticks()
            
    def lin_accelerate(self, limit, speed, increment):
        if limit < 0:
            increment *= -1
        
        if abs(speed) < abs(limit):
            speed += increment
        else:
            speed = limit
        
        return speed
    
    def update_tail_sprite(self):
        #change tail sprite overlay
        dmg_states = len(self.frame_dict[4])
        for i in range(dmg_states):
            if self.hits_tanked >= int(self.hp*(i/dmg_states)) and i > self.frame_index4:
                self.frame_index4 = i
                self.image4 = self.frame_dict[4][self.frame_index4]
    
    def take_dmg(self, player_action):
        dmg_dict = {
            7: 2,
            8: 2,
            10: 4,
            16: 4,
            24: 2
        }
        self.hits_tanked += dmg_dict[player_action]
        
    def explode(self, sp_group_list):
        particle_name = self.id_ + '_death'
        sp_group_list[3].sprite.add_particle(particle_name, self.rect.centerx, self.rect.centery, self.direction, self.scale, False, 0)
            
    def move(self, player, world_solids, scrollx, sp_group_list):
        player_rect = player.hitbox_rect
        player_atk_rect = player.atk_rect_scaled
        player_action = player.action
        player_direction = player.direction
        
        
        dx = 0
        dy = 0
        d = self.width//2
        speed = self.speed
        if self.death_phase < 1:
            self.update_pos_list(speed)

        self.head_hitbox_rect.center = self.rect.center
        self.tail_hitbox_rect.center = self.pos_list[0]
        
        if self.i_frames_en and pygame.time.get_ticks() > self.i_frames_time + 2000:
            self.i_frames_en = False
            
        if self.hits_tanked >= self.hp and not self.dying: #dying
            self.death_ref_time = pygame.time.get_ticks()
            self.atk_rect_scaled = pygame.rect.Rect(-32,-32,0,0)
            self.dying = True
            self.m_player.play_sound(self.m_player.sfx[8], (self.rect.centerx, self.rect.centery, None, None))
            for i in range(3):
                sp_group_list[12].add(Item('Cursed Flesh', self.rect.centerx + random.randint(-d,d), self.rect.centery + random.randint(-d,d), 1, False))
            
            update_time = pygame.time.get_ticks()
            for i in range(20):
                sp_group_list[5].sprite.add_particle('player_bullet_explosion', 
                                                                    self.tail_hitbox_rect.centerx+random.randrange(-2*d,2*d), self.tail_hitbox_rect.centery+random.randrange(-2*d,2*d), 
                                                                    -self.direction, self.scale, False, random.randrange(0,3), update_time)
            for pos in self.pos_list:
                spread = 8
                self.pos_list2.append([pos[0] - scrollx + random.randint(-spread*self.width,spread*self.width), pos[1] + random.randint(-spread*self.height,spread*self.height)])
            
                
            
        if self.dying: #true death
            if self.death_ref_time + 1000 < pygame.time.get_ticks():
                self.death_phase += 1
                self.death_ref_time = pygame.time.get_ticks()
                
            if self.death_phase == 3:
                self.m_player.play_sound(self.m_player.sfx[3], (self.rect.centerx, self.rect.centery, None, None))
                self.explode(sp_group_list)
                self.m_player.play_sound(self.m_player.sfx[0], (self.rect.centerx, self.rect.centery, None, None))
                self.Alive = False
                self.kill()
            
        #self.head_img_rect.center = self.rect.center
        if self.angular_increment <= 2*m.pi:
            self.angular_increment += 0.12
        else:
            self.angular_increment = 0
        
        self.moving = True
        
        
        
        #movement
        # #tile collisions
        # self.colliding = False
        # for tile in [tile for tile in world_solids 
        #                 if tile[1].x > -224 and tile[1].x < 864 and 
        #                     tile[1].bottom < self.rect.bottom + 64 and tile[1].y > self.rect.y - 64 or
        #                     (tile[1].bottom > self.rect.bottom and tile[1].y < self.rect.y)
        #             ]:
        #     if tile[1].colliderect(self.rect):
        #         self.colliding = True
        #         self.pathlist[0] = list(tile[1].center)
                
        
        if not self.dying:
            #self.tail_hitbox_rect.center = self.pos_list[0]
            if self.hits_tanked > 0 and pygame.time.get_ticks()%(5-self.frame_index4) == 0:
                #for i in range(1+self.frame_index4):
                sp_group_list[5].sprite.add_particle('player_bullet_explosion', 
                                                                self.tail_hitbox_rect.centerx+random.randrange(-d,d), self.tail_hitbox_rect.centery+random.randrange(-d,d), 
                                                                -self.direction, self.scale*0.3, False, random.randrange(0,3))
            
            #target player
            if self.hostile:
                self.pathlist[0] = [player_rect.centerx -scrollx, player_rect.centery]
                if not self.dying:
                    self.atk_rect_scaled = pygame.rect.Rect(self.rect.centerx - self.flip*self.width//2, self.rect.y, self.width//2, self.height)
                self.rand_mvmt_ct = -1
                speed = int(self.speed * 2.5)
            else:
                pester_dist = int(m.sqrt((self.rect.centerx - player_rect.centerx)**2 + (self.rect.centery - player_rect.centery)**2))
                if pester_dist > 640:
                    self.pathlist.append([player_rect.centerx - scrollx + random.randint(-4*self.width,4*self.width), 
                                        player_rect.centery + random.randint(-4*self.height,4*self.height)]
                                        )
                    self.pathlist.pop(0)
                
                
                if pester_dist > self.width*5:
                    speed = self.speed + int(10*(self.width/pester_dist)*self.speed)
                else:
                    speed = self.speed
                
                self.atk_rect_scaled = pygame.rect.Rect(-32,-32,0,0)
            
            if self.rect.centerx < self.pathlist[0][0] - self.width//4:
                self.speed_x = self.lin_accelerate(speed, self.speed_x, 0.1)
                dx += self.speed_x
            elif self.rect.centerx > self.pathlist[0][0] + self.width//4:
                self.speed_x = self.lin_accelerate(-speed, self.speed_x, 0.1)
                dx += self.speed_x
            if self.rect.centery < self.pathlist[0][1] - self.height//4:
                self.speed_y = self.lin_accelerate(speed, self.speed_y, 0.1)
                dy += self.speed_y
            elif self.rect.centery > self.pathlist[0][1] + self.height//4:
                self.speed_y = self.lin_accelerate(-speed, self.speed_y, 0.1)
                dy += self.speed_y
            
            #random movement logic once the head gets close enough
            if (self.rect.centerx in range(self.pathlist[0][0] - self.width//2, self.pathlist[0][0] + self.width//2) and 
                self.rect.centery in range(self.pathlist[0][1] - self.height//2, self.pathlist[0][1] + self.height//2)
                ):
                #if not self.colliding:
                if self.rand_mvmt_ct < len(self.pathlist) + 1:
                    self.rand_mvmt_ct += 1
                else:
                    self.rand_mvmt_ct = 0
                    
                if self.hostile and player_action not in (9,7,8,10,16,18):
                    self.rand_mvmt_ct = 0
                    if self.hostile:
                        self.m_player.play_sound(self.m_player.sfx[9], (self.rect.centerx, self.rect.centery, None, None))
                    self.hostile = False
                    #print("gottem")
                    self.pathlist[0] = [player_rect.centerx - scrollx + player_direction*8*self.height, 
                                            player_rect.centery + random.randint(-8*self.height,8*self.height)]
                                            
                else:
                    self.pathlist.append([player_rect.centerx - scrollx + random.randint(-4*self.width,4*self.width), 
                                        player_rect.centery + random.randint(-4*self.height,4*self.height)]
                                        )
                    self.pathlist.pop(0)
                
            #player collisions
            #trigger attack if player attacks close to end of tail
            if player_atk_rect.width != 0:
                #trigger hostility
                if (not self.rect.colliderect(player_atk_rect) and
                    player_atk_rect.centerx in range(self.pos_list[0][0] - 2*self.width, self.pos_list[0][0] + 2*self.width) and
                    player_atk_rect.centery in range(self.pos_list[0][1] - 2*self.height, self.pos_list[0][1] + 2*self.height)
                    ):
                    self.hostile = True
                    #self.rand_mvmt_ct = len(self.pathlist) + 1
                    
                #hitting tail
                hitting_tail = False
                #self.tail_hitbox_rect.center = self.pos_list[0]
                if self.tail_hitbox_rect.colliderect(player_atk_rect):
                    if not self.i_frames_en:
                        hitting_tail = True
                        x_avg = (self.tail_hitbox_rect.centerx + player_atk_rect.centerx)//2
                        y_avg = (self.tail_hitbox_rect.centery + player_atk_rect.centery)//2
                        sp_group_list[5].sprite.add_particle('player_impact', x_avg, y_avg, -self.direction, self.scale*1.05, True, random.randint(0,2))
                        dx = 0
                        dy = 0
                        #self.m_player.play_sound(self.m_player.sfx[3], (self.rect.centerx, self.rect.centery, None, None))
                        self.m_player.play_sound(self.m_player.sfx[2], (self.rect.centerx, self.rect.centery, None, None))
                        self.m_player.play_sound(self.m_player.sfx[1], (self.rect.centerx, self.rect.centery, None, None))
                        self.take_dmg(player_action)
                        self.update_tail_sprite()
                        self.i_frames_time = pygame.time.get_ticks()
                        self.i_frames_en = True
                
                #hitting head
                if self.head_hitbox_rect.colliderect(player_atk_rect):
                    
                    if not self.trig_once:
                        update_time = pygame.time.get_ticks()
                        for i in range(4):
                            sp_group_list[5].sprite.add_particle('player_bullet_explosion', 
                                                                self.rect.centerx+random.randrange(-d,d), self.rect.centery+random.randrange(-d,d), 
                                                                -self.direction, self.scale, False, random.randrange(0,3), update_time)
                        self.m_player.play_sound(self.m_player.sfx[4], (self.rect.centerx, self.rect.centery, None, None))
                        self.trig_once = True
                        
                    self.hostile = False
                    if self.rand_mvmt_ct < 0:#player is bitten
                        dx = -dx
                        dy = -dy
                        self.pathlist[0] = [player_rect.centerx - scrollx + player_direction*8*self.height, 
                                            player_rect.centery + random.randint(-8*self.height,8*self.height)]
                        self.rand_mvmt_ct = 0
                else:
                    self.trig_once = False
                    
                    
                #hitting body
                for pos in self.pos_list[1:]: #-1 at end to exclude last one
                    temp_rect = pygame.rect.Rect(self.hitbox_dim)
                    temp_rect.center = pos
                    if not self.trig_once2 and temp_rect.colliderect(player_atk_rect) and not self.trig_once and not hitting_tail:
                        self.m_player.play_sound(self.m_player.sfx[7], (self.rect.centerx, self.rect.centery, None, None))
                        update_time = pygame.time.get_ticks()
                        for i in range(5):
                            sp_group_list[5].sprite.add_particle('stone_breaking', temp_rect.centerx+random.randrange(-2*d,2*d), temp_rect.centery+random.randrange(-2*d,2*d), -self.direction, self.scale*0.5, False, random.randrange(0,3), update_time)
                        self.trig_once2 = True
            else:
                self.trig_once2 = False 
                
            #bullet collisions
            for bullet in sp_group_list[2]:
                if bullet.rect.colliderect(self.tail_hitbox_rect):
                    sp_group_list[5].sprite.add_particle('stone_breaking', 
                                                         self.tail_hitbox_rect.centerx+random.randrange(-2*d,2*d), 
                                                         self.tail_hitbox_rect.centery+random.randrange(-2*d,2*d), -
                                                         self.direction, self.scale*0.5, False, random.randrange(0,3))
                if bullet.rect.colliderect(self.rect):
                    sp_group_list[5].sprite.add_particle('stone_breaking', 
                                                         self.rect.centerx+random.randrange(-2*d,2*d), 
                                                         self.rect.centery+random.randrange(-2*d,2*d), 
                                                         -self.direction, self.scale*0.5, False, random.randrange(0,3))
                    
                for pos in self.pos_list[1:]: #-1 at end to exclude last one
                    temp_rect = pygame.rect.Rect(self.hitbox_dim)
                    temp_rect.center = pos
                    if bullet.rect.colliderect(temp_rect):
                        sp_group_list[5].sprite.add_particle('stone_breaking', 
                                                             temp_rect.centerx+random.randrange(-2*d,2*d), 
                                                             temp_rect.centery+random.randrange(-2*d,2*d), 
                                                             -self.direction, self.scale*0.5, False, random.randrange(0,3))
                
            
        elif self.death_phase < 3:
            self.hostile = True
            speed = 5*self.speed - self.death_phase
            for pos in self.pos_list2:
                pos[0] -= (scrollx)
            for tup in enumerate(self.pos_list):
                i = tup[0]
                
                if self.pos_list[i][0] not in range(self.pos_list2[i][0] - 2*speed, self.pos_list2[i][0] + 2*speed):
                    if tup[1][0] < self.pos_list2[i][0]:
                        self.pos_list[i][0] += speed
                        dx += self.speed
                    elif tup[1][0] > self.pos_list2[i][0]:
                        self.pos_list[i][0] -= speed
                        dx -= self.speed
                        
                if self.death_phase < 1:
                    if pygame.time.get_ticks()%20 == 0:
                        sp_group_list[4].sprite.add_particle('bloom', 
                                                             self.pos_list[i][0] + random.randrange(-speed, speed), 
                                                             self.pos_list[i][1] + random.randrange(-speed, speed), 
                                                             self.direction, self.scale*0.4, False, 0)
                elif self.death_phase == 1:   
                    if self.pos_list[i][1] not in range(self.pos_list2[i][1] - 2*speed, self.pos_list2[i][1] + 2*speed):
                        if tup[1][1] < self.pos_list2[i][1]:
                            self.pos_list[i][1] += 2*speed
                            #self.rect.y += self.speed//2
                        elif tup[1][1] > self.pos_list2[i][1]:
                            self.pos_list[i][1] -= 2*speed
                            #self.rect.y -= self.speed//2
                    else:
                        self.death_phase += 1
                elif self.death_phase > 1:      
                    self.pos_list[i][1] += speed//2
                    dy = random.randint(-1,1)*self.speed
                    dx = random.randint(-1,1)*self.speed//2
    
            
    
        #set direction
        if dx < 0:
            self.flip = True
            self.direction = -1
        else:
            self.flip = False
            self.direction = 1
                
        #normalize diagonal motion
        absx = abs(dx)
        absy = abs(dy)
        if (dx != 0) and (dy != 0):
            dist = m.sqrt(absx + absy)
            dx = dx/absx * dist
            dy = dy/absy * dist
        
        #set v_flip
        if absy > absx and dy != 0:
            if dy > 0:
                self.v_flip = -90
            else:
                self.v_flip = 90
        else:
            self.v_flip = 0
        
        self.atk_rect_scaled.x += (dx - scrollx)
        self.rect.centerx += (dx - scrollx)
        
        #scrolling body and paths
        for pos in self.pos_list:
            pos[0] -= (scrollx)
            
        for pos in self.pathlist:
            pos[0] -= (scrollx)
        
        
        self.rect.centery += dy
        
    def force_ini_position(self, scrollx):
        self.rect.x -= scrollx
        for pos in self.pos_list:
            pos[0] -= (scrollx)
    
    def draw_body(self, screen):
        for tup in enumerate(self.pos_list[1:]): #-1 at end to exclude last one
            temp_rect = pygame.rect.Rect(self.body_dimensions)
            temp_rect.center = tup[1]
            screen.blit(pygame.transform.rotate(pygame.transform.flip(self.body_img_list[tup[0]], self.flip, False), self.v_flip), temp_rect)
            
        if not self.dying:
            temp_rect2 = pygame.rect.Rect(self.body_dimensions)
            temp_rect2.center = self.pos_list[0]
            if self.i_frames_en:
                if pygame.time.get_ticks()%3 == 0:
                    screen.blit(pygame.transform.flip(self.image3, self.flip, False), temp_rect2)
                    screen.blit(pygame.transform.flip(self.image4, self.flip, False), temp_rect2)
            else:
                screen.blit(pygame.transform.flip(self.image3, self.flip, False), temp_rect2)
                screen.blit(pygame.transform.flip(self.image4, self.flip, False), temp_rect2)

        if self.hostile:
            rect = self.rect
        else:
            rect = pygame.rect.Rect((0,0), (self.width, self.height))
            rect.center = self.pos_list[-1]
        screen.blit(pygame.transform.flip(pygame.transform.rotate(self.image, self.v_flip), self.flip, False), rect)
        
    def draw(self, screen):
        #self.animate()
        if self.check_if_onscreen():
            if self.inundated and self.frame_index < 1:
                if pygame.time.get_ticks()%5 != 0:
                    self.draw_body(screen)
            else:
                self.draw_body(screen)
        #pygame.draw.rect(screen, (255,0,0), self.atk_rect_scaled)
    
    def animate(self, sp_group_list, player_rect):
        self.mask = pygame.mask.from_surface(self.image)
        
        #animating head
        self.image = self.frame_dict[3*self.action + 3*self.hostile][self.frame_index]
        
        if pygame.time.get_ticks() - self.update_time > self.framerates[self.action][0] - self.hostile * 80:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            
        if self.frame_index >= len(self.frame_dict[3*self.action]):
            self.frame_index = 0
            if self.hostile:
                self.m_player.play_sound(self.m_player.sfx[6], (self.rect.centerx, self.rect.centery, None, None))
        
        #animating body
        self.body_img_list.append(self.frame_dict[3*self.action + 1][self.frame_index2])
        self.body_img_list.pop(0)
        
        if pygame.time.get_ticks() - self.update_time2 > self.framerates[self.action][1]:
            self.update_time2 = pygame.time.get_ticks()
            self.frame_index2 += 1
            
        if self.frame_index2 >= len(self.frame_dict[3*self.action + 1]):
            self.frame_index2 = 0
            
        #animating tail
        self.image3 = self.frame_dict[3*self.action + 2][self.frame_index3]
        
        if pygame.time.get_ticks() - self.update_time3 > self.framerates[self.action][2]:
            self.update_time3 = pygame.time.get_ticks()
            self.frame_index3 += 1
            
        if self.frame_index3 >= len(self.frame_dict[3*self.action + 2]):
            self.frame_index3 = 0