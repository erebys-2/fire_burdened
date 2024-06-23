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
		
		self.sp_groups_with_vol = [
			self.enemy0_group,
			self.enemy_bullet_group
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
			self.enemy_bullet_group2
		]
  
		self.hostiles_group = (self.enemy0_group, self.enemy_bullet_group, self.enemy_bullet_group2)
  
	def update_vol_lvl(self, level):
		for sp_group in self.sp_groups_with_vol:
			for sprite in sp_group:
				sprite.m_player.set_vol_all_sounds(level)

	def purge_sprite_groups(self):
		for group in self.sp_group_list:
			group.empty()
			
	def update_groups_behind_player(self, pause_game, screen, player_hitbox_rect, player_atk_rect_scaled, world_solids, scroll_x, player_action, player_direction, obj_list):
		for particle in self.particle_group_bg:
			particle.draw(screen)
			if not pause_game:
				particle.animate()
				particle.move(scroll_x)
			if particle.Active == False:
				self.particle_group_bg.remove(particle)

		for enemy0 in self.enemy0_group:
			enemy0.draw(screen)
			if not pause_game:
				enemy0.animate(self.sp_group_list, obj_list)
				enemy0.move(player_hitbox_rect, player_atk_rect_scaled, world_solids, scroll_x, player_action, self.sp_group_list)
			# elif update_vol:
			# 	enemy0.m_player.update_eq_regime()
			if enemy0.Alive == False:
				self.enemy0_group.remove(enemy0)

		for enemy_bullet in self.enemy_bullet_group:
			enemy_bullet.draw(screen)
			if not pause_game:
				enemy_bullet.animate()
				enemy_bullet.move(player_hitbox_rect, player_atk_rect_scaled, world_solids, scroll_x, player_action, self.sp_group_list, player_direction)
			# elif update_vol:
			# 	enemy_bullet.m_player.update_eq_regime()
			if enemy_bullet.Active == False:
				self.enemy_bullet_group.remove(enemy_bullet)
    
		for enemy_bullet in self.enemy_bullet_group2:
			enemy_bullet.draw(screen)
			if not pause_game:
				enemy_bullet.animate()
				enemy_bullet.move(player_hitbox_rect, player_atk_rect_scaled, world_solids, scroll_x, player_action, self.sp_group_list, player_direction)
			# elif update_vol:
			# 	enemy_bullet.m_player.update_eq_regime()
			if enemy_bullet.Active == False:
				self.enemy_bullet_group2.remove(enemy_bullet)
	
		for player_bullet in self.player_bullet_group:
			player_bullet.draw(screen)
			if not pause_game:
				player_bullet.animate()
				player_bullet.move(player_hitbox_rect, player_atk_rect_scaled, world_solids, scroll_x, player_action, self.sp_group_list, player_direction)
			# elif update_vol:
			# 	player_bullet.m_player.update_eq_regime()
			if player_bullet.Active == False:
				self.player_bullet_group.remove(player_bullet)
    
		for particle in self.particle_group:
			particle.draw(screen)
			if not pause_game:
				particle.animate()
				particle.move(scroll_x)
			if particle.Active == False:
				self.particle_group.remove(particle)
    
	def update_groups_infront_player(self, pause_game, screen, scroll_x):
		for particle in self.particle_group_fg:
			particle.draw(screen)
			if not pause_game:
				particle.animate()
				particle.move(scroll_x)
			if particle.Active == False:
				self.particle_group_fg.remove(particle)

