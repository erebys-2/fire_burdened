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


class enemy_32wide(pygame.sprite.Sprite): #Generic enemy class for simple enemies
    #constructors
    def __init__(self, x, y, speed, scale, id, enemy0_order_id, ini_vol, frame_list, sfx_list_ext):
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
        
        self.id = id
        animation_types = []
        self.frame_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.update_time2 = pygame.time.get_ticks()
        self.getting_shot_delay = pygame.time.get_ticks()
        
        self.do_screenshake = False
        
        self.increment = 0

        #fill animation frames
        if id == 'dog':
            animation_types = ['0', '1', '2', '3']
            self.hp = 6
            self.recoil = 58
            self.recoil_slow = 2
            sfx_list = ['bassdrop2.mp3', 'hit.mp3', 'dog_hurt.mp3', 'woof.mp3', 'step2soft.mp3']
        elif id == 'shooter':   
            animation_types = ['0', '1', '2', '3', '4', '5'] 
            self.hp = 8
            self.recoil = 58
            self.recoil_slow = 2
            sfx_list = ['bassdrop2.mp3', 'hit.mp3', 'roblox2.mp3', 'shoot.mp3', 'step2soft.mp3']
            #, '', 'bite.mp3', 'bee.mp3'
        elif id == 'fly':
            animation_types = ['0', '1', '2', '3']
            self.hp = 4
            self.recoil = 43
            self.recoil_slow = 3
            sfx_list = ['bassdrop2.mp3', 'hit.mp3', 'bee_hurt.mp3', 'bee.mp3', 'step2soft.mp3']
        elif id == 'walker':
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

        if frame_list == None:
            for animation in animation_types:
                temp_list = []
                frames = len(os.listdir(f'assets/sprites/enemies/{self.id}/{animation}'))

                for i in range(frames):
                    img = pygame.image.load(f'assets/sprites/enemies/{self.id}/{animation}/{i}.png').convert_alpha()
                    
                    if animation == '2' and i < 2:
                        img = pygame.transform.scale(img, (int(img.get_width() * 0.5 * scale), int(img.get_height() * 1.2 * scale)))
                    else:
                        img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    
                    temp_list.append(img)
                self.frame_list.append(temp_list)
        else:
            self.frame_list = frame_list

        self.image = self.frame_list[self.action][self.frame_index]
        self.mask = pygame.mask.from_surface(self.image)
        if self.id != 'fly':
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
            if p_int.collision_and_hostility[p_int.id][0]:
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
                        
                    if self.id == 'walker' and not self.inundated:
                        self.direction = -self.direction
                        self.flip = not self.flip
                        dx = self.direction*8
 
                    
            #taking damage from crushing traps
            if p_int.collision_and_hostility[p_int.id][1]:
                rate = self.hp//3
                if (self.rect.colliderect(p_int.atk_rect)):
                    if self.hits_tanked + rate > self.hp:
                        self.hits_tanked = self.hp
                    else:
                        self.hits_tanked += rate
        return (dx,dy)
        
    def move(self, player_rect, player_atk_rect, player_direction, world_solids, scrollx, player_action, sp_group_list):
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
                #enemy id specific behaviors--------------------------------------------------------------------------------------
                if self.id == 'dog':
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
                        
                        
                elif self.id == 'shooter':
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
                                
                        if self.action == 5 and not  self.inundated: #when the shooter is jumping it has an attack hitbox
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
                        
                    
                elif self.id == 'fly':
                    #print(self.action)
                    if self.inundated == False: #cannot move towards player when inundated
                        #move if the player gets too close
                        chase_range = 3
                    
                        if player_rect.x > self.rect.x - chase_range*self.width and player_rect.x <= self.rect.x:
                            dx = -self.speed
                            moving = True
                            self.direction = -1
                        elif player_rect.x < self.rect.x + self.width + chase_range*self.width and player_rect.x >= self.rect.x:
                            dx = self.speed
                            moving = True
                            self.direction = 1
                            
                        if player_rect.x > self.rect.x - chase_range*self.width and player_rect.x < self.rect.x + self.width + chase_range*self.width:
                            if player_rect.y - self.height*2.5 > self.rect.y - 2*chase_range*self.height and player_rect.y - self.half_height <= self.rect.y:
                                self.vel_y = -self.speed*0.75
                                moving = True
                            elif player_rect.y - self.height*2.5 < self.rect.y + 4*chase_range*self.height and player_rect.y - self.height*2.5 >= self.rect.y:
                                self.vel_y = self.speed*2
                                moving = True
                            if self.vel_y == 0:
                                if player_rect.y > self.rect.bottom:
                                    self.vel_y = self.speed
                                else:
                                    self.vel_y = -self.speed
                            
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
                        
                        
                elif self.id == 'walker':
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
            
            #action tree-------------------------------------------------------------------------------------------------------------
            if self.hits_tanked < self.hp:#alive
                
                if self.inundated == True:
                    
                    self.update_action(2)
                    if self.frame_index < 1:
                        dx = 0
                        # x_avg = (self.rect.centerx + player_atk_rect.centerx)/2
                        # y_avg = (self.rect.centery + player_atk_rect.centery)/2
                        sp_group_list[5].sprite.add_particle('player_bullet_explosion', self.rect.centerx+random.randrange(-48,48), self.rect.centery+random.randrange(-48,48), -self.direction, 0.3*self.scale, False, random.randrange(0,3))

                        #dy = 0
                    else:
                        dx += self.direction * self.recoil_slow
                    #dy-= 2
                    
                else:
                    # if self.recovering:
                    #     self.update_action(0)
                    if self.shoot == True and (self.idle_counter == 1 or self.idle_bypass == True) and self.direction != 0:#2
                        if self.frame_index <= 4:
                            self.shoot = True
                        self.update_action(4)
                    elif self.jump == True:
                        self.update_action(5)
                    elif moving == True:
                        self.update_action(1)
                        if dx < 0:
                            self.flip = False
                        else:
                            self.flip = True
                    else:
                        self.update_action(0)
            else:#dies
                self.dead = True
                
    
            
            #gravity 
            if self.id != 'fly':
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
                and self.inundated == False
                ):
                #pygame.time.wait(8)
                #the average point in a collision between rects is literally just the average of the coords opposite respective corners of rects
                x_avg = (self.rect.centerx + player_atk_rect.centerx)/2
                dx = player_direction * self.recoil
                y_avg = (self.rect.centery + player_atk_rect.centery)/2
                
                
                
                if self.rando_frame < 2:
                    self.rando_frame += 1
                else:
                    self.rando_frame = 0
                
                if self.id == 'fly':
                    dy += self.vertical_direction * self.recoil//2
                else:
                    dy += self.vel_y * 2

                self.direction = player_direction
                
                self.do_screenshake = True
                self.inundated = True
                
                if player_action ==  10 or player_action == 9:
                    self.dmg_multiplier = 6
                    self.heavy_recoil = True
                elif player_action == 16:
                    self.dmg_multiplier = 4
                    self.heavy_recoil = True
                elif player_action == 7 or player_action == 8:
                    self.dmg_multiplier = 2
                    self.heavy_recoil = False
                    
                sp_group_list[5].sprite.add_particle('player_impact', x_avg + dx/4, y_avg, -self.direction, self.scale*1.05, True, self.rando_frame)
                particle_ct = 3
                sfx_index = 1
                if self.heavy_recoil:
                    particle_ct = 15
                    sfx_index = 5
                    p_update_time = pygame.time.get_ticks()
                    for i in range(particle_ct//2):
                        sp_group_list[5].sprite.add_particle('extra_dmg', self.rect.centerx+random.randrange(-48,48), y_avg+random.randrange(-48,48), -self.direction, 0.75*self.scale, False, random.randrange(0,2), p_update_time)
                    self.heavy_recoil = False
                
                # for i in range(particle_ct):
                #     sp_group_list[5].sprite.add_particle('player_bullet_explosion', self.rect.centerx+random.randrange(-48,48), y_avg+random.randrange(-48,48), -self.direction, 0.3*self.scale, False, random.randrange(0,3))

                self.m_player.play_sound(self.m_player.sfx[sfx_index], (self.rect.centerx, self.rect.centery, None, None))
                #pygame.time.delay(50)
                    
            elif (player_atk_rect.width == 0 and   
                player_rect.x > self.rect.x - 64 and player_rect.right < self.rect.right + 64 and
                    (self.rect.colliderect(player_rect.scale_by(0.2)) or (self.rect.x < player_rect.x and self.rect.right > player_rect.right ))
                    and self.id != 'walker'
                #and not (self.inundated or self.rect.colliderect(player_atk_rect))
                ):
                dx = -dx
                self.direction = 0
                if self.id == 'shooter':
                    self.jump = True
                
            elif player_action == 6 and self.rect.colliderect(player_rect):
                dx = 0
            
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

            
            if self.id != 'fly':
                dxdy = self.do_p_int_group_collisions(sp_group_list[8], dx, dy)
                dx = dxdy[0]
                dy = dxdy[1]
            #world collisions
            
            
            if self.id != 'fly':
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
                                if self.id == 'shooter':
                                    self.jump = True
                                if self.id == 'dog' and self.rect.bottom == tile[1].top + 16 and self.inundated == False:
                                    self.vel_y = -8.5
                                    self.in_air = True
                            
                            if self.id == 'walker':
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
                        if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width , self.height):
                            if self.vel_y >= 0:
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

                            elif self.vel_y < 0:
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
            # elif self.id != 'fly':
            #     dy = 0
            #     dx = 0
            #     self.moving = False
            #     self.in_air = False
            #     self.vel_y = 0
                        
            if self.rect.bottom + dy > 480 + self.rect.height:
                self.Alive = False
                self.kill()
            if self.id == 'shooter':
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
        
        #colliding with bullet 
        #this is fucked, look into collide rect
        if (pygame.sprite.spritecollide(self, sp_group_list[1], False)):
            #self.hits_tanked += 5
            self.inundated = True
            # if self.inundated  == True and self.dmg_multiplier != 0:
            #     self.hits_tanked += 5
            # else:
            self.dmg_multiplier = 5
            self.rect.x += -self.direction * 2
            #print("hit" + str(self.hits_tanked))
            
        if (pygame.sprite.spritecollide(self, sp_group_list[2], False)):
            self.inundated = True
            self.dmg_multiplier = 0
            self.hits_tanked += 1
            self.rect.x += -self.direction * 2
            #print("hit" + str(self.hits_tanked))
            
        if (pygame.sprite.spritecollide(self, sp_group_list[9], False)):
            if pygame.sprite.spritecollide(self, sp_group_list[9], False, pygame.sprite.collide_mask):
                self.inundated = True
                self.dmg_multiplier = 0
                self.hits_tanked += 3
                self.rect.x += -self.direction * 2
            
        if self.action == 0 and self.id != 'fly':#idle
            frame_update = 140
        elif self.action == 3:
            frame_update = 70
        elif self.action == 2:#hurting
            frame_update = 80
        elif self.action == 4:
            frame_update = 120
        else:
            frame_update = 95
            
        if self.id == 'walker' and not self.inundated:
            frame_update = 90

        #--shooting bullet---------------------------------------------------------------------------------
        if self.action == 4 and self.frame_index == 4 and self.shoot_done == False and self.direction != 0:
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
        
        #setting the image
        self.image = self.frame_list[self.action][self.frame_index]
        self.mask = pygame.mask.from_surface(self.image)

        #update sprite dimensions
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        if pygame.time.get_ticks() - self.update_time > frame_update:
            # if self.action == 5 and self.frame_index == 0:
            #     self.m_player.play_sound (self.m_player.sfx[4])
            if self.check_if_in_simulation_range(0):
                if self.id == 'walker' and self.action == 0 and self.frame_index == 2:
                    self.m_player.play_sound(self.m_player.sfx[3], (self.rect.centerx, self.rect.centery, None, None))
                elif self.id == 'fly' and self.action != 2 and self.frame_index in (0,2):
                    self.m_player.play_sound(self.m_player.sfx[3], (self.rect.centerx, self.rect.centery, 
                                                                    pygame.rect.Rect(player_rect.x - self.width, 
                                                                                     player_rect.y - self.width, 
                                                                                     player_rect.width + 2*self.width, 
                                                                                     player_rect.height + 2*self.width),
                                                                    6*self.width
                                                                    ))
            
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        #END OF ANIMATION FRAMES    
        if self.frame_index >= len(self.frame_list[self.action]):
            
            self.frame_index = 0
            
            if self.action == 2:#hurting
                #boolean to whether just take damage or die
                if self.inundated == True:
                    self.inundated = False
                self.recovering = True
                self.idle_counter = 0
                
                if self.id == 'walker':
                    if (self.flip and self.direction == -1) or (not self.flip and self.direction == 1):
                        self.flip = not self.flip
                

            elif self.action == 3:
                self.kill()
                self.Alive = False
            
            elif self.action == 0:
                self.idle_counter += 1
                if self.idle_counter > 1: #2
                    self.idle_counter = 0
                #print(self.idle_counter)
                self.recovering = False
                
            elif self.action == 4:
                self.idle_counter = 0
                self.shoot_done = False
                
            elif self.action == 5:
                self.jump_counter += 1
                if self.jump_counter > 1:
                    self.jump = False
                    self.jump_counter = 0
    
    def explode(self, sp_group_list):
        particle_name = self.id + '_death'
        sp_group_list[3].sprite.add_particle(particle_name, self.rect.x - self.half_width, self.rect.y - self.half_height, self.direction, self.scale, False, 0)
        

    def draw(self, p_screen):
        #self.animate()
        if self.check_if_onscreen():
            if self.inundated and self.frame_index < 1:
                if pygame.time.get_ticks()%5 != 0:
                    p_screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
            else:
                p_screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        #pygame.draw.rect(p_screen, (255,0,0), self.atk_rect_scaled)
    
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
                
                if self.id == 'dog':
                    self.vel_y = -7
                    self.in_air = True
                elif self.id == 'walker':
                    self.vel_y = -3
                    self.in_air = True
            elif new_action == 1:
                if self.id == 'dog' and self.in_air == False:
                    self.speed_boost = 8
                    self.m_player.play_sound(self.m_player.sfx[3], (self.rect.centerx, self.rect.centery, None, None))
            # elif new_action == 5:
            #     self.m_player.play_sound (self.m_player.sfx[4])
            
                #print(self.hits_tanked)
            

        
                
            
    