import pygame

class sprite_group():
	def __init__(self):
		self.enemy0_group = pygame.sprite.Group()
		self.enemy_bullet_group = pygame.sprite.Group()
		self.player_bullet_group = pygame.sprite.Group()
		self.particle_group = pygame.sprite.Group()
		self.particle_group_bg = pygame.sprite.Group()
		self.particle_group_fg = pygame.sprite.Group()
		self.button_group = pygame.sprite.Group()
		self.enemy_bullet_group2 = pygame.sprite.Group()
		self.p_int_group = pygame.sprite.Group()
		self.p_int_group2 = pygame.sprite.Group()
		self.textprompt_group = pygame.sprite.Group()
		self.bg_sprite_group = pygame.sprite.Group()
		self.item_group = pygame.sprite.Group()
		
		self.sp_groups_with_vol = [
			self.enemy0_group,
			self.enemy_bullet_group,
			self.p_int_group,
			self.p_int_group2,
			self.textprompt_group,
			self.item_group
			#self.enemy_bullet_group2
		]
  
		self.sp_group_list = [
			self.enemy0_group, 
			self.enemy_bullet_group, 
			self.player_bullet_group,
			self.particle_group,
			self.particle_group_bg,
			self.particle_group_fg,
			self.button_group,
			self.enemy_bullet_group2,
			self.p_int_group,
			self.p_int_group2,
			self.textprompt_group,
			self.bg_sprite_group,
			self.item_group
		]
  
		self.hostiles_group = (self.enemy0_group, self.enemy_bullet_group, self.enemy_bullet_group2, self.p_int_group2)
		self.textbox_output = ('', False, False, '', 0)
  
	def update_vol_lvl(self, level):
		for sp_group in self.sp_groups_with_vol:
			for sprite in sp_group:
				sprite.m_player.set_vol_all_sounds(level)

	def purge_sprite_groups(self):
		for group in self.sp_group_list:
			group.empty()
   
		self.textbox_output = ('', False, False, '', 0)
  
	def update_item_group(self, pause_game, player_hitbox_rect, scroll_x, screen):
		for item in self.item_group:
			item.draw(screen)
			item.scroll_along(scroll_x)
			item.enable(player_hitbox_rect, pause_game)#player has to send pick up confirmation
			
			
	def update_groups_behind_player(self, pause_game, screen, player_hitbox_rect, player_atk_rect_scaled, world_solids, scroll_x, player_action, player_direction, 
                                 dialogue_enable, next_dialogue):
		for particle in self.particle_group_bg:
			particle.draw(screen)
			if not pause_game:
				particle.animate()
				particle.move(scroll_x)
			if particle.Active == False:
				self.particle_group_bg.remove(particle)
    
		for bg_sprite in self.bg_sprite_group:
			bg_sprite.draw(screen)
			if not pause_game:
				bg_sprite.enable(scroll_x, player_hitbox_rect, player_atk_rect_scaled, self.particle_group)
				bg_sprite.animate(bg_sprite.frame_rate)
    
		for obj in self.textprompt_group:
			obj.draw(screen)
			if not pause_game and obj.enabled:
				obj.animate(self.sp_group_list)
				obj.get_dialogue_index(obj.current_level, obj.current_p_inv, obj.current_dialogue_index)
				obj.display_interaction_prompt(dialogue_enable, player_hitbox_rect, screen)
				obj.scroll_along(scroll_x)
				if obj.player_collision:
					self.textbox_output = obj.enable(dialogue_enable, next_dialogue)
					#print(obj.enable(dialogue_enable, next_dialogue, screen, player_hitbox_rect, scroll_x))

		for enemy0 in self.enemy0_group:
			enemy0.draw(screen)
			if not pause_game:
				enemy0.animate(self.sp_group_list)
				enemy0.move(player_hitbox_rect, player_atk_rect_scaled, world_solids, scroll_x, player_action, self.sp_group_list)
			if enemy0.Alive == False:
				self.enemy0_group.remove(enemy0)

		for enemy_bullet in self.enemy_bullet_group:
			enemy_bullet.draw(screen)
			if not pause_game:
				enemy_bullet.animate()
				enemy_bullet.move(player_hitbox_rect, player_atk_rect_scaled, world_solids, scroll_x, player_action, self.sp_group_list, player_direction)
			if enemy_bullet.Active == False:
				self.enemy_bullet_group.remove(enemy_bullet)
    
		for enemy_bullet in self.enemy_bullet_group2:
			enemy_bullet.draw(screen)
			if not pause_game:
				enemy_bullet.animate()
				enemy_bullet.move(player_hitbox_rect, player_atk_rect_scaled, world_solids, scroll_x, player_action, self.sp_group_list, player_direction)
			if enemy_bullet.Active == False:
				self.enemy_bullet_group2.remove(enemy_bullet)
	
		for player_bullet in self.player_bullet_group:
			player_bullet.draw(screen)
			if not pause_game:
				player_bullet.animate()
				player_bullet.move(player_hitbox_rect, player_atk_rect_scaled, world_solids, scroll_x, player_action, self.sp_group_list, player_direction)
			if player_bullet.Active == False:
				self.player_bullet_group.remove(player_bullet)

		for particle in self.particle_group:
			particle.draw(screen)
			if not pause_game:
				particle.animate()
				particle.move(scroll_x)
			if particle.Active == False:
				self.particle_group.remove(particle)
    

	def update_groups_infront_player(self, pause_game, screen, scroll_x, world_solids, player_hitbox_rect, player_atk_rect_scaled, player_action):
    
		for p_int in self.p_int_group:
			p_int.draw(screen)
			if not pause_game:
				p_int.enable(player_hitbox_rect, player_atk_rect_scaled, world_solids, scroll_x, player_action, self.sp_group_list)
    
		for p_int2 in self.p_int_group2:
			p_int2.draw(screen)
			if not pause_game:
				p_int2.enable(player_hitbox_rect, player_atk_rect_scaled, world_solids, scroll_x, player_action, self.sp_group_list)
	
		for particle in self.particle_group_fg:
			particle.draw(screen)
			if not pause_game:
				particle.animate()
				particle.move(scroll_x)
			if particle.Active == False:
				self.particle_group_fg.remove(particle)

