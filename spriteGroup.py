import pygame

class sprite_group(): #Class that instantiates and contains sprite groups and updates them by calling sprite internal methods
	def __init__(self):
		self.enemy0_group = pygame.sprite.Group()
		self.enemy_bullet_group = pygame.sprite.Group()
		self.player_bullet_group = pygame.sprite.Group()
		self.particle_group = pygame.sprite.GroupSingle()
		self.particle_group_bg = pygame.sprite.GroupSingle()
		self.particle_group_fg = pygame.sprite.GroupSingle()
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
			self.textprompt_group
			#self.item_group
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
		self.textbox_output = None
	
		self.scroll_x = 0
		self.pause_game = False
		self.enemy_death_count = 0
  
	def update_vol_lvl(self, level):
		for sp_group in self.sp_groups_with_vol:
			for sprite in sp_group:
				sprite.m_player.set_vol_all_sounds(level)

	def purge_sprite_groups(self):
		for group in self.sp_group_list:
			if group not in (self.particle_group, self.particle_group_bg, self.particle_group_fg):
				group.empty()
			elif group in (self.particle_group, self.particle_group_bg, self.particle_group_fg):
				group.sprite.empty_list()
   
		self.enemy_death_count = 0
		self.textbox_output = None
  
	# def update_scroll_x(self, scroll_x):
	# 	self.scroll_x = scroll_x
 
	def text_prompt_prioritize_hitboxes(self): #disable normal NPC hitboxes when a cutscene hitbox is overlapping
		for obj in [obj for obj in self.textprompt_group if not obj.is_cutscene]:
			for obj1 in [obj1 for obj1 in self.textprompt_group if obj1.is_cutscene]:
				if obj.rect.colliderect(obj1.rect):
					obj.collisions_disabled = True
				else:
					obj.collisions_disabled = False
  
	def update_text_prompt_group(self, screen, dialogue_enable, next_dialogue, player, world, selected_slot):
		self.text_prompt_prioritize_hitboxes()
		update_all_ini_indexes = False
		for obj in self.textprompt_group:
			obj.draw(screen)
			if obj.player_choice_flag:
				update_all_ini_indexes = True
			if not self.pause_game and obj.enabled:
				obj.animate(self)
				obj.get_dialogue_index(player, obj.current_dialogue_index, world, self, selected_slot)#takes world's plot_index_list, modifies it directly
				obj.display_interaction_prompt(dialogue_enable, player.hitbox_rect, screen)
				obj.scroll_along(world.rect.x, self.scroll_x)
				if obj.player_collision:
					self.textbox_output = obj.enable2(dialogue_enable, next_dialogue)

					#print(obj.enable(dialogue_enable, next_dialogue, screen, player_hitbox_rect, scroll_x))
		#annoying but necessary or else the indexing goes wrong
		if update_all_ini_indexes and obj.player_collision:
			for obj in self.textprompt_group:
				if obj.is_initial_index:
					obj.is_initial_index = False
			update_all_ini_indexes = False
  
  
	def update_item_group(self, screen, player_hitbox_rect):
		for item in self.item_group:
			item.draw(screen)
			item.scroll_along(self.scroll_x)
			item.enable(player_hitbox_rect, self, self.pause_game)#player has to send pick up confirmation
	
	def update_bg_sprite_group(self, screen, player):
		particle = self.particle_group_bg.sprite
		particle.draw(screen)
		if not self.pause_game:
			particle.animate()
			particle.move(self.scroll_x)
		if particle.Active == False:
			self.particle_group_bg.remove(particle)

		for bg_sprite in self.bg_sprite_group:
			bg_sprite.draw(screen)
			if not self.pause_game:
				bg_sprite.enable(self.scroll_x, player, self.particle_group)
				bg_sprite.animate(bg_sprite.frame_rate)		
			
			
	def update_groups_behind_player(self, screen, player, world_solids):
		for enemy0 in self.enemy0_group: #[enemy0 for enemy0 in list(self.enemy0_group) if enemy0.rect.x > -32 and enemy0.rect.x < 640]:
			enemy0.draw(screen)
			if not self.pause_game:
				if enemy0.check_if_in_simulation_range(0):
					enemy0.animate(self.sp_group_list, player.hitbox_rect)
				enemy0.move(player, world_solids, self.scroll_x, self.sp_group_list)
			if enemy0.Alive == False:
				self.enemy_death_count += 1
				self.enemy0_group.remove(enemy0)

		for enemy_bullet in self.enemy_bullet_group:
			enemy_bullet.draw(screen)
			if not self.pause_game:
				enemy_bullet.animate()
				enemy_bullet.move(player, world_solids, self.scroll_x, self.sp_group_list)
			if enemy_bullet.Active == False:
				self.enemy_bullet_group.remove(enemy_bullet)
    
		for enemy_bullet in self.enemy_bullet_group2:
			enemy_bullet.draw(screen)
			if not self.pause_game:
				enemy_bullet.animate()
				enemy_bullet.move(player, world_solids, self.scroll_x, self.sp_group_list)
			if enemy_bullet.Active == False:
				self.enemy_bullet_group2.remove(enemy_bullet)
	
		for player_bullet in self.player_bullet_group:
			player_bullet.draw(screen)
			if not self.pause_game:
				player_bullet.animate()
				player_bullet.move(player, world_solids, self.scroll_x, self.sp_group_list)
			if player_bullet.Active == False:
				self.player_bullet_group.remove(player_bullet)

		particle = self.particle_group.sprite
		particle.draw(screen)
		if not self.pause_game:
			particle.animate()
			particle.move(self.scroll_x)
		if particle.Active == False:
			self.particle_group.remove(particle)
    

	def update_groups_infront_player(self, screen, player, world_solids):
    
		for p_int in self.p_int_group:
			p_int.draw(screen)
			if not self.pause_game:
				p_int.enable(player, world_solids, self.scroll_x, self.sp_group_list)
    
		for p_int2 in self.p_int_group2:
			p_int2.draw(screen)
			if not self.pause_game:
				p_int2.enable(player, world_solids, self.scroll_x, self.sp_group_list)
	
		particle = self.particle_group_fg.sprite
		particle.draw(screen)
		if not self.pause_game:
			particle.animate()
			particle.move(self.scroll_x)
		if particle.Active == False:
			self.particle_group_fg.remove(particle)

