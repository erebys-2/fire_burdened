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
		
		self.sp_group_list = [
			self.enemy0_group,
			self.enemy_bullet_group,
			self.player_bullet_group,
			self.particle_group,
			self.particle_group_bg,
			self.particle_group_fg,
			self.button_group
		]

	def purge_sprite_groups(self):
		for group in self.sp_group_list:
			group.empty()
			
	def update_groups_behind_player(self, screen, player_hitbox_rect, player_atk_rect_scaled, world_solids, scroll_x, player_action, player_direction):
		for particle in self.particle_group_bg:
			particle.draw(screen)
			particle.animate()
			particle.move(scroll_x)
			if particle.Active == False:
				self.particle_group_bg.remove(particle)

		for enemy0 in self.enemy0_group:
			enemy0.draw(screen)
			enemy0.animate(self.sp_group_list)
			enemy0.move(player_hitbox_rect, player_atk_rect_scaled, world_solids, scroll_x, player_action, self.sp_group_list)
			if enemy0.Alive == False:
				self.enemy0_group.remove(enemy0)
    
		for enemy_bullet in self.enemy_bullet_group:
			enemy_bullet.draw(screen)
			enemy_bullet.animate()
			enemy_bullet.move(player_hitbox_rect, player_atk_rect_scaled, world_solids, scroll_x, player_action, self.sp_group_list, player_direction)
			if enemy_bullet.Active == False:
				self.enemy_bullet_group.remove(enemy_bullet)
	
		for player_bullet in self.player_bullet_group:
			player_bullet.draw(screen)
			player_bullet.animate()
			player_bullet.move(player_hitbox_rect, player_atk_rect_scaled, world_solids, scroll_x, player_action, self.sp_group_list, player_direction)
			if player_bullet.Active == False:
				self.player_bullet_group.remove(player_bullet)
    
		for particle in self.particle_group:
			particle.draw(screen)
			particle.animate()
			particle.move(scroll_x)
			if particle.Active == False:
				self.particle_group.remove(particle)
    
	def update_groups_infront_player(self, screen, scroll_x):
		for particle in self.particle_group_fg:
			particle.draw(screen)
			particle.animate()
			particle.move(scroll_x)
			if particle.Active == False:
				self.particle_group_fg.remove(particle)

