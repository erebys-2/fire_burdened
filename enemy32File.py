import pygame
import os
#from game_window import sprite_group
from bullet import bullet_ #type: ignore
#print('directory: ' + os.getcwd())
from particle import particle_ #type: ignore
from music_player import music_player #type: ignore
 
#GRAVITY = 0.75

class enemy_32wide(pygame.sprite.Sprite):
    #constructors
    def __init__(self, x, y, speed, scale, type, enemy0_id, eq_regime):
        pygame.sprite.Sprite.__init__(self)
        self.m_player = music_player(['bassdrop2.wav', 'hit.wav', 'roblox2.wav', 'shoot.wav'], eq_regime)
        self.eq_regime = eq_regime
        self.m_player.set_sound_vol(self.m_player.sfx[0], 7) #looks like you can adjust vol in the constructor

        self.player_collision = False
        self.id = enemy0_id
        
        self.Alive = True
        self.action = 0
        self.scale = scale

        self.inundated = False
        self.speed = speed
        self.slower_speed = speed - 1
        self.direction = -1
        self.flip = False
        self.recoil = 42
        self.recoil_slow = 3
        self.speed_boost = 1

        self.vel_y = 0
        self.in_air = True
        self.jump = False
        self.jump_counter = 0
        self.on_ground = False
        
        self.hp = 6 #how many hits can he take
        self.dead = False
        self.hits_tanked = 0
        self.dmg_multiplier = 0
        self.rando_frame = 0
        
        self.shoot = False
        self.shoot_done = False
        self.idle_counter = 0
        self.idle_bypass = False
        
        self.enemy_type = type
        self.animation_types = []
        self.frame_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.update_time2 = pygame.time.get_ticks()
        self.getting_shot_delay = pygame.time.get_ticks()

        #fill animation frames
        if type == 'dog':
            self.animation_types = ['idle', 'move', 'hurt', 'die']
            self.hp = 6
            self.recoil = 52
            self.recoil_slow = 2
        elif type == 'shooter':   
            self.animation_types = ['idle', 'move', 'hurt', 'die', 'shoot', 'jump'] 
            self.hp = 10
            self.recoil = 46
            self.recoil_slow = 2
            
        for animation in self.animation_types:
            temp_list = []
            frames = len(os.listdir(f'sprites/{self.enemy_type}/{animation}'))

            for i in range(frames):
                img = pygame.image.load(f'sprites/{self.enemy_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.frame_list.append(temp_list)

        self.image = self.frame_list[self.action][self.frame_index]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        

    #methods----------------------------------------------------------------------------------------
        
    def move(self, player_rect, player_atk_rect, world_solids, scrollx, player_action, sp_group_list):
        dx = 0
        dy = 0
        moving = False
        # if player is within left range, or right range
        if self.inundated == False:
            #enemy type specific behaviors--------------------------------------------------------------------------------------
            if self.enemy_type == 'dog':
                if player_rect.x > self.rect.x - 5*32 and player_rect.x <= self.rect.x:
                    dx = -self.speed *self.speed_boost
                    self.direction = -1
                    moving = True
                elif player_rect.x < self.rect.x + self.width + 5*32 and player_rect.x >= self.rect.x:
                    dx = self.speed *self.speed_boost
                    self.direction = 1
                    moving = True
                
                if self.speed_boost != 1:
                    self.speed_boost = 1
                    particle = particle_(self.rect.centerx, self.rect.centery, -self.direction, self.scale, 'player_mvmt', True, 1, False)
                    sp_group_list[3].add(particle)
                    self.in_air = True
                    self.vel_y = -8
                    
            elif self.enemy_type == 'shooter':
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
                    chase_range = 1.8
                
                    if player_rect.x > self.rect.x - chase_range*self.width and player_rect.x <= self.rect.x:
                        dx = -self.speed
                        moving = True
                    elif player_rect.x < self.rect.x + self.width + chase_range*self.width and player_rect.x >= self.rect.x:
                        dx = self.speed
                        moving = True
                    #jump if the player is within this range
                    jump_range = 1.3
                    if self.rect.top <= player_rect.top:
                        if player_rect.x > self.rect.x - (jump_range*self.width) and player_rect.x <= self.rect.x:
                            self.jump = True
                        elif player_rect.x < self.rect.x + self.width + (jump_range*self.width) and player_rect.x >= self.rect.x:
                            self.jump = True

                    
                jump_cooldown = 720
                if (self.jump and self.in_air == False and self.on_ground and
                    (pygame.time.get_ticks() - self.update_time2 > jump_cooldown)):
                    self.update_time2 = pygame.time.get_ticks()
                    particle = particle_(self.rect.centerx, self.rect.centery, -self.direction, self.scale, 'player_mvmt', True, 1, False)
                    sp_group_list[3].add(particle)
                    self.vel_y = -10
                    self.in_air = True


         
        else:
            moving = False
        
        #action tree-------------------------------------------------------------------------------------------------------------
        if self.hits_tanked < self.hp:#alive
            
            if self.inundated == True:
                self.update_action(2)
                dx += -self.direction * self.recoil_slow
                #dy-= 2
                
            else:
                if self.shoot == True and (self.idle_counter == 1 or self.idle_bypass == True):#2
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
        if self.Alive == True:  
            # if self.inundated:
            #     self.vel_y = -10
            #     self.in_air = True
           
            g = 0.4
            self.vel_y += g
            
            if self.vel_y > 10:
                self.vel_y
                
        else:
            self.vel_y = 0
        dy = self.vel_y
        
        #player collisions------------------------------------------------------------------------------------------------------------------
        
        if ((player_action == 7 or player_action == 8 or player_action == 10)
            and self.rect.colliderect(player_atk_rect)
            and self.inundated == False
            ):
           
            #the average point in a collision between rects is literally just the average of the coords opposite respective corners of rects
            x_avg = (self.rect.x + player_atk_rect.right)/2
            y_avg = (self.rect.y + player_atk_rect.bottom)/2
            
            particle = particle_(x_avg, y_avg, -self.direction, self.scale, 'player_impact', True, self.rando_frame, False)
            sp_group_list[5].add(particle)
            self.m_player.play_sound(self.m_player.sfx[1])
            
            if self.rando_frame < 2:
                self.rando_frame += 1
            else:
                self.rando_frame = 0
            
            self.inundated = True
            dx += -self.direction * self.recoil
            if player_action ==  10 or player_action == 9:
                self.dmg_multiplier = 6
            elif player_action == 7 or player_action == 8:
                self.dmg_multiplier = 2
        elif (self.rect.colliderect(player_rect.scale_by(0.2)) and (player_action == 0 or player_action == 6)
              or (self.rect.x < player_rect.x and self.rect.right > player_rect.right 
                and not (player_action == 10))
              ):
            dx = 0
        elif player_action == 6 and self.rect.colliderect(player_rect):
            dx = 0

        
        #enemy0 collisions
        for enemy0 in sp_group_list[0]:
            if self.rect.colliderect(enemy0.rect) and self.id != enemy0.id:
                # if self.rect.x > enemy0.rect.x:
                #     dx += -self.direction
                # elif self.rect.x < enemy0.rect.x:
                #     dx += self.direction

                if self.id < enemy0.id:
                    dx += -self.direction * 2
                else:
                    dx += self.direction * 2


        
        #world collisions
        for tile in world_solids:
            if tile[2] != 2 and tile[2] != 17:
                #x tile collisions
                if tile[1].colliderect(self.rect.x + dx, self.rect.y + self.height//4, self.width , 3*self.height//4 - 12):
                    dx = 0
                    if self.in_air == False:
                        if self.enemy_type == 'shooter':
                            self.jump = True
                        if self.enemy_type == 'dog' and self.rect.bottom == tile[1].top + 16 and self.inundated == False:
                            self.vel_y = -5

                #make sure to not get pushed into blocks        
                if tile[1].colliderect(self.rect.x , self.rect.y , self.width//2 , self.height*0.8):     #+ self.height//4
                    if self.rect.x <= tile[1].right:
                        dx += 8
                    self.on_ground = False
                    self.in_air = True
                    self.jump = False 
                elif tile[1].colliderect(self.rect.x + self.width//2, self.rect.y , self.width//2 , self.height*0.8):     #+ self.height//4
                    if self.rect.right > tile[1].x:
                        dx += -8
                    self.on_ground = False
                    self.in_air = True
                    self.jump = False    

                #y collisions
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width , self.height):

                    if self.vel_y >= 0:
                        #self.vel_y = 0 
                        if tile[1].colliderect(self.rect.x + self.width//4 + 2, self.rect.y + (self.height//2), self.width//2 - 4, self.height//2):
                            #print("working_too")
                            if tile[1].bottom > self.rect.bottom:
                                dy = tile[1].top  - self.rect.bottom #-1
                                #print('hi')
                            self.on_ground = True
                            self.in_air = False
                            self.vel_y = 0 
                        # if self.vel_y > 0:
                        #     self.in_air = True
                        # else:
                        #     self.in_air = False
                    
                    elif self.vel_y < 0:
                        if tile[1].colliderect(self.rect.x + self.width//8, self.rect.y, self.width - self.width//4, self.height//2):
                            dy = 32
                            self.on_ground = False
                            self.in_air = True
                            self.jump = False
            elif tile[2] == 2:
                if tile[1].colliderect(self.rect.x + self.width//8, self.rect.y, self.width - self.width//4, self.height - 8):
                    self.dead = True
                    self.m_player.play_sound(self.m_player.sfx[2])
            elif(tile[2] == 17):#one way tiles
                if tile[1].colliderect(self.rect.x + dx, self.rect.bottom - 16 + dy, self.width, 17):
                    if self.vel_y >= 0: 
                        self.vel_y = 0
                        self.in_air = False
                        self.on_ground = True
                    elif self.vel_y < 0:
                        self.vel_y *= 0.6#velocity dampening when passing thru tile
                        self.in_air = True
                        self.on_ground = False

                    dy = tile[1].top - self.rect.bottom
                    
        if self.rect.bottom + dy > 480:
            dy = 480 - self.rect.bottom
            self.in_air = False
        if self.enemy_type == 'shooter':
            if self.in_air == True and self.inundated == False:
                dx *=0.70
        self.rect.x += (dx - scrollx)
        self.rect.y += dy
    
    def animate(self, sp_group_list):
        
        if self.dead == True:
            self.m_player.play_sound(self.m_player.sfx[0])
            self.explode(sp_group_list)
            self.Alive = False
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
            self.hits_tanked += 1
            self.rect.x += -self.direction * 2
            #print("hit" + str(self.hits_tanked))
            
        if self.action == 0:#idle
            frame_update = 140
        elif self.action == 3:
            frame_update = 70
        elif self.action == 2:#hurting
            frame_update = 80
        elif self.action == 4:
            frame_update = 120
        else:
            frame_update = 95

        #--shooting bullet---------------------------------------------------------------------------------
        if self.action == 4 and self.frame_index == 4 and self.shoot_done == False:
            #print("Pew!")
            
            if self.flip == True:
                x = self.rect.right + 12
                #print("flipped") this is flipped
            else:
                x = self.rect.left - 28
            y = self.rect.y + self.height//3 - 4
            enemy_bullet = bullet_(x, y, 8, self.direction, self.scale, '8x8_red', self.eq_regime)
            self.m_player.play_sound(self.m_player.sfx[3])
            sp_group_list[1].add(enemy_bullet)
            self.shoot_done = True
            self.shoot = False
        
        #setting the image
        self.image = self.frame_list[self.action][self.frame_index]

        #update sprite dimensions
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        if pygame.time.get_ticks() - self.update_time > frame_update:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        #END OF ANIMATION FRAMES    
        if self.frame_index >= len(self.frame_list[self.action]):
            
            self.frame_index = 0
            
            if self.action == 2:#hurting
                #boolean to whether just take damage or die
                if self.inundated == True:
                    # self.hits_tanked += self.dmg_multiplier
                    # self.dmg_multiplier = 0
                    # print(self.hits_tanked)
                    # if self.enemy_type == 'dog':
                    #     self.vel_y -= 10
                    #     self.in_air = True
                    self.inundated = False
                    
                self.idle_counter = 0

            elif self.action == 3:
                self.kill()
                self.Alive = False
            
            elif self.action == 0:
                self.idle_counter += 1
                if self.idle_counter > 1: #2
                    self.idle_counter = 0
                #print(self.idle_counter)
                
            elif self.action == 4:
                self.idle_counter = 0
                self.shoot_done = False
                
            elif self.action == 5:
                self.jump_counter += 1
                if self.jump_counter > 1:
                    self.jump = False
                    self.jump_counter = 0
    
    def explode(self, sp_group_list):
        if self.enemy_type == 'shooter':   
            particle = particle_(self.rect.x - self.width//2, self.rect.y - self.height//2, self.direction, self.scale, 'shooter_death', False, 0, False)
            sp_group_list[3].add(particle)
        elif self.enemy_type == 'dog':
            particle = particle_(self.rect.x - self.width//2, self.rect.y - self.height//2, self.direction, self.scale, 'dog_death', False, 0, False)
            sp_group_list[3].add(particle)

    def draw(self, p_screen):
        #self.animate()
        p_screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        #pygame.draw.rect(p_screen, (255,0,0), self.ref_rect)
    
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
                self.m_player.play_sound(self.m_player.sfx[2])
                self.hits_tanked += self.dmg_multiplier
                self.dmg_multiplier = 0
                if self.enemy_type == 'dog':
                    self.vel_y = -7
                    self.in_air = True
            elif new_action == 1:
                if self.enemy_type == 'dog' and self.inundated == False and self.in_air == False:
                    self.speed_boost = 8
            
                #print(self.hits_tanked)
            

        
                
            
    