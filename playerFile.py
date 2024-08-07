import pygame
import os
from bullet import bullet_ #type: ignore
from particle import particle_ #type: ignore
from music_player import music_player #type: ignore
import math
import random
#print('directory: ' + os.getcwd())

class player(pygame.sprite.Sprite):
    #constructors
    def __init__(self, x, y, speed, hp, stamina, hits_tanked, stamina_used, ini_vol):
        pygame.sprite.Sprite.__init__(self)
        #internal variables
        scale = 2
        self.scale = scale
        self.Alive = True
        self.action = 0

        self.speed = speed
        self.default_speed = self.speed
        self.direction = 1
        self.flip = False
        self.brain_damage = False

        self.scrollx = 0
        self.x_coord = x
        self.y_coord = y

        self.squat = False
        self.squat_done = False
        self.jump_dampen = False

        self.jump = False
        self.in_air = False
        self.vel_y = 0
        self.landing = False
        self.curr_state = self.in_air #for particles ...again

        self.atk1_alternate = False
        self.atk1 = False
        self.atk_show_sprite = False
        
        self.disp_flag = False
        self.curr_disp_flag = False

        self.rolled_into_wall = False
        
        self.hurting = False
        self.hits_tanked = hits_tanked
        self.i_frames_en = False
        self.crit = False
        self.flicker = False
        self.i_frames_time = 0
        self.do_screenshake = False
        self.screenshake_profile = (0,0,0)
		
        self.shoot = False
        self.shot_charging = False
        self.ini_cost_spent = False
        self.charge_built = 0
        self.shoot_recoil = False
        self.extra_recoil = 0
        self.frame_updateBP = 150
  
        self.rolling = False
        self.roll_count = 0
        self.roll_limit = 1
        self.roll_stam_rate = 0.25
        self.hitting_wall = False
        
        self.sprint = False
        self.change_direction = False
        self.last_direction = self.direction
        
        self.hp = hp
        self.stamina = stamina
        self.stamina_used = stamina_used
        self.ini_stamina = 0

        self.frame_list = []
        self.frame_index = 0
        self.frame_index2 = 0
        self.last_frame = -1 #used for walking particles
        self.update_time = pygame.time.get_ticks()#animations
        self.update_time2 = pygame.time.get_ticks()#iframes
        self.update_time3 = pygame.time.get_ticks()#stamina regen
        self.particle_update = pygame.time.get_ticks()#crit particles
        self.BP_update_time = pygame.time.get_ticks()#charging particles
        self.coyote_jump_update_time = pygame.time.get_ticks()
        
        self.angle = 0
        
        self.dialogue_trigger_ready = False

        #fill animation frames
        animation_types = ('idle', 'run', 'jump', 'land', 'squat', 'hurt', 
                           'die', 'atk1', 'atk1_2', 'roll', 'atk1_3', 'shoot',
                           'charging', 'atk1_2_particle', 'turn_around')
        for animation in animation_types:
            temp_list = []
            frames = len(os.listdir(f'sprites/player/{animation}'))

            for i in range(frames):
                img = pygame.image.load(f'sprites/player/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.frame_list.append(temp_list)

        self.image = self.frame_list[self.action][self.frame_index]
        self.image2 = self.frame_list[self.action][self.frame_index]
        self.image3 = self.frame_list[13][0]
        self.rect = self.image.get_rect()
        self.collision_rect = self.image.get_bounding_rect()

        self.mask = pygame.mask.from_surface(self.image)
        
        self.width = self.collision_rect.width #THIS NEEDS TO CHANGE WHEN YOU CHANGE THE SPRITE SIZE
        self.height = self.collision_rect.height
       
        self.hitbox_rect = pygame.Rect(self.collision_rect.x + 2, self.collision_rect.y + 8, self.width - 4, self.height*0.75 - 6)

        self.BP_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.height, 2*self.rect.width)
        self.atk_rect = pygame.Rect(-32, -32, 0,0)#self.rect.x, self.rect.y, self.rect.height, 2*self.rect.width
        self.atk_rect_scaled = pygame.Rect(-32, -32, 0,0)
        
        self.m_player = music_player(['hat.wav', 'hat2.wav', 'step.wav', 'step2.wav', 'slash.wav', 'shoot.wav', 'slash2.wav', 'boonk.wav'], ini_vol)
        self.ini_vol = ini_vol
        self.play_sound_once_en = True
        
        self.disp_states = ( #actions/states when the player has a larger and or displaced hitbox
            False, #idle
            False, #run
            False, #jump
            False, #land
            False, #squat
            False, #hurt
            False, #die
            True, #atk1
            True, #atk1_2
            True, #roll
            True, #atk1_3
            True, #shoot
            False, #
            False, #
            False #turn_around
        )
       
    #methods
    

    def rotate(self, rate, angle):
        self.angle += rate
        if self.angle >= angle:
            self.angle = 0
        self.image = pygame.transform.rotozoom(self.image, self.angle, 1)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        if self.angle % 60 == 0:
            self.m_player.play_sound(self.m_player.sfx[random.randint(0,(len(self.m_player.sfx)-1))])

            
    def update_landing(self, the_sprite_group):
        
        if self.in_air != self.curr_state and not self.disp_flag and self.action != 1:#self.action < 5:
            if not self.in_air:
                particle = particle_(self.rect.centerx, self.rect.centery, -self.direction, self.scale, 'player_mvmt', True, 0, False)
                the_sprite_group.particle_group.add(particle)
                self.m_player.play_sound(self.m_player.sfx[2])
            else:
                particle = particle_(self.rect.centerx, self.rect.centery, -self.direction, self.scale, 'player_mvmt', True, 1, False)
                the_sprite_group.particle_group.add(particle)
            self.curr_state = self.in_air
            
    def particles_by_frame(self, particle_index, the_sprite_group, sound):
        if self.frame_index != self.last_frame:# or self.frame_index == 0:
            if not self.disp_flag: #self.action < 5:
                x = self.rect.centerx
            else:
                x = self.rect.right
            particle = particle_(x, self.rect.centery, -self.direction, self.scale, 'player_mvmt', True, particle_index, False)
            the_sprite_group.particle_group.add(particle)
            self.m_player.play_sound(self.m_player.sfx[sound])
        self.last_frame = self.frame_index
        
    def atk1_kill_hitbox(self):
        self.atk_show_sprite = False
        self.atk_rect.x = 0
        self.atk_rect.y = 0
        self.atk_rect.width = 0
        self.atk_rect.height = 0
        self.atk_rect_scaled  = self.atk_rect
        
    def atk1_set_hitbox(self, the_sprite_group):
        if (self.frame_index == 1 or self.frame_index == 2) and (self.action == 8 or self.action == 7):#(pygame.time.get_ticks() - self.update_time < 10)
            #adjust hitbox location for default atks
            self.atk_rect.width = self.collision_rect.height
            self.atk_rect.height = self.collision_rect.height
            if self.direction == -1:
                x_loc = self.collision_rect.left - 3*self.collision_rect.width//2
            else:
                x_loc = self.collision_rect.right - self.collision_rect.width//2
            #handling player mvmt and frames specific to atks and setting atk_rect (hitbox) location
            if self.action == 8:
                y_loc = self.collision_rect.y
                self.image3 = self.frame_list[13][0]
                x_loc += self.direction *16
            elif self.action == 7:
                x_loc += self.direction *2
                y_loc = self.collision_rect.y - self.width//4
                if self.frame_index == 1:
                    self.image3 = self.frame_list[13][2]
                elif self.frame_index == 2:
                    self.image3 = self.frame_list[13][3]
            
            self.atk_rect.x = x_loc
            self.atk_rect.y = y_loc
            self.atk_show_sprite = True#variable for displaying atk sprite in draw)
            
        elif (self.frame_index >= 1 and self.frame_index < 4) and (self.action==10):#adjust atk hitbox location for crit
            self.atk_show_sprite = False
            self.atk_rect.width = self.collision_rect.height*0.75
            self.atk_rect.height = self.collision_rect.height - 8*self.frame_index
            if self.flip:
                x_loc = self.collision_rect.x - (self.width + self.frame_index*2)
            else:
                x_loc = self.collision_rect.x + (self.width//2 + self.frame_index*2)
            y_loc = self.collision_rect.y + 4*self.frame_index
            
            self.atk_rect.x = x_loc
            self.atk_rect.y = y_loc
        else:#kill atk hitbox (h and w -> 0 and move to upper left)
            self.atk1_kill_hitbox()
        #adjusting atk hitbox size
        if self.action != 10:
            self.atk_rect_scaled  = self.atk_rect.scale_by(0.90)
        else:
            self.atk_rect_scaled  = self.atk_rect.scale_by(1)
            if (pygame.time.get_ticks() - self.particle_update > 200) and self.frame_index  < 3:
                self.particle_update = pygame.time.get_ticks()
                particle = particle_(self.rect.centerx, self.rect.centery, -self.direction, self.scale, 'player_crit', True, self.frame_index, False)
                the_sprite_group.particle_group.add(particle)
                i = 0
                for i in range(5):
                    particle2 = particle_(self.rect.centerx + random.randrange(-48,48), self.rect.centery + random.randrange(-48,48), -self.direction, 0.3*self.scale, 
                                          'player_bullet_explosion', True, random.randrange(0,3), False)
                    the_sprite_group.particle_group.add(particle2)
                    i+= 1

                
    def atk1_grinding(self, rect, the_sprite_group):
        disp = 0
        if not self.flip and self.action != 10:
            disp = 12
        elif self.flip and self.action != 10:
            disp = -12
        else:
            disp = 0
        if rect.colliderect(self.atk_rect_scaled) and self.frame_index == 1 and pygame.time.get_ticks() - self.update_time < 10:
            x_loc = (rect.centerx + self.atk_rect.centerx)//2 + disp
            y_loc = (rect.centery + self.atk_rect.centery)//2
            particle = particle_(x_loc, y_loc, -self.direction, 0.9*self.scale, 'player_bullet_explosion', False, random.randrange(0,3), False)
            the_sprite_group.particle_group_fg.add(particle)
    
    
    def do_entity_collisions(self, the_sprite_group, obj_list, level_transitioning):
        #----------------------------------------------entity collisions
        damage = 0
        if ((self.action < 7 or self.action > 10) and not self.i_frames_en and not self.hurting and self.Alive and not level_transitioning):
            #sprite based collisions
            for enemy in enumerate(the_sprite_group.hostiles_group):
                if pygame.sprite.spritecollide(self, enemy[1], False): 
                    if pygame.sprite.spritecollide(self, enemy[1], False, pygame.sprite.collide_mask):
                        # if enemy[1] == the_sprite_group.enemy0_group:
                        #     print(enemy)
                        if enemy[1] == the_sprite_group.enemy_bullet_group:
                            damage += 3
                            self.hurting = True
                            self.take_damage(damage)
                        if enemy[1] == the_sprite_group.enemy_bullet_group2:
                            damage += 2
                            self.hurting = True
                            self.take_damage(damage)
                        if enemy[1] == the_sprite_group.p_int_group2:
                            #print(pygame.time.get_ticks())
                            damage += self.hp//2
                            self.hurting = True
                            self.take_damage(damage)
                    #print(damage)
                damage = 0

            #rect based collisions
            for enemy in obj_list[0]:
                if (self.hitbox_rect.colliderect(enemy.atk_rect_scaled)):
                    damage += 1.5
                    self.hurting = True
                    self.take_damage(damage) 
                damage = 0
                
    def do_obj_list_collisions(self, obj_list, dx, dy, the_sprite_group):
        in_air = self.in_air
        for p_int in obj_list[1]:
            if p_int.collision_and_hostility[p_int.type][0]:
                #self.atk1_grinding(p_int.rect, the_sprite_group)
                #y collisions
                if (p_int.rect.colliderect(self.collision_rect.x+2, self.collision_rect.y + dy, self.width-4, self.height)):
                    if self.collision_rect.bottom >= p_int.rect.top and self.collision_rect.bottom <= p_int.rect.y + 32:
                        in_air = False
                        self.vel_y = 0.5
                        dy = p_int.vel_y
                        dx += p_int.vel_x
                        if self.collision_rect.bottom != p_int.rect.top:
                            dy -= self.collision_rect.bottom- p_int.rect.top
                    elif self.collision_rect.top <= p_int.rect.bottom and self.collision_rect.top >= p_int.rect.y + 32 and p_int.vel_y >= 0:
                        dy = p_int.vel_y
                        self.vel_y = 0.5
                    else:
                        in_air = True

                #x collisions
                if (p_int.rect.colliderect(self.collision_rect.x + dx, self.collision_rect.y+2, self.width, self.height- 2)):
                    if self.collision_rect.x > p_int.rect.x and self.collision_rect.right < p_int.rect.right:
                        dx = 0
                    else:
                        dx = -dx + p_int.vel_x
                elif (self.action != 9
                    and self.disp_flag #and self.action == 67
                    and p_int.rect.colliderect(self.collision_rect.x + self.direction*self.width//2 + dx, self.collision_rect.y+2, self.width, self.height - 2)
                    ):
                    dx = -16*self.direction
                elif (self.action == 9
                      and p_int.rect.colliderect(self.collision_rect.x + dx, self.collision_rect.y + 16, self.width, self.height - 16)
                    ):
                    dx = -dx + p_int.vel_x
                
                if not (p_int.rect.colliderect(self.collision_rect.x, self.collision_rect.y + dy, self.width, self.height)):
                    self.in_air = True
                
                    
            #taking damage from crushing traps
            if p_int.collision_and_hostility[p_int.type][1]:
                rate = 0.5
                if (self.hitbox_rect.colliderect(p_int.atk_rect)):
                    if self.hits_tanked + rate > self.hp:
                        self.hits_tanked = self.hp
                    else:
                        self.hits_tanked += rate
                        
            for obj in obj_list[2]:
                if self.collision_rect.colliderect(obj.rect) and self.action == 0 and dx == 0:
                    self.dialogue_trigger_ready = True
                #     #print(obj.name)
                # else:
                #     self.dialogue_trigger_ready = False
                
        return (dx, dy, in_air)
            
    def do_tile_collisions(self, world_solids, the_sprite_group, dx, dy, obj_list):
        lvl_transition_flag = False
        lvl_transition_data = []
        dxdy = self.do_obj_list_collisions(obj_list, dx, dy, the_sprite_group)
        
        dx = dxdy[0]
        dy = dxdy[1] 
        self.in_air = dxdy[2]
        #self.hitting_wall = False
        
        
        #size adjust for displaced rects
        if self.direction < 0:
            disp_x = -self.width//2
        else:
            disp_x = self.width//2
        
        for tile in world_solids:
            #x collisions
            if (tile[2] != 17 and tile[2] != 10 and tile[2] != 2):
                self.atk1_grinding(tile[1], the_sprite_group)
                    
                #dx collisions, tile walls
                
                #hitting wall while rolling
                if self.action == 9 and tile[1].colliderect(self.collision_rect.x + dx, self.collision_rect.y + self.height//2 + dy, self.width, self.height//4 - 2):
                    dx = -1 * self.direction 
                    self.rolled_into_wall = True
                    self.hitting_wall = True
                    if self.frame_index > 0:
                        if self.rolling:#you can die via concussion now
                            self.m_player.play_sound(self.m_player.sfx[7])
                            if self.stamina_used >= 5:
                                self.hits_tanked += 0.1
                                if random.randint(1,69) == 69:
                                    self.brain_damage = True
                        self.rolling = False
                    #self.debuggin_rect  = (self.collision_rect.x + dx, self.collision_rect.y + self.height//2 + dy, self.width, self.height//4 - 2)
                
                #displaced hitbox x collisions
                elif (self.action != 9
                    and self.disp_flag #and self.action == 67
                    and tile[1].colliderect(self.collision_rect.x + disp_x + dx, self.collision_rect.y, self.width, self.height - 17)
                    ):
                    dx = -16*self.direction
                    self.hitting_wall = True
                
                #wall collisions while NOT rolling
                elif (tile[1].colliderect(self.collision_rect.x + dx, self.collision_rect.y, self.width, self.height - 17) 
                    and self.action != 9 #this line is important for consistency
                    ):
                    dx = 0
                    self.hitting_wall = True
                    #print(self.hitting_wall)
                    
                    if (tile[1].colliderect(self.collision_rect.x, self.collision_rect.y, self.width, self.height - 17) 
                        #and self.vel_y > 0
                        ):
                        if dx < 0:
                            dx = 8*self.direction
                        elif dx > 0:
                            dx = -8*self.direction
                    # self.in_air = False
                    # self.curr_state = False
                    #self.landing = False
                else:
                    self.hitting_wall = False
                        
                #dy collision stuff, sinking through tiles etc
                
                if (tile[1].colliderect(self.collision_rect.x + 1, self.collision_rect.y + dy, self.width - 2, self.height)
                    #and not self.disp_flag
                    ):

                    if self.vel_y >= 0 or not dxdy[2]: #making sure gravity doesn't pull player under the tile
                        self.vel_y = 0
                    elif self.vel_y < 0 and dxdy[2]: #prevents player from gliding on ceiling
                        self.vel_y *= 0.5
                        self.in_air = True
                        self.squat = False
                        
                    if (self.action == 9): #rolling collisions
                        if (tile[1].y > self.collision_rect.y + self.height -32): #lower collisions
                            dy = tile[1].top  - self.rect.bottom 
                        elif (tile[1].bottom < self.collision_rect.y + self.height -32): #upper collisions
                            dy = tile[1].bottom  - self.rect.top
                            
                    else: #IMPORTANT---------------------default floor and ceiling collisions
                        #basically there's 2 collision checks that each make up half of the collision rect, upper and lower
                        
                        if tile[1].colliderect(self.collision_rect.x + 1, self.collision_rect.y + self.height//2 + dy, self.width - 2, self.height//2):
                            dy = tile[1].top  - self.rect.bottom #-1
                            self.rolled_into_wall = False
                            self.in_air = False
                            
                        elif tile[1].colliderect(self.collision_rect.x + 1, self.collision_rect.y + dy, self.width - 2, self.height//2):
                            dy = tile[1].bottom  - self.rect.top
                elif  (not tile[1].colliderect(self.collision_rect.x, self.collision_rect.y + dy, self.width , self.height)
                        and not self.in_air
                        and self.vel_y > 6 #velocity based coyote jump
                        ):
                    self.curr_state = True
                    self.in_air = True
                    self.squat = False
                    
                            
            #special tiles
            elif(tile[2] == 2):#spikes/ other trap tiles
                if tile[1].colliderect(self.collision_rect.x + self.width//4 + dx, self.collision_rect.y + dy, self.width//2, self.height - 8):
                    self.hits_tanked = 6
            
            elif(tile[2] == 17):#one way tiles
                if tile[1].colliderect(self.collision_rect.x, self.collision_rect.bottom - 16 + dy, self.width, 18):
                    if self.vel_y >= 0: 
                        self.vel_y = 0
                        self.in_air = False
                    elif self.vel_y < 0:
                        self.vel_y *= 0.8#velocity dampening when passing thru tile
                        self.in_air = True

                    dy = tile[1].top - self.collision_rect.bottom
                    self.rolled_into_wall = False
                           
            elif(tile[2] == 10 and not self.disp_flag):#level transition tiles
                if tile[1].colliderect(self.collision_rect.x + dx, self.collision_rect.y + dy, 2, self.height):
                    #this collision will be used to initiate a level change
                    #tile[3][0]: next_level, [1]: player new x, [2]: player new y
                    lvl_transition_flag = True
                    lvl_transition_data = tile[3]

        
        #debuggin bottom boundary
        if self.rect.bottom + dy > 480:
            dy = 480 - self.rect.bottom
            self.in_air = False
            

            
            
        return (dx, dy, (lvl_transition_flag, lvl_transition_data))
    
    def move(self, pause_game, moveL, moveR, world_solids, world_coords, world_limit, x_scroll_en, y_scroll_en, screenW, screenH, obj_list, the_sprite_group):
        #reset mvmt variables
        self.dialogue_trigger_ready = False
        self.collision_rect.x = self.rect.x + self.width
        self.collision_rect.y = self.rect.y
        
        if self.Alive == False or pause_game:
            dx = 0
        dx = 0
        dy = 0
        self.scrollx = 0
        #move
        if self.action == 1 and self.frame_index%2 == 0:
            self.particles_by_frame(self.frame_index//2 + 2, the_sprite_group, 3)
        
        if not self.disp_flag and self.action != 5: #self.action < 5:# and self.rolled_into_wall == False:
            if moveL:
                dx = -self.speed
                self.flip = True
                self.direction = -1
            if moveR:
                dx = self.speed
                self.flip = False
                self.direction = 1
            if (moveL or moveR) or self.action == 1:
                self.landing = False
                
        elif self.action == 5:#taking damage, hurting----------------------
            if self.frame_index < 3:
                self.hurting = True #perpetuates the action for the entire animation after the collision has ended

        elif self.action == 10: #disables jumping during crit
            if self.action == 10:
                self.squat = False
            
        elif self.action == 9:
            self.squat_done = False
        elif self.action == 6:
            dx = 0
            
        #does not work   
        # if self.direction != self.last_direction and not self.in_air and not (moveL and moveR):
        #     self.last_direction = self.direction
        #     self.flip = not self.flip
        #     self.change_direction = True
        #     dx = 0




		#rolling 
        if self.rolling and not self.hurting:
            if self.flip:
                dx = -(self.speed + 2)
            else:
                dx = (self.speed + 2)
            
            if ((moveL and self.direction == 1) or (moveR and self.direction == -1) #BREAK ROLLING
                or self.squat
                or self.stamina_used + self.roll_stam_rate > self.stamina
                or (self.atk1)# and ((self.action == 7 or self.action ==8) and self.frame_index < 2))
                or self.roll_count >= self.roll_limit
                #or self.rolled_into_wall
                ):
                if (self.action != 7 and self.action != 8):
                    self.rolling = False
                    #self.roll_count = self.roll_limit
                
        #------------------------------------------------------------------------------------------------------------------------------------------------------
        #atk1------------------------------------------------------------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------------------------

        
        if self.atk1 and not self.hurting:#adjusting speed to simulate momentum, motion stuff
            self.curr_state = self.in_air
            #if not break atk1
            if (not (((moveL and self.direction == 1) or (moveR and self.direction == -1)) and self.frame_index > 2) 
                and not (self.rolling and self.frame_index > 2) 
                and not (self.squat and self.frame_index > 2)
                ): #not (self.rolling) and 
                
                if (self.frame_index == 0 and self.rolled_into_wall == False):#fast initial impulse
                    # if pygame.time.get_ticks() < self.update_time + 20:
                    #     self.m_player.play_sound(self.m_player.sfx[1])
                    if self.crit:
                        dx = self.direction * 4 * self.speed
                        if self.in_air and self.vel_y + 5 <= 20:
                            self.vel_y += 5
                    else:
                        if moveL or moveR:
                            multiplier = 2
                        else:
                            multiplier = 1
                        dx = self.direction * (multiplier * (self.speed) + 2)
                        
                        if self.action == 7:
                            self.vel_y -= 0.6
                        elif self.action == 8 and self.vel_y + 7 <= 28 and self.vel_y > 0 and self.in_air: #25 max 
                            self.vel_y += 7

                elif self.frame_index > 1 :# slow forward speed
                    if self.crit:
                        dx = self.direction * 2
                    else:
                        if (moveL and self.direction == 1) or (moveR and self.direction == -1):
                            dx = 0
                        else:
                            dx = self.direction
            
                #drawing atk sprite and setting hitboxes            
                self.atk1_set_hitbox(the_sprite_group)
            else:
                self.atk1_kill_hitbox()
                self.atk1 = False
                self.crit = False
        else:
            self.atk1_kill_hitbox()
            self.atk1 = False
            self.crit = False

        #==========================================================================================================================================
        
        #jump
        if (self.jump == True and self.in_air == False) or self.squat_done == True:
            # if self.squat_done == False:
            #     self.squat = True
            if self.squat_done == True and not(self.atk1):
                
                self.squat_done = False
                self.vel_y = -9.5
                self.in_air = True
                
        elif self.in_air and not (moveL or moveR):
            if self.action != 8 and self.action != 10 and self.action != 1 and self.action != 5:
                self.landing = True
            else:
                self.landing = False
                
        if self.jump_dampen:
            if self.squat or (self.squat_done and self.in_air):
                self.vel_y *= 0.4
                
            elif self.vel_y <= -1: #minimum jump velocity
                self.vel_y *= 0.4
            self.in_air = True
            self.squat_done = False
            self.squat = False
            self.jump_dampen = False
            
        if self.action == 3 or self.action == 1 or self.action == 0:
            self.jump_dampen = False
            self.in_air = False
        
        #land
        
        self.update_landing(the_sprite_group)
        
        #shooting
        if self.action == 11:
            if self.frame_index == 3:
                dx += -(5) * self.direction#recoil
                
                if not self.shoot_recoil:#playing sound
                    self.m_player.play_sound(self.m_player.sfx[5])
                    self.vel_y = 0
                self.shoot_recoil = True
            else:
                dx += -self.extra_recoil * self.direction
                self.extra_recoil = 0
                
                self.shoot_recoil = False
            #print(dx)
            
            #self.vel_y *= 0.5
                
        #make this scale with the charge
            
        #hurting/ enemy collisions
        if self.hurting and not self.rolling:
            if not self.hitting_wall and self.frame_index < 2:
                dx -= self.direction * 4
                self.do_screenshake = True
                self.screenshake_profile = (-1, 3, 2)
            elif self.hitting_wall:
                dx = 0
            
            # elif self.frame_index > 1:
            #     dx = -self.direction * 2

        #gravity
        
        
        if self.vel_y <= 25:#25 = terminal velocity
            self.vel_y += 0.6
        if self.shoot and self.frame_index == 2:
            self.vel_y *= 0.8
        dy = self.vel_y
        
        
        #--------------------------------------------------------------coordinate test
        #USED FOR CAMERA SCROLLING
        for tile in world_coords:
            if tile[0].colliderect(self.collision_rect.x + dx, self.collision_rect.y + dy, 1, 1):
                x_coord = tile[1][0]
                y_coord = tile[1][1]
                if self.x_coord != x_coord or self.y_coord != y_coord:
                    self.x_coord = x_coord
                    self.y_coord = y_coord
                    #curr_coord = (self.x_coord, self.y_coord)
                    #print(curr_coord)

        #---------------------------------------------------------world boundaries------------------------------------------------------------------
        if self.collision_rect.x < 0:
            dx = 1
        elif self.x_coord >= world_limit[0]:
            dx = -1
        
        #----------------------------------------------------------------------------------------------------------------------------------
        #================================================================TILE COLLISIONS=====================================================================
        #====================================================================================================================================
        if self.brain_damage or self.angle != 0:
            dxdy = (0,0)
            lvl_transition_flag_and_data = (False, [])
        else:
            dxdy = self.do_tile_collisions(world_solids, the_sprite_group, dx, dy, obj_list)
            
        dx = dxdy[0]
        dy = dxdy[1]
        lvl_transition_flag_and_data = dxdy[2]

        #update pos------------------------------------------------------------------------------------------------------------------------

        self.rect.y += dy
        self.hitbox_rect.centery = self.rect.centery #don't delete, keeping hitbox rect on the player is used by the camera and enemies alike
        
        #rudimentary scrolling adjust====================================================================================================================
        if self.Alive:
            if x_scroll_en:
                if self.x_coord < screenW//2 or self.shoot_recoil or self.hurting: 
                    self.rect.x += dx
                elif self.x_coord >= world_limit[0] - (screenW//2 + 32) or self.shoot_recoil or self.action == 5:
                    self.rect.x += dx
                elif self.x_coord >= screenW//2  and self.x_coord < world_limit[0] - (screenW//2 - 16): 
                    self.scrollx = dx
            else:
                self.rect.x += dx
        else:
            dx = 0
            #self.scrollx

        self.hitbox_rect.centerx = self.collision_rect.centerx
        
        if self.brain_damage or self.angle != 0:
            self.rotate(5, 360)
            
        return lvl_transition_flag_and_data

    #method for status bars, can probably return a list---------------------------    
    def get_status_bars(self):
        hp_remaining = self.hp - self.hits_tanked
        hp_ratio = hp_remaining/self.hp
        
        stamina_remaining = self.stamina - self.stamina_used
        stamina_ratio = stamina_remaining/self.stamina
        
        if self.shot_charging == True:
            charge_start = self.stamina - self.ini_stamina
            charge_ratio = charge_start/self.stamina
        else:
            charge_ratio = 0
            
        #print(stamina_remaining)
        return [hp_ratio, stamina_ratio, charge_ratio]
        
    #i frames method    -----------------------------------------------------------------------------------------
    def i_frames(self, i_frames_duration, update_time):
        #i_frames_duration = 736
        if self.i_frames_en:
            if pygame.time.get_ticks() - update_time > i_frames_duration:
                self.i_frames_en = False
                self.flicker = False
            else:
                self.i_frames_en = True
        

    def stamina_regen(self):
        if (self.shot_charging == False):
            rate = 80
            # if self.rolling:
            #     unit = -0.05
            # else:
            if self.speed > self.default_speed and not self.rolling:
                unit = -0.12
            elif self.rolling and self.stamina_used + self.roll_stam_rate <= self.stamina:
                unit = self.roll_stam_rate
            else:
                unit = -0.22
            # if self.action >= 7 and self.frame_index <= 1:
            #     unit = 0
            # else:
            #     unit = -0.25
            
                
            self.ini_stamina = self.stamina_used
            
            if self.stamina_used + unit >= 0:
                boolean = True
            elif (self.stamina_used > 0 and self.stamina_used + unit <= 0):
                self.stamina_used = 0
                boolean = False
            else:
                boolean = False
        else:
            rate = 150
            unit = 0.15
            self.charge_built = self.stamina_used - self.ini_stamina
            if self.stamina_used + unit <= self.stamina:
                boolean = True
            else:
                boolean = False
            
        if boolean: 
            if pygame.time.get_ticks() - self.update_time3 > rate:
                self.update_time3 = pygame.time.get_ticks()
                self.stamina_used += unit
                
    def take_damage(self, damage):
        self.hits_tanked += damage
        if self.hits_tanked >= self.hp:#killing the player------------------------------------------------
            self.hits_tanked = self.hp
            self.Alive = False
            self.hurting = False
            
    
    #drawing during game and animations----------------------------------------
    def BP_animate(self):

        if self.shot_charging:
            animation_index = 12
            #update particle rect location
            self.BP_rect.centerx = self.collision_rect.centerx
            self.BP_rect.centery = self.collision_rect.centery + 64
        #set image
        self.image2 = self.frame_list[animation_index][self.frame_index2]
        
        #update frame
        if pygame.time.get_ticks() - self.BP_update_time > self.frame_updateBP:
            self.BP_update_time = pygame.time.get_ticks()
            self.frame_index2 += 1 
        
        #loop frame
        if self.frame_index2 >= len(self.frame_list[animation_index]):
            self.frame_index2 = 0
            # if self.frame_updateBP >= 50:
            #     self.frame_updateBP -= 15
            if self.frame_updateBP >= int(self.stamina_used * 20):
                self.frame_updateBP -= int(self.charge_built * 10)
    
    
    def animate(self, the_sprite_group):
        self.mask = pygame.mask.from_surface(self.image)
        
        framerates = (
            200, #idle
            160, #run
            145, #jump
            80, #land
            20, #squat
            50, #take damage
            145, #die
            105, #upstrike
            105, #downstrike
            100, #roll
            110, #crit
            85, #shoot
            145, #idk
            100
        )
        #everything speeds up when pressing alt/sprint except shooting at the cost of slower stamina regen
        adjustment = 0
        if self.sprint and self.action != 11 and self.action != 6: 
            adjustment = 12
        else:
            adjustment = 0
        frame_update = framerates[self.action] - adjustment
        
        if not self.disp_flag: #self.action != 9 and self.action != 7 and self.action != 8 and self.action != 10:
            self.roll_count = 0
		
        #regen
        if self.Alive:
            self.stamina_regen()
        else:
            self.stamina_used = self.stamina
        
        #update frame
        if self.i_frames_en:
            self.i_frames(self.i_frames_time, self.update_time2)

        #setting the image
        self.image = self.frame_list[self.action][self.frame_index]
        
        
        #change frame index---------------------------------------------------------------
        if pygame.time.get_ticks() - self.update_time > frame_update:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1 

        #END OF ANIMATION FRAMES    
        if self.frame_index >= len(self.frame_list[self.action]):
            self.landing = False
            if self.action != 5 and self.action != 6:
                self.frame_index = 0

            if self.action == 14:
                self.change_direction = False
    
            if self.action == 5:
                self.hurting = False
                self.i_frames_en = True #triggers i_frames for next tick
                self.update_time2 = pygame.time.get_ticks()
                self.i_frames_time = 836
                self.flicker = True

            if self.action == 4:
                self.squat_done = True #squatting finished when it loops frames
                self.squat = False

            if self.action == 7 or self.action == 8 or self.action == 10:
                
                #self.squat = False #this line will cancel jumps that have been inputted before the atk
                
                if self.action == 7:
                    self.atk1_alternate = False
                elif self.action == 8:
                    self.atk1_alternate = True
                elif self.action == 10:
                    self.crit = False
                self.landing = False
                self.atk1 = False
                    
            if self.action == 9: 
                #self.image = pygame.image.load('sprites/player/end_of_roll/0.png') #this fucks everything do not add back
                if self.roll_count == self.roll_limit:# or self.rolled_into_wall:#roll limit, this ends up getting incremented once more after 
                    self.rolling = False
                self.roll_count += 1
                self.rolled_into_wall = False
            
            if self.action == 6:
                self.frame_index = 5   
                
            if self.action == 11:
                self.shoot = False
                self.ini_cost_spent = False
                #spawn bullet---------------------------------------------------------------------------------------------
                if self.flip == False:
                    x = self.rect.right + 0
                else:
                    x = self.rect.left - 32
                y = int(self.rect.y + 0.25 * self.height)
                player_bullet = bullet_(x, y, 20, self.direction, self.scale, 'player_basic', self.ini_vol)
                the_sprite_group.player_bullet_group.add(player_bullet)
                self.charge_built -= 2
                
                i = 0
                while self.charge_built - 0.35 > 0:
                    i+= 1
                    self.charge_built -= 0.35
                    #x+= self.direction * 32
                    if i < 4:
                        x+= self.direction * 32
                    else:
                        x-= self.direction * 24
                    if i%2 == 0:
                        y += (i)
                    else:
                        y -= (i)
                    player_bullet = bullet_(x , y, 20, self.direction, self.scale, 'player_basic', self.ini_vol)
                    the_sprite_group.player_bullet_group.add(player_bullet)
                
                self.extra_recoil = i*3
                self.charge_built = 0
                
                self.roll_count = 3
                
                self.rolling = False
    
    def draw(self, p_screen):
        if self.shot_charging and self.action < 5:
            self.BP_animate()
            p_screen.blit(pygame.transform.flip(self.image2, self.flip, False), self.BP_rect)
        
        # pygame.draw.rect(p_screen, (0,0,255), self.collision_rect)
        # pygame.draw.rect(p_screen, (255,0,0), self.hitbox_rect)
        # pygame.draw.rect(p_screen, (0,255,0), self.atk_rect_scaled)
        # pygame.draw.rect(p_screen, (0,0,255), self.debuggin_rect)
        
        if self.flicker == False:
            p_screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        else: 
            if pygame.time.get_ticks()%2 == 0:
                p_screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
                
        if self.atk_show_sprite:
            p_screen.blit(pygame.transform.flip(self.image3, self.flip, False), self.atk_rect)
        
    
    
    def update_action(self, new_action):
        #check if action has changed
        if new_action != self.action:
            if (self.action == 7 or self.action == 8) and (self.rolling or self.action == 9):
                self.crit = False
                self.atk1 = False
            elif self.action == 9 and (new_action == 7 or new_action == 8) and self.atk1:
                self.crit = True
                self.do_screenshake = True
                self.screenshake_profile = (16, 6, 2)
                self.m_player.play_sound(self.m_player.sfx[4])
            elif self.action != 9 and (new_action == 7 or new_action == 8):
                self.crit == False
                self.m_player.play_sound(self.m_player.sfx[1])
            elif new_action == 5:
                print("oof") #make player hurting sound

            self.action = new_action
            self.disp_flag = self.disp_states[self.action]
            
            #update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            #update stamina bar
            #should play a sound when there's no stamina
            if new_action == 7 or new_action == 8:
                self.stamina_used += 1
                self.ini_stamina += 1
            if new_action == 9:
                self.stamina_used += self.roll_stam_rate
                self.ini_stamina += self.roll_stam_rate
        
        if self.shot_charging == True and self.ini_cost_spent == False:
            self.stamina_used += 2
            self.ini_cost_spent = True
            
        

                

