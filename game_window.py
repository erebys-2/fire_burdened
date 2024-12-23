import pygame
import pygame._sdl2 as pg_sdl2
import os
os.environ['SDL_VIDEO_CENTERED'] = '1' 
pygame.init()

#print('directory: ' + os.getcwd())
import csv
from playerFile import player 
from worldManager import World 
from StatusBarsFile import StatusBars 
from Camera import Camera 
from music_player import music_player 
from button import Button 
from textManager import text_manager, dialogue_box 
from textfile_handler import textfile_formatter
from ui_manager import ui_manager 
from spriteGroup import sprite_group 
from ItemFile import inventory_UI
from playerChoiceHandler import player_choice_handler
from particle import particle_, group_particle
import gc
import random
from profilehooks import profile

#@profile

def main():
	monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]

	#setting the screen-----------------------------------------------------------
	SCREEN_WIDTH = 640
	HALF_SCREEN_W = SCREEN_WIDTH//2
	SCREEN_HEIGHT = 480
	standard_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
	flags = pygame.DOUBLEBUF|pygame.SHOWN #windowed mode
	#flags = pygame.DOUBLEBUF|pygame.FULLSCREEN #full screen mode
	screen = pygame.display.set_mode(standard_size, flags)

	icon = pygame.image.load('icon.png')
	pygame.display.set_icon(icon)

	pygame.display.set_caption('Fire Burdened 0.7')
	
 
	#controller set up..?
	# pg_sdl2.INIT_GAMECONTROLLER
	# pg_sdl2.INIT_EVENTS


	#framerate set up------------------------------------
	clock = pygame.time.Clock()
	FPS = 60
	#pygame.key.set_repeat(5,5)

	#local variables
	move_L = False
	move_R = False

	change_once = True

	pause_game = False
	inventory_opened = False

	text_delay = pygame.time.get_ticks()

	player0_lvl_transition_data = (False, [])#flag, data

	player_en = True
	level = 0
	next_level = 0
	rows = 0
	cols = 0
	BG_color = [0,0,0]
	gradient_type = 'none'
	level_transitioning = False

	tile_size = 32
	tile_set = 'standard'
	tile_types = len(os.listdir(f'sprites/tileset/{tile_set}'))

	damage = 0
	scroll_x = 0
	scroll_y = 0

	# t1 = textfile_formatter()
	# cutscene_data_dict = t1.str_list_to_dict(t1.read_text_from_file('save_files/initial/cutscene_data.txt'), 'true_list')
	world = World(SCREEN_WIDTH, SCREEN_HEIGHT)

	#instantiate status bars
	status_bars = StatusBars()

	#define font
	font = pygame.font.SysFont('SimSun', 12)
	font_larger = pygame.font.SysFont('SimSun', 16)
	font_massive = pygame.font.SysFont('SimSun', 48)

	#camera instance
	camera_offset = 24
	camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, camera_offset)
 
	#instantiate sprite groups=========
	the_sprite_group = sprite_group()

	#colors
	blue_0 = [100, 82, 88]
	blue1 = [97, 88, 102]
	orang = [140, 123, 108]
	black = [0,0,0]
	white = [255,255,255]
	white2 = [190,162,178]
	maroonish = [140, 107, 116]
	reddish =  [170,143,167]
	jade = [119, 121, 124]
	grey = [110, 95, 111]

	#dictionaty for gradients
	gradient_dict = {
		'none':(0,0,0),
		'sunset':(-1,-1,1),
		'rain':(-1,1,2)
	}

	#tuple for level transitions
	#level_dict: (color, gradient, y tile count, x tile count, lvl trans data, player enable)
	#lvl trans data: (width, height, next_level, player_new_x, player_new_y)
 	# 			=> (tile rect, next level, new player location)
	level_dict = {
		0:[black, 'none', 15, 30, [], False], #lvl 0
		1:[grey, 'none', 15, 200, [(2, 15*32, 2, 44*32, 160), (2, 15*32, 2, 0, 384)], True], #lvl 1
		2:[grey, 'none', 15, 45, [(2, 15*32, 1, 0, 160)], True] #lvl 2
	}
 
	level_ambiance_dict = {#scale, p_type, frame, density, sprite_group
		1:((0.5, 'dust0', 0, -10, the_sprite_group.particle_group_fg), (0, 'none')),#have to put a second dummy tuple in
		2:((0.3, 'player_bullet_explosion', 0, 1, the_sprite_group.particle_group_bg), (0.5, 'dust0', 0, -10, the_sprite_group.particle_group_fg))
	}

	#lists for dynamic CSVs
	vol_lvl = [10,10]
	ctrls_list = [119, 97, 115, 100, 105, 111, 112, 1073742054, 121, 117]
	
	# last_save_slot = int(t1.read_text_from_file('save_files/last_save_slot.txt')[0])

	text_speed = 40




	#methods--------------

	def draw_bg(screen, gradient_dict, gradient_type, bg_color):
		
		rgb = gradient_dict[gradient_type]
		#drawing bg color
		if gradient_type != 'none':
			for i in range(SCREEN_HEIGHT//32):
				pygame.draw.rect(screen, [bg_color[0]+ i*rgb[0], bg_color[1]+i*rgb[1], bg_color[2] + i*rgb[2]], ((0,i*32), (SCREEN_WIDTH,(i+1)*32)))
		else:
			screen.fill(bg_color)
	
	

	#reading settings data
	def read_settings_data(data):
		temp_list = []
		with open(f'dynamic_CSVs/{data}.csv', newline= '') as csvfile:
			reader = csv.reader(csvfile, delimiter= ',') #what separates values = delimiter
			for row in reader:
				for entry in row:
					temp_list.append(int(entry))
					
		return temp_list

	def fill_player_inv(inventory):
		player0.inventory_handler.inventory = inventory
		return False

	def set_player_coords(coords):
		player0.rect.x = coords[0]
		player0.rect.y = coords[1]
		return False

	def check_double_tap(tap, double_tap_time, double_tap_initiated, double_tap_interval):
		double_tapped = False
		#initial state, first single tap
		#set timer
		if not double_tap_initiated and tap:
			double_tap_time = pygame.time.get_ticks()
			double_tap_initiated = True
		#check if second tap falls in range and reset
		elif tap and double_tap_initiated and pygame.time.get_ticks() < double_tap_time + double_tap_interval:
			double_tapped = True
			double_tap_initiated = False
		#reset timer if second tap falls out of range
		elif tap and double_tap_initiated and pygame.time.get_ticks() > double_tap_time + double_tap_interval:
			double_tap_time = pygame.time.get_ticks()
			#double_tap_initiated = False

		return (double_tapped, double_tap_time, double_tap_initiated)


	vol_lvl = read_settings_data('vol_data') #read saved eq regime
	#more instantiations

	#dialogue box handler
	dialogue_box0 = dialogue_box(vol_lvl)

	#music player instance-------------------------------------------------------------------------------------------
	m_player_sfx_list_main = ['roblox_oof.wav', 'hat.wav']
	m_player = music_player(m_player_sfx_list_main, vol_lvl)

	#particle group handler
	group_particle_handler = group_particle()

	#player choice handler
	p_choice_handler0 = player_choice_handler([font, font_larger, font_massive], m_player_sfx_list_main, vol_lvl)

	#ui manager
	ui_manager0 = ui_manager(SCREEN_WIDTH, SCREEN_HEIGHT, [font, font_larger, font_massive], vol_lvl, monitor_size)
	update_vol = False

	#player inventory manager
	player_inv_UI = inventory_UI(3, 3, [font, font_larger, font_massive], SCREEN_WIDTH, SCREEN_HEIGHT, vol_lvl)



	#instantiate player at the start of load
	hp = 6
	speed = 4
	ccsn_chance = 10
	
	player0 = player(32, 0, speed, hp, 6, 0, 0, vol_lvl, camera_offset)#6368 #5856 #6240 #test coords for camera autocorrect
	#good news is that the player's coordinates can go off screen and currently the camera's auto scroll will eventually correct it
	normal_speed = player0.speed

	#load initial level-------------------------------------------------------------------------------------------------
	the_sprite_group.purge_sprite_groups()#does as the name suggests at the start of each load of the game

	# load level data
	world.process_data(level, the_sprite_group, SCREEN_WIDTH, SCREEN_HEIGHT, level_dict[level][2:5], vol_lvl)

	#running the game----------------------------------------------------------------------------------------------------------------------
	#https://www.youtube.com/watch?v=XPHDiibNiCM <- motivational music

	run = True
	player_new_x = 32
	player_new_y = 32
	ld_title_screen_en = True

	world_tile0_coord = (0,0)
	do_screenshake_master = False
	screenshake_profile = (8,5)

	ctrls_list = read_settings_data('ctrls_data')

	dialogue_enable = False
	next_dialogue = False
	dialogue_trigger_ready = False

	player_enable_master = False

	hold_jump_update = pygame.time.get_ticks()

	double_tap_time = pygame.time.get_ticks()
	double_tap_initiated = False
 
	selected_slot = -1
 
	joysticks = {}
 
	

	while run:
		clock.tick(FPS)
		#screen.fill((0, 0, 0)) 
		temp_move_R = False
		temp_move_L = False
		player_enable_master = (level_dict[level][5] and not level_transitioning and not camera.set_ini_pos)
	
		if level == 0 or pause_game or not player0.Alive or inventory_opened or dialogue_enable:#delete mouse when out of the main menu
			pygame.mouse.set_visible(1)
		else:
			pygame.mouse.set_visible(0)
   
	

		if player0_lvl_transition_data[0]:#test for player collision w/ level transition rects
			next_level = player0_lvl_transition_data[1][0]
			player_new_x = player0_lvl_transition_data[1][1]
			player_new_y = player0_lvl_transition_data[1][2]
   
		#need to set a player new_x and directly set player's rect y, need to set level as well

		#----------------------------------------------------------------------level changing-------------------------------------------------
		if level != next_level:
			player_en = False
			scroll_x = 0
			scroll_y = 0
			the_sprite_group.purge_sprite_groups()
			dialogue_box0.reset_internals()
			world.clear_data()
			level_transitioning = True
			level = next_level

			# load level data
			world.process_data(level, the_sprite_group, SCREEN_WIDTH, SCREEN_HEIGHT, level_dict[level][2:5], vol_lvl)
			
			if move_L:
				temp_move_L = move_L
				move_L = False
			if move_R:
				temp_move_R = move_R
				move_R = False

			if ui_manager0.set_player_location:
				ui_manager0.set_player_location = set_player_coords(ui_manager0.player_new_coords)
			else:
				player0.rect.x = player_new_x - 32 #set player location
				#player0.rect.y = player_new_y #disabling this makes it so that you can jump between levels
				player0.vel_y = 0
			
			camera.rect.centerx = HALF_SCREEN_W
			if world.x_scroll_en:
				camera.set_ini_pos = True #signal to force camera into position next cycle
	
			if temp_move_R:
				move_R = temp_move_R
			if temp_move_L:
				move_L = temp_move_L
	
		# elif level_transitioning and pygame.time.get_ticks() - 180 > level_trans_timing:
		# 	level_trans_timing = pygame.time.get_ticks()
		# 	level_transitioning = False
		elif not camera.set_ini_pos:
			level_transitioning = False
		
		
		#---------------------------------------------------------drawing level and sprites------------------------------------------------------------------
		#---------------------------------------------------------handling movement and collisions and AI----------------------------------------------------
		draw_bg(screen, gradient_dict, level_dict[level][1], level_dict[level][0])#this just draws the color
		if camera.is_visible:
			camera.draw(screen)#for camera debugging
		if world.x_scroll_en and not pause_game:
			camera.auto_correct(player0.rect, player0.direction, player0.x_coord, 
                       [tile for tile in world.coords if tile[1][0] > -32 and tile[1][0] < 640], 
                       world_tile0_coord, world.world_limit, SCREEN_WIDTH, SCREEN_HEIGHT)
		world_tile0_coord = world.draw(screen, scroll_x, scroll_y, player0.hitting_wall)#this draws the world and scrolls it 
  
		#vertical screenshake correction
		if not do_screenshake_master and world_tile0_coord[1] != 0:
			if world_tile0_coord[1] < 0:
				correction_y = -1
			elif world_tile0_coord[1] > 0:
				correction_y = 1
			else:
				correction_y = 0
			
			for data_list in world.detailed_lvl_data_list:
				for tile in data_list:
					tile[1][1] -= correction_y
		
		
		if not pause_game:
			
			if player_enable_master: 
				player0.animate(the_sprite_group)
				player0.do_entity_collisions(the_sprite_group)
				player0_lvl_transition_data = player0.move(pause_game, move_L, move_R, [tile for tile in world.solids if tile[1][0] > -32 and tile[1][0] < 640], 
                                               				world.coords, world.world_limit, world.x_scroll_en, world.y_scroll_en, 
															HALF_SCREEN_W, SCREEN_HEIGHT, the_sprite_group, ccsn_chance)
				use_item_tuple = player0.inventory_handler.item_usage_hander0.process_use_signal(player_inv_UI.use_item_flag, player_inv_UI.item_to_use, player0)
				player_inv_UI.use_item_flag = use_item_tuple[0] #use_item_flag (internal variable) is set to false
				if use_item_tuple[1]: #item_was_used, once item_was_used returns true the item gets discarded
					player_inv_UI.discard_item(player0.inventory_handler.inventory)#discard will discard the item in the current slot
			else:
				player0.scrollx = 0

			scroll_x = player0.scrollx + camera.scrollx
		else:
			scroll_x = 0
		
			
	
		#---------------------------------------screen shake------------------------------------------------------------------------
		if player0.do_screenshake:
			screenshake_profile = player0.screenshake_profile #intensity x, intensity y, cycle count
			player0.do_screenshake = False
			if not do_screenshake_master:
				do_screenshake_master = True

		for p_int in [p_int for p_int in the_sprite_group.p_int_group if p_int.do_screenshake]: #the_sprite_group.p_int_group: 
			p_int.do_screenshake = False
			if not do_screenshake_master:
				do_screenshake_master = True
				screenshake_profile = (4, 8, 3)


		for enemy in [enemy for enemy in the_sprite_group.enemy0_group if enemy.do_screenshake]: #the_sprite_group.enemy0_group:
			enemy.do_screenshake = False
			if not do_screenshake_master:
				do_screenshake_master = True
				if player0.sprint:
					screenshake_profile = (10, 6, 2)
				else:
					screenshake_profile = (6, 4, 2)

		if do_screenshake_master:
			ss_output = camera.screen_shake(screenshake_profile, do_screenshake_master)
			do_screenshake_master = ss_output[0]
			player0.rect.x += ss_output[1][0]
			scroll_x += ss_output[1][1]
			player0.vel_y += ss_output[1][2]*1.02
			scroll_y = -ss_output[1][3]
		# elif not do_screenshake_master and world.screen_rect.y != 0:
		# 	world.screen_rect.y = 0
  
		# if not do_screenshake_master and world.coords[0][1][1] != 0:
		# 	if world.coords[0][1][1] < 0:
		# 		correction_y = -1
		# 	elif world.coords[0][1][1] > 0:
		# 		correction_y = 1
		# 	else:
		# 		correction_y = 0
			
		# 	for data_list in world.detailed_lvl_data_list:
		# 		for tile in data_list:
		# 			tile[1][1] -= correction_y

			#player0.rect.x += player0.direction * 5
	
	

		#updating all sprites
		if not level_transitioning:
			#dialogue trigger sent here
			the_sprite_group.pause_game = pause_game or ui_manager0.saves_menu_enable
			the_sprite_group.scroll_x = scroll_x
			#if not level_transitioning: #surpress sprite logic while level transitioning
				
			the_sprite_group.update_bg_sprite_group(screen, player0.hitbox_rect, player0.atk_rect_scaled)
   
			screen.blit(world.world_map_non_parallax_bg, (world.coords[0][1][0], world.coords[0][1][1]))
			world.draw_filter_layer(screen, world.bg3)
			screen.blit(world.world_map_non_parallax, (world.coords[0][1][0], world.coords[0][1][1]))
			#player, world
			the_sprite_group.update_text_prompt_group(screen, dialogue_enable, next_dialogue, player0, world, selected_slot)#player and world
			next_dialogue = False
			the_sprite_group.update_groups_behind_player(screen, player0.hitbox_rect, player0.atk_rect_scaled, player0.action, player0.direction, [tile for tile in world.solids if tile[1][0] > -160 and tile[1][0] < 800])

			the_sprite_group.update_item_group(screen, player0.hitbox_rect)
			if not player0.in_cutscene:
				player0.draw(screen)
    
			world.draw_foreground(screen)
			the_sprite_group.update_groups_infront_player(screen, player0.hitbox_rect, player0.atk_rect_scaled, player0.action, world.solids)
		
			status_bars.draw(screen, player0.get_status_bars(), font)
		else:
			for group in the_sprite_group.sp_group_list:
				for sprite_ in group:
					sprite_.force_ini_position(scroll_x)
		
		#creating group particles
		if not pause_game and level in level_ambiance_dict:#scale, p_type, frame, density, sprite_group
			for particle_group_data in level_ambiance_dict[level]:
				if particle_group_data[0] != 0:
					group_particle_handler.create_particles((0-32,0), (SCREEN_WIDTH+32,SCREEN_HEIGHT), 1, particle_group_data)
		
		

  
		#adding ambience particles
		

		#--------------------------------------------------------------------handling drawing text boxes------------------------------------------------------------------
		#textboxes have a maximum of 240 characters
		
		if the_sprite_group.textbox_output[0] != '' and the_sprite_group.textbox_output[1] and the_sprite_group.textbox_output[2] and not the_sprite_group.textbox_output[6][0]:
			#the_sprite_group.textbox_output = (
			# name, (string)
   			# player_collision, (boolean)
			# dialogue_enable, (boolean)
   			# message, (string)
			# expression, (int)
			# self.character_index_dict[self.name], (int)
			# (player choice tuple)
			# enable
			# )
			
			dialogue_box0.draw_text_box(the_sprite_group.textbox_output, font_larger, screen, text_speed, player0.in_cutscene)

		elif the_sprite_group.textbox_output[6][0] and the_sprite_group.textbox_output[2]: #handling player choice
		
			dialogue_box0.draw_box_and_portrait(screen, the_sprite_group.textbox_output[4], the_sprite_group.textbox_output[5])
			p_choice_output = p_choice_handler0.deploy_buttons(the_sprite_group.textbox_output[6][1], screen, player0, level, world)
			next_dialogue_index = p_choice_output[0]
   
			if next_dialogue_index != -3:
				for npc in the_sprite_group.textprompt_group: #look for npc in sprite group what has a player choice open
					if npc.player_choice_flag:
						npc.force_dialogue_index(next_dialogue_index)
						p_choice_handler0.trigger_once = True
						dialogue_box0.type_out = True


	
		#----------black screen while transitioning---------------------------------------------------------
		if level_transitioning:
			pygame.draw.rect(screen, (0,0,0), (0,0,SCREEN_WIDTH,SCREEN_HEIGHT))
	
		#--------------------------------------------------------------MAIN MENU CODE---------------------------------------------------------------------
		if level == 0 or ui_manager0.saves_menu_enable: 
			draw_bg(screen, gradient_dict, level_dict[level][1], level_dict[level][0])
			pause_game = False
			exit_to_title = False

			#plot index list's csv is read within ui_manager
			if ui_manager0.saves_menu_enable:
				ui_output = ui_manager0.show_saves_menu(screen)
				if ui_manager0.selected_slot != -1 and selected_slot != ui_manager0.selected_slot:
        			#change slot and reset death counters across levels if a different slot is selected
					world.death_counters_dict = {0: 0}
					selected_slot = ui_manager0.selected_slot
			elif ui_manager0.saves_menu2_enable:
				ui_output = ui_manager0.show_saves_menu2(screen)
				if ui_manager0.selected_slot != -1:# and selected_slot != ui_manager0.selected_slot:
					world.death_counters_dict = {0: 0}
					selected_slot = ui_manager0.selected_slot
			else:
				ui_output = ui_manager0.show_main_menu(screen)
	
			world.set_plot_index_dict(plot_index_dict = ui_output[2])#world plot index saved here
			run = ui_output[1]
			next_level = ui_output[0]
	
			if not run:
				pygame.time.wait(100)   
			
			elif run and ui_manager0.saves_menu_enable and player0.hits_tanked == hp and not player0.Alive:
				#reset player0
				player0 = player(32, 0, speed, hp, 6, 0, 0, vol_lvl, camera_offset)
	
		#-------------------------------------------------pausing game--------------------------------------------------------
		if pause_game:
			#this code draws the actual pause menu
			#need another conditional for pressing esc while in a cut scene
			ui_tuple0 = ui_manager0.show_pause_menu(screen)
			pause_game = ui_tuple0[0]
			if ui_tuple0[1]:
				next_level = 0
				player0 = player(32, 0, speed, hp, 6, 0, 0, vol_lvl, camera_offset)
				player_new_x = 32
				player_new_y = 32
		
		#-----------------------------------------inventory and items
		#opening inventory
		if inventory_opened:
			player_inv_UI.open_inventory(player0.inventory_handler.inventory, screen, ctrls_list[8])
			if player_inv_UI.use_item_btn_output and player_inv_UI.press_use_item_btn(player0.inventory_handler.inventory) and player0.action != 15:
				player0.using_item = player_inv_UI.use_item_btn_output #start use item animation
				player0.speed = 0
				player_inv_UI.use_item_btn_output = False
				
  
		if player0.finished_use_item_animation:
			player_inv_UI.use_item_flag = True
			player0.finished_use_item_animation = False
   
		if ui_manager0.set_player_inv:
			ui_manager0.set_player_inv = fill_player_inv(ui_manager0.player_new_inv)
   

		#---------------------------------updates from ui manager-----------------------------------------
		if ui_manager0.ctrls_updated:
			ctrls_list = read_settings_data('ctrls_data')
			ui_manager0.ctrls_updated = False
	
		if update_vol: #updates all m_players' sounds with new volume setting
		#objects already instantiated have their volumes updated here
		#new objects take vol_lvl as their ini_vol parameter so their volumes match the setting upon instantiation
			vol_lvl = read_settings_data('vol_data')
			dialogue_box0.m_player.set_vol_all_sounds(vol_lvl)
			m_player.set_vol_all_sounds(vol_lvl)
			the_sprite_group.update_vol_lvl(vol_lvl)
			player0.m_player.set_vol_all_sounds(vol_lvl)
			player_inv_UI.m_player.set_vol_all_sounds(vol_lvl)
			p_choice_handler0.m_player.set_vol_all_sounds(vol_lvl)
	
		update_vol = ui_manager0.raise_volume or ui_manager0.lower_volume #2 different signals from ui_manager or'd together
	
	
		#-----------------------------------------------------------------------------------------------------------------------------------------------------------
		#handling player death and game over screen------------------------------------------------------------------------------------
		
		if player0.hits_tanked >= player0.hp or player0.rect.y > 480:#killing the player------------------------------------------------
			if player0.Alive:
				player0.Alive = False
				#death counters will probably belong to an instance of world amd reset upon new games
				#increment level death counters
				if level in world.death_counters_dict:
					world.death_counters_dict[level] += 1

			if inventory_opened:#exit inventory if opened
				inventory_opened = False
				player_inv_UI.close_inventory()

			if ui_manager0.show_death_menu(screen):
				next_level = 0
				player0 = player(32, 0, speed, hp, 6, 0, 0, vol_lvl, camera_offset)
				player_new_x = 32
				player_new_y = 32
	
		if player0.brain_damage:
			temp_list = []
			for i in range(len(ctrls_list)):
				temp_list.append(random.randint(90,120))
			ui_manager0.write_csv_data('ctrls_data',  temp_list)
			ctrls_list = read_settings_data('ctrls_data')
			temp_list *= 0
			if ccsn_chance > 1:
				ccsn_chance = ccsn_chance//2
			move_L = False
			move_R = False
			player0.brain_damage = False

		#============================================================update player action for animation=======================================================
		#this is remnant code from following Coding with Russ' tutorial, I wasn't sure how to integrate this into playerFile.py
		#when I was separating the files (he wrote his whole tutorial game in virtually one single file)
	
		#takes change_once, move_L, move_R 
		if dialogue_enable:
			player0.atk1 = False
			player0.atk1_kill_hitbox()
			player0.action = 0
			player0.rolled_into_wall = True
			inventory_opened = False
		else:#important spaghetti code for making dialogue boxes work
			dialogue_box0.reset_internals()
			text_speed = 40
			
		if player0.in_cutscene:#dialogue system will activate as soon as the player collides with a 'cutscene' npc
			dialogue_enable = True
			
		if player0.hurting or not player0.dialogue_trigger_ready:
			dialogue_enable = False
			
			
			
		#note there is a problem with the dialogue system where if an npc is trying to modify another npc's plot index list and the dialogue is cut off mid typing,
		#the current index will linger (one of the parameters for changing plot index list), even if the player talks to another npc, the next time the player
		#talks to the npc that was cut off plot index will be reset to the value from when it first changed since npc's will continue their dialogue from when they
		#were cut off
	
		#dialogue boxes can no longer be exited if an npc is mid dialogue
		#however they can still be interupted by the player getting damaged

	
		if player0.Alive:
			dialogue_trigger_ready = player0.dialogue_trigger_ready
   
			if player0.sprint and player0.using_item:
				player0.speed = 0
			elif player0.sprint and not player0.using_item:
				player0.speed = normal_speed + 1
    
			if (player0.hurting):
				player0.update_action(5) #hurting
			else:
			
				if player0.shoot:
					player0.update_action(11)
				
				elif player0.atk1:
					
					if change_once:
						if player0.vel_y < -0.1:
							player0.atk1_alternate = True
						elif player0.vel_y > 0.1:
							player0.atk1_alternate = False
						change_once = False

					if player0.crit:
						player0.update_action(10)
					else:
						if player0.atk1_alternate:# and player0.in_air == False:
							player0.update_action(7)	
						else:
							player0.update_action(8)#8: atk1
				elif player0.using_item:#and player0.action != 15:
					player0.update_action(15)
					# move_L = False
					# move_R = False
					player0.rolling = False
					player0.atk1 = False
					player0.shoot = False
					
				elif player0.rolling: 
					player0.update_action(9)#rolling
					player0.atk1_alternate = False
				else:
					#print(player0.in_air)
					if player0.in_air or player0.squat_done:# or (player0.vel_y > 1):
						player0.update_action(2)#2: jump

					elif ( not (move_L or move_R) and
						not player0.in_air and
						player0.vel_y >= 0 and
						player0.landing
						):
						player0.update_action(3)#3: land
						
					elif player0.squat: 
						player0.update_action(4)#4: squat

					elif move_R or move_L:
						player0.update_action(1)#1: run
					else:
						player0.update_action(0)#0: idle
		else:
			player0.update_action(6) #dead
			player0.scrollx = 0
		
		#print(the_sprite_group.textbox_output)
		#---------------------------------------------------------------------------------------------------------------------------------------------
		#-------------------------------------------------------KBD inputs----------------------------------------------------------------------------
		#---------------------------------------------------------------------------------------------------------------------------------------------
		for event in pygame.event.get():
			#quit game
			if(event.type == pygame.QUIT):
				run = False

			#from pygame joysticks example
			if event.type == pygame.JOYDEVICEADDED: #only kind of works
				# This event will be generated when the program starts for every
				# joystick, filling up the list without needing to create them manually.
				joy = pygame.joystick.Joystick(event.device_index)
				joysticks[joy.get_instance_id()] = joy
				print(f"Joystick {joy.get_instance_id()} connencted")
				ui_manager0.controller_connected = True

			if event.type == pygame.JOYDEVICEREMOVED:
				del joysticks[event.instance_id]
				print(f"Joystick {event.instance_id} disconnected")
				ui_manager0.controller_connected = False

			#key press
			
			if(event.type == pygame.KEYDOWN):
				#print(pygame.key.name(event.key))
				if player0.Alive and level_dict[level][5] and not pause_game and not dialogue_enable:
					
					if event.key == ctrls_list[1]: #pygame.K_a
						move_L = True
						#move_R = False
						# output = check_double_tap(True, double_tap_time, double_tap_initiated, 320)
						# double_tap_initiated = output[2]
						# double_tap_time = output[1]
						# if output[0]:
						# 	player0.sprint = True
					if event.key == ctrls_list[3]: #pygame.K_d
						move_R = True
						#move_L = False
						# output = check_double_tap(True, double_tap_time, double_tap_initiated, 320)
						# double_tap_initiated = output[2]
						# double_tap_time = output[1]
						# if output[0]:
						# 	player0.sprint = True
					# if event.key == ctrls_list[0] and event.key == ctrls_list[4] and player0.stamina_used + 1 <= player0.stamina:
					# 	player0.squat = True
					# 	player0.squat_done = True
					# 	player0.atk1_alternate = False
					# 	change_once = False
					# 	player0.atk1 = (event.key == ctrls_list[4])
					if event.key == ctrls_list[0]: #pygame.K_w 
						
						player0.landing = False

						if not player0.in_air: #player is on ground
							player0.squat = True
						elif player0.in_air and pygame.time.get_ticks() - 10 > hold_jump_update:
							hold_jump_update = pygame.time.get_ticks()
							player0.squat = True 

						if player0.rolling and player0.in_air == False:
							player0.roll_count = player0.roll_limit
							player0.squat = True

					if event.key == ctrls_list[4] and player0.stamina_used + player0.atk1_stamina_cost <= player0.stamina and event.key != ctrls_list[0] and not player0.using_item: #pygame.K_i, pygame.K_w
						change_once = True
						player0.atk1 = True # (event.key == ctrls_list[4])

					elif event.key == ctrls_list[4] and player0.stamina_used + player0.atk1_stamina_cost > player0.stamina: #pygame.K_i
						status_bars.warning = True
					
					if event.key == ctrls_list[5] and player0.stamina_used + player0.shoot_stamina_cost <= player0.stamina and not player0.using_item: #pygame.K_o
						player0.shot_charging = True
					elif event.key == ctrls_list[5] and player0.stamina_used + player0.shoot_stamina_cost > player0.stamina: #pygame.K_o
						status_bars.warning = True
		

					if event.key == ctrls_list[2] and player0.stamina_used + player0.roll_stam_rate + player0.roll_stamina_cost <= player0.stamina: #pygame.K_s
						player0.squat = False
						player0.rolling = True

					elif event.key == ctrls_list[2] and player0.stamina_used + player0.roll_stam_rate + player0.roll_stamina_cost > player0.stamina: #pygame.K_s
						status_bars.warning = True
		
					if event.key == ctrls_list[7]: #pygame.K_RALT
						player0.sprint = True
					#press button and check if item selected can be used
					if ((event.key == ctrls_list[9] or player_inv_UI.use_item_btn_output) 
						and player_inv_UI.press_use_item_btn(player0.inventory_handler.inventory)
                        #and player0.inventory_handler.item_usage_hander0.sub_function_dict[][0] != 'nothing'
                    	):
						
						#trigger an animation here
						#let the last frame of the animation trigger apply the effects of the item
						#player_inv_UI.press_use_item_btn(player0.inventory_handler.inventory)
						if not player_inv_UI.use_item_btn_output: #using the use item key
							player0.using_item = (event.key == ctrls_list[9])
						elif event.key != ctrls_list[9]: #using the use item button
							player0.using_item = player_inv_UI.use_item_btn_output
							player_inv_UI.use_item_btn_output = False
						player0.speed = 0 #set speed to 0, it will be reset to default speed at the end of the animation
						#insert test inventory:
						#player0.inventory_handler.load_saved_inventory([['a', 1], ['b', 1], ['c', 1], ['d', 1], ['e', 1], ['f', 1], ['g', 1], ['h', 1], ['i', 1], ['empty', 0]])
					
					#open inventory
					if event.key == ctrls_list[8] and not dialogue_enable:
						inventory_opened = not inventory_opened
						if inventory_opened:
							player_inv_UI.close_inventory()
		
		
					#debugging flight button
					#if you fly over the camera object the level breaks
					if event.key == pygame.K_0:
						player0.squat_done = True

				#===============================================================UI Related Keys=============================================================

				# if event.key == pygame.K_m:
				# 	m_player.play_song('newsong18.wav')
				if event.key == pygame.K_c:
					camera.is_visible = not camera.is_visible

				if (event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE) and not ui_manager0.options_menu_enable and not ui_manager0.saves_menu_enable: 
				#escape exits UI ONLY before the options sub menu is shown and any deeper into sub menus
					if level != 0:
						ui_manager0.trigger_once = True

						if (pause_game or not player0.Alive) and not dialogue_enable: #exit to main menu from pause game
							next_level = 0
							player0 = player(32, 0, speed, hp, 6, 0, 0, vol_lvl, camera_offset)
							player_new_x = 32
							player_new_y = 32
							dialogue_box0.reset_internals()
							pygame.mixer.stop()
							m_player.play_sound(m_player.sfx[1])

						elif not dialogue_enable and not inventory_opened: #pause game, will trigger if player is not in dialogue
							pause_game = True
							pygame.mixer.pause()
							m_player.play_sound(m_player.sfx[1])
		
						elif (not player0.in_cutscene and #cannot esc out of cutscene
            					(dialogue_box0.str_list_rebuilt == dialogue_box0.current_str_list or 
                  				the_sprite_group.textbox_output[6][0])
                 				): #exits dialogue window if an NPC finishes speaking (is this way to avoid bugs)
							dialogue_enable = False
							p_choice_handler0.disable()

						if inventory_opened:#exit inventory if opened
							inventory_opened = False
							player_inv_UI.close_inventory()
							
					else:#if on the main menu, the game will exit on button press
						run = False
				
		
				if event.key == pygame.K_RETURN:
					if pause_game and not ui_manager0.options_menu_enable:
						ui_manager0.trigger_once = True
						dialogue_trigger_ready = False
						pause_game = False
						pygame.mixer.unpause()
					
					if dialogue_trigger_ready or player0.in_cutscene:
						dialogue_enable = True
					if dialogue_enable and not the_sprite_group.textbox_output[6][0]:
						if dialogue_box0.str_list_rebuilt != dialogue_box0.current_str_list:
							text_speed = 0
							m_player.play_sound(m_player.sfx[1])
						else:
							text_speed = 40
							next_dialogue = True
							dialogue_box0.type_out = True				
     
					if level == 0:#default case, auto saving will overwrite data in file 0
						m_player.play_sound(m_player.sfx[1])
						ui_manager0.trigger_once = True
						next_level = 1
						selected_slot = 0

				# #temp bg adjustment
				# amnt = 1
				# if event.key == pygame.K_5:
				# 	amnt = -1
				# 	print(amnt)
				# elif event.key == pygame.K_6:
				# 	amnt = 1
				# 	print(amnt)
				# if event.key == pygame.K_1 or event.key == pygame.K_2 or event.key == pygame.K_3:
				# 	pygame.key.set_repeat(5,60)
				# 	if event.key == pygame.K_1 and BG_color[0] < 256 and BG_color[0] > 0:
				# 		BG_color[0] += amnt
				# 		#print(BG_color[0])
				# 	if event.key == pygame.K_2 and BG_color[1] < 256 and BG_color[1] > 0:
				# 		BG_color[1] += amnt
				# 	if event.key == pygame.K_3 and BG_color[2] < 256 and BG_color[2] > 0:
				# 		BG_color[2] += amnt
				# else:
				# 	pygame.key.set_repeat(0,0)
				
				# if event.key == pygame.K_4:
				# 	print(BG_color)
				


			if(event.type == pygame.KEYUP):
				if event.key == ctrls_list[1]:#pygame.K_a
					move_L = False
					
				if event.key == ctrls_list[3]:#pygame.K_d
					move_R = False
					
				#delayed full jump bug:
				#if the the animation for squatting before a jump is just slow enough, it might finish AFTER  the jump key is released
				#so the code below to limit the jump height will not execute, resulting in a full height jump if the jump key is pressed sufficiently fast enough
				#switched to continuous signal
				if event.key == ctrls_list[0]:#variable height jumping
					player0.jump_dampen = True

				if event.key == ctrls_list[4]:#pygame.K_i
					status_bars.warning = False
				if event.key == ctrls_list[2]:#pygame.K_s
					status_bars.warning = False
				if event.key == ctrls_list[5]:#pygame.K_o
					status_bars.warning = False
					player0.frame_updateBP = 150
					if player0.shot_charging == True:
						player0.shoot = True
						player0.shot_charging = False

				if event.key == ctrls_list[7]: #pygame.K_RALT
					player0.speed = normal_speed
					player0.sprint = False
     
		#==============================================================================================================
		#==============================================CONTROLLER EVENT INPUTS==========================================
		#==================================================================================================================
			if(event.type == pygame.JOYBUTTONDOWN):
				#print(pygame.button.name(event.button))
				if player0.Alive and level_dict[level][5] and not pause_game and not dialogue_enable:
					
					if event.button == ctrls_list[1]: #pygame.K_a
						move_L = True
						#move_R = False
						# output = check_double_tap(True, double_tap_time, double_tap_initiated, 320)
						# double_tap_initiated = output[2]
						# double_tap_time = output[1]
						# if output[0]:
						# 	player0.sprint = True
					if event.button == ctrls_list[3]: #pygame.K_d
						move_R = True
						#move_L = False
						# output = check_double_tap(True, double_tap_time, double_tap_initiated, 320)
						# double_tap_initiated = output[2]
						# double_tap_time = output[1]
						# if output[0]:
						# 	player0.sprint = True
					# if event.button == ctrls_list[0] and event.button == ctrls_list[4] and player0.stamina_used + 1 <= player0.stamina:
					# 	player0.squat = True
					# 	player0.squat_done = True
					# 	player0.atk1_alternate = False
					# 	change_once = False
					# 	player0.atk1 = (event.button == ctrls_list[4])
					if event.button == ctrls_list[0]: #pygame.K_w 
						
						player0.landing = False

						if not player0.in_air: #player is on ground
							player0.squat = True
						elif player0.in_air and pygame.time.get_ticks() - 10 > hold_jump_update:
							hold_jump_update = pygame.time.get_ticks()
							player0.squat = True 

						if player0.rolling and player0.in_air == False:
							player0.roll_count = player0.roll_limit
							player0.squat = True

					if event.button == ctrls_list[4] and player0.stamina_used + player0.atk1_stamina_cost <= player0.stamina and event.button != ctrls_list[0] and not player0.using_item: #pygame.K_i, pygame.K_w
						change_once = True
						player0.atk1 = True # (event.button == ctrls_list[4])

					elif event.button == ctrls_list[4] and player0.stamina_used + player0.atk1_stamina_cost > player0.stamina: #pygame.K_i
						status_bars.warning = True
					
					if event.button == ctrls_list[5] and player0.stamina_used + player0.shoot_stamina_cost <= player0.stamina and not player0.using_item: #pygame.K_o
						player0.shot_charging = True
					elif event.button == ctrls_list[5] and player0.stamina_used + player0.shoot_stamina_cost > player0.stamina: #pygame.K_o
						status_bars.warning = True
		

					if event.button == ctrls_list[2] and player0.stamina_used + player0.roll_stam_rate + player0.roll_stamina_cost <= player0.stamina: #pygame.K_s
						player0.squat = False
						player0.rolling = True

					elif event.button == ctrls_list[2] and player0.stamina_used + player0.roll_stam_rate + player0.roll_stamina_cost > player0.stamina: #pygame.K_s
						status_bars.warning = True
		
					if event.button == ctrls_list[7]: #pygame.K_RALT
						player0.sprint = True
					#press button and check if item selected can be used
					if ((event.button == ctrls_list[9] or player_inv_UI.use_item_btn_output) 
						and player_inv_UI.press_use_item_btn(player0.inventory_handler.inventory)
                        #and player0.inventory_handler.item_usage_hander0.sub_function_dict[][0] != 'nothing'
                    	):
						
						#trigger an animation here
						#let the last frame of the animation trigger apply the effects of the item
						#player_inv_UI.press_use_item_btn(player0.inventory_handler.inventory)
						if not player_inv_UI.use_item_btn_output: #using the use item key
							player0.using_item = (event.button == ctrls_list[9])
						elif event.button != ctrls_list[9]: #using the use item button
							player0.using_item = player_inv_UI.use_item_btn_output
							player_inv_UI.use_item_btn_output = False
						player0.speed = 0 #set speed to 0, it will be reset to default speed at the end of the animation
						#insert test inventory:
						#player0.inventory_handler.load_saved_inventory([['a', 1], ['b', 1], ['c', 1], ['d', 1], ['e', 1], ['f', 1], ['g', 1], ['h', 1], ['i', 1], ['empty', 0]])
					
					#open inventory
					if event.button == ctrls_list[8] and not dialogue_enable:
						inventory_opened = not inventory_opened
						if inventory_opened:
							player_inv_UI.close_inventory()
		
		
					#debugging flight button
					#if you fly over the camera object the level breaks
					if event.button == pygame.K_0:
						player0.squat_done = True

				#===============================================================UI Related Keys=============================================================

				# if event.button == pygame.K_m:
				# 	m_player.play_song('newsong18.wav')
				if event.button == pygame.K_c:
					camera.is_visible = not camera.is_visible

				if (event.button == pygame.K_BACKSPACE or event.button == pygame.K_ESCAPE) and not ui_manager0.options_menu_enable and not ui_manager0.saves_menu_enable: 
				#escape exits UI ONLY before the options sub menu is shown and any deeper into sub menus
					if level != 0:
						ui_manager0.trigger_once = True

						if (pause_game or not player0.Alive) and not dialogue_enable: #exit to main menu from pause game
							next_level = 0
							player0 = player(32, 0, speed, hp, 6, 0, 0, vol_lvl, camera_offset)
							player_new_x = 32
							player_new_y = 32
							dialogue_box0.reset_internals()
							pygame.mixer.stop()
							m_player.play_sound(m_player.sfx[1])

						elif not dialogue_enable and not inventory_opened: #pause game, will trigger if player is not in dialogue
							pause_game = True
							pygame.mixer.pause()
							m_player.play_sound(m_player.sfx[1])
		
						elif (not player0.in_cutscene and #cannot esc out of cutscene
            					(dialogue_box0.str_list_rebuilt == dialogue_box0.current_str_list or 
                  				the_sprite_group.textbox_output[6][0])
                 				): #exits dialogue window if an NPC finishes speaking (is this way to avoid bugs)
							dialogue_enable = False
							p_choice_handler0.disable()

						if inventory_opened:#exit inventory if opened
							inventory_opened = False
							player_inv_UI.close_inventory()
							
					else:#if on the main menu, the game will exit on button press
						run = False
				
		
				if event.button == pygame.K_RETURN:
					if pause_game and not ui_manager0.options_menu_enable:
						ui_manager0.trigger_once = True
						dialogue_trigger_ready = False
						pause_game = False
						pygame.mixer.unpause()
					
					if dialogue_trigger_ready or player0.in_cutscene:
						dialogue_enable = True
					if dialogue_enable and not the_sprite_group.textbox_output[6][0]:
						if dialogue_box0.str_list_rebuilt != dialogue_box0.current_str_list:
							text_speed = 0
							m_player.play_sound(m_player.sfx[1])
						else:
							text_speed = 40
							next_dialogue = True
							dialogue_box0.type_out = True				
     
					if level == 0:#default case, auto saving will overwrite data in file 0
						m_player.play_sound(m_player.sfx[1])
						ui_manager0.trigger_once = True
						next_level = 1
						selected_slot = 0

				# #temp bg adjustment
				# amnt = 1
				# if event.button == pygame.K_5:
				# 	amnt = -1
				# 	print(amnt)
				# elif event.button == pygame.K_6:
				# 	amnt = 1
				# 	print(amnt)
				# if event.button == pygame.K_1 or event.button == pygame.K_2 or event.button == pygame.K_3:
				# 	pygame.button.set_repeat(5,60)
				# 	if event.button == pygame.K_1 and BG_color[0] < 256 and BG_color[0] > 0:
				# 		BG_color[0] += amnt
				# 		#print(BG_color[0])
				# 	if event.button == pygame.K_2 and BG_color[1] < 256 and BG_color[1] > 0:
				# 		BG_color[1] += amnt
				# 	if event.button == pygame.K_3 and BG_color[2] < 256 and BG_color[2] > 0:
				# 		BG_color[2] += amnt
				# else:
				# 	pygame.button.set_repeat(0,0)
				
				# if event.button == pygame.K_4:
				# 	print(BG_color)
				


			if(event.type == pygame.JOYBUTTONUP):
				if event.button == ctrls_list[1]:#pygame.K_a
					move_L = False
					
				if event.button == ctrls_list[3]:#pygame.K_d
					move_R = False
					
				#delayed full jump bug:
				#if the the animation for squatting before a jump is just slow enough, it might finish AFTER  the jump key is released
				#so the code below to limit the jump height will not execute, resulting in a full height jump if the jump key is pressed sufficiently fast enough
				#switched to continuous signal
				if event.button == ctrls_list[0]:#variable height jumping
					player0.jump_dampen = True

				if event.button == ctrls_list[4]:#pygame.K_i
					status_bars.warning = False
				if event.button == ctrls_list[2]:#pygame.K_s
					status_bars.warning = False
				if event.button == ctrls_list[5]:#pygame.K_o
					status_bars.warning = False
					player0.frame_updateBP = 150
					if player0.shot_charging == True:
						player0.shoot = True
						player0.shot_charging = False

				if event.button == ctrls_list[7]: #pygame.K_RALT
					player0.speed = normal_speed
					player0.sprint = False



		pygame.display.update()
		pygame.display.set_caption(f"Fire Burdened 0.7 @ {clock.get_fps():.1f} FPS")

	pygame.quit()



if __name__ == '__main__':
    main()