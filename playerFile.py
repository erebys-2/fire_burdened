import pygame
import os
from bullet import bullet_ #type: ignore
from music_player import music_player #type: ignore
from ItemFile import inventory_handler
from textfile_handler import textfile_formatter
import math
import random
#print('directory: ' + os.getcwd())

class player(pygame.sprite.Sprite):
    #constructors
    def __init__(self, x, y, speed, hp, stamina, hits_tanked, stamina_usage_cap, ini_vol, camera_offset):
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
        self.dx = 0
        self.dy = 0

        self.squat = False
        self.squat_done = False
        self.jump_dampen = False
        self.double_jump = False
        self.double_jump_en = False
        self.coyote_vel = 12
        self.coyote_ratio = 0
        self.hold_jump = False
        self.upstrike = False

        self.in_air = False
        
        self.vel_y = 0
        self.landing = False
        self.curr_state = self.in_air #for particles ...again
        self.jump_counter = 0

        self.atk1_alternate = False
        self.atk1 = False
        self.atk_show_sprite = False
        self.draw_trail = False
        self.trail_coords = []
        self.consecutive_upstrike = 0
        self.upstrike_limit = 2

        
        self.melee_hit = False
        self.inst_stamina = 1.5
        
        self.disp_flag = False
        self.curr_disp_flag = False

        self.rolled_into_wall = False
        
        self.hurting = False
        self.hits_tanked = hits_tanked
        self.i_frames_en = False
        self.crit = False
        self.heavy = False
 
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
        self.roll_stam_rate = 0.22
        self.hitting_wall = False
        
        self.wall_slide = False
        self.hitting_wall2 = False
        
        self.using_item = False
        self.finished_use_item_animation = False
        
        self.sprint = False
        self.change_direction = False
        self.last_direction = self.direction
        
        self.hp = hp
        self.stamina = stamina
        self.stamina_usage_cap = stamina_usage_cap
        self.stamina_used = 0
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

        self.hitting_wall_timer = pygame.time.get_ticks()
        self.coyote_time = pygame.time.get_ticks()
        
        self.angle = 0
        
        self.dialogue_trigger_ready = False

        #fill animation frames
        animation_types = ('idle', 'run', 'jump', 'land', 'squat', 'hurt', 
                           'die', 'atk1', 'atk1_2', 'roll', 'atk1_3', 'shoot',
                           'charging', 'atk1_2_particle', 'turn_around', 'use_item', 'atk1_4', 'wall_slide', 
                           'atk1_5', 'jump_up', 'jump_down', 'flip', 'sprint', 'throw', 'upstrike')
        
        
        #print(os.listdir(f'sprites/player'))
        base_path = os.path.join('assets', 'sprites', 'player')
        for animation in animation_types:
            temp_list = []
            frames = len(os.listdir(os.path.join(base_path, animation)))

            for i in range(frames):
                img = pygame.image.load(os.path.join(base_path, animation, f'{i}.png')).convert_alpha()
                img = pygame.transform.hsl(img, 10.1, 0.3, 0.11)
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.frame_list.append(temp_list)

        self.image = self.frame_list[self.action][self.frame_index]
        self.image2 = self.frame_list[self.action][self.frame_index]
        self.image3 = self.frame_list[13][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x_coord + 32, self.y_coord)
        self.collision_rect = self.image.get_bounding_rect()

        self.mask = pygame.mask.from_surface(self.image)
        
        self.width = self.collision_rect.width 
        self.half_w = self.width//2
        self.qrtr_w = self.width//4
        self.height = self.collision_rect.height
        self.half_h = self.height//2
        self.qrtr_h = self.height//4
        
        self.hitbox_rect = pygame.Rect(self.collision_rect.x + 4, self.collision_rect.y + 8, self.width - 8, self.height*0.75 - 6)

        self.BP_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.height, 2*self.rect.width)
        self.atk_rect = pygame.Rect(-32, -32, 0,0)#self.rect.x, self.rect.y, self.rect.height, 2*self.rect.width
        self.atk_rect_scaled = pygame.Rect(-32, -32, 0,0)
        
        self.m_player = music_player(['hat.mp3', 'hat2.mp3', 'step.mp3', 'step2.mp3', 'slash.mp3', 'shoot.mp3', 'slash2.mp3', 'boonk.mp3', 'woop.mp3', 'woop2.mp3'], ini_vol)
        self.ini_vol = ini_vol
        self.play_sound_once_en = True
        
        self.action_dict = {#invulnerable, disp, framerate
            0: (False, False, 200), #idle
            1: (False, False, 100), #run160
            2: (False, False, 145), #jump
            3: (False, False, 90), #land
            4: (False, False, 15), #squat
            5: (True, False, 50), #take damage
            6: (True, True, 145), #die
            7: (True, True, 100), #upstrike
            8: (True, True, 100), #downstrike
            9: (True, False, 100), #roll
            10: (True, True, 110), #crit
            11: (False, False, 85), #shoot
            12: (False, False, 145),
            13: (False, False, 145),
            14: (False, False, 145),
            15: (False, False, 120), #use item
            16: (False, True, 130), #heavy
            17: (False, False, 200), #wall slide
            18: (True, True, 105), #slide kick
            19: (False, False, 145), #jump up
            20: (False, False, 145), #jump down
            21: (True, False, 100), #flip
            22: (False, False, 100), #sprint
            23: (False, True, 100), #throw
            24: (True, True, 90) #upstrike
        }
        self.is_invulnerable = {key:self.action_dict[key][0] for key in self.action_dict}
        self.disp_states = {key:self.action_dict[key][1] for key in self.action_dict}
        self.framerates = {key:self.action_dict[key][2] for key in self.action_dict}

        
        t = textfile_formatter()
        config_path = os.path.join('assets', 'config_textfiles', 'player_config')
        stamina_ini_cost_dict = t.str_list_to_dict(t.read_text_from_file(os.path.join(config_path, 'player_stamina_base_costs_config.txt')), 'float')
        self.len_action_history = 4
        self.action_history = [-1]*self.len_action_history
        self.recovery_counter = 1
        
        self.atk1_stamina_cost = stamina_ini_cost_dict['atk1']
        self.atk1_default_stam = self.atk1_stamina_cost
        self.roll_stamina_cost = stamina_ini_cost_dict['roll']
        self.shoot_stamina_cost = stamina_ini_cost_dict['shoot']
        
        self.char_level = 0
        self.char_dict = t.str_list_to_dict(t.read_text_from_file(os.path.join(config_path, 'player_char.txt')), 'float')
        

        self.inventory_handler = inventory_handler(10)
        
        self.camera_offset = camera_offset
        
        self.in_cutscene = False
        self.current_npc_enabled = False
        
        self.slide_kick = False
        self.lvls_visited = set([0,1])
       
    #methods
    def cancel_shoot(self):
        self.shoot = False
        self.charge_built = 0
    
    def update_action_history(self, action):
        if action != 0 and action != 1:# and action != 4: 
            self.action_history.append(action)
            if len(self.action_history) > 4:#pop first element if the list goes over 4
                self.action_history.pop(0)
            #print(self.action_history)
                
    def check_atk1_history(self):
        count = 0
        for action in self.action_history:
            if action in (7,8,16):
                count += 1
        return count
        

    def rotate(self, rate, angle):
        self.angle += rate
        if self.angle >= angle:
            self.angle = 0
        self.image = pygame.transform.rotozoom(self.image, self.angle, 1)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        if self.angle % 60 == 0:
            self.m_player.play_sound(self.m_player.sfx[random.randint(0,(len(self.m_player.sfx)-1))], None)

            
    def update_landing(self, the_sprite_group):
        
        if not self.wall_slide:
            if self.in_air != self.curr_state and not self.disp_flag and self.action != 1 and not self.in_cutscene and self.Alive:
                if not self.in_air:
                    the_sprite_group.particle_group.sprite.add_particle('player_mvmt', self.rect.centerx, self.rect.centery, self.direction, self.scale, True, 0)
                    self.m_player.play_sound(self.m_player.sfx[2], None)
                # else:
                #     the_sprite_group.particle_group.sprite.add_particle('player_mvmt', self.rect.centerx, self.rect.centery, self.direction, self.scale, True, 1)
                self.curr_state = self.in_air
                
    def particles_by_frame(self, particle_index, the_sprite_group, sound):
        if self.frame_index != self.last_frame:
            # if not self.disp_flag or self.action == 18: 
            #     x = self.rect.centerx
            # else:
            #     x = self.rect.right
            x = self.rect.centerx
                
            scale = self.scale
            y = self.rect.centery
            if self.sprint:
                scale = self.scale * 1.5
                y -= 16
            the_sprite_group.particle_group.sprite.add_particle('player_mvmt', x + self.direction*scale, y, self.direction, scale, True, particle_index)
            if sound > 0:
                self.m_player.play_sound(self.m_player.sfx[sound], None)
        self.last_frame = self.frame_index
        
    def atk1_kill_hitbox(self):
        self.melee_hit = False
        self.atk_show_sprite = False
        self.atk_rect.x = 0
        self.atk_rect.y = 0
        self.atk_rect.width = 0
        self.atk_rect.height = 0
        self.atk_rect_scaled  = self.atk_rect
        
    def atk1_set_hitbox(self, the_sprite_group):
        if (self.frame_index == 1 or self.frame_index == 2) and self.action in (7,8,24):
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
                x_loc += self.direction *12
            elif self.action == 7:
                x_loc += self.direction * 2
                y_loc = self.collision_rect.y - self.qrtr_w# - 4
                if self.frame_index == 1:
                    self.image3 = self.frame_list[13][2]
                elif self.frame_index == 2:
                    self.image3 = self.frame_list[13][3]
            elif self.action == 24:
                y_loc = self.collision_rect.y - self.qrtr_w - 4
                if self.frame_index == 1:
                    self.image3 = self.frame_list[13][2]
                elif self.frame_index == 2:
                    self.image3 = self.frame_list[13][3]
            self.atk_rect.x = x_loc
            self.atk_rect.y = y_loc
            self.atk_show_sprite = True#variable for displaying atk sprite in draw)
        elif self.action == 16 and self.frame_index == 1:
            self.atk_rect.width = self.collision_rect.height * 1.25
            self.atk_rect.height = self.collision_rect.height * 1.25
            if self.direction == -1:
                x_loc = self.collision_rect.left - 9/4*self.collision_rect.width
            else:
                x_loc = self.collision_rect.right - self.collision_rect.width/4
            x_loc += self.direction *4
            y_loc = self.collision_rect.y - self.collision_rect.width//2
            self.image3 = self.frame_list[13][4]
            
            self.atk_rect.x = x_loc
            self.atk_rect.y = y_loc
            self.atk_show_sprite = True
            
        elif (self.frame_index >= 1 and self.frame_index < 4) and (self.action==10):#adjust atk hitbox location for crit
            self.atk_show_sprite = False
            self.atk_rect.width = self.collision_rect.height
            self.atk_rect.height = self.collision_rect.height - 8*self.frame_index
            if self.flip:
                x_loc = self.collision_rect.x - (self.width - self.frame_index*2)
            else:
                x_loc = self.collision_rect.x - ( self.frame_index*2)

            y_loc = self.collision_rect.y + 4*self.frame_index
            
            self.atk_rect.x = x_loc
            self.atk_rect.y = y_loc
        else:#kill atk hitbox (h and w -> 0 and move to upper left)
            self.atk1_kill_hitbox()
        #adjusting atk hitbox size
        if self.action != 10:
            self.atk_rect_scaled  = self.atk_rect.scale_by(0.90)
        else:
            self.atk_rect_scaled  = self.atk_rect
            if self.frame_index < 3 and (pygame.time.get_ticks() - self.particle_update > 200):
                self.particle_update = pygame.time.get_ticks()
                the_sprite_group.particle_group.sprite.add_particle('player_crit', self.rect.centerx, self.rect.centery, self.direction, self.scale, True, self.frame_index, self.particle_update)
                for i in range(5):
                    the_sprite_group.particle_group.sprite.add_particle('player_bullet_explosion', 
                                                                        self.rect.centerx + random.randrange(-48,48), 
                                                                        self.rect.centery + random.randrange(-48,48), 
                                                                        -self.direction, 0.3*self.scale, 
                                                                        True, random.randrange(0,3), self.particle_update)


                
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
            the_sprite_group.particle_group.sprite.add_particle('player_bullet_explosion', x_loc, y_loc, -self.direction, 0.9*self.scale, False, random.randrange(0,3))
    
    def check_if_in_ss_range(self):
        return self.collision_rect.x >= 64 and self.collision_rect.right <= 576
    
    
    def do_entity_collisions(self, the_sprite_group):
        #----------------------------------------------entity collisions
        damage = 0
        if (not self.is_invulnerable[self.action] and not self.i_frames_en and self.Alive):
            #sprite based collisions
            #expensive
            # for enemy in enumerate(the_sprite_group.hostiles_group):
            #     if pygame.sprite.spritecollide(self, enemy[1], False): 
            #         if pygame.sprite.spritecollide(self, enemy[1], False, pygame.sprite.collide_mask):
            #             # if enemy[1] == the_sprite_group.enemy0_group:
            #             #     print(enemy)
            #             if enemy[1] == the_sprite_group.enemy_bullet_group:
            #                 damage += 3
            #                 self.take_damage(damage, 826)
            #             if enemy[1] == the_sprite_group.enemy_bullet_group2:
            #                 damage += 2
            #                 self.take_damage(damage, 836)
            #             if enemy[1] == the_sprite_group.p_int_group2:
            #                 damage += 0.75*self.hp
            #                 self.take_damage(damage, 836)
            #         #print(damage)
            #     damage = 0
            
            for bullet in the_sprite_group.enemy_bullet_group:
                if self.hitbox_rect.colliderect(bullet.rect):
                    self.take_damage(bullet.dmg, 836) 

            #rect based collisions
            for enemy in [enemy for enemy in the_sprite_group.enemy0_group 
                          if enemy.is_on_screen and enemy.atk_rect_scaled.width != 0
                         ]:
                if self.hitbox_rect.colliderect(enemy.atk_rect_scaled):
                    if enemy.id_ == 'worm':
                        damage += 2
                    else:
                        damage += 1.5
                    
                    if enemy.shielded:
                        damage *= 2
                    self.take_damage(damage, 836) 
                damage = 0
                
    def do_extended_hitbox_collisions(self, the_sprite_group):
        flag = 0
        if not self.is_invulnerable[self.action]:
            for enemy in [enemy for enemy in the_sprite_group.enemy0_group 
                            if enemy.is_on_screen and enemy.atk_rect_scaled.width != 0
                            ]:
                
                if enemy.atk_rect_scaled.colliderect(self.rect.x - 1.5*self.width, 
                                                    self.rect.y - 2*self.width, 
                                                    self.rect.width + 3*self.width, 
                                                    self.rect.height + 4*self.width
                                                    ):
                    if enemy.shielded:
                        flag = 2
                    else:
                        flag = 1
                    
            if not self.inventory_handler.check_for_item('Rock'):
                for bb1 in [p_int for p_int in the_sprite_group.p_int_group
                              if p_int.is_onscreen and p_int.id_ == 'breakable_brick1'
                              ]:
                    if bb1.rect.centerx - self.rect.centerx < 2*self.width:
                        if bb1.rect.colliderect(self.rect.x - 1.5*self.width, 
                                                        self.rect.y - 2*self.width, 
                                                        self.rect.width + 3*self.width, 
                                                        self.rect.height + 4*self.width
                                                        ):
                            flag = 1
        
        return flag
    
    def check_for_breakable2(self, the_sprite_group):
        flag = False
        for p_int in [p_int for p_int in the_sprite_group.p_int_group 
                            if p_int.is_onscreen and p_int.id_ == 'breakable_brick2'
                            ]:
            flag = (((self.rect.x < p_int.rect.x and self.direction > 0) or 
                    (self.rect.x > p_int.rect.x and self.direction < 0)) and
                     p_int.rect.colliderect(self.rect.x - 2*self.width, 
                                            self.rect.y, 
                                            self.rect.width + 4*self.width, 
                                            self.rect.height
                                            ))
        
        return flag
                    
        
    def do_instant_st_regen(self, amnt):
        if amnt == 0:
            amnt = self.inst_stamina
        
        if not self.melee_hit:
            if self.stamina_used > 0 and self.stamina_used - amnt <= self.stamina_usage_cap:
                self.stamina_used = self.stamina_usage_cap
                
            elif self.stamina_used > 0 and self.stamina_used - amnt > self.stamina_usage_cap:
                self.stamina_used -= amnt
                        
            self.melee_hit = True
        
    def check_melee_hits(self, the_sprite_group):
        if self.atk1:
            for enemy in [enemy for enemy in the_sprite_group.enemy0_group 
                            if enemy.is_on_screen
                            ]:
                if self.atk_rect.colliderect(enemy.rect):
                    self.do_instant_st_regen(0)
            
            for p_int in [p_int for p_int in the_sprite_group.p_int_group
                        if p_int.id_ == 'breakable_brick1' and p_int.is_onscreen
                        ]:
                if self.atk_rect.colliderect(p_int.rect):
                    self.do_instant_st_regen(1)
                    
            for bullet in the_sprite_group.enemy_bullet_group: #[bullet for bullet in the_sprite_group.enemy_bullet_group]:
                if self.atk_rect.colliderect(bullet.rect):
                    self.do_instant_st_regen(0)

    def check_item_pickup(self, the_sprite_group):#player side confirmation an item is picked up
        for item in the_sprite_group.item_group:
            if (self.hitbox_rect.colliderect(item.rect)):
                #last param is a boolean for exluding items in the item id list prior, when set to False it will only include those items
                if self.inventory_handler.pick_up_item(self.collision_rect, the_sprite_group.item_group, ['Cursed Flesh'], True):
                    self.m_player.play_sound(self.m_player.sfx[8], None)

    
    def do_npc_collisions(self, the_sprite_group):
        for obj in [obj for obj in the_sprite_group.textprompt_group 
                    if obj.rect.x > -32 and obj.rect.x < 640# and obj.enabled
                    ]:
            obj_collision = obj.rect.colliderect(self.collision_rect.x + self.collision_rect.width//16, 
                                                 self.collision_rect.y, 
                                                 0.875*self.collision_rect.width, 
                                                 self.collision_rect.height)
            if not obj.is_cutscene and obj_collision and self.action == 0 and self.dx == 0:
                self.dialogue_trigger_ready = True
                if obj.name == 'save_pt':
                    if self.hits_tanked > 0 and self.hits_tanked < self.hp:
                        self.hits_tanked -= 0.03
                        
                        the_sprite_group.particle_group.sprite.add_particle('player_bullet_explosion', 
                                                                            self.rect.centerx + random.randrange(-24,24), 
                                                                            self.rect.centery + random.randrange(-24,24), 
                                                                            -self.direction, 0.5*self.scale, 
                                                                            True, random.randrange(0,3))
                    elif self.hits_tanked <= 0:
                        self.hits_tanked = 0
                    
                    if self.stamina_usage_cap != 0:
                        self.stamina_usage_cap = 0
                # print(obj.name)
            elif obj.is_cutscene and obj_collision:
                self.dialogue_trigger_ready = True
                if obj.is_cutscene and not self.in_cutscene:#selects cutscenes out of collided npcs
                    self.in_cutscene = True
            else:#not colliding with an npc
                if obj.is_cutscene:#selects cutscenes out of not collided npcs
                    self.in_cutscene = False
                    

    def do_platform_sprite_collisions(self, platform_sprite_group):
        # in_air = self.in_air
        # hitting_wall = self.hitting_wall
        # hitting_wall_timer = self.hitting_wall_timer
        
        for p_int in [p_int for p_int in platform_sprite_group if p_int.rect.x <= self.rect.right + self.width and p_int.rect.right >= self.rect.x - self.width]:
            if p_int.collision_and_hostility[p_int.id_][0]:
                #self.atk1_grinding(p_int.rect, the_sprite_group)
                #y collisions
                if (p_int.rect.colliderect(self.collision_rect.x+2, self.collision_rect.y + self.dy, self.width-4, self.height)
                    ):
                    if self.collision_rect.bottom >= p_int.rect.top and self.collision_rect.bottom <= p_int.rect.y + 32:# and p_int.vel_y < 0:
                        self.in_air = False
                        self.coyote_time = pygame.time.get_ticks()
                        
                        self.vel_y = 0.5
                        self.dy = p_int.vel_y
                        #self.dx += p_int.vel_x
                        if self.collision_rect.bottom != p_int.rect.top and (p_int.is_moving_plat or not self.hitting_wall):
                            self.dy -= self.collision_rect.bottom - p_int.rect.top
                    elif self.collision_rect.top <= p_int.rect.bottom and self.collision_rect.top >= p_int.rect.y + 32 and p_int.vel_y > 0:
                        self.dy = p_int.vel_y
                        self.in_air = False
                        self.coyote_time = pygame.time.get_ticks()
                        
                        self.vel_y = 0.5
                    elif (self.collision_rect.top <= p_int.rect.bottom 
                          and self.collision_rect.bottom > p_int.rect.bottom 
                          and p_int.vel_y == 0
                          and not p_int.is_moving_plat):
                        #works for the most part but screenshake can still cause the player to phase through
                        in_air = False
                        self.coyote_time = pygame.time.get_ticks()
                        
                        self.vel_y = 0
                        self.dy = -self.dy
                        self.dy += p_int.rect.bottom - self.collision_rect.top
                    else:
                        self.in_air = True

                #x collisions
                if (not self.disp_flag  
                    and p_int.rect.colliderect(self.collision_rect.x + self.dx, self.collision_rect.y+2, self.width, self.height- 2)):
                    
                    self.hitting_wall = True
                    self.hitting_wall_timer = pygame.time.get_ticks()
                    
                    if p_int.vel_y == 0:
                        if (self.dx > 1 and self.direction > 0) or (self.dx < -1 and self.direction < 0):
                            self.dx = -self.direction + p_int.vel_x
                        elif (self.dx < -1 and self.direction > 0) or (self.dx > 1 and self.direction < 0):
                            self.dx = self.direction + p_int.vel_x
                            
                    else:
                        self.dx = 0
                        
                elif (self.action not in (9, 21)
                    and self.disp_flag #and self.action == 67
                    and p_int.rect.colliderect(self.collision_rect.x + self.direction*self.half_w + self.dx, self.collision_rect.y+2, self.width, self.height - 2)
                    ):
                    self.dx = -16*self.direction
            
                    self.hitting_wall = True
                    self.hitting_wall_timer = pygame.time.get_ticks()
                    
                elif (self.action in (9, 21)
                      and p_int.rect.colliderect(self.collision_rect.x + self.dx, self.collision_rect.y + 16, self.width, self.height - 16)
                    ):
                    self.dx = -self.direction + p_int.vel_x
                    
                    self.hitting_wall = True
                    self.hitting_wall_timer = pygame.time.get_ticks()
        
                
                    
            #taking damage from crushing traps
            if p_int.collision_and_hostility[p_int.id_][1]:
                rate = 0.5
                if (self.hitbox_rect.colliderect(p_int.atk_rect)):
                    if self.hits_tanked + rate > self.hp:
                        self.hits_tanked = self.hp
                    else:
                        self.hits_tanked += rate
                
        #return (in_air, hitting_wall, hitting_wall_timer)
            
    def do_tile_collisions(self, world_solids, the_sprite_group, ccsn_chance):
        lvl_transition_flag = False
        lvl_transition_data = {}
        lvl_trans_orientation = 'vertical'
        lvl_trans_disp = 0
        self.do_platform_sprite_collisions(the_sprite_group.p_int_group)
        
        # self.dx = self.dxself.dy[0]
        # self.dy = self.dxself.dy[1] 
        # self.in_air = self.dxself.dy[2]
        # self.hitting_wall = self.dxself.dy[3]
        # self.hitting_wall_timer = self.dxself.dy[4]
        
        
        self.do_npc_collisions(the_sprite_group)
        
        #timer based update for hitting wall

        if self.hitting_wall and self.hitting_wall_timer + 100 < pygame.time.get_ticks():
            self.hitting_wall = False
        
        one_way_tiles = (17, 69, 70)
        
        #size adjust for displaced rects
        # if self.direction < 0:
        #     disp_x = -self.half_w
        # else:
        #     disp_x = self.half_w
            
        disp_x = self.direction*self.half_w
        
        #col_dist = int(3*self.width)
        for tile in [tile for tile in world_solids 
                     if (tile[1].x > self.collision_rect.x - 64 and tile[1].right < self.collision_rect.right + 64 and 
                        tile[1].y > self.collision_rect.y - 64 and tile[1].bottom < self.collision_rect.bottom + 64 )
                        or tile[2] == 10
                     ]:
            #x collisions
            if (tile[2] not in (10, 2, 60) and tile[2] not in one_way_tiles):
                self.atk1_grinding(tile[1], the_sprite_group)
                
                
                #self.dx collisions, tile walls
                
                #hitting wall while rolling
                if self.action in (9, 21) and tile[1].colliderect(self.collision_rect.x + self.dx, self.collision_rect.centery + self.dy, self.width, self.qrtr_h - 2):
                    self.dx = -self.direction 
                    self.dy /= 2
                    self.rolled_into_wall = True
                    self.hitting_wall = True
                    self.hitting_wall_timer = pygame.time.get_ticks()
                    #if not self.in_air:
                        
                    if self.frame_index > 0:
                        if self.rolling:#you can die via concussion now
                            self.m_player.play_sound(self.m_player.sfx[7], None)
                            if self.stamina_used >= 5:
                                self.hits_tanked += 0.1
                                if random.randint(1, ccsn_chance) == 1:
                                    self.brain_damage = True
                        self.rolling = False
                    #self.debuggin_rect  = (self.collision_rect.x + self.dx, self.collision_rect.y + self.half_h + self.dy, self.width, self.qrtr_h - 2)
                
                #displaced hitbox x collisions
                elif (self.action not in (9, 21)
                    and self.disp_flag #and self.action == 67
                    and tile[1].colliderect(self.collision_rect.x + disp_x + self.dx, self.collision_rect.y, self.width, self.height - 17)
                    ):
                    self.dx = -16*self.direction
                    self.dy = 0
                    self.hitting_wall = True
                    self.hitting_wall_timer = pygame.time.get_ticks()
                    
                # elif (self.action == 5#going backwards collisions
                #       and tile[1].colliderect(self.collision_rect.x + 2 + self.dx, self.collision_rect.y, self.width - 4, self.height - 16) ):
                #     self.dx = 2*self.direction
                #     #self.scrollx = 0
                
                #wall collisions while NOT rolling
                elif (self.action not in (9, 21) #this line is important for consistency
                    and self.dx != 0
                    and not self.disp_flag
                    and tile[1].colliderect(self.collision_rect.x + 2 + self.dx, self.collision_rect.y, self.width - 4, self.height - 16) 
                    ):
                    self.hitting_wall = True
                    self.hitting_wall_timer = pygame.time.get_ticks()

                    m = 2
                    if self.hurting:
                        m = 16
                    if abs(self.direction + self.dx) < abs(self.dx) or self.hurting:
                        self.rect.x += m*self.direction
                        #self.dx += m*self.direction
                        #print('oof1 ' + str(pygame.time.get_ticks()))
                    elif abs(self.direction + self.dx) > abs(self.dx):
                        self.rect.x += -m*self.direction
                        #print('oof2 ' + str(pygame.time.get_ticks()))
                    self.dx = 0
                        
                #self.dy collision stuff, sinking through tiles etc
                
                if (self.vel_y != 0 and tile[1].colliderect(self.collision_rect.x + 2, self.collision_rect.y + self.dy, self.width - 4, self.height)
                    #and not self.disp_flag
                    ):
                    if self.vel_y >= 0 or not self.in_air: #making sure gravity doesn't pull player under the tile
                        self.vel_y = 0
                    elif self.vel_y < 0 and self.in_air: #prevents player from gliding on ceiling
                        self.vel_y *= 0.5
                        self.in_air = True
                        self.squat = False
                        
                    if (self.action in (9, 21) or self.action == 18): #rolling collisions
                        if (tile[1].y > self.collision_rect.y + self.height -32): #lower collisions
                            self.dy = tile[1].top  - self.rect.bottom 
                        elif (tile[1].bottom < self.collision_rect.y + self.height + 32): #upper collisions
                            self.dy = tile[1].bottom  - self.rect.top
                            
                    else: 
                        #IMPORTANT---------------------default floor and ceiling collisions
                        #basically there's 2 collision checks that each make up half of the collision rect, upper and lower
                        
                        #bottom collisions
                        if self.half_h < tile[1].y - self.rect.y:# and tile[1].colliderect(self.collision_rect.x + 2, self.collision_rect.y + self.half_h + self.dy, self.width - 4, self.half_h):
                            self.dy = tile[1].top - self.rect.bottom #-1
                            self.rolled_into_wall = False
                            self.in_air = False
                            self.coyote_time = pygame.time.get_ticks()
                            
                        #upper collisions
                        if self.rect.bottom - tile[1].bottom > self.half_h:# and tile[1].colliderect(self.collision_rect.x + 2, self.collision_rect.y + self.dy, self.width - 4, self.half_h):
                            self.dy = tile[1].bottom  - self.rect.top
                            
                #  #wall_slide collisions doesn't work     
                # if self.direction > 0:
                #     ws_disp = self.width
                # else:
                #     ws_disp = -2
                # #if tile[1].y < self.collision_rect.centery:
                # self.hitting_wall2 = tile[1].colliderect(self.collision_rect.x + ws_disp, self.collision_rect.y + self.dy, 2, self.height)
                # # if self.hitting_wall2:
                # #     self.dx = 0
                

                            
            #special tiles
            elif(tile[2] in (2, 60)):#spikes/ other trap tiles
                if self.Alive and not self.i_frames_en and tile[1].colliderect(self.collision_rect.x + 3*self.width//8 + self.dx, self.collision_rect.y + self.dy, self.qrtr_w, self.height - self.qrtr_w):
                    #if self.frame_index%4 == 0:
                    if self.frame_index < 1:
                        self.take_damage(0.2, 140)#80
                    self.vel_y = 0
                    self.in_air = False
                    self.coyote_time = pygame.time.get_ticks()
                    
            
            elif(tile[2] in one_way_tiles):#one way tiles
                if tile[1].colliderect(self.collision_rect.x, self.collision_rect.bottom - 16 + self.dy, self.width, 18):
                    if tile[1].top - self.rect.bottom >= -16:
                        if self.vel_y >= 0: 
                            self.vel_y = 0
                            self.in_air = False
                            
                            self.coyote_time = pygame.time.get_ticks()
                        elif self.vel_y < 0:
                            self.vel_y *= 0.6#velocity dampening when passing thru tile
                            self.in_air = True
                        
                        self.dy = tile[1].top - self.collision_rect.bottom
                        self.rolled_into_wall = False
                           
            elif(tile[2] == 10):#level transition tiles
                    
                if tile[1].colliderect(self.collision_rect.x + self.dx, self.collision_rect.y + self.height*0.25 + self.dy, 4, 0.5*self.height):
                    #this collision will be used to initiate a level change
                    #tile[3][0]: next_level, [1]: player new x, [2]: player new y
                    if tile[1].width < tile[1].height:
                        lvl_trans_orientation = 'vertical'
                    else:
                        lvl_trans_orientation = 'horizontal'
                    
                    self.scrollx = 0
                    if not self.disp_flag or lvl_trans_orientation == 'horizontal':
                        self.do_screenshake = False
                        self.dx = 0
                        self.dy = 0
                        lvl_transition_flag = True
                        lvl_transition_data = tile[3]
                        lvl_trans_disp = self.rect.x - tile[1].x

                    elif lvl_trans_orientation == 'vertical':
                        self.dx = -self.direction*8
    


        #debuggin bottom boundary
        if self.rect.y + self.rect.height//2 + self.dy > 480:
            self.dy -= self.rect.bottom - (480)
            self.in_air = False
            self.coyote_time = pygame.time.get_ticks()
            
        return (lvl_transition_flag, lvl_transition_data, lvl_trans_orientation, lvl_trans_disp)
    
    
    def update_coords(self, world_rect):
        self.y_coord = self.rect.y + self.dy - world_rect.y
        self.x_coord = self.rect.x + self.dx - world_rect.x
        
    
    def move(self, pause_game, moveL, moveR, world_solids, world_rect, x_scroll_en, y_scroll_en, half_screen, screenH, the_sprite_group, ccsn_chance):
        #reset mvmt variables
        self.dialogue_trigger_ready = False
        self.collision_rect.center = self.rect.center
        self.hitbox_rect.center = self.rect.center
        
        # if pause_game:
        #     self.dx = 0
        self.dx = 0
        self.dy = 0
        self.scrollx = 0
        
        if not self.in_air:
            self.consecutive_upstrike = 0
            self.jump_counter = 0
        
        #move
        if (self.action in (1, 22)) and self.frame_index%3 == 0:
            self.particles_by_frame(self.frame_index//2 + 2, the_sprite_group, 3)
        
        if not self.disp_flag and self.action != 5 and not self.hitting_wall and not self.using_item and not self.shoot: #self.action < 5:# and self.rolled_into_wall == False:
            if moveL and not moveR:
                self.dx = -self.speed
                self.flip = True
                self.direction = -1
                self.last_direction = -1
            elif moveR and not moveL:
                self.dx = self.speed
                self.flip = False
                self.direction = 1
                self.last_direction = 1
            elif moveL and moveR and self.last_direction == -1:
                self.dx = self.speed
                self.flip = False
                self.direction = 1
            elif moveL and moveR and self.last_direction == 1:
                self.dx = -self.speed
                self.flip = True
                self.direction = -1
            
                
            if (moveL or moveR) or self.action == 1:
                self.landing = False
                
        elif self.action == 5:#taking damage, hurting----------------------
            #print(self.direction)
            self.cancel_shoot()
            self.slide_kick = False
            self.dx = -self.direction * 4
            if self.vel_y > 10:
                self.vel_y -= self.vel_y - 10

            if self.check_if_in_ss_range():
                self.do_screenshake = True
                self.screenshake_profile = (0, 3, 2)
                
            if self.frame_index < 3:
                self.hurting = True #perpetuates the action for the entire animation after the collision has ende
      
            

		#rolling 
        if self.rolling and not self.hurting:
                
            if self.flip:
                self.dx = -(self.speed + 3)
            else:
                self.dx = (self.speed + 3)
            
            if (#(moveL and self.direction == 1) or (moveR and self.direction == -1) #BREAK ROLLING
               #or 
                self.squat
                or self.roll_count >= self.roll_limit
                or self.stamina_used + self.roll_stam_rate > self.stamina
                or (self.atk1 and self.check_atk1_history() != 4)
                # and (self.check_atk1_history() != 4 or
                # ( self.atk1
                # ))
                #or self.rolled_into_wall #stops rolling if player rolls into wall
                ):
                if (self.action not in (7,8,10,23,24)):
                    self.rolling = False
                    #self.roll_count = self.roll_limit
                #self.reset_jump()
                if self.squat and self.consecutive_upstrike < self.upstrike_limit and self.jump_counter < 2 + self.consecutive_upstrike:#(self.action_history[2] not in (9, 21) and self.action_history[0] != 7)):
                    #the_sprite_group.particle_group.sprite.add_particle('player_mvmt', self.rect.centerx, self.rect.centery, self.direction, self.scale, True, 1)
                    self.squat_done = True
                    
                    #self.vel_y += 2
                    
        #slide kick
        if (self.action == 18
            and not self.hurting 
            and not (moveL and self.direction == 1)
            and not (moveR and self.direction == -1)
            ):
            # if not self.in_air:
            #     self.particles_by_frame(self.frame_index//2 + 2, the_sprite_group, 3)
            # else:
            #     self.particles_by_frame(self.frame_index//2 + 2, the_sprite_group, -1)
                
            self.particles_by_frame(self.frame_index//2 + 2, the_sprite_group, 3)

            self.roll_count = 0
            #self.roll_stam_rate = 0
            # self.atk1 = False
            # self.atk1_kill_hitbox()
            if moveL or moveR:
                multiplier = 2
            else:
                multiplier = 1
                
            if self.frame_index == 1:
                self.dx = self.direction * (multiplier * 3 + self.speed)
                self.rect.x += self.direction * self.speed
                
            else:
                self.dx = self.direction * ((multiplier * 2) + 1)
            #self.vel_y = 0
        
        # if self.action == 24:
        #     print(self.rolling)
        #     if self.rolling:
        #         self.upstrike = False
                
        #------------------------------------------------------------------------------------------------------------------------------------------------------
        #atk1------------------------------------------------------------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------------------------
        if self.action == 10 and self.frame_index < 1:
            the_sprite_group.particle_group.sprite.add_particle('bloom', self.rect.centerx, self.rect.centery, -self.direction, self.scale/5, True, -1)
            
        if self.atk1 and not self.hurting:#adjusting speed to simulate momentum, motion stuff
            self.curr_state = self.in_air
            
            #self.slide_kick = False
            #if not break atk1
            if (#self.collision_rect.x >= 0 and self.collision_rect.right <= 640 and
                not (((moveL and self.direction == 1) or (moveR and self.direction == -1)) and self.frame_index > 2) 
                and not (self.rolling and self.frame_index > 2 + self.crit - 2*self.heavy) 
                and not (self.squat and self.frame_index > 2 + self.crit - 2*self.heavy)
                and not (self.slide_kick and self.frame_index > 2 + self.crit - 2*self.heavy)
                ): #not (self.rolling) and 
                if (self.frame_index == 0):#fast initial impulse
                    self.slide_kick = False
                    # if pygame.time.get_ticks() < self.update_time + 20:
                    #     self.m_player.play_sound (self.m_player.sfx[1])
                    if self.crit and self.check_if_in_ss_range():
                        crit_speed =int(self.speed * 1.5)
                        self.dx = self.direction * 2 * self.speed
                        self.rect.x += self.direction * crit_speed
                        
 
                        self.vel_y = 15
                    elif self.heavy:
                        self.dx = self.direction * self.speed
                        self.rect.x += self.direction
                    elif self.atk1_stamina_cost == self.atk1_default_stam:
                        if moveL or moveR:
                            multiplier = 9
                        else:
                            multiplier = 3
                            
                        # if self.rect.centerx in range(288, 352):
                        #     self.dx = self.direction * (multiplier * (2))
                        #     self.rect.x += self.direction * self.speed * 2
                        # else:
                        self.dx = self.direction * multiplier
                        self.rect.x += self.direction * (self.speed + 1)
                        
                        if self.action == 24:#7:
                            if self.vel_y > 0:
                                self.vel_y = -5
                            else:
                                self.vel_y -= 0.7
                            
                        elif self.action == 8 and self.vel_y + 7 <= 28 and self.vel_y > 0 and self.in_air: #25 max 
                            self.vel_y *= 1.7

                elif self.frame_index > 1 :# slow forward speed
                    if self.crit and self.check_if_in_ss_range():

                        if not self.in_air:
                            self.dx = self.direction
                        else:
                            self.rect.x += self.direction * 2 * self.speed
                    else:
                        if self.action == 24 and self.frame_index <= 2 and self.vel_y > 0: #add hang time for upstrike
                            self.vel_y = 0
                        
                        if (moveL and self.direction == 1) or (moveR and self.direction == -1):
                            self.dx = -self.direction
                        else:
                            self.dx = self.direction

                
                #add trailing particles
                if not self.heavy and not self.crit and self.frame_index < 1:
                    self.draw_trail = True
                else:
                    self.draw_trail = False

                #drawing atk sprite and setting hitboxes            
                self.atk1_set_hitbox(the_sprite_group)
            else:
                self.atk1_kill_hitbox()
                self.atk1 = False
                self.crit = False
                self.heavy = False
                #self.upstrike = False
                self.atk1_stamina_cost = self.atk1_default_stam
                self.draw_trail = False
                
        else:
            self.atk1_kill_hitbox()
            self.atk1 = False
            self.crit = False
            self.heavy = False
            #self.upstrike = False
            self.atk1_stamina_cost = self.atk1_default_stam
            self.draw_trail = False
            

        #==========================================================================================================================================
        
        #jump
        if self.squat_done and (not(self.atk1)):# or (self.atk1 and self.frame_index == 0)):
            self.double_jump_en = True
            the_sprite_group.particle_group.sprite.add_particle('player_mvmt', self.rect.centerx, self.rect.centery, self.direction, self.scale, True, 1)
            self.squat_done = False
            self.vel_y = -8 #-9.5
            self.in_air = True
            self.jump_counter += 1

        elif self.in_air and not (moveL or moveR):
            if self.action != 8 and self.action != 10 and self.action != 1 and self.action != 5:
                self.landing = True
            else:
                self.landing = False
        
        # elif not self.in_air:
        #     # if self.vel_y > self.coyote_vel: #(self.coyote_time + 200 < pygame.time.get_ticks()):
        #     #     self.curr_state = True
        #     #     self.in_air = True
        #     #     self.squat = False
  
        #     if self.coyote_time + 100 > pygame.time.get_ticks():
        #         self.vel_y = 0


        if self.jump_dampen:
            if self.squat or (self.squat_done and self.in_air): #very small hold jump
                self.vel_y *= 0.8
                
            elif self.vel_y <= -1: #minimum jump velocity, longer hold jump
                self.vel_y *= 0.5

            self.in_air = True
            self.squat_done = False
            self.squat = False
            self.jump_dampen = False
            
        if self.action == 3 or self.action == 1 or self.action == 0:
            self.jump_dampen = False
                    
        #land
        
        self.update_landing(the_sprite_group)
        
        #shooting
        if self.action == 11:
            if self.frame_index == 3:
                if not self.hitting_wall:
                    self.dx += -(5) * self.direction#recoil
                else:
                    self.dx = 0
                
                if not self.shoot_recoil:#playing sound
                    self.m_player.play_sound(self.m_player.sfx[5], None)
                    self.vel_y = 0
                self.shoot_recoil = True
            else:
                if not self.hitting_wall:
                    self.dx += -self.extra_recoil * self.direction
                else:
                    self.dx = 0
                self.extra_recoil = 0
                
                self.shoot_recoil = False
                
        #throwing
        if self.action == 23:
            if self.frame_index < 2:
                self.particles_by_frame(self.frame_index//2 + 2, the_sprite_group, 3)
            
            # if self.frame_index == 0 and not self.hitting_wall and not self.in_air:
            #     self.dx = -self.direction*self.speed
            if self.frame_index == 1 and self.charge_built == 1:
                #self.dx += self.direction*self.speed
                #self.vel_y = 0
                self.charge_built = 0
                self.rolling = False
                self.m_player.play_sound(self.m_player.sfx[5], None)
                #self.shoot = False
                #spawn bullet---------------------------------------------------------------------------------------------
                if self.flip == False:
                    x = self.rect.right
                else:
                    x = self.rect.left
                y = int(self.rect.y + 0.5 * self.height)
                #have different projectiles depending on what's in the current slot
                if self.inventory_handler.get_item_name_in_slot() == 'Rock':
                    player_bullet = bullet_(x, y, 32, self.direction, self.scale, 'player_basic', self.ini_vol)
                    the_sprite_group.player_bullet_group.add(player_bullet)
                self.inventory_handler.discard_item_by_slot()
                    
                self.stamina_used += self.shoot_stamina_cost
            if self.frame_index >= 1:
                self.dx = self.direction*self.speed//2

            
            if moveL or moveR:
                if self.frame_index == 1:
                    self.dx += self.direction*self.speed*2
                else:
                    self.dx += self.direction*self.speed//2


        #hurting/ enemy collisions
        # if self.hurting:
        #     # if not self.hitting_wall and self.frame_index < 2:
        #     self.dx -= self.direction * 4
        #     if self.vel_y > 10:
        #         self.vel_y -= self.vel_y - 10

        #     if self.check_if_in_ss_range():
        #         self.do_screenshake = True
        #         self.screenshake_profile = (-1, 3, 2)


        #gravity
        
        
        
        # if self.shoot and self.frame_index == 2:
        #     self.vel_y *= 0.8
        if self.slide_kick and self.frame_index == 1:
            self.vel_y *= 0.99
        # elif self.rolling and self.in_air and self.frame_index == 0:
        #     self.vel_y 
        elif self.vel_y <= 20:#25 = terminal velocity
            self.vel_y += 0.4    
        elif self.vel_y > 20:
            self.vel_y = 20
            
        self.dy = self.vel_y
        
        #--------------------------------------------------------------coordinate test
        #USED FOR CAMERA SCROLLING
        self.update_coords(world_rect)

        #---------------------------------------------------------world boundaries------------------------------------------------------------------
        if self.collision_rect.x < -6:
            self.dx = 1
        elif self.x_coord > world_rect.width + 6:
            self.dx = -1
        
        #--------------------------------------window boundaries
        if self.collision_rect.x < -4:
            self.dy = 0
            self.dx = 6
        elif self.collision_rect.x >= 604:
            self.dy = 0
            self.dx = -6
        
        #----------------------------------------------------------------------------------------------------------------------------------
        #================================================================TILE COLLISIONS=====================================================================
        #====================================================================================================================================
        if not self.in_air and self.vel_y > 0.5 and not self.vel_y > self.coyote_vel:
            self.coyote_ratio = self.vel_y/self.coyote_vel
        else:
            self.coyote_ratio = 0
        
        
        if self.brain_damage or self.angle != 0:
            self.dx = 0
            self.dy = 0
            lvl_transition_flag_and_data = (False, [])
        else:
            lvl_transition_flag_and_data = self.do_tile_collisions(world_solids, the_sprite_group, ccsn_chance)

        # self.dx = self.dxself.dy[0]
        # self.dy = self.dxself.dy[1]
        
        if self.in_cutscene:
            self.dx = 0
            self.dy = 0
            self.vel_y = 0
            
        #wall_slide
        # if self.hitting_wall2:# and self.vel_y >= -5:# and not (self.last_direction < 0 and moveL) and not (self.last_direction > 0 and moveR):
            
        #     self.wall_slide = True
        #     self.in_air = False
        #     # if not self.disp_flag:
        #     #     self.dx = 0
        #     if not self.squat_done:
        #         self.vel_y = 0
        #     # if self.squat:
        #     #     self.vel_y -= 2
        #     #     self.squat_done = True
        #     # self.jump = False
        # else:
        #     #self.hitting_wall2 = False
        #     self.wall_slide = False
            

            

        #update pos------------------------------------------------------------------------------------------------------------------------

        if self.draw_trail:
            self.trail_coords.append([[self.rect.centerx - 3*self.direction, self.rect.centery], [self.rect.centerx + self.dx + 3*self.direction, self.rect.centery + self.dy]])
        else:
            self.trail_coords = []
            
        for trail_coord in self.trail_coords:
            trail_coord[0][0] -= self.dx//6
            trail_coord[1][0] -= self.dx//6
        
        self.rect.y += self.dy
        self.hitbox_rect.centery = self.rect.centery #don't delete, keeping hitbox rect on the player is used by the camera and enemies alike
        
        #rudimentary scrolling adjust====================================================================================================================
        if self.Alive:
            if x_scroll_en:
                if self.x_coord < half_screen + self.camera_offset or self.shoot_recoil or self.hurting: 
                    self.rect.x += self.dx
                elif self.x_coord >= world_rect.width - (half_screen + 36 + self.camera_offset) or self.shoot_recoil or self.action == 5:
                    self.rect.x += self.dx
                elif self.x_coord >= half_screen + self.camera_offset and self.x_coord < world_rect.width - (half_screen - 16 + self.camera_offset): 
                    self.scrollx = self.dx
                    
                if self.trail_coords != []:
                    for vect_pair in self.trail_coords:
                        vect_pair[0][0] -= self.scrollx
                        vect_pair[1][0] -= self.scrollx
            else:
                self.rect.x += self.dx
                #print(self.dx)
        else:
            self.hurting = False
            self.action = 6
            self.crit = False
            self.heavy = False
            self.atk1_stamina_cost = self.atk1_default_stam
            self.atk1 = False
            self.atk1_kill_hitbox()
            self.rolling = False
            self.dx = 0
            self.scrollx = 0

        
        
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
        if self.i_frames_en:
            if pygame.time.get_ticks() - update_time > i_frames_duration:
                self.i_frames_en = False
        
    def stamina_regen(self):
        if (self.shot_charging == False):
            rate = 80
 
            if self.speed > self.default_speed or self.action == 16 and not self.rolling:
                stamina_increment_unit = -0.16
            if self.rolling and self.stamina_used + self.roll_stam_rate <= self.stamina:
                stamina_increment_unit = self.roll_stam_rate
            else:
                stamina_increment_unit = -0.32
            
                
            self.ini_stamina = self.stamina_used
            

            
            if self.stamina_used + stamina_increment_unit >= self.stamina_usage_cap: #change 0 to some int, the int will be the limit to which stamina will regen
                do_stam_regen = True

            elif (self.stamina_used > 0 and self.stamina_used + stamina_increment_unit <= self.stamina_usage_cap): #regen to max stamina cap
                self.stamina_used = self.stamina_usage_cap #change this to change stamina cap
                do_stam_regen = False
                
            else:
                do_stam_regen = False
        else:
            rate = 150
            stamina_increment_unit = 0.15
            self.charge_built = self.stamina_used - self.ini_stamina
            if self.stamina_used + stamina_increment_unit <= self.stamina:
                do_stam_regen = True
            else:
                do_stam_regen = False
            
        if do_stam_regen: 
            if pygame.time.get_ticks() - self.update_time3 > rate:
                self.update_time3 = pygame.time.get_ticks()
                self.stamina_used += stamina_increment_unit
                
    def take_damage(self, damage, i_frames_time):
        if self.Alive:
            if not self.hurting:
                self.frame_index = 0
            self.rolling = False
            
            self.i_frames_time = i_frames_time
            
            self.hurting = True
            self.hits_tanked += damage
            if self.hits_tanked >= self.hp:#killing the player------------------------------------------------
                self.hits_tanked = self.hp
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
                
    # def reset_jump(self):
    #     if -1 in self.action_history:
    #         if self.action_history[2] in (9, 21):
    #             self.action_history[2] = -1
    #         if self.action_history[0] == 7:
    #             self.action_history[0] = -1
    
    
    def animate(self, the_sprite_group):
        

        #everything speeds up when pressing alt/sprint except shooting at the cost of slower stamina regen
        adjustment = 0
        if self.sprint and self.action != 11 and self.action != 6: 
            adjustment = 12
        elif self.atk1 and self.atk1_stamina_cost > self.atk1_default_stam:
            adjustment = -20
        else:
            adjustment = 0
        frame_update = self.framerates[self.action] - adjustment
        
        if not self.disp_flag: 
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
        self.mask = pygame.mask.from_surface(self.image)
        
        #change frame index---------------------------------------------------------------
        if pygame.time.get_ticks() - self.update_time > frame_update:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1 

        #END OF ANIMATION FRAMES    
        if self.frame_index >= len(self.frame_list[self.action]):
            self.landing = False
            if self.action != 5 and self.action != 6:
                self.frame_index = 0
            if self.action == 1 or self.action == 0:
                self.recovery_counter -= 1
                if self.recovery_counter <= 0:
                    self.recovery_counter = 1
                    self.update_action_history(-1)
                self.atk1_stamina_cost = self.atk1_default_stam
            
            if self.action == 15:
                update_time = pygame.time.get_ticks()
                for i in range(5):
                    the_sprite_group.particle_group.sprite.add_particle('player_bullet_explosion', 
                                                                        self.rect.centerx + random.randrange(-48,48), 
                                                                        self.rect.centery + random.randrange(-24,24), 
                                                                        -self.direction, 0.3*self.scale, 
                                                                        True, random.randrange(0,3), update_time)
                self.m_player.play_sound(self.m_player.sfx[9], None)
                self.using_item = False
                self.speed = self.default_speed
                self.finished_use_item_animation = True
 
            
            elif self.action == 16:
                self.recovery_counter *= 2
                self.atk1 = False
                self.heavy = False
                
            elif self.action == 18:
                self.slide_kick = False
                self.atk1 = False
                self.crit = False
                self.heavy = False
    
            elif self.action == 5:
                self.hurting = False
                self.i_frames_en = True #triggers i_frames for next tick
                self.update_time2 = pygame.time.get_ticks()
                #self.i_frames_time = 836

            elif self.action == 4:
                self.squat_done = True #squatting finished when it loops frames
                self.squat = False

            elif self.action in (7,8,10,24):
                
                #self.squat = False #this line will cancel jumps that have been inputted before the atk
                
                # if self.action == 7:
                #     self.atk1_alternate = False
                # elif self.action == 8:
                #     self.atk1_alternate = True
                if self.action == 10:
                    self.crit = False
                self.upstrike = False
                self.landing = False
                self.atk1 = False
                    
            elif self.action in (9, 21): 
                #self.image = pygame.image.load('sprites/player/end_of_roll/0.png') #this messes up everything do not add back
                if self.roll_count == self.roll_limit:# or self.rolled_into_wall:#roll limit, this ends up getting incremented once more after 
                    self.rolling = False
                self.roll_count += 1
                self.rolled_into_wall = False
            
            elif self.action == 6:
                self.frame_index = 5  
                
            elif self.action == 23:
                self.shoot = False 
                
            elif self.action == 11:
                if self.inventory_handler.discard_item_by_name('Rock'):
                    self.charge_built = 0
                self.shoot = False
                self.ini_cost_spent = False
                #spawn bullet---------------------------------------------------------------------------------------------
                if self.flip == False:
                    x = self.rect.right + 0
                else:
                    x = self.rect.left - 32
                y = int(self.rect.y + 0.25 * self.height)
                player_bullet = bullet_(x, y, 32, self.direction, self.scale, 'player_basic', self.ini_vol)
                the_sprite_group.player_bullet_group.add(player_bullet)
                self.charge_built -= 2
                i = 0
                while self.charge_built - 0.35 > 0:
                    i+= 1
                    if self.inventory_handler.discard_item_by_name('Rock'):
                        self.charge_built = 0
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
                    player_bullet = bullet_(x , y, 32, self.direction, self.scale, 'player_basic', self.ini_vol)
                    the_sprite_group.player_bullet_group.add(player_bullet)
                
                self.extra_recoil = i*3
                self.charge_built = 0
                
                self.roll_count = 3
                
                self.rolling = False
                
    def draw_trail_line(self, screen, color, trail_coords):
        if trail_coords != []:
            for vect_pair in trail_coords:
                width = trail_coords.index(vect_pair) + 2
                pygame.draw.line(screen, color, vect_pair[0], vect_pair[1], width)
                
    def draw_with_flicker(self, image, rect, screen, flicker):
        if flicker:
            if pygame.time.get_ticks()%2 == 0:
                screen.blit(pygame.transform.flip(image, self.flip, False), rect)
        else:
            screen.blit(pygame.transform.flip(image, self.flip, False), rect)
        
    
    def draw(self, screen):
        
        if self.atk1:
            color = (255,0,86)
        else:
            color = (255,255,255)
        self.draw_trail_line(screen, color, self.trail_coords)
        
        if self.shot_charging and self.action < 5:
            self.BP_animate()
            screen.blit(pygame.transform.flip(self.image2, self.flip, False), self.BP_rect)

        # if self.flip:
        #     dispx = 1
        # else:
        #     dispx = -1
        # outline_surf = pygame.surface.Surface((self.rect.width+2, self.rect.height+2), flags=pygame.SRCALPHA, depth=32)
        # for pix in self.mask.outline():
        #     pygame.draw.rect(outline_surf, (255, 0, 0, 100), pygame.rect.Rect(pix[0]+dispx, pix[1]-2, 3, 3))
        # outline_surf.blit(self.mask.to_surface(setcolor=(255, 0, 0, 100), unsetcolor=(0,0,0,0)))
        # screen.blit(pygame.transform.flip(outline_surf, self.flip, False), self.rect)
        
        #pygame.draw.rect(screen, (0,0,255), self.collision_rect)
        # pygame.draw.rect(screen, (255,0,0), self.hitbox_rect)
        # pygame.draw.rect(screen, (0,255,0), self.atk_rect_scaled)
        # pygame.draw.rect(screen, (0,0,255), self.debuggin_rect)
        # if self.direction > 0:
        #     ws_disp = self.width
        # else:
        #     ws_disp = -2
        # pygame.draw.rect(screen, (255,0,0), pygame.rect.Rect(self.collision_rect.x + ws_disp, self.collision_rect.y, 2, self.height))
        
        self.draw_with_flicker(self.image, self.rect, screen, self.i_frames_en)#drawing sprite
       
        if self.atk_show_sprite: #drawing melee sprite
            self.draw_with_flicker(self.image3, self.atk_rect, screen, self.atk1_stamina_cost > self.atk1_default_stam)
            
        # if self.vel_y > 1 and self.action == 1 and self.coyote_ratio > 0:# and pygame.time.get_ticks()%2 == 0:
        #     num = int(255*(1-self.coyote_ratio))
        #     pygame.draw.rect(screen, (num,num,num), 
        #                      pygame.rect.Rect(self.collision_rect.x, 
        #                                       self.collision_rect.y, 
        #                                       self.collision_rect.width*(1-self.coyote_ratio), 
        #                                       2)
        #                      )
        

    def execute_action_tree(self, move_R, move_L, debugger_sprint, change_once):
        if self.sprint and self.using_item:
            self.speed = 0
        elif self.sprint and not self.using_item:
            self.speed = self.default_speed + 1

        if debugger_sprint:
            self.speed = self.default_speed * 5
            self.hits_tanked = 0
        elif not debugger_sprint and not self.sprint:
            self.speed = self.default_speed
        

        if (self.hurting):
            self.update_action(5) #hurting
        else:
        
            if self.shoot:
                self.update_action(23)#11
    
            
            
            elif self.atk1:# and not self.slide_kick:
                #self.slide_kick = False
                if change_once:
                    # if self.vel_y < -0.1:# or (self.hold_jump and self.vel_y < 2 and self.in_air and self.action_history[self.len_action_history-1] in [2,4]):
                    #     self.atk1_alternate = True
                    # elif self.vel_y >= 0 and self.in_air:
                    #     self.atk1_alternate = False
                    # else:
                    #     self.atk1_alternate = not self.atk1_alternate
                    # if self.in_air and self.hold_jump and self.consecutive_upstrike <= self.upstrike_limit:
                    #     self.atk1_alternate = True
                    if self.in_air and (not self.hold_jump or self.consecutive_upstrike > self.upstrike_limit):
                        self.atk1_alternate = False
                    elif not self.in_air:
                        self.atk1_alternate = not self.atk1_alternate
                    change_once = False
                # elif not self.in_air:
                # 	self.atk1_alternate = True

                if self.crit:
                    self.update_action(10)
                elif self.heavy:
                    self.update_action(16)
                elif self.upstrike:
                    self.update_action(24)
                    self.atk1_alternate = False
                    #self.upstrike = True
                else:
                    if self.atk1_alternate:# and self.in_air == False: # or (self.hold_jump and self.frame_index == 0)
                        self.update_action(7)	
                    else:
                        self.update_action(8)#8: atk1
                        
                #print(self.action)
            elif self.using_item:#and self.action != 15:
                self.update_action(15)
                # move_L = False
                # move_R = False
                self.rolling = False
                self.atk1 = False
                self.shoot = False
                self.slide_kick = False
            elif self.slide_kick:
                self.update_action(18)

            elif self.rolling: 
                # if self.in_air:
                #     self.update_action(21)
                # else:
                self.update_action(9)#rolling
                self.atk1_alternate = False
                #self.upstrike = False
                
            elif self.wall_slide:
                self.update_action(17)#17: wall slide
            else:
                #print(self.in_air)
                
                if (self.in_air or self.squat_done) and not self.wall_slide:# or (self.vel_y > 1):
                    if self.vel_y < -1.5:
                        self.update_action(19)
                    elif self.vel_y > 2:
                        self.update_action(20)
                    else:
                        self.update_action(2)#2: jump

                elif ( not (move_L or move_R) and
                    not self.in_air and
                    self.vel_y >= 0 and
                    self.landing
                    ):
                    self.update_action(3)#3: land
                    
                elif self.squat: 
                    self.update_action(4)#4: squat

                elif (move_R or move_L) and not self.wall_slide:
                    if self.sprint:
                        self.update_action(22)
                    else:
                        self.update_action(1)#1: run
                else:
                    self.update_action(0)#0: idle

        return change_once
    
    
    def update_action(self, new_action):
        #check if action has changed
        if new_action != self.action:
            do_not_crit = self.check_atk1_history() == 4
            if self.action not in (5, 22):
                self.update_action_history(self.action)#updated with the last action
            if self.action in (7,8,24) and (self.rolling or self.action in (9, 21)):
                self.upstrike = False
                self.crit = False
                self.heavy = False
                self.atk1_stamina_cost = self.atk1_default_stam
                self.atk1 = False
                self.char_level += self.char_dict['melee']
                #print(self.char_level)
            elif self.action == 9 and (new_action == 7 or new_action == 8) and self.atk1:
                self.heavy = False
                if do_not_crit:
                    self.atk1 = False
                    self.atk1_kill_hitbox()
                else:
                    self.crit = True
                    if self.check_if_in_ss_range():
                        self.do_screenshake = True
                        self.screenshake_profile = (16, 6, 3)
                    self.m_player.play_sound(self.m_player.sfx[4], None)
                    self.char_level += self.char_dict['crit']
            elif self.action != 9 and new_action in (7,8,24):
                self.crit = False
                self.m_player.play_sound(self.m_player.sfx[1], None)
                self.char_level += self.char_dict['melee']
                #print(self.char_level)
            elif new_action == 5:
                print("oof") #make player hurting sound
            elif new_action == 11:
                self.char_level += self.char_dict['shoot']
            # else:
            #     self.crit = False
            #     self.heavy = False
            #     self.atk1_stamina_cost = self.atk1_default_stam
            #     self.atk1 = False
            #     self.atk1_kill_hitbox

            self.action = new_action
            self.disp_flag = self.disp_states[self.action]
            
            #update animation settings
            if self.action not in (1, 22):
                self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            #update stamina bar
            #should play a sound when there's no stamina
            if new_action == 7 or new_action == 8:
                if self.check_atk1_history() == 4: #stamina cost for melee will exponentially increase if the action history is just all atk1
                    self.atk1_stamina_cost = self.stamina*2/3
                    if self.atk1:
                        self.heavy = True
                        self.char_level += 2*self.char_dict['melee']
                else:
                    self.recovery_counter = 1
                    self.heavy = False
                    self.atk1_stamina_cost = self.atk1_default_stam
                if self.stamina_used + self.atk1_stamina_cost >= self.stamina:
                    self.stamina_used = self.stamina
                    
                else:
                    self.stamina_used += self.atk1_stamina_cost
                self.ini_stamina += self.atk1_stamina_cost
            elif new_action == 18:
                if self.stamina_used + self.atk1_stamina_cost >= self.stamina:
                    self.stamina_used = self.stamina
                else:
                    self.stamina_used += self.atk1_stamina_cost
                self.ini_stamina += self.atk1_stamina_cost
                
            elif new_action in (9, 21) and self.check_atk1_history() != 4:
                self.stamina_used += self.roll_stam_rate
                self.ini_stamina += self.roll_stam_rate
                
        
        if self.shot_charging == True and self.ini_cost_spent == False:
            self.stamina_used += self.shoot_stamina_cost
            self.ini_cost_spent = True
            
        

                

