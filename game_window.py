import pygame
import os
os.environ['SDL_VIDEO_CENTERED'] = '1' 
pygame.init()

#print('directory: ' + os.getcwd())
import csv
from playerFile import player #type: ignore
from worldManager import World #type: ignore
from StatusBarsFile import StatusBars #type: ignore
from Camera import Camera #type: ignore
from music_player import music_player #type: ignore
from button import Button #type: ignore
from textManager import text_manager #type: ignore
from ui_manager import ui_manager #type: ignore
from spriteGroup import sprite_group #type: ignore
import gc
import random
#from pygame.locals import *


#setting the screen-----------------------------------------------------------
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
flags = pygame.SHOWN #windowed mode
#flags = pygame.DOUBLEBUF|pygame.FULLSCREEN #full screen mode
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)

pygame.display.set_caption('game window')

#framerate set up------------------------------------
clock = pygame.time.Clock()
FPS = 60
#pygame.key.set_repeat(5,5)

#local variables
move_L = False
move_R = False

change_once = True

hold_jmp_update = pygame.time.get_ticks()
hold_jmp_time = 1
hold_jump = False

hold_roll_update = pygame.time.get_ticks()
hold_roll_time = 20
hold_roll = False

level_trans_timing = pygame.time.get_ticks()
show_controls_en = False

pause_game = False
#exit_to_title = False

text_delay = pygame.time.get_ticks()

level_transitions = []
#level transition system:
#each level in load_level_data will have its own level_transitions list which will (in order) contain the next levels
#each level will have level transition objects, that can be placed with the level editor,
#and their order will correspond to the level's respective level_tranisition list's index
#upon player collision the object will trigger a level change to the next level
#the player's position in the new level should be set
#update: the list should contain tuples: (width, height, next_level, player_new_x, player_new_y)
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

fg_data = []
coord_data = []
world_data = []
bg1_data = []
bg2_data = []
bg3_data = []
bg4_data = []
bg5_data = []
bg6_data = []

level_data_list = [
	coord_data,
	fg_data,
	world_data,
	bg1_data,
	bg2_data,
	bg3_data,
	bg4_data,
	bg5_data,
	bg6_data
]

level_data_str_tuple = ( #names of the corresponding csv files
	'coord_data',
	'fg_data',
	'data',
	'bg1_data',
	'bg2_data',
	'bg3_data',
	'bg4_data',
	'bg5_data',
	'bg6_data'
)

world = World()
obj_list = world.obj_list

#instantiate status bars
status_bars = StatusBars()

#define font
font = pygame.font.SysFont('SimSun', 12)
font_larger = pygame.font.SysFont('SimSun', 16)
font_massive = pygame.font.SysFont('SimSun', 48)



#camera instance
camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

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

#dictionaty for gradients
gradient_dict = {
	'none':(0,0,0),
	'sunset':(-1,-1,1),
	'rain':(-1,1,2)
}

#dictionary for level transitions
#level_tuple: (color, gradient, y tile count, x tile count, lvl trans data, player enable)
#lvl trans data: (width, height, next_level, player_new_x, player_new_y)
level_tuple = (
    [black, 'none', 15, 30, [], False], #lvl 0
    [maroonish, 'rain', 15, 200, [(2, 15*32, 2, 44*32 -2, 288), (2, 15*32, 2, 2, 384)], True], #lvl 1
    [maroonish, 'rain', 15, 45, [(2, 15*32, 1, 199*32 -2, 384), (2, 15*32, 1, 2, 288)], True] #lvl 2
)

vol_lvl = [10,10]

#controls
ctrls_list = [119, 97, 115, 100, 105, 111, 112, 1073742054]

#text manager instance
text_manager0 = text_manager()
type_out_en = True
text_speed = 200
type_out = True

#methods--------------

def draw_bg(screen, gradient_dict, gradient_type, bg_color):
    
	rgb = gradient_dict[gradient_type]
	#drawing bg color
	if gradient_type != 'none':
		for i in range(SCREEN_HEIGHT//32):
			pygame.draw.rect(screen, [bg_color[0]+ i*rgb[0], bg_color[1]+i*rgb[1], bg_color[2] + i*rgb[2]], ((0,i*32), (SCREEN_WIDTH,(i+1)*32)))
	else:
		screen.fill(bg_color)
  

#reading and loading level data-----------------------------------------------------------------------------------------------------------------

def read_level_data(level, rows, cols, data_, data_str):

	for current_row in range(rows):
		r = [-1] * cols
		data_.append(r)

	with open(f'level_files/level{level}_{data_str}.csv', newline= '') as csvfile:
		reader = csv.reader(csvfile, delimiter= ',') #what separates values = delimiter
		for x, current_row in enumerate(reader):
			for y, tile in enumerate(current_row):
				data_[x][y] = int(tile)
    
def clear_world_data(level_data_list):
	for level_data in level_data_list:
		level_data *= 0
	
def load_level_data(level, level_data_list, level_data_str_tuple, level_tuple, vol_lvl):
	#level_tuple[level]: 0:BG_color, 1:gradient_type, 2:rows, 3:cols, 4:level_transitions, 5:player_en

	#reading csv files 
	index = 0
	for level_data in level_data_list:
		read_level_data(level, level_tuple[level][2], level_tuple[level][3], level_data, level_data_str_tuple[index])
		index += 1
  
	#world has self data lists that get cleared each time this is called
	world.process_data(level_data_list, the_sprite_group, SCREEN_WIDTH, SCREEN_HEIGHT, level_tuple[level][4], vol_lvl)
	
	return [level_tuple[level][1], level_tuple[level][0], level_tuple[level][5], world.obj_list]# gradient, BG_color, player enable

#reading settings data
def read_settings_data(data):
	temp_list = []
	with open(f'settings_files/{data}.csv', newline= '') as csvfile:
		reader = csv.reader(csvfile, delimiter= ',') #what separates values = delimiter
		for row in reader:
			for entry in row:
				temp_list.append(int(entry))
				
	return temp_list


vol_lvl = read_settings_data('vol_data') #read saved eq regime
#more instantiations

#music player instance-------------------------------------------------------------------------------------------
m_player_sfx_list_main = ['roblox_oof.wav', 'hat.wav']
m_player = music_player(m_player_sfx_list_main, vol_lvl)

#ui manager
ui_manager0 = ui_manager(SCREEN_WIDTH, SCREEN_HEIGHT, [font, font_larger, font_massive], vol_lvl)
update_vol = False

#instantiate sprite groups=========
the_sprite_group = sprite_group()

#instantiate player at the start of load
hp = 6
player0 = player(32, 128, 4, hp, 6, 0, 0, vol_lvl)#6368 #5856 #6240 #test coords for camera autocorrect
#good news is that the player's coordinates can go off screen and currently the camera's auto scroll will eventually correct it
normal_speed = player0.speed

#load initial level-------------------------------------------------------------------------------------------------
the_sprite_group.purge_sprite_groups()#does as the name suggests at the start of each load of the game
lvl_data = load_level_data(0, level_data_list, level_data_str_tuple, level_tuple, vol_lvl)
color_n_BG = lvl_data[0:3]
obj_list = lvl_data[3]


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



while run:
    # #testing general audio mixing
	# m_player.set_vol_all_channels2(9)
    
	clock.tick(FPS)
	#reset temporary values
	text_box_on = False
 
	temp_move_R = False
	temp_move_L = False
	player0.gravity_on = color_n_BG[2] #disables player movement w/ accordance to enable signal
	
	if level == 0 or pause_game or not player0.Alive:#delete mouse when out of the main menu
		pygame.mouse.set_visible(1)
	else:
		pygame.mouse.set_visible(0)
  
	if player0.lvl_transition_flag:#test for player collision w/ level transition rects
		next_level = player0.lvl_transition_data[0]
		player_new_x = player0.lvl_transition_data[1]
		player_new_y = player0.lvl_transition_data[2]
		player0.lvl_transition_flag = False
	
	#----------------------------------------------------------------------level changing-------------------------------------------------
	if level != next_level:
		scroll_x = 0
		the_sprite_group.purge_sprite_groups()
		clear_world_data(level_data_list)
		world.clear_data()
		level_transitioning = True
		level = next_level
		lvl_data = load_level_data(level, level_data_list, level_data_str_tuple, level_tuple, vol_lvl)
		color_n_BG = lvl_data[0:3]
		obj_list = lvl_data[3]
		
		if move_L:
			temp_move_L = move_L
			move_L = False
		if move_R:
			temp_move_R = move_R
			move_R = False
		player0.rect.x = player_new_x - 32 #set player location
        
		#player0.rect.y = player_new_y #disabling this makes it so that you can jump between levels
		player0.vel_y = 0
		camera.set_ini_pos = True #force camera into position
		player0.current_x = player_new_x #set player internal position
  
		if temp_move_R:
			move_R = temp_move_R
		if temp_move_L:
			move_L = temp_move_L
   
	elif level_transitioning and pygame.time.get_ticks() - 180 > level_trans_timing:
		level_trans_timing = pygame.time.get_ticks()
		level_transitioning = False
	
	
	#---------------------------------------------------------drawing level and sprites------------------------------------------------------------------
	draw_bg(screen, gradient_dict, color_n_BG[0], color_n_BG[1])#this just draws the color
	#camera.draw(screen)#for camera debugging
	if world.x_scroll_en:
		camera.auto_correct(player0.rect, world.coords, world_tile0_coord, world.world_limit, SCREEN_WIDTH, SCREEN_HEIGHT)
	
	world_tile0_coord = world.draw(screen, scroll_x, 0)#this draws the world and scrolls it 
	
	
	if not pause_game:
		player0.animate(the_sprite_group)
		player0.do_entity_collisions(the_sprite_group, obj_list, level_transitioning)
		player0.move(pause_game, move_L, move_R, world.solids, world.coords, world.world_limit, world.x_scroll_en, world.y_scroll_en, 
					SCREEN_WIDTH, SCREEN_HEIGHT, obj_list, the_sprite_group)
		scroll_x = player0.scrollx + camera.scrollx
	else:
		scroll_x = 0

	the_sprite_group.update_groups_behind_player(pause_game, screen, player0.hitbox_rect, player0.atk_rect_scaled, world.solids, scroll_x, player0.action, player0.direction, obj_list)
	player0.draw(screen)
	the_sprite_group.update_groups_infront_player(pause_game, screen, scroll_x, world.solids, player0.hitbox_rect, player0.atk_rect_scaled, player0.action)
   
	status_bars.draw(screen, player0.get_status_bars(), font)
 
	#---------------------------------------screen shake------------------------------------------------------------------------
	if player0.do_screenshake:
		player0.do_screenshake = False
		if not do_screenshake_master:
			do_screenshake_master = True
			screenshake_profile = (10,4)

	for p_int in obj_list[1]:
		if p_int.do_screenshake:
			p_int.do_screenshake = False
			if not do_screenshake_master:
				do_screenshake_master = True
				screenshake_profile = (8,6)
   
	if do_screenshake_master:
		tuple = camera.horizonatal_screen_shake(screenshake_profile, do_screenshake_master)
		do_screenshake_master = tuple[0]
		scroll_x += tuple[1]
		player0.rect.x += tuple[2]
  
	# for enemy in obj_list[0]:
	# 	if enemy.do_screenshake:
	# 		tuple = camera.horizonatal_screen_shake(12, 3, player0.rect, enemy.do_screenshake)
	# 		enemy.do_screenshake = tuple[0]
	# 		scroll_x += tuple[1]
 
	#----------black screen while transitioning---------------------------------------------------------
	if level_transitioning:
		pygame.draw.rect(screen, (0,0,0), (0,0,SCREEN_WIDTH,SCREEN_HEIGHT))
 
	#--------------------------------------------------------------MAIN MENU CODE---------------------------------------------------------------------
	if level == 0: 
		draw_bg(screen, gradient_dict, color_n_BG[0], color_n_BG[1])
		pause_game = False
		exit_to_title = False
		tuple = ui_manager0.show_main_menu(screen)
		run = tuple[1]
		next_level = tuple[0]
		if not run:
			pygame.time.wait(100)   
	
	#--------------------------------------showing controls----------------------------
	#depreciated, still a useful example for typing out though
	if show_controls_en:
		text = (
            '',
            '	-MOVEMENT AND ATTACKING-',
            'W: Jump',
            'A: Left',
            'D: Right',
            'S: Roll',
            'ALT: Sprint Enable',
            'I: Melee, I + S: Dash Strike,',
            'I + upwards momentum: Upstrike, I + Downwards momentum: Downstrike',
            'O: Projectile, HOLD O: Charge Projectile',
            '',
            '	-UI RELATED-',
            'Enter: Inspect/ Confirm/ New Game from Title',
            'ESC: Exit to Title/ Quit Game from Title - DOES NOT PAUSE GAME',
            'F: Toggle Fullscreen',
            'C: Show Controls - DOES NOT PAUSE GAME'
		)
		text_box_on = text_manager0.disp_text_box(screen, font_larger, text, black, white, (0,0,SCREEN_WIDTH,SCREEN_HEIGHT), 
                                            type_out, type_out_en, 'none')
		text_speed = 120
 
	#-------------------------------------------------pausing game--------------------------------------------------------
	if pause_game:
		ui_tuple0 = ui_manager0.show_pause_menu(screen)
		pause_game = ui_tuple0[0]
		if ui_tuple0[1]:
			next_level = 0
			player0 = player(32, 128, 4, hp, 6, 0, 0, vol_lvl)
			player_new_x = 32
			player_new_y = 32
   
	#---------------------------------updates from ui manager-----------------------------------------
	if ui_manager0.ctrls_updated:
		ctrls_list = read_settings_data('ctrls_data')
		ui_manager0.ctrls_updated = False
  
	if update_vol: #updates all m_players' sounds with new volume setting
    #objects already instantiated have their volumes updated here
    #new objects take vol_lvl as their ini_vol parameter so their volumes match the setting upon instantiation
		vol_lvl = read_settings_data('vol_data')
		m_player.set_vol_all_sounds(vol_lvl)
		the_sprite_group.update_vol_lvl(vol_lvl)
		player0.m_player.set_vol_all_sounds(vol_lvl)
  
	update_vol = ui_manager0.raise_volume or ui_manager0.lower_volume #2 different signals from ui_manager or'd together
  
 
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    #handling player death and game over screen------------------------------------------------------------------------------------
    
	if player0.hits_tanked >= player0.hp:#killing the player------------------------------------------------
		player0.Alive = False
		# text = (
		# 	'',
		# 	'		You Died.',
		# 	'(ESC to Restart)'
		# )
		# text_box_on = text_manager0.disp_text_box(screen, font_larger, text, black, white, (0, SCREEN_HEIGHT//2 -24, SCREEN_WIDTH, 72), 
        #                                    False, type_out_en, 'centered')
		if ui_manager0.show_death_menu(screen):
			next_level = 0
			player0 = player(32, 128, 4, hp, 6, 0, 0, vol_lvl)
			player_new_x = 32
			player_new_y = 32
   
	if player0.brain_damage:
		temp_list = []
		for i in range(8):
			temp_list.append(random.randint(90,120))
		ui_manager0.write_settings_data('ctrls_data',  temp_list)
		ctrls_list = read_settings_data('ctrls_data')
		temp_list *= 0
		player0.brain_damage = False

	#============================================================update player action for animation=======================================================
	#this is remnant code from following Coding with Russ' tutorial, I wasn't sure how to integrate this into playerFile.py
	#when I was separating the files (he wrote his whole tutorial game in virtually one single file)
	if player0.Alive:
		
		if (player0.hurting):
			player0.update_action(5) #hurting
		else:
			if player0.shoot:
				player0.update_action(11)

				#player0.change_direction = False
			
			elif player0.rolling or hold_roll:
				player0.update_action(9)#rolling
				player0.atk1_alternate = False
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
					if player0.atk1_alternate == True:# and player0.in_air == False:
						player0.update_action(7)	
					else:
						player0.update_action(8)#8: atk1
					
					# else:
					# 	player0.update_action(8)#8: atk1
			else:
					#hold_jump = False
				if player0.in_air:
					player0.update_action(2)#2: jump
					#hold_jump = False
					
				elif (player0.in_air == False and player0.vel_y >= 0 and player0.landing == True
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
  
	#---------------------------------------------------------------------------------------------------------------------------------------------
	#-------------------------------------------------------KBD inputs----------------------------------------------------------------------------
	#---------------------------------------------------------------------------------------------------------------------------------------------
	for event in pygame.event.get():
		#quit game
		if(event.type == pygame.QUIT):
			run = False
		#key press
		
		if(event.type == pygame.KEYDOWN):
			#print(pygame.key.name(event.key))
   
			if player0.Alive and color_n_BG[2] and not pause_game:
				if event.key == ctrls_list[1]: #pygame.K_a
					move_L = True
				if event.key == ctrls_list[3]: #pygame.K_d
					move_R = True
				if event.key == ctrls_list[0] and event.key == ctrls_list[4] and player0.stamina_used + 1 <= player0.stamina: #pygame.K_w, pygame.K_i
					#player0.squat = True
					#player0.squat_done = True
					player0.atk1_alternate = False
					player0.atk1 = True
				elif event.key == ctrls_list[0]: #pygame.K_w 
					player0.landing = False
					if hold_jump == False:
						hold_jump = True
						hold_jmp_update = pygame.time.get_ticks()
					
					# if pygame.time.get_ticks() - hold_jmp_time > hold_jmp_update:
					# 	hold_jmp_update = pygame.time.get_ticks()
					# 	player0.jump = False
					# else:
					# 	player0.jump = True
					if player0.rolling and player0.in_air == False:
						player0.roll_count = player0.roll_limit
						player0.squat = True
						#print("jump")
     
				if event.key == ctrls_list[4] and player0.stamina_used + 1 <= player0.stamina and event.key != ctrls_list[0]: #pygame.K_i, pygame.K_w
					change_once = True
					player0.atk1 = True
					hold_jump = False
				elif event.key == ctrls_list[4] and player0.stamina_used + 1 > player0.stamina: #pygame.K_i
					status_bars.warning = True
				
				if event.key == ctrls_list[5] and player0.stamina_used + 2 <= player0.stamina: #pygame.K_o
					player0.shot_charging = True
				elif event.key == ctrls_list[5] and player0.stamina_used + 2 > player0.stamina: #pygame.K_o
					status_bars.warning = True
     

				if event.key == ctrls_list[2] and player0.stamina_used + player0.roll_stam_rate <= player0.stamina: #pygame.K_s
					if hold_roll == False:
						hold_roll = True
						#hold_roll_update = pygame.time.get_ticks()
					hold_jump = False
				elif event.key == ctrls_list[2] and player0.stamina_used + player0.roll_stam_rate > player0.stamina: #pygame.K_s
					status_bars.warning = True
     
				if event.key == ctrls_list[7]: #pygame.K_RALT
					player0.speed = normal_speed + 1
					player0.sprint = True

			#===============================================================UI Related Keys=============================================================

			# if event.key == pygame.K_m:
			# 	m_player.play_song('newsong18.wav')
			# if event.key == pygame.K_c:
			# 	show_controls_en = True

			if (event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE) and not ui_manager0.options_menu_enable: #escape exits the window when testing...
				#run = False
				if level != 0:
					ui_manager0.trigger_once = True
					if pause_game or not player0.Alive:
						next_level = 0
						player0 = player(32, 128, 4, hp, 6, 0, 0, vol_lvl)
						player_new_x = 32
						player_new_y = 32
						#m_player.stop_sound()
						pygame.mixer.stop()
						
					else:
						#print("game is paused")
						pause_game = True
						pygame.mixer.pause()
      
					m_player.play_sound(m_player.sfx[1])
				else:
					run = False
				
    
			if event.key == pygame.K_RETURN:
				if pause_game and not ui_manager0.options_menu_enable:
					ui_manager0.trigger_once = True
					pause_game = False
					pygame.mixer.unpause()
				
				if level == 0 and not show_controls_en:
					m_player.play_sound(m_player.sfx[1])
					ui_manager0.trigger_once = True
					next_level = 1
				if (text_manager0.str_list_rebuilt != text_manager0.current_str_list):
					if type_out:
						m_player.play_sound(m_player.sfx[1])
					type_out = False #kill type_out signal while it's typing
				#else load next dialogue bubble
					#print(type_out)

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

			if event.key == ctrls_list[0] and player0.squat == False and player0.vel_y <= 1:#variable height jumping
				if player0.action == 7:
					player0.vel_y *= 0.3
				else:
					player0.vel_y *= 0.45 #rate at which jump vel decreases
				hold_jump = False
					
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
					#player0.squat = False
					#player0.squat_done = False
			if event.key == ctrls_list[7]: #pygame.K_RALT
				player0.speed = normal_speed
				player0.sprint = False
			# if event.key == pygame.K_a or event.key == pygame.K_d:
			# 	player0.sprint = False
			if event.key == pygame.K_c:
				show_controls_en = False
		
		if hold_jump:
			if pygame.time.get_ticks() - hold_jmp_time > hold_jmp_update:
				hold_jmp_update = pygame.time.get_ticks()
				hold_jump = False
				if player0.in_air == False:
					player0.squat_done = True
				# else:
				# 	player0.squat_done = False
				#print("fin")
			elif player0.in_air == False and player0.landing == False:
				player0.squat = True
				hold_jump = False
			else:
				hold_jump = True

		if hold_roll: #and (not player0.atk1 or player0.action <= 2):
			if  player0.stamina_used + player0.roll_stam_rate <= player0.stamina:
				player0.rolling = True
				hold_roll = False
				
    
			# if pygame.time.get_ticks() - hold_roll_time > hold_roll_update:
			# 	hold_roll_update = pygame.time.get_ticks()
			# 	hold_roll = False
			# else:
			# 	hold_roll = True

				
				#print("holding")
		
	#clock for textbox 
	if text_box_on and type_out and (text_manager0.str_list_rebuilt != text_manager0.current_str_list):
		if pygame.time.get_ticks() - text_delay > text_speed:
			text_delay = pygame.time.get_ticks()
			#print(text_delay)
			
			type_out_en = True
		else:
			type_out_en = False
   
	elif not type_out:#reset type_out signal
		text_manager0.str_list_rebuilt = text_manager0.current_str_list
		type_out = True
	
	# if pygame.time.get_ticks()%150 == 0:
	# 	print(type_out)

	pygame.display.update()

pygame.quit()

