import pygame
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
from ItemFile import inventory_UI, trade_menu_ui
from playerChoiceHandler import player_choice_handler
from particle import particle_2, group_particle2
import random
# import moderngl
# from array import array
# from shadersHandler import modernGL_handler
from profilehooks import profile

#@profile

def main():
	print('starting game')
	icon = pygame.image.load('assets/icon.png')
	pygame.display.set_icon(icon)
	monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]

	#setting the screen-----------------------------------------------------------
	SCREEN_WIDTH = 640
	HALF_SCREEN_W = SCREEN_WIDTH//2
	SCREEN_HEIGHT = 480
	standard_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
	flags = pygame.DOUBLEBUF|pygame.SHOWN #|pygame.OPENGL #windowed mode

	# window = pygame.display.set_mode(standard_size, flags, vsync=0)
	# screen = pygame.Surface(standard_size)
	screen = pygame.display.set_mode(standard_size, flags, vsync=0)

	

	pygame.display.set_caption(' ')
	

	#framerate set up------------------------------------
	clock = pygame.time.Clock()
	FPS = 60
	#pygame.key.set_repeat(5,5)

	#local variables
	move_L = False
	move_R = False
	inv_directions = [False] * 5
 
	change_once = True

	pause_game = False
	inventory_opened = False

	area_name_time = pygame.time.get_ticks()
	last_area_name = ''

	player0_lvl_transition_data = (False, [])#flag, data

	player_en = True
	level = 0
	next_level = 0
	BG_color = [0,0,0]
	gradient_type = 'none'
	level_transitioning = False
	lvl_transition_counter = 0

	ts = 32 #tile size

	scroll_x = 0
	scroll_y = 0

	world = World(SCREEN_WIDTH, SCREEN_HEIGHT)#also instantiates sp_ini

	#instantiate status bars
	status_bars = StatusBars(SCREEN_WIDTH, SCREEN_HEIGHT, ts)


	#define font
	font = pygame.font.SysFont('SimSun', 12)
	font_larger = pygame.font.SysFont('SimSun', 16)
	font_largerer = pygame.font.SysFont('SimSun', 24)
	font_massive = pygame.font.SysFont('SimSun', 48)

	#camera instance
	camera_offset = int(0.75 * ts)
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
	dark_grey = [30, 29, 36]

	#dictionaty for gradients
	gradient_dict = {
		'none':(0,0,0),
		'sunset':(-1,-1,1),
		'rain':(-1,1,2)
	}

	#tuple for level transitions
	#level_dict: (color, gradient, y tile count, x tile count, lvl trans data, player enable)
	#lvl trans data: (width, height, next_level, player_new_x, player_new_y, paired_index)
 	# 			=> (tile rect, next level, new player location)
	null = -999
	ht = SCREEN_HEIGHT
	wd = SCREEN_WIDTH
	std_y_disp = ht - 3*ts
	
	level_dict = {
		#==================================================================Note that tile order priority is row then column=================================================================
		0:[black, 'none', [], False, ''], #lvl 0
		1:[grey, 'none', [(2, ht, 2, 44*ts, null, null), (2, ht, 3, 0, null, null)], True, 'Outer City Ruins'], #lvl 1
		2:[grey, 'none', [(2, ht, 1, 0, null, null)], True, "Barrier's Edge"], #lvl 2
		3:[grey, 'none', [(2, ht, 1, 214*ts, null, null), (2, ht, 4, 0, null, null)], True, 'Outer City Ruins'],
		4:[grey, 'none', [(2, ht, 3, 39*ts, null, null), (SCREEN_WIDTH, 2, 5, null, 2, 0)], True, 'Outer City Ruins'],
		5:[dark_grey, 'none', [(wd, 2, 4, null, std_y_disp, 1)], True, 'Outer City Ruins']
	}
 
	level_ambiance_dict = {#scale, p_type, frame, density, sprite_group
		1:((0.5, 'dust0', 0, -10, the_sprite_group.particle_group_fg),),#have to put an extra comma in
		2:((0.3, 'player_bullet_explosion', 0, 1, the_sprite_group.particle_group_bg), (0.5, 'dust0', 0, -10, the_sprite_group.particle_group_fg)),
		3:((0.5, 'dust0', 0, -10, the_sprite_group.particle_group_fg),),
		4:((0.5, 'dust0', 0, -10, the_sprite_group.particle_group_fg),),
		5:((0.5, 'dust0', 0, -10, the_sprite_group.particle_group_fg),)
	}
	
	#populate area name dict
	area_name_dict = {}
	for entry in level_dict:
		area_name_dict[entry] = level_dict[entry][4]
	area_name_img = pygame.image.load('assets/sprites/pause_bg2.png').convert_alpha()
	area_name_img = pygame.transform.scale(area_name_img, (SCREEN_WIDTH, SCREEN_HEIGHT//15))

	#lists for game_settings
	vol_lvl = [10,10]
	ctrls_list = [119, 97, 115, 100, 105, 111, 112, 1073742054, 121, 117]
 
	default_text_speed = 30
	text_speed = default_text_speed

	#---------------------------------------------------------MODERNGL THINGS---------------------------------------------------
	#moderngl_handler0 = modernGL_handler()
	


	#methods--------------

	def draw_bg(screen, gradient_dict, gradient_type, bg_color):
		
		rgb = gradient_dict[gradient_type]
		#drawing bg color
		if gradient_type != 'none':
			for i in range(SCREEN_HEIGHT//32):
				pygame.draw.rect(screen, [bg_color[0]+ i*rgb[0], bg_color[1]+i*rgb[1], bg_color[2] + i*rgb[2]], ((0,i*32), (SCREEN_WIDTH,(i+1)*32)))
		else:
			screen.fill((bg_color))
	
	

	#reading settings data
	def read_settings_data(data):
		temp_list = []
		with open(f'assets/game_settings/{data}.csv', newline= '') as csvfile:
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

	def play_click_sound():
		m_player.play_sound(m_player.sfx[1], None)

	vol_lvl = read_settings_data('vol_data')[0] #read saved eq regime
	#more instantiations

	#dialogue box handler
	dialogue_box0 = dialogue_box(vol_lvl)

	#music player instance-------------------------------------------------------------------------------------------
	m_player_sfx_list_main = ['roblox_oof.mp3', 'hat.mp3']
	m_player = music_player(m_player_sfx_list_main, vol_lvl)

	#particle group handler
	group_particle_handler = group_particle2()

	#player choice handler
	p_choice_handler0 = player_choice_handler([font, font_larger, font_massive], m_player_sfx_list_main, vol_lvl)

	#ui manager
	ui_manager0 = ui_manager(SCREEN_WIDTH, SCREEN_HEIGHT, [font, font_larger, font_massive], vol_lvl, monitor_size)
	update_vol = False

	#player inventory manager
	player_inv_UI = inventory_UI(3, 3, [font, font_larger, font_massive], SCREEN_WIDTH, SCREEN_HEIGHT, vol_lvl)
	inv_toggle = False
	inv_toggle_en = False

	#trade ui stuff
	trade_ui_en = False
	trade_ui = trade_menu_ui(3*3 + 1, [font, font_larger, font_massive], SCREEN_WIDTH, SCREEN_HEIGHT, vol_lvl)

	#instantiate player at the start of load
	stam = 6
	hp = 6
	speed = 4
	ccsn_chance = 10
	
	player0 = player(32, 160, speed, hp, stam, 0, 0, vol_lvl, camera_offset)#6368 #5856 #6240 #test coords for camera autocorrect
	#good news is that the player's coordinates can go off screen and currently the camera's auto scroll will eventually correct it
	normal_speed = player0.speed
	debugger_sprint = False
	shift = False

	#load initial level-------------------------------------------------------------------------------------------------
	
	#load img dict for particles
	particle_path = 'assets/sprites/particle'
	particle_img_dict = world.sp_ini.load_img_dict(particle_path)
	
	#add particle_2 objects into particle sprite groups
	particle_2_ = particle_2(particle_img_dict)
	the_sprite_group.particle_group.add(particle_2_)
 
	particle_2_fg = particle_2(particle_img_dict)
	the_sprite_group.particle_group_fg.add(particle_2_fg)
 
	particle_2_bg = particle_2(particle_img_dict)
	the_sprite_group.particle_group_bg.add(particle_2_bg)
	
	the_sprite_group.purge_sprite_groups()#does as the name suggests at the start of each load of the game
 
	passive_effects_dict = {
		'salted_earth':False
	}

	# load level data
	world.process_data(level, the_sprite_group, SCREEN_WIDTH, SCREEN_HEIGHT, level_dict[level][2], vol_lvl)

	#running the game----------------------------------------------------------------------------------------------------------------------

	run = True
	player_new_x = 32
	player_new_y = 32
	bound_index = null
	transition_orientation = 'vertical'
	ld_title_screen_en = True


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
	screen_blacked = False
 
	joysticks = {}
 

	show_cursor_signals = [level == 0, pause_game, not player0.Alive, inventory_opened, dialogue_enable, trade_ui_en]
	print('game is running')

	while run:
		
		#screen.fill((0, 0, 0)) 
		temp_move_R = False
		temp_move_L = False
		player_enable_master = (level_dict[level][3] and not level_transitioning and not camera.set_ini_pos)

		#deleting curser
		show_cursor_signals = [level == 0, 
                         		pause_game, 
                           		not player0.Alive, 
                             	inventory_opened, 
                              	dialogue_enable, 
                               	trade_ui_en
                                ]#update the list
		if True in show_cursor_signals:#delete mouse when out of the main menu
			pygame.mouse.set_visible(1)
		else:
			pygame.mouse.set_visible(0)

		if player0_lvl_transition_data[0]:#test for player collision w/ level transition rects
			next_level = player0_lvl_transition_data[1][0]
			player_new_x = player0_lvl_transition_data[1][1]
			player_new_y = player0_lvl_transition_data[1][2]
			bound_index = player0_lvl_transition_data[1][3]
			transition_orientation = player0_lvl_transition_data[2]
			transition_disp = player0_lvl_transition_data[3]
		else:
			transition_orientation = 'vertical' #default case
	
   
		#need to set a player new_x and directly set player's rect y, need to set level as well

		#----------------------------------------------------------------------level changing-------------------------------------------------
		if level != next_level:
			do_screenshake_master = False
			screenshake_profile = (0,0,0)
			level_transitioning = True
			#print(pygame.time.get_ticks())
			#update world's persistent dictionaries
			world.update_lvl_completion(level, the_sprite_group.enemy_death_count, next_level != 0, passive_effects_dict)
			world.check_onetime_spawn_dict(level)
   
			player_en = False
			
			player0.scrollx = 0
			scroll_x = 0
			scroll_y = 0
			the_sprite_group.purge_sprite_groups()
			dialogue_box0.reset_internals()

			lvl_transition_counter = 3#how many cycles to show a black screen
			level = next_level

			# load level data
			world.process_data(level, the_sprite_group, SCREEN_WIDTH, SCREEN_HEIGHT, level_dict[level][2], vol_lvl)
			# each tile is set with data
			
			if move_L:
				temp_move_L = move_L
				move_L = False
			if move_R:
				temp_move_R = move_R
				move_R = False

			if ui_manager0.set_player_location: #loading in from a save file
				ui_manager0.set_player_location = set_player_coords(ui_manager0.rtn_dict['PNC']) #returns signal for completion
			else:
				if transition_orientation == 'vertical':
					player0.rect.x = player_new_x - 32 #set player location
				else:
					#loads all the lvl trans tiles from new level, these have specific coordinates
					loaded_lvl_trans_tiles = []
					for tile in [tile for tile in world.solids if tile[2] == 10]:
						loaded_lvl_trans_tiles.append(tile)
					#set new x to the x position of the paired lvl trans tile 
     				#with some transition_disp = previous player rect.x - previous lvl trans tile rect.x
					player0.rect.x = loaded_lvl_trans_tiles[bound_index][3][4][0] + transition_disp
					player0.rect.y = player_new_y
					camera.scrollx = 0				
	
				player0.vel_y = 0
			
			camera.rect.centerx = HALF_SCREEN_W
   
			if temp_move_R:
				move_R = temp_move_R
			if temp_move_L:
				move_L = temp_move_L
			
			if world.x_scroll_en:
				camera.set_ini_pos = True #signal to force camera into position next cycle
			else:
				camera.set_ini_pos = False
	
		elif not camera.set_ini_pos:
			level_transitioning = False
		
			
		

		#---------------------------------------------------------drawing level and sprites------------------------------------------------------------------
		#---------------------------------------------------------handling movement and collisions and AI----------------------------------------------------
		draw_bg(screen, gradient_dict, level_dict[level][1], level_dict[level][0])#this just draws the color
		if camera.is_visible:
			camera.draw(screen)#for camera debugging
		if world.x_scroll_en and not pause_game:
			camera.auto_correct(player0.rect, player0.direction, player0.x_coord, 
                       world.rect, 
                       SCREEN_WIDTH, SCREEN_HEIGHT)
		world.draw(screen, scroll_x, scroll_y, player0.hitting_wall)#this draws the world and scrolls it 
  
		#vertical screenshake correction
		if world.rect.y != 0 and not do_screenshake_master:
			correction_y = world.rect.y/abs(world.rect.y)

			world.rect.y -= correction_y
			for data_list in world.detailed_lvl_data_dict:
				for tile in world.detailed_lvl_data_dict[data_list]:
					tile[1][1] -= correction_y

		
		if not pause_game:
			
			if player_enable_master: 
				player0.animate(the_sprite_group)
				player0.do_entity_collisions(the_sprite_group)
				player0_lvl_transition_data = player0.move(pause_game, move_L, move_R, world.solids, 
															world.rect, world.x_scroll_en, world.y_scroll_en, 
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
			#area_name_time = pygame.time.get_ticks()
		
			
	
		#---------------------------------------screen shake------------------------------------------------------------------------
		
		if not level_transitioning:
			if do_screenshake_master:
				ss_output = camera.screen_shake(screenshake_profile, do_screenshake_master)
				do_screenshake_master = ss_output[0]
				player0.rect.x += ss_output[1][0]
				scroll_x += ss_output[1][1]
				player0.vel_y += ss_output[1][2]*1.02
				scroll_y = -ss_output[1][3]

			if not do_screenshake_master and player0.do_screenshake:
				screenshake_profile = player0.screenshake_profile #intensity x, intensity y, cycle count
				player0.do_screenshake = False
				#if not do_screenshake_master:
				do_screenshake_master = True 
    
    
			if not do_screenshake_master:
				for p_int in [p_int for p_int in the_sprite_group.p_int_group if p_int.do_screenshake]: #the_sprite_group.p_int_group: 
					p_int.do_screenshake = False
					#if not do_screenshake_master:
					do_screenshake_master = True
					screenshake_profile = (4, 8, 3)

			if not do_screenshake_master:
				for enemy in [enemy for enemy in the_sprite_group.enemy0_group if enemy.do_screenshake]: #the_sprite_group.enemy0_group:
					enemy.do_screenshake = False
					#if not do_screenshake_master:
					do_screenshake_master = True
					if player0.sprint:
						screenshake_profile = (10, 6, 2)
					else:
						screenshake_profile = (6, 4, 2)

		

		#=================================================================updating and drawing all sprites=====================================
		if not level_transitioning and not player0.in_cutscene:
			#dialogue trigger sent here
			the_sprite_group.pause_game = pause_game or ui_manager0.saves_menu_enable
			the_sprite_group.scroll_x = scroll_x
			#if not level_transitioning: #surpress sprite logic while level transitioning

			screen.blit(world.world_map_non_parallax, (world.rect.x, world.rect.y))
			the_sprite_group.update_bg_sprite_group(screen, player0.hitbox_rect, player0.atk_rect_scaled)
			the_sprite_group.update_text_prompt_group(screen, dialogue_enable, next_dialogue, player0, world, selected_slot)#player and world
			next_dialogue = False
			player0.check_melee_hits(the_sprite_group)#seems to work, wasn't responsive at first
			player0.check_item_pickup(the_sprite_group)
			the_sprite_group.update_groups_behind_player(screen, player0.hitbox_rect, player0.atk_rect_scaled, player0.action, player0.direction, [tile for tile in world.solids if tile[1][0] > -160 and tile[1][0] < 800])
   
			the_sprite_group.update_item_group(screen, player0.hitbox_rect)
			player0.draw(screen)
    
			screen.blit(world.world_map_non_parallax_fg,  (world.rect.x, world.rect.y))
			the_sprite_group.update_groups_infront_player(screen, player0.hitbox_rect, player0.atk_rect_scaled, player0.action, world.solids)
		
			status_bars.very_charred = player0.char_level/player0.char_dict['max_char'] > 0.9
			status_bars.draw(screen, player0.get_status_bars(), player0.action, (7,8,9,10,16), font, False)
			status_bars.draw2(screen, player0.action_history, (7,8,16), font_larger)
			status_bars.draw_status_icons(screen, player0, font_larger)
			if world.plot_index_dict != {} and world.plot_index_dict['opening_scene'] == -4:
				status_bars.draw_tutorial_cues(screen, player0, player0.do_extended_hitbox_collisions(the_sprite_group), player0.check_for_breakable2(the_sprite_group), ui_manager0.controller_connected, ctrls_list, font_largerer)
			player_inv_UI.show_selected_item(player0.inventory_handler.inventory, screen)
   
			#passive items temp code
			passive_effects_dict['salted_earth'] = player0.inventory_handler.check_for_item('Talisman of Salted Earth')
				
   
			#draw area name here
			if area_name_time + 2500 > pygame.time.get_ticks():
				if screen_blacked and area_name_time + 40 > pygame.time.get_ticks():
					pygame.draw.rect(screen, (0,0,0), screen.get_rect())
				else:
					screen_blacked = False
				
				coord = (SCREEN_WIDTH//2 - 8*len(area_name_dict[level])//2, SCREEN_HEIGHT//2 - 8)
				coord2 = (0, SCREEN_HEIGHT//2 - 16)
				if area_name_time + 2000 > pygame.time.get_ticks():
					screen.blit(area_name_img, coord2)
					screen.blit(font_larger.render(area_name_dict[level], True, (white)), (coord))
				elif area_name_time + 2000 < pygame.time.get_ticks() and pygame.time.get_ticks()%2 == 0:
					screen.blit(area_name_img, coord2)
					screen.blit(font_larger.render(area_name_dict[level], True, (white)), (coord))
					last_area_name = area_name_dict[level]

		elif level_transitioning:
			screen_blacked = True
			for group in the_sprite_group.sp_group_list:
				for sprite_ in group:
					sprite_.force_ini_position(scroll_x)
     
		elif player0.in_cutscene:
			the_sprite_group.pause_game = pause_game or ui_manager0.saves_menu_enable
			the_sprite_group.scroll_x = scroll_x
			the_sprite_group.update_bg_sprite_group(screen, player0.hitbox_rect, player0.atk_rect_scaled)
			the_sprite_group.update_text_prompt_group(screen, dialogue_enable, next_dialogue, player0, world, selected_slot)#player and world
			the_sprite_group.update_groups_infront_player(screen, player0.hitbox_rect, player0.atk_rect_scaled, player0.action, world.solids)
			next_dialogue = False
     
		if lvl_transition_counter > 0:
			pygame.draw.rect(screen, (0,0,0), screen.get_rect())
			if lvl_transition_counter == 1 and last_area_name != area_name_dict[level]:
				area_name_time = pygame.time.get_ticks() #start area name timer
				if not player0.in_cutscene:
					last_area_name = area_name_dict[level]
			lvl_transition_counter -= 1
		
		#ambiance particles
		#creating group particles
		if not pause_game and level in level_ambiance_dict:#scale, p_type, frame, density, sprite_group
			for particle_group_data in level_ambiance_dict[level]:
				if particle_group_data[0] != 0:
					group_particle_handler.create_particles((0-32,0), (SCREEN_WIDTH+32,SCREEN_HEIGHT), 1, particle_group_data)
     
		#--------------------------------------------------------------------handling drawing text boxes------------------------------------------------------------------
		#textboxes have a maximum of 240 characters
		
		if (the_sprite_group.textbox_output[0] != '' and 
      		the_sprite_group.textbox_output[1] and 
        	the_sprite_group.textbox_output[2] and not 
         	the_sprite_group.textbox_output[6][0]
          	):
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
		#handling player choice 
		elif the_sprite_group.textbox_output[6][0] and the_sprite_group.textbox_output[2]: #(p choice flag, dialogue enable)
			p_choice_key = the_sprite_group.textbox_output[6][1]
			if p_choice_key[0:5] == 'trade':
				next_dialogue_index = trade_ui.open_trade_ui(player0.inventory_handler.inventory, p_choice_key, screen, ctrls_list)
			else:
				dialogue_box0.draw_box_and_portrait(screen, the_sprite_group.textbox_output[4], the_sprite_group.textbox_output[5])
				#first input of deploy buttons is the key
				p_choice_output = p_choice_handler0.deploy_buttons(p_choice_key, screen, player0, level, world)
				next_dialogue_index = p_choice_output[0]
   
			if next_dialogue_index != -3:
				for npc in the_sprite_group.textprompt_group: #look for npc in sprite group what has a player choice open
					if npc.player_choice_flag:#force close it and move on to the next index
						npc.force_dialogue_index(next_dialogue_index)
						p_choice_handler0.trigger_once = True
						trade_ui.close_trade_ui()
						dialogue_box0.type_out = True


	
		#----------black screen while transitioning---------------------------------------------------------
		if level_transitioning or camera.set_ini_pos:
			pygame.draw.rect(screen, (0,0,0), screen.get_rect())
	
		#--------------------------------------------------------------MAIN MENU CODE---------------------------------------------------------------------
		if level == 0 or ui_manager0.saves_menu_enable: 
			draw_bg(screen, gradient_dict, level_dict[level][1], level_dict[level][0])
			world.lvl_completion_dict = {0:0} #reset 
			world.onetime_spawn_dict = {}
			pause_game = False

			#plot index list's csv is read within ui_manager
			if ui_manager0.saves_menu_enable: #load file
				ui_output_dict = ui_manager0.show_saves_menu(screen)
				if ui_manager0.selected_slot != -1 and selected_slot != ui_manager0.selected_slot:
        			#change slot and reset death counters and lvl copmletion dict across levels if a different slot is selected
					world.death_counters_dict = {0: 0}
					selected_slot = ui_manager0.selected_slot
				if ui_manager0.reset_all_slots: #reset death counters if reset button is pressed
					ui_manager0.reset_all_slots = False
					world.death_counters_dict = {0: 0}
			elif ui_manager0.saves_menu2_enable: #new game menu
				ui_output_dict = ui_manager0.show_saves_menu2(screen) #select slot for new game
				if ui_manager0.selected_slot != -1:# and selected_slot != ui_manager0.selected_slot:
					world.death_counters_dict = {0: 0}#slot changes from -1 if a slot is chosen, this will always execute
					selected_slot = ui_manager0.selected_slot
			else:
				ui_output_dict = ui_manager0.show_main_menu(screen)
    
			player0.frame_index = 0			
			world.onetime_spawn_dict = ui_output_dict['OSD']
			world.lvl_completion_dict = ui_output_dict['LCD']
			world.set_plot_index_dict(ui_output_dict['PID'])#world plot index saved here
			run = ui_output_dict['RG']
			next_level = ui_output_dict['NL']
			fill_player_inv(ui_manager0.rtn_dict['PNI'])
			#set player stats
			for stat in ui_manager0.rtn_dict['PS']:
				if ui_manager0.rtn_dict['PS'][stat] != -1:
					if stat == 'hits_tanked':
						player0.hits_tanked = ui_manager0.rtn_dict['PS'][stat]
					elif stat == 'st_cap':
						anmt = ui_manager0.rtn_dict['PS'][stat]
						player0.stamina_usage_cap = anmt
						player0.stamina_used = anmt
					elif stat == 'char':
						player0.char_level = ui_manager0.rtn_dict['PS'][stat]
	
			if not run:
				pygame.time.wait(100)   
			
			elif run and ui_manager0.saves_menu_enable and player0.hits_tanked == hp and not player0.Alive and not ui_manager0.set_player_location:
				#reset player0
				player0 = player(32, 160, speed, hp, stam, 0, 0, vol_lvl, camera_offset)
	
		#-------------------------------------------------pausing game--------------------------------------------------------
		if pause_game:
			#this code draws the actual pause menu
			#need another conditional for pressing esc while in a cut scene
			ui_tuple0 = ui_manager0.show_pause_menu(screen)
			pause_game = ui_tuple0[0] #game is paused signal
			if ui_tuple0[1]:#exit to title signal
				next_level = 0
				player0 = player(32, 160, speed, hp, stam, 0, 0, vol_lvl, camera_offset)
				player_new_x = 32
				player_new_y = 32
		
		#-----------------------------------------inventory and items
		#opening inventory
		if trade_ui_en:
			trade_ui.open_trade_ui(player0.inventory_handler.inventory, 'test', screen, ctrls_list)

		if inventory_opened:
			player_inv_UI.open_inventory(player0.inventory_handler.inventory, player0.char_level/player0.char_dict['max_char'], screen, ctrls_list)
			if player_inv_UI.use_item_btn_output and player_inv_UI.press_use_item_btn(player0.inventory_handler.inventory) and player0.action != 15:
				player0.using_item = player_inv_UI.use_item_btn_output #start use item animation
				player0.speed = 0
				player_inv_UI.use_item_btn_output = False
			elif True in inv_directions:
				player0.inventory_handler.inventory = player_inv_UI.move_item(inv_directions, inv_toggle, player0.inventory_handler.inventory)
				inv_directions = [False] * 5
		else:
			inv_directions = [False] * 5
   
		if player0.finished_use_item_animation:
			player_inv_UI.use_item_flag = True
			player0.finished_use_item_animation = False

		if inv_toggle_en:
			player_inv_UI.toggle_inv_slot(300)
   

		#---------------------------------updates from ui manager-----------------------------------------
		if ui_manager0.ctrls_updated:
			ctrls_list = read_settings_data('ctrls_data')
			ui_manager0.ctrls_updated = False
	
		if update_vol: #updates all m_players' sounds with new volume setting
		#objects already instantiated have their volumes updated here
		#new objects take vol_lvl as their ini_vol parameter so their volumes match the setting upon instantiation
			vol_lvl = read_settings_data('vol_data')[0]
			dialogue_box0.m_player.set_vol_all_sounds(vol_lvl)
			m_player.set_vol_all_sounds(vol_lvl)
			the_sprite_group.update_vol_lvl(vol_lvl)
			player0.m_player.set_vol_all_sounds(vol_lvl)
			player_inv_UI.m_player.set_vol_all_sounds(vol_lvl)
			p_choice_handler0.m_player.set_vol_all_sounds(vol_lvl)
			world.sp_ini.m_player.set_vol_all_sounds(vol_lvl)
	
		update_vol = ui_manager0.raise_volume or ui_manager0.lower_volume #2 different signals from ui_manager or'd together
	
	
		#-----------------------------------------------------------------------------------------------------------------------------------------------------------
		#handling player death and game over screen------------------------------------------------------------------------------------
		
		if player0.hits_tanked >= player0.hp or player0.rect.y > 480 or player0.char_level >= player0.char_dict['max_char']:#killing the player------------------------------------------------
			player0.action_history = [-1] * 4
			if player0.Alive:
				player0.Alive = False
				#death counters will probably belong to an instance of world amd reset upon new games
				#increment level death counters
				if level in world.death_counters_dict:
					world.death_counters_dict[level] += 1
			else:
				player0.hits_tanked = player0.hp

			if inventory_opened:#exit inventory if opened
				inventory_opened = False
				player_inv_UI.close_inventory()

			if ui_manager0.show_death_menu(screen):
				next_level = 0
				player0 = player(32, 160, speed, hp, stam, 0, 0, vol_lvl, camera_offset)
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
			player0.frame_index = 0
			player0.action = 0
			player0.rolled_into_wall = True
			inventory_opened = False
		else:#important spaghetti code for making dialogue boxes work
			dialogue_box0.reset_internals()
			text_speed = default_text_speed
			
		if player0.in_cutscene:#dialogue system will activate as soon as the player collides with a 'cutscene' npc
			dialogue_enable = True #start signal for dialogue handler
			if last_area_name != area_name_dict[level]:
				area_name_time = pygame.time.get_ticks() #extend area name time on screen
			
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
    
			if debugger_sprint:
				player0.speed = normal_speed * 3
				player0.hits_tanked = 0
			elif not debugger_sprint and not player0.sprint:
				player0.speed = normal_speed
			
    
			if (player0.hurting):
				player0.update_action(5) #hurting
			else:
			
				if player0.shoot:
					player0.update_action(11)
				
				elif player0.atk1:
					
					if change_once:
						if player0.vel_y < -0.1 or (player0.hold_jump and player0.vel_y < 2 and player0.in_air and player0.action_history[player0.len_action_history-1] in [2,4]):
							player0.atk1_alternate = True
						elif player0.vel_y > 0 and player0.in_air:
							player0.atk1_alternate = False
						else:
							player0.atk1_alternate = not player0.atk1_alternate
						change_once = False

					if player0.crit:
						player0.update_action(10)
					elif player0.heavy:
						player0.update_action(16)
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
				if player0.Alive and level_dict[level][3] and not pause_game and not dialogue_enable:
					if inventory_opened:
						inv_directions[0] = (event.key == pygame.K_RIGHT) #Right
						inv_directions[1] = (event.key == pygame.K_LEFT) #Left
						inv_directions[2] = (event.key == pygame.K_UP) #Up
						inv_directions[3] = (event.key == pygame.K_DOWN) #Down
						inv_directions[4] = (event.key == ctrls_list[4]) #discard
						move_L = False
						move_R = False
					else:
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
							player0.hold_jump = True
							if player0.in_air and pygame.time.get_ticks() - 10 > hold_jump_update:
								hold_jump_update = pygame.time.get_ticks()
								player0.squat = True 
								
							elif not player0.in_air:
								player0.squat = True
        
							# if player0.in_air and player0.double_jump_en: #and some other signal
							# 	player0.double_jump = True
							# 	print("double jump here " + str(pygame.time.get_ticks()))
       
							if player0.rolling and not player0.in_air:
								player0.roll_count = player0.roll_limit
								player0.squat = True

						if event.key == ctrls_list[4] and player0.stamina_used + player0.atk1_stamina_cost <= player0.stamina and event.key != ctrls_list[0] and not player0.using_item: #pygame.K_i, pygame.K_w
							#player0.atk1_stamina_cost is not getting updated during heavy attack
							change_once = True
							player0.atk1 = True # (event.key == ctrls_list[4])
							player0.melee_hit = False

						elif event.key == ctrls_list[4] and player0.stamina_used + player0.atk1_stamina_cost > player0.stamina: #pygame.K_i
							status_bars.warning = True
						
						if event.key == ctrls_list[5] and player0.stamina_used + player0.shoot_stamina_cost <= player0.stamina and not player0.using_item and player0.inventory_handler.check_for_item('Rock'): #pygame.K_o
							player0.shot_charging = True
						elif event.key == ctrls_list[5] and player0.stamina_used + player0.shoot_stamina_cost > player0.stamina: #pygame.K_o
							status_bars.warning = True
			

						if event.key == ctrls_list[2] and (player0.check_atk1_history() == 4 or player0.stamina_used + player0.roll_stam_rate + player0.roll_stamina_cost <= player0.stamina): #pygame.K_s
							player0.squat = False
							player0.rolling = True

						elif event.key == ctrls_list[2] and player0.stamina_used + player0.roll_stam_rate + player0.roll_stamina_cost > player0.stamina: #pygame.K_s
							status_bars.warning = True
		
					if event.key == ctrls_list[7]: #pygame.K_RALT
						player0.sprint = True
						inv_toggle = True
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

					#open inventory
					if event.key == ctrls_list[8] and not dialogue_enable:
						if not inv_toggle:
							inventory_opened = not inventory_opened
							if inventory_opened:
								player_inv_UI.close_inventory()
						else:
							inv_toggle_en = True
							player_inv_UI.toggle_inv_slot_once()
		
					#debugging flight button
					#if you fly over the camera object the level breaks
					if event.key == pygame.K_0:
						player0.squat_done = True

				#===============================================================UI Related Keys=============================================================

				# if event.key == pygame.K_m:
				# 	m_player.play_song('newsong18.mp3')
    
				if event.key == pygame.K_BACKSLASH and pygame.display.is_fullscreen():
					pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
					ui_manager0.in_fullscreen = False

				if event.key == pygame.K_c and shift:
					camera.is_visible = not camera.is_visible
				if event.key == pygame.K_MINUS:
					debugger_sprint = True
				if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
					shift = True
				# if event.key == pygame.K_t:
				# 	trade_ui_en = not trade_ui_en

				if (event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE) and not ui_manager0.options_menu_enable and not ui_manager0.saves_menu_enable: 
				#escape exits UI ONLY before the options sub menu is shown and any deeper into sub menus
					if level != 0:
						ui_manager0.trigger_once = True

						if not player0.Alive or (shift and pause_game):#(pause_game or not player0.Alive) and not dialogue_enable: #exit to main menu from pause game
							ui_manager0.rtn_dict = ui_manager0.reset_rtn_dict()
							next_level = 0
							player0 = player(32, 160, speed, hp, stam, 0, 0, vol_lvl, camera_offset)
							player_new_x = 32
							#player_new_y = 32
							dialogue_box0.reset_internals()
							pygame.mixer.stop()
							play_click_sound()

						elif not dialogue_enable and not inventory_opened: #pause game, will trigger if player is not in dialogue
							pause_game = not pause_game
							pygame.mixer.pause()
							play_click_sound()
		
						elif (not player0.in_cutscene and #cannot esc out of cutscene
								not trade_ui.enabled and
            					(dialogue_box0.str_list_rebuilt == dialogue_box0.current_str_list or 
                  				the_sprite_group.textbox_output[6][0])
                 				): #exits dialogue window if an NPC finishes speaking (is this way to avoid bugs)
							dialogue_enable = False
							p_choice_handler0.disable()

						if inventory_opened:#exit inventory if opened
							inventory_opened = False
							player_inv_UI.close_inventory()

						if trade_ui.enabled:
							trade_ui.exit_to_dialogue()

						# if trade_ui_en:
						# 	trade_ui_en = False
						# 	trade_ui.close_trade_ui()
							
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
							play_click_sound()
						else:
							text_speed = default_text_speed
							next_dialogue = True
							dialogue_box0.type_out = True				
     
					if level == 0:#default case, auto saving will overwrite data in file 0
						if ui_manager0.main_menu_enable:
							play_click_sound()
							ui_manager0.kbd_new_game = True
						elif ui_manager0.saves_menu2_enable:
							play_click_sound()
							ui_manager0.kbd_new_game = True


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
				
			#=============================================== key lift =================

			if(event.type == pygame.KEYUP):
				if event.key == ctrls_list[1]:#pygame.K_a
					move_L = False
					
				if event.key == ctrls_list[3]:#pygame.K_d
					move_R = False
					
				#delayed full jump bug:
				#if the the animation for squatting before a jump is just slow enough, it might finish AFTER  the jump key is released
				#so the code below to limit the jump height will not execute, resulting in a full height jump if the jump key is pressed sufficiently fast enough
				#switched to continuous signal
				if event.key == ctrls_list[0] and not inventory_opened:#variable height jumping
					player0.jump_dampen = True
					player0.hold_jump = False

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
					inv_toggle = False
					inv_toggle_en = False

				if event.key == pygame.K_MINUS:
					debugger_sprint = False
     
				if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
					shift = False

				if event.key == ctrls_list[8]:
					inv_toggle_en = False

     
		#==============================================================================================================
		#==============================================CONTROLLER EVENT INPUTS==========================================
		#==================================================================================================================
			if(event.type == pygame.JOYBUTTONDOWN):
				#print(pygame.button.name(event.button))
				if player0.Alive and level_dict[level][3] and not pause_game and not dialogue_enable:
					if inventory_opened:
						inv_directions[0] = (event.button == ctrls_list[3]) #Right
						inv_directions[1] = (event.button == ctrls_list[1]) #Left
						inv_directions[2] = (event.button == ctrls_list[0]) #Up
						inv_directions[3] = (event.button == ctrls_list[2]) #Down
						inv_directions[4] = (event.button == ctrls_list[4]) #discard
					else:
						
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
							player0.hold_jump = True
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
							player0.melee_hit = False

						elif event.button == ctrls_list[4] and player0.stamina_used + player0.atk1_stamina_cost > player0.stamina: #pygame.K_i
							status_bars.warning = True
						
						if event.button == ctrls_list[5] and player0.stamina_used + player0.shoot_stamina_cost <= player0.stamina and not player0.using_item and player0.inventory_handler.check_for_item('Rock'): #pygame.K_o
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
						inv_toggle = True
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

					#open inventory
					if event.button == ctrls_list[8] and not dialogue_enable:
						if not inv_toggle:
							inventory_opened = not inventory_opened
							if inventory_opened:
								player_inv_UI.close_inventory()
						else:
							inv_toggle_en = True
							player_inv_UI.toggle_inv_slot_once()
		
		
					#debugging flight button
					#if you fly over the camera object the level breaks
					# if event.button == pygame.K_0:
					# 	player0.squat_done = True

				#===============================================================UI Related Keys=============================================================

				# # if event.button == pygame.K_m:
				# # 	m_player.play_song('newsong18.mp3')
				# if event.button == pygame.K_c:
				# 	camera.is_visible = not camera.is_visible
			
				# if (event.button == pygame.K_BACKSPACE or event.button == pygame.K_ESCAPE) and not ui_manager0.options_menu_enable and not ui_manager0.saves_menu_enable: 
				# #escape exits UI ONLY before the options sub menu is shown and any deeper into sub menus
				# 	if level != 0:
				# 		ui_manager0.trigger_once = True

				# 		if (pause_game or not player0.Alive) and not dialogue_enable: #exit to main menu from pause game
				# 			next_level = 0
				# 			player0 = player(32, 160, speed, hp, stam, 0, 0, vol_lvl, camera_offset)
				# 			player_new_x = 32
				# 			player_new_y = 32
				# 			dialogue_box0.reset_internals()
				# 			pygame.mixer.stop()
				# 			play_click_sound()

				# 		elif not dialogue_enable and not inventory_opened: #pause game, will trigger if player is not in dialogue
				# 			pause_game = True
				# 			pygame.mixer.pause()
				# 			play_click_sound()
		
				# 		elif (not player0.in_cutscene and #cannot esc out of cutscene
            	# 				(dialogue_box0.str_list_rebuilt == dialogue_box0.current_str_list or 
                #   				the_sprite_group.textbox_output[6][0])
                #  				): #exits dialogue window if an NPC finishes speaking (is this way to avoid bugs)
				# 			dialogue_enable = False
				# 			p_choice_handler0.disable()

				# 		if inventory_opened:#exit inventory if opened
				# 			inventory_opened = False
				# 			player_inv_UI.close_inventory()
							
				# 	else:#if on the main menu, the game will exit on button press
				# 		run = False
				
		
				# if event.button == pygame.K_RETURN:
				# 	if pause_game and not ui_manager0.options_menu_enable:
				# 		ui_manager0.trigger_once = True
				# 		dialogue_trigger_ready = False
				# 		pause_game = False
				# 		pygame.mixer.unpause()
					
				# 	if dialogue_trigger_ready or player0.in_cutscene:
				# 		dialogue_enable = True
				# 	if dialogue_enable and not the_sprite_group.textbox_output[6][0]:
				# 		if dialogue_box0.str_list_rebuilt != dialogue_box0.current_str_list:
				# 			text_speed = 0
				# 			play_click_sound()
				# 		else:
				# 			text_speed = default_text_speed
				# 			next_dialogue = True
				# 			dialogue_box0.type_out = True				
     
				# 	if level == 0:#default case, auto saving will overwrite data in file 0
				# 		play_click_sound()
				# 		ui_manager0.trigger_once = True
				# 		next_level = 1
				# 		selected_slot = 0

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
				if event.button == ctrls_list[0] and not inventory_opened:#variable height jumping
					player0.jump_dampen = True
					player0.hold_jump = True

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
					inv_toggle = False
					inv_toggle_en = False

		#code to prevent drawing empty space beyond the level
		screen_l_edge = 0
		screen_r_edge = 0
		if world.rect.x > 0:
			screen_l_edge = world.rect.x
		elif world.rect.x < -world.rect.width + (SCREEN_WIDTH - ts):
			screen_r_edge = SCREEN_WIDTH - (world.rect.x + world.rect.width)

		# pygame.display.flip()
  
		# frame_tex = moderngl_handler0.surf_to_texture(screen)
		# frame_tex.use(0) #using a texture at index 0
		# moderngl_handler0.program['tex'] = 0 #write to tex uniform, the number 0, also used to update
		# moderngl_handler0.render_object.render(mode=moderngl.TRIANGLE_STRIP)
  
		pygame.display.update(pygame.rect.Rect(screen_l_edge, world.rect.y, SCREEN_WIDTH - screen_r_edge, SCREEN_HEIGHT-2*world.rect.y))
		pygame.display.set_caption(f"Fire Burdened 0.723 @ {clock.get_fps():.1f} FPS")
  
		#frame_tex.release()
		clock.tick(FPS)

	pygame.quit()
 



if __name__ == '__main__':
    main()