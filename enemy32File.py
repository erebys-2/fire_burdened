import pygame
import os
#from game_window import sprite_group
from bullet import bullet_ #type: ignore
#print('directory: ' + os.getcwd())
from music_player import music_player #type: ignore
from ItemFile import Item #type: ignore
#from combat_vfx import combat_vfx
import random
import math
from geometry import geometry
from healthbars import health_bar


class enemy_32wide(pygame.sprite.Sprite): #Generic enemy class for simple enemies
    #constructors
    def __init__(self, x, y, speed, scale, id_, enemy0_order_id, ini_vol, frame_dict, sfx_list_ext):
        pygame.sprite.Sprite.__init__(self)

        #self.m_player.set_sound_vol(self.m_player.sfx[0], 7) #looks like you can adjust vol in the constructor

        self.spawn_order_id = enemy0_order_id
        
        self.Alive = True
        self.action = 0
        self.scale = scale

        self.inundated = False
        self.speed = speed
        self.slower_speed = speed - 1
        self.direction = -1
        self.vertical_direction = 0
        self.flip = False
        self.recoil = 42
        self.recoil_slow = 3
        self.speed_boost = 1
        self.recovering = False

        self.vel_y = 0
        self.in_air = True
        self.jump = False
        self.jump_counter = 0
        self.on_ground = False
        self.hit_ground = False
        
        self.hp = 6 #how many hits can he take
        self.dead = False
        self.hits_tanked = 0
        self.dmg_multiplier = 0
        self.rando_frame = 0
        
        self.shoot = False
        self.shoot_done = False
        self.idle_counter = 0
        self.idle_bypass = False
        
        self.shielded = False
        self.player_atk_collided = False
        if '_v2' in id_:
            self.id_ = id_[:-3]
            self.shielded = True
        else:
            self.id_ = id_
            
        #animation_types = []
        self.frame_dict = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.update_time2 = pygame.time.get_ticks()
        self.getting_shot_delay = pygame.time.get_ticks()
        
        self.do_screenshake = False
        
        self.increment = 0
        
        self.fly_atk_ready = False
        self.fly_atk_finished = True
        self.fly_aimline_tgt = (-1,-1)
        
        self.theta = 0
        self.g = geometry()
        self.hp_bar = health_bar()

        #fill animation frames
        if self.id_ == 'dog':
            animation_types = ['0', '1', '2', '3']
            self.hp = 6
            self.recoil = 58
            self.recoil_slow = 2
            sfx_list = ['bassdrop2.mp3', 'hit.mp3', 'dog_hurt.mp3', 'woof.mp3', 'step2soft.mp3']
        elif self.id_ == 'shooter':   
            animation_types = ['0', '1', '2', '3', '4', '5'] 
            self.hp = 8
            self.recoil = 58
            self.recoil_slow = 2
            sfx_list = ['bassdrop2.mp3', 'hit.mp3', 'roblox2.mp3', 'shoot.mp3', 'step2soft.mp3']
            #, '', 'bite.mp3', 'bee.mp3'
        elif self.id_ == 'fly':
            animation_types = ['0', '1', '2', '3']
            self.hp = 4
            self.recoil = 43
            self.recoil_slow = 3
            sfx_list = ['bassdrop2.mp3', 'hit.mp3', 'bee_hurt.mp3', 'bee.mp3', 'step2soft.mp3', 'shoot.mp3']
        elif self.id_ == 'walker':
            animation_types = ['0', '1', '2']
            self.action = 1
            self.hp = 6
            self.recoil = 54
            self.recoil_slow = 2
            sfx_list = ['bassdrop2.mp3', 'hit.mp3', 'cough.mp3', 'bite.mp3', 'step2soft.mp3']
            
        self.m_player = music_player(None, ini_vol)
        self.m_player.sfx = sfx_list_ext
        self.ini_vol = ini_vol
        self.heavy_recoil = False
        

        # if frame_dict == None:
        #     base_path = os.path.join('assets', 'sprites', 'enemies', self.id)
        #     for animation in animation_types:
        #         temp_list = []
        #         base_path2 = os.listdir(os.path.join(base_path, animation))
        #         frames = len(base_path2)#f'assets/sprites/enemies/{self.id}/{animation}'))

        #         for i in range(frames):
        #             img = pygame.image.load(os.path.join(base_path2, f'{i}.png')).convert_alpha()
        #             img = pygame.transform.hsl(img, 11, 0.3, 0.1)
        #             if animation == '2' and i < 2:
        #                 img = pygame.transform.scale(img, (int(img.get_width() * 0.5 * scale), int(img.get_height() * 1.2 * scale)))
        #             else:
        #                 img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    
        #             temp_list.append(img)
        #         self.frame_dict(temp_list)
        # else:
        self.frame_dict = frame_dict

        self.image = self.frame_dict[self.action][self.frame_index]
        self.mask = pygame.mask.from_surface(self.image)
        if self.id_ != 'fly':
            self.rect = self.image.get_rect()
        else:
            self.rect = self.image.get_bounding_rect()
        self.rect.topleft = (x,y)
        self.ini_y = self.rect.centery
        self.atk_rect = pygame.Rect(-32, -32, 0,0)
        self.atk_rect_scaled = pygame.Rect(-32, -32, 0,0)#self.atk_rect.scale_by(0.8)
        
        self.width = self.rect.width
        self.half_width = self.width//2
        self.quarter_width = self.half_width//2
        self.height = self.rect.height
        self.half_height = self.height//2
        self.quarter_height = self.half_width//2
        
        self.is_on_screen = False
        
        self.pos_list = []
        
        

    #methods----------------------------------------------------------------------------------------
    
    def check_if_onscreen(self):
        self.is_on_screen = (self.rect.x > -self.rect.width and self.rect.x < 640)
        return self.is_on_screen
    
    def check_if_in_simulation_range(self, adjustment):
        return (self.rect.x > - (160 + adjustment) and self.rect.right < 640 + (160 + adjustment))
    
    def atk1_kill_hitbox(self):
        self.atk_rect.x = 0
        self.atk_rect.y = 0
        self.atk_rect.width = 0
        self.atk_rect.height = 0
        self.atk_rect_scaled = self.atk_rect
        
    def do_p_int_group_collisions(self, p_int_group, dx, dy):
        for p_int in [p_int for p_int in p_int_group if p_int.rect.x > -160 and p_int.rect.x < 800]:
            if p_int.collision_and_hostility[p_int.id_][0]:
                if (p_int.rect.colliderect(self.rect.x+2, self.rect.y + dy, self.width-4, self.height) and self.action != 2):
                    if self.rect.bottom >= p_int.rect.top and self.rect.bottom <= p_int.rect.y + 32:
                        self.in_air = False
                        self.vel_y = 0.5
                        self.on_ground = True
                        dy = p_int.vel_y
                        dx += p_int.vel_x
                        if self.rect.bottom != p_int.rect.top:
                            dy -= self.rect.bottom- p_int.rect.top
                        self.speed_boost = 0.2
                    elif self.rect.top <= p_int.rect.bottom and self.rect.top >= p_int.rect.y + 32 and p_int.vel_y >= 0:
                        dy = p_int.vel_y
                        self.vel_y = 0.5
                    else:
                        self.in_air = True

                if (p_int.rect.colliderect(self.rect.x + dx, self.rect.y+2, self.width, self.height-2)):
                    if self.rect.x > p_int.rect.x and self.rect.right < p_int.rect.right:
                        dx = 0
                    else:
                        dx = -dx + p_int.vel_x
                        
                    if self.id_ == 'walker' and not self.inundated:
                        self.direction = -self.direction
                        self.flip = not self.flip
                        dx = self.direction*8
 
                    
            #taking damage from crushing traps
            if p_int.collision_and_hostility[p_int.id_][1]:
                rate = self.hp//3
                if (self.rect.colliderect(p_int.atk_rect)):
                    if self.hits_tanked + rate > self.hp:
                        self.hits_tanked = self.hp
                    else:
                        self.hits_tanked += rate
        return (dx,dy)
        
    def move(self, player, world_solids, scrollx, sp_group_list):
        player_rect = player.hitbox_rect
        p_rect_shifted_centerx = player.rect.centerx + player.direction*int(2.5*self.width) + 32
        player_atk_rect = player.atk_rect_scaled
        player_action = player.action
        player_direction = player.direction
        player_mvmt = (player.dx, player.dy)
        
        
        dx = 0
        dy = 0
        moving = False
        
        if self.check_if_in_simulation_range(-40):
            # if self.vel_y == 0:
            #     self.vertical_direction = 0
            if self.vel_y <= 0:
                self.vertical_direction = 1
            elif self.vel_y > 0:
                self.vertical_direction = -1
            
            # if player is within left range, or right range
            if self.inundated == False:# and self.check_if_in_simulation_range():
                #enemy id_ specific behaviors--------------------------------------------------------------------------------------
                if self.id_ == 'dog':
                    chase_range = 1.5
                    if player_rect.y > self.rect.y - 2*chase_range*self.height and  player_rect.y < self.rect.y + self.height + 2*chase_range*self.height:
                        if player_rect.x > self.rect.x - 5*32 and player_rect.x <= self.rect.x:
                            dx = -self.speed *self.speed_boost
                            self.direction = -1
                            moving = True
                            
                        elif player_rect.x < self.rect.x + self.width + 5*32 and player_rect.x >= self.rect.x:
                            dx = self.speed *self.speed_boost
                            self.direction = 1
                            moving = True
                            


                    if player_rect.centerx > self.rect.x and player_rect.centerx < self.rect.right:
                        self.direction = 0
                        
                    
                    if self.action == 1 and not self.inundated: #when the dog is running it has an attack hitbox
                        if self.direction == -1:
                            self.atk_rect = pygame.Rect(self.rect.x, self.rect.y + 16, self.half_width, self.height - 32)
                        elif self.direction == 1:
                            self.atk_rect = pygame.Rect(self.rect.x + self.half_width - 8, self.rect.y + 16, self.half_width, self.height - 32)
                        else:
                            self.atk_rect.centerx = self.rect.centerx
                            self.atk_rect.centery = self.rect.centery
                        self.atk_rect_scaled = self.atk_rect
                    else:
                        self.atk1_kill_hitbox()
                    
                    if self.speed_boost != 1:
                        self.speed_boost = 1
                        sp_group_list[3].sprite.add_particle('player_mvmt', self.rect.centerx, self.rect.centery, -self.direction, self.scale, True, 1)
                        self.in_air = True
                        self.vel_y = -8
                        
                        
                elif self.id_ == 'shooter':
                    #always face the player
                    
                    if player_rect.centerx >= self.rect.left and player_rect.centerx <= self.rect.right:
                        self.flip = self.flip
                        self.direction = self.direction
                    else:
                        if player_rect.centerx > self.rect.right:
                            self.direction = 1
                            self.flip = True
                        elif player_rect.centerx < self.rect.left:
                            self.direction = -1
                            self.flip = False

                    
                    #shoot when the player is in range
                    shoot_range = 7
                    if (((player_rect.x > self.rect.x - shoot_range*self.width  - scrollx 
                        and player_rect.x < self.rect.x + self.width + shoot_range*self.width  - scrollx)
                        and (self.rect.bottom >= player_rect.y - 8 and self.rect.y < player_rect.bottom + 8))
                        #or (self.frame_index < 4 and self.shoot == True)
                        ):
                        self.shoot = True
                        #print("hi")
                    
                    
                    #recoil from shooting
                    if self.action == 4 and self.frame_index == 3:
                        dx = self.direction * -1
                    
                    if self.inundated == False: #cannot move towards player when inundated
                        #move if the player gets too close
                        chase_range = 1.4
                    
                        if player_rect.x > self.rect.x - chase_range*self.width and player_rect.x <= self.rect.x:
                            dx = -self.speed
                            moving = True
                        elif player_rect.x < self.rect.x + self.width + chase_range*self.width and player_rect.x >= self.rect.x:
                            dx = self.speed
                            moving = True
                        #jump if the player is within this range
                        jump_range = 1.6
                        if self.rect.top <= player_rect.top:
                            if player_rect.x > self.rect.x - (jump_range*self.width) and player_rect.x <= self.rect.x:
                                self.jump = True
                            elif player_rect.x < self.rect.x + self.width + (jump_range*self.width) and player_rect.x >= self.rect.x:
                                self.jump = True
                                
                        if self.action == 5 and not self.inundated and self.vel_y > 0: #when the shooter is jumping it has an attack hitbox
                            self.atk_rect = pygame.Rect(self.rect.x, self.rect.y + self.half_height, self.width, self.half_height)
                            self.atk_rect_scaled = self.atk_rect.scale_by(0.8)
                        else:
                            self.atk1_kill_hitbox()

                    
                        
                    jump_cooldown = 720
                    if (self.jump and self.in_air == False and self.on_ground and (pygame.time.get_ticks() - self.update_time2 > jump_cooldown)):
                        self.update_time2 = pygame.time.get_ticks()
                        # if self.hit_ground:
                        #     enemy_bullet = bullet_(self.rect.x - 64, self.rect.y, 0, self.direction, self.scale, 'ground_impact', self.ini_vol)
                        #     #self.m_player.play_sound (self.m_player.sfx[3])
                        #     sp_group_list[7].add(enemy_bullet)
                        #     self.hit_ground = False
                        sp_group_list[3].sprite.add_particle('player_mvmt', self.rect.centerx, self.rect.centery, -self.direction, self.scale, True, 1, self.update_time2)
                        self.vel_y = -8.5
                        self.in_air = True
                        
                    
                elif self.id_ == 'fly':
                    #print(self.action)
                    self.fly_aimline_tgt = (-1,-1)
                    x_in_range = False
                    y_in_range = False
                    if self.inundated == False: #cannot move towards player when inundated
                        #move if the player gets too close
                        chase_range = 3
                        atk_range = 1.2
                        
                        #move towards player until threshold
                        if p_rect_shifted_centerx + atk_range*self.width > self.rect.centerx - chase_range*self.width and p_rect_shifted_centerx + atk_range*self.width < self.rect.centerx:
                            dx = -self.speed
                            self.direction = -1
                            self.flip = False
                            #self.vel_y = 0
                        elif p_rect_shifted_centerx - atk_range*self.width < self.rect.centerx + chase_range*self.width and p_rect_shifted_centerx - atk_range*self.width > self.rect.centerx:
                            dx = self.speed
                            self.direction = 1
                            self.flip = True
                            #self.vel_y = 0
                        #go back and forth in threshold
                        elif p_rect_shifted_centerx + atk_range*self.width >= self.rect.centerx and p_rect_shifted_centerx - atk_range*self.width <= self.rect.centerx:
                            moving = True
                            x_in_range = True
                            if self.direction == 1:
                                dx = self.speed
                            elif self.direction == -1:
                                dx = -self.speed
                            
                        low = 1
                        high = 2.1
                        if p_rect_shifted_centerx + 6*self.width >= self.rect.centerx and p_rect_shifted_centerx - 6*self.width <= self.rect.centerx:
                        #hover above player when in the above range
                            #rise
                            if player_rect.centery - low*self.width > self.rect.centery - 3*chase_range*self.width and player_rect.centery - low*self.width < self.rect.centery:
                                self.vel_y = -self.speed
                            #fall
                            elif player_rect.centery - high*self.width < self.rect.centery + 3*chase_range*self.width and player_rect.centery - high*self.width > self.rect.centery:
                                self.vel_y = self.speed
                            #hover
                            elif player_rect.centery - low*self.width >= self.rect.centery and player_rect.centery - high*self.width <= self.rect.centery:
                                if self.vel_y <= 0:
                                    self.vel_y = -1.1*self.speed
                                elif self.vel_y > 0:
                                    self.vel_y = 1.1*self.speed
                                y_in_range = True
                                self.vel_y *= 0.5
                                
                                if self.action == 4 and self.frame_index <= 6:
                                    
                                    dx *= 0.4
                                    if self.frame_index in range(2,6):
                                        self.fly_aimline_tgt = player_rect.midtop
                                        s = 24
                                        if pygame.time.get_ticks()%6 != 0:
                                            sp_group_list[4].sprite.add_particle('bloom_orange', self.rect.centerx + random.randrange(-s,s), self.rect.centery+16 + random.randrange(-s,s), -self.direction, self.scale/4, True, -1)
                                            sp_group_list[4].sprite.add_particle('bloom_yellow', self.rect.centerx + random.randrange(-s,s), self.rect.centery+16 + random.randrange(-s,s), -self.direction, self.scale/4, True, -1)
                                        
                                # else:
                                #     dx += random.randrange(-2,2)
                                    
                            if self.action == 4 and self.frame_index <= 6:
                                self.theta = self.g.get_angle_from_pts(self.rect.center, player.rect.center)
                        else:   
                            self.vel_y = 0

                    self.fly_atk_ready = y_in_range and x_in_range
                    # if self.fly_atk_ready:
                    #     print('attacking')
                            
                    if not self.inundated and self.action == 1:
                        if self.direction == -1:
                            self.atk_rect = pygame.Rect(self.rect.x + self.quarter_height//2, self.rect.y + self.quarter_height, self.half_width, self.half_height)
                        elif self.direction == 1:
                            self.atk_rect = pygame.Rect(self.rect.x + self.half_width - self.quarter_height//2, self.rect.y + self.quarter_height, self.half_width, self.half_height)
                        self.atk_rect_scaled = self.atk_rect
                        
                        if self.vel_y == 0:
                            self.vel_y += 1
                    else:
                        self.atk1_kill_hitbox()
                        
                    if self.action == 0 and not moving:
                        self.vel_y = 0
                        self.rect.centery = self.ini_y - 9*math.sin(self.increment)

                        if self.increment > 2*math.pi:
                            self.rect.centery = self.ini_y
                            self.increment = 0
                            
                        self.increment += math.pi/24
                    else:
                        self.ini_y = self.rect.centery
                        
                        
                elif self.id_ in 'walker':
                    self.moving = True
                    dx = self.direction * self.speed
        
                    if self.direction == -1:
                        self.atk_rect = pygame.Rect(self.rect.x + 4, self.rect.y + 16, self.half_width - 8, self.half_height)
                    elif self.direction == 1:
                        self.atk_rect = pygame.Rect(self.rect.x + self.half_width, self.rect.y + 16, self.half_width - 8, self.half_height)
                    self.atk_rect_scaled = self.atk_rect
                    # else:
                    #     self.moving = False
                    #     dx = -dx
                    #     self.atk1_kill_hitbox()
                        
                        
                
            
            else:
                moving = False
                self.atk1_kill_hitbox()
                
                
            if self.shielded:
                #for pt in self.g.get_radial_pts(self.width, self.rect.center, 6):
                if pygame.time.get_ticks()%10 == 0:
                    sp_group_list[4].sprite.add_particle('bloom_yellow_real', self.rect.centerx, self.rect.centery, -self.direction, self.scale/3, True, -1)
                    
                #sp_group_list[4].sprite.add_particle('bloom_blue', self.rect.centerx + random.randrange(-32,32), self.rect.centery + random.randrange(-8,8), -self.direction, self.scale/10, True, -1)
                sp_group_list[4].sprite.add_particle('char_yellow', self.rect.centerx + random.randrange(-32,32), self.rect.centery + random.randrange(-40,32), -self.direction, 1, True, -1)
    
                sp_group_list[4].sprite.add_particle('dust0', self.rect.centerx + random.randrange(-32,32), self.rect.centery + random.randrange(-32,32), -self.direction, 0.5, True, -1)
                if pygame.time.get_ticks()%5 == 0:
                    sp_group_list[5].sprite.add_particle('char_yellow', self.rect.centerx + random.randrange(-32,32), self.rect.centery + random.randrange(-40,32), -self.direction, 1, True, -1)
    
            
            #action tree-------------------------------------------------------------------------------------------------------------
            if self.hits_tanked < self.hp:#alive
                
                if self.inundated == True:
                    
                    self.update_action(2)
                    
                    if self.frame_index < 1:
                        dx = 0

                        # x_avg = (self.rect.centerx + player_atk_rect.centerx)/2
                        # y_avg = (self.rect.centery + player_atk_rect.centery)/2
                        sp_group_list[5].sprite.add_particle('player_bullet_explosion', self.rect.centerx+random.randrange(-48,48), self.rect.centery+random.randrange(-48,48), -self.direction, 0.2*self.scale, False, random.randrange(0,3))
                        sp_group_list[5].sprite.add_particle('player_bullet_explosion', self.rect.centerx+random.randrange(-32,32), self.rect.centery+random.randrange(-32,32), -self.direction, 0.5*self.scale, False, random.randrange(0,3))

                        #dy = 0
                    else:
                        dx += self.direction * self.recoil_slow
                    #dy-= 2
                    
                else:
                    # if self.recovering:
                    #     self.update_action(0)
                    if self.id_ == 'shooter' and self.shoot == True and (self.idle_counter == 1 or self.idle_bypass == True) and self.direction != 0:#2
                        if self.frame_index <= 4:
                            self.shoot = True
                        self.update_action(4)
                    elif self.jump == True:
                        self.update_action(5)
                    elif self.id_ == 'fly' and self.fly_atk_ready and self.fly_atk_finished and self.idle_counter == 1:
                        self.fly_atk_finished = False
                        self.update_action(4)
                    elif moving == True:
                        if self.id_ != 'fly':
                            self.update_action(1)
                        elif self.id_ == 'fly' and self.fly_atk_finished:
                            self.update_action(0)
                            
                        if dx < 0:
                            self.flip = False
                        else:
                            self.flip = True
                    else:
                        if self.id_ == 'fly' and self.fly_atk_finished:
                            self.update_action(0)
                        elif self.id_ != 'fly':
                            self.update_action(0)
            else:#dies
                self.dead = True
                
    
            
            #gravity 
            if self.id_ != 'fly':
                if self.Alive:# == True and self.check_if_in_simulation_range():  
                
                    g = 0.4
                    self.vel_y += g

                else:
                    self.vel_y = 0
            dy += self.vel_y
            
            #player collisions------------------------------------------------------------------------------------------------------------------
            
            if (player_atk_rect.width != 0 
                and player_atk_rect.centerx in range(self.rect.centerx - self.width, self.rect.centerx + self.width)
                and self.rect.colliderect(player_atk_rect)
                #and self.inundated == False
                ):
                #pygame.time.wait(8)
                if not self.shielded:
                #the average point in a collision between rects is literally just the average of the coords opposite respective corners of rects
                    self.direction = player_direction
                    dx += 2*player_mvmt[0] + player_direction * self.recoil
                    if self.in_air:# and self.id_ != 'fly':
                        #self.vel_y = 0
                        if 2*player_mvmt[1] <= 20:
                            dy = 2*player_mvmt[1]
                        else:
                            dy = 20
                x_avg = (self.rect.centerx + player_atk_rect.centerx)/2
                y_avg = (self.rect.centery + player_atk_rect.centery)/2
                self.shoot_done = True
                
                
                if self.rando_frame < 2:
                    self.rando_frame += 1
                else:
                    self.rando_frame = 0
        
                
                # if self.id_ == 'fly':
                #     dy += self.vertical_direction * self.recoil//2
                # else:
                #     dy += self.vel_y * 2
                self.pos_list.append(self.rect.topleft)
                
                
                
                
                if player_action ==  10 or player_action == 9:
                    self.dmg_multiplier = 6
                    self.heavy_recoil = True
                elif not self.shielded and  player_action == 16:
                    self.dmg_multiplier = 4
                    self.heavy_recoil = True
                elif not self.shielded and player_action in (7,8,24):
                    self.dmg_multiplier = 2
                    self.heavy_recoil = False
                #self.dmg_multiplier = 0
                
                particle_ct = 3
                if self.heavy_recoil:
                    particle_ct = 8
                    sfx_index = 5
                    p_update_time = pygame.time.get_ticks()
                    for i in range(particle_ct//2):
                        sp_group_list[5].sprite.add_particle('extra_dmg', self.rect.centerx+random.randrange(-48,48), y_avg+random.randrange(-48,48), -self.direction, 0.75*self.scale, False, random.randrange(0,2), p_update_time)
                    self.heavy_recoil = False
                    
                if self.dmg_multiplier > 0 and not self.inundated:
                    self.do_screenshake = True
                    self.m_player.play_sound(self.m_player.sfx[1], (self.rect.centerx, self.rect.centery, None, None))

                    sp_group_list[5].sprite.add_particle('player_impact', x_avg + dx/4, y_avg, -self.direction, self.scale*1.05, True, self.rando_frame)
                    self.inundated = True
                    
                if self.shielded and not self.player_atk_collided:
                    for i in range(5):
                        sp_group_list[4].sprite.add_particle('bloom_yellow_real', self.rect.centerx + random.randrange(-16,16), self.rect.centery + random.randrange(-16,16), -self.direction, 0.7, True, -1)
                    for pt in self.g.get_radial_pts(self.width*1.15, self.rect.center, 12, phi=self.rando_frame):
                        sp_group_list[4].sprite.add_particle('char_yellow', pt[0], pt[1], self.direction, 1, False, -1)
                        if self.id_ == 'walker' and self.hits_tanked + self.dmg_multiplier < self.hp:
                            self.m_player.play_sound(self.m_player.sfx[6], (self.rect.centerx, self.rect.centery, None, None))
                        
                    if player_action != 10 and player.frame_index >= 1:
                        player.take_damage(0.5, 100) 

                # self.shoot = False
                # self.shoot_done = True
                # self.idle_counter = -2
                # self.fly_atk_ready = False
                self.shoot_done = False
                self.player_atk_collided = True
                # for i in range(particle_ct):
                #     sp_group_list[5].sprite.add_particle('player_bullet_explosion', self.rect.centerx+random.randrange(-48,48), y_avg+random.randrange(-48,48), -self.direction, 0.3*self.scale, False, random.randrange(0,3))

                
                #pygame.time.delay(50)
                    
            elif (player_atk_rect.width == 0 and   
                player_rect.x > self.rect.x - 64 and player_rect.right < self.rect.right + 64 and
                    (self.rect.colliderect(player_rect.scale_by(0.2)) or (self.rect.x < player_rect.x and self.rect.right > player_rect.right ))
                    and self.id_ not in ('walker', 'fly')
                    and not self.inundated
                #and not (self.inundated or self.rect.colliderect(player_atk_rect))
                ):
                dx = -dx
                self.direction = 0
                if self.id_ == 'shooter':
                    self.jump = True
                    
                self.player_atk_collided = False
                
            elif player_action == 6 and self.rect.colliderect(player_rect):
                dx = 0
                self.player_atk_collided = False
            else:
                self.player_atk_collided = False
                
            if self.direction == 0 and player_action != 9:
                if self.flip:
                    self.direction = 1
                else:
                    self.direction = -1
            
            #enemy0 collisions
            for enemy0 in [enemy0 for enemy0 in sp_group_list[0] 
                        if enemy0.rect.x > -32 and enemy0.rect.x < 640 and
                            enemy0.rect.x > self.rect.x - 64 and enemy0.rect.right < self.rect.right + 64 and 
                            enemy0.rect.y > self.rect.y - 64 and enemy0.rect.bottom < self.rect.bottom + 64 or
                            (enemy0.rect.bottom > self.rect.bottom and enemy0.rect.y < self.rect.y) or
                            (enemy0.rect.right > self.rect.bottom and enemy0.rect.x < self.rect.x)
                        ]:
                if self.spawn_order_id != enemy0.spawn_order_id and self.rect.colliderect(enemy0.rect):

                    if self.spawn_order_id < enemy0.spawn_order_id:
                        dx += -self.direction * 2
                    else:
                        dx += self.direction * 2

            
            if self.id_ != 'fly':
                dxdy = self.do_p_int_group_collisions(sp_group_list[8], dx, dy)
                dx = dxdy[0]
                dy = dxdy[1]
                
            #bullet collisions =====================================================================
            direction = 0
            if player.rect.centerx < self.rect.centerx:
                direction = 1
            elif player.rect.centerx > self.rect.centerx:
                direction = -1
            #this is fucked, look into collide rect
            if (pygame.sprite.spritecollide(self, sp_group_list[1], False)):
                #self.hits_tanked += 5
                if not self.inundated:
                    self.hits_tanked += 5
                    
                    dx += direction * 10
                    self.inundated = True

                #print("hit" + str(self.hits_tanked))
                
            if not self.shielded and (pygame.sprite.spritecollide(self, sp_group_list[2], False)):#player bullet
                self.inundated = True
                self.dmg_multiplier = 0
                self.hits_tanked += 0.5
                dx += direction * 32
                #print("hit" + str(self.hits_tanked))
                
            if (pygame.sprite.spritecollide(self, sp_group_list[9], False)):#looks like a p_int
                if pygame.sprite.spritecollide(self, sp_group_list[9], False, pygame.sprite.collide_mask):
                    self.inundated = True
                    self.dmg_multiplier = 0
                    self.hits_tanked += 3
                    dx -= self.direction * 2
            #world collisions
            
            
            if self.id_ != 'fly':
                for tile in [tile for tile in world_solids 
                            if tile[1].x > -224 and tile[1].x < 864 and 
                                tile[1].bottom < self.rect.bottom + 64 and tile[1].y > self.rect.y - 64 or
                                (tile[1].bottom > self.rect.bottom and tile[1].y < self.rect.y)
                                ]:
                    one_way_tiles = (17, 69, 70)
                    if tile[2] not in (2, 60) and tile[2] not in one_way_tiles:
                        #x tile collisions

                        if tile[1].colliderect(self.rect.x + dx, self.rect.y + self.quarter_height, self.width, self.height*0.6):
                            dx = 0
                            if self.in_air == False:
                                if self.id_ == 'shooter':
                                    self.jump = True
                                if self.id_ == 'dog' and self.rect.bottom == tile[1].top + 16 and self.inundated == False:
                                    self.vel_y = -8.5
                                    self.in_air = True
                            
                            if self.id_ == 'walker':
                                self.flip = not self.flip
                                dx = -self.direction*8
                                self.direction = -self.direction

                        
                        #make sure to not get pushed into blocks collision by half sprite width       
                        if tile[1].colliderect(self.rect.x, self.rect.y , self.half_width , self.height*0.8):     
                            if self.rect.x <= tile[1].right:
                                dx += 8
                            self.on_ground = False
                            self.in_air = True
                            self.jump = False

                        elif tile[1].colliderect(self.rect.x + self.half_width, self.rect.y , self.half_width , self.height*0.8):     
                            if self.rect.right > tile[1].x:
                                dx += -8
                            self.on_ground = False
                            self.in_air = True
                            self.jump = False    

                        #y collisions
                        if tile[1].colliderect(self.rect.x, self.rect.y, self.width , self.height):
                            if self.vel_y >= 0 or dy >= 0:
                                #self.vel_y = 0 
                                #lower half collision
                                if tile[1].colliderect(self.rect.x, self.rect.y + (self.half_height), self.width, self.half_height):
                                    if tile[1].bottom > self.rect.bottom:
                                        dy = tile[1].top - self.rect.bottom #-1
                                        #print('hi')
                                        self.on_ground = True
                                    self.in_air = False
                                    self.vel_y = 0 
                                    
                                    if self.action == 5:
                                        self.hit_ground = True

                            elif self.vel_y < 0 or dy < 0:
                                #upper half collision
                                if tile[1].colliderect(self.rect.x + self.quarter_width//2, self.rect.y, self.width - self.quarter_width, self.half_height):
                                    dy = 32
                                    self.on_ground = False
                                    self.in_air = True
                                    #print("hi")
                                    self.jump = False
                    elif tile[2] in (2, 60):
                        if tile[1].colliderect(self.rect.x + self.quarter_width//2, self.rect.y, self.width - self.quarter_width, self.height - 8):
                            self.dead = True
                            self.m_player.play_sound(self.m_player.sfx[2], (self.rect.centerx, self.rect.centery, None, None))
                    elif(tile[2] in one_way_tiles):#one way tiles
                        if tile[1].colliderect(self.rect.x + dx, self.rect.bottom - 16 + dy, self.width, 17):
                            if self.vel_y >= 0: 
                                self.vel_y = 0
                                self.in_air = False
                                self.on_ground = True
                                
                                if self.action == 5:
                                    self.hit_ground = True
                            elif self.vel_y < 0:
                                self.vel_y *= 0.6#velocity dampening when passing thru tile
                                self.in_air = True
                                self.on_ground = False

                            dy = tile[1].top - self.rect.bottom
            # elif self.id_ != 'fly':
            #     dy = 0
            #     dx = 0
            #     self.moving = False
            #     self.in_air = False
            #     self.vel_y = 0
                        
            if self.rect.bottom + dy > 480 + self.rect.height:
                self.Alive = False
                self.kill()
            if self.id_ == 'shooter':
                if self.in_air == True and self.inundated == False:
                    dx *=0.70
                
        self.atk_rect_scaled.x += (dx - scrollx)
        self.rect.x += (dx - scrollx)
        self.rect.y += dy
        
    def force_ini_position(self, scrollx):
        self.rect.x -= scrollx
    
    def animate(self, sp_group_list, player_rect):
        
        if self.dead and self.Alive:
            self.m_player.play_sound(self.m_player.sfx[0], (self.rect.centerx, self.rect.centery, None, None
                                    #   pygame.rect.Rect(player_rect.x - self.rect.width, 
                                    #                    player_rect.y - self.rect.width, 
                                    #                    player_rect.width + 2*self.rect.width, 
                                    #                    player_rect.height + 2*self.rect.width)
                                      ))
            self.explode(sp_group_list)
            self.Alive = False
            # #print(obj_list[0].index(self))
            # #obj_list[0].pop(obj_list[0].index(self))
            # del obj_list[0][obj_list[0].index(self)]
            sp_group_list[12].add(Item('Cursed Flesh', self.rect.centerx + 2*random.randint(-5,5), self.rect.centery + 2*random.randint(-5,5), 1, False))
            #sp_group_list[12].add(Item('test', self.rect.centerx + 2*random.randint(-5,5), self.rect.centery + 2*random.randint(-5,5), 1, False))
            self.kill()
        
        
            
        if self.action == 0 and self.id_ != 'fly':#idle
            frame_update = 140
        elif self.action == 3:
            frame_update = 70
        elif self.action == 2:#hurting
            frame_update = 80
        elif self.action == 4:
            if self.id_ == 'shooter':
                frame_update = 120
            else:
                frame_update = 130
        else:
            frame_update = 95
            
        if self.id_ == 'walker' and not self.inundated:
            frame_update = 90

        #--shooting bullet---------------------------------------------------------------------------------
        if self.id_ == 'shooter':
            if self.action == 4 and self.frame_index == 4 and not self.shoot_done and self.direction != 0:
                #print("Pew!")
                
                if self.flip == True:
                    x = self.rect.right + 12
                    #print("flipped") this is flipped
                else:
                    x = self.rect.left - 28
                y = self.rect.y + self.height//3 - 4
                enemy_bullet = bullet_(x, y, 8, self.direction, self.scale, '8x8_red', self.ini_vol)
                self.m_player.play_sound(self.m_player.sfx[3], (self.rect.centerx, self.rect.centery, None, None))
                sp_group_list[1].add(enemy_bullet)
                
                self.shoot_done = True
                self.shoot = False
        elif self.id_ == 'fly':
            if self.action == 4 and self.frame_index == 6 and not self.shoot_done:
                #print('pew!')
                sp_group_list[5].sprite.add_particle('enemy_bullet_explosion', self.rect.centerx, self.rect.bottom+4, -self.direction, self.scale, False, random.randrange(0,2))
                for i in range(7):
                    sp_group_list[5].sprite.add_particle('enemy_bullet_explosion', self.rect.centerx+random.randrange(-16,16), self.rect.bottom+random.randrange(-16,16), -self.direction, 0.3*self.scale, False, random.randrange(0,2))
                enemy_bullet = bullet_(self.rect.centerx, self.rect.bottom+16, 7, self.direction, 1.5, '8x8_red', self.ini_vol, angle=self.theta, dmg=1)
                enemy_bullet1 = bullet_(self.rect.centerx, self.rect.bottom+16, 7, self.direction, 1.5, '8x8_red', self.ini_vol, angle=self.theta+0.3, dmg=1)
                enemy_bullet2 = bullet_(self.rect.centerx, self.rect.bottom+16, 7, self.direction, 1.5, '8x8_red', self.ini_vol, angle=self.theta-0.3, dmg=1)
                self.m_player.play_sound(self.m_player.sfx[5], (self.rect.centerx, self.rect.centery, None, None))
                sp_group_list[1].add(enemy_bullet)
                sp_group_list[1].add(enemy_bullet1)
                sp_group_list[1].add(enemy_bullet2)
                
                self.shoot_done = True
            
        #setting the image
        self.image = self.frame_dict[self.action][self.frame_index]
        self.mask = pygame.mask.from_surface(self.image)

        #update sprite dimensions
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        if pygame.time.get_ticks() - self.update_time > frame_update:
            # if self.action == 5 and self.frame_index == 0:
            #     self.m_player.play_sound (self.m_player.sfx[4])
            if self.check_if_in_simulation_range(0):
                if self.id_ == 'walker' and self.action == 0 and self.frame_index == 2:
                    self.m_player.play_sound(self.m_player.sfx[3], (self.rect.centerx, self.rect.centery, None, None))
                elif self.id_ == 'fly' and self.action not in (2,4) and self.frame_index in (0,2):
                    self.m_player.play_sound(self.m_player.sfx[3], (self.rect.centerx, self.rect.centery, 
                                                                    pygame.rect.Rect(player_rect.x - self.width, 
                                                                                     player_rect.y - self.width, 
                                                                                     player_rect.width + 2*self.width, 
                                                                                     player_rect.height + 2*self.width),
                                                                    6*self.width
                                                                    ))
                elif self.id_ == 'fly' and self.action == 4 and self.frame_index == 0:
                    self.m_player.play_sound(self.m_player.sfx[2], (self.rect.centerx, self.rect.centery, None, None))
                    
            
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        #END OF ANIMATION FRAMES    
        if self.frame_index >= len(self.frame_dict[self.action]):
            
            self.frame_index = 0
            
            if self.action == 2:#hurting
                #print('hi')
                #boolean to whether just take damage or die
                #if self.inundated == True:
                self.pos_list *= 0
                self.inundated = False
                self.recovering = True
                self.idle_counter = 0
                self.fly_atk_finished = True
                
                if self.id_ == 'walker':
                    if (self.flip and self.direction == -1) or (not self.flip and self.direction == 1):
                        self.flip = not self.flip
                

            elif self.action == 3:
                self.kill()
                self.Alive = False
            
            elif self.action == 0:
                self.idle_counter += 1
                if self.idle_counter > 1: #2
                    self.idle_counter = 1
                #print(self.idle_counter)
                self.recovering = False
                
            elif self.action == 4:
                self.idle_counter = 0
                self.shoot_done = False
                if self.id_ == 'fly':
                    self.fly_atk_finished = True
                    self.idle_counter -= 3
                
            elif self.action == 5:
                self.jump_counter += 1
                if self.jump_counter > 1:
                    self.jump = False
                    self.jump_counter = 0
                    
            
    
    def explode(self, sp_group_list):
        particle_name = self.id_ + '_death'
        p_scale = 0.2
        for i in range(15):
            sp_group_list[5].sprite.add_particle('bloom', self.rect.centerx+random.randrange(-32,32), self.rect.centery+random.randrange(-32,32), -self.direction, p_scale*self.scale, False, random.randrange(0,2))
            sp_group_list[5].sprite.add_particle('player_bullet_explosion', self.rect.centerx+random.randrange(-72,72), self.rect.centery+random.randrange(-72,72), -self.direction, 0.2*self.scale, False, random.randrange(0,3))
        sp_group_list[3].sprite.add_particle(particle_name, self.rect.x - self.half_width, self.rect.y - self.half_height, self.direction, self.scale, False, 0)
        

    def draw(self, screen):
        #self.animate()
        if self.check_if_onscreen():
            if self.fly_aimline_tgt != (-1,-1) and pygame.time.get_ticks()%2 == 0:
                pygame.draw.line(screen, (255,0,0), (self.rect.centerx, self.rect.centery+24), self.fly_aimline_tgt, 3)
                # if self.frame_index == 4 and pygame.time.get_ticks()%5 != 0:
                #     pygame.draw.line(screen, (255,255,255), self.rect.center, self.fly_aimline_tgt) 
                
            #if self.shielded
            
            # outline_surf = pygame.surface.Surface((self.rect.width+2, self.rect.height+2), flags=pygame.SRCALPHA, depth=32)
            # for pix in self.mask.outline():
            #     pygame.draw.rect(outline_surf, (255, 255, 255, 100), pygame.rect.Rect(pix[0]+self.direction, pix[1]-2, 3, 3))
            # outline_surf.blit(self.mask.to_surface(setcolor=(255, 255, 255, 100), unsetcolor=(0,0,0,0)))
            # screen.blit(pygame.transform.flip(outline_surf, self.flip, False), pygame.rect.Rect(self.rect.x-1, self.rect.y-1, self.rect.width+2, self.rect.height+2))
                
            if self.inundated and self.frame_index < 1:
                if pygame.time.get_ticks()%5 != 0:
                    screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
            else:
                screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
                
            self.hp_bar.render_bar((self.rect.centerx, int(self.rect.y-8)), (self.hp-self.hits_tanked)/self.hp, screen)
                    
                
            # if self.pos_list != []:
            #     for pos in self.pos_list:
            #         screen.blit(pygame.transform.flip(self.image, self.flip, False), pygame.rect.Rect(pos[0], pos[1], self.width, self.height))
                
        #pygame.draw.rect(screen, (255,0,0), self.atk_rect_scaled)
    
    def update_action(self, new_action):
        #check if action has changed

        if new_action != self.action:
            #if new_action != 5:
                #self.jump_counter = 0
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            if new_action == 2:
                self.m_player.play_sound(self.m_player.sfx[2], (self.rect.centerx, self.rect.centery, None, None))
                self.hits_tanked += self.dmg_multiplier
                self.dmg_multiplier = 0
                
                if self.id_ == 'dog':
                    self.vel_y = -7
                    self.in_air = True
                elif self.id_ == 'walker':
                    self.vel_y = -3
                    self.in_air = True
            elif new_action == 1:
                if self.id_ == 'dog' and self.in_air == False:
                    self.speed_boost = 8
                    self.m_player.play_sound(self.m_player.sfx[3], (self.rect.centerx, self.rect.centery, None, None))
            # elif new_action == 5:
            #     self.m_player.play_sound (self.m_player.sfx[4])
            
                #print(self.hits_tanked)
            

        
                
            
    