import pygame
pygame.init()
import os
#print('directory: ' + os.getcwd())
import csv
#check out cs 418
from playerFile import player
from worldManager import World
from StatusBarsFile import StatusBars
from Camera import Camera
from music_player import music_player
from button import Button
from textManager import text_manager
import gc
#from pygame.locals import *


#setting the screen-----------------------------------------------------------
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
#flags = pygame.SHOWN #windowed mode
flags = pygame.DOUBLEBUF|pygame.FULLSCREEN #full screen mode
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)

pygame.display.set_caption('game window')

#framerate set up------------------------------------
clock = pygame.time.Clock()
FPS = 60
#pygame.key.set_repeat(5,5)

#local variables
move_L = False
move_R = False

#[171, 113, 100]#[116, 73, 67]#[102, 69, 67]#[131, 72, 65] #[183, 123, 108]
#(100,64,58)/ [95, 51, 54] [102, 69, 67]rusty sunset [120, 75, 67]
#(58,62,110)/(66,62,100) evening
#(30, 30, 80) darker evening
#(30, 30, 50) basement gray
#(7, 8, 13) night
#jade [119, 121, 124]

hold_jmp_update = pygame.time.get_ticks()
hold_jmp_time = 1
hold_jump = False

hold_roll_update = pygame.time.get_ticks()
hold_roll_time = 20
hold_roll = False

level_trans_timing = pygame.time.get_ticks()
show_controls_en = False

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
enemy_collision = False

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

level_data_dict = {
	0: 'coord_data',
	1: 'fg_data',
	2: 'data',
	3: 'bg1_data',
	4: 'bg2_data',
	5: 'bg3_data',
	6: 'bg4_data',
	7: 'bg5_data',
	8: 'bg6_data'
}

world = World()
#instantiate status bars
status_bars = StatusBars()

#define font
font = pygame.font.SysFont('SimSun', 12)
font_larger = pygame.font.SysFont('SimSun', 16)

#music player instance-------------------------------------------------------------------------------------------
m_player_sfx_list_main = ['roblox_oof.wav', 'hat.wav']
m_player = music_player(m_player_sfx_list_main)

#camera instance
camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

#colors
blue_0 = [100, 82, 88]
blue1 = [97, 88, 102]
orang = [140, 123, 108]
black = [0,0,0]
white = [255,255,255]
maroonish = [134, 107, 116]

#text manager instance
text_manager0 = text_manager()
type_out_en = True
text_speed = 200
type_out = True

#methods--------------

def draw_bg(screen, gradient_type, bg_color):
    #sets gradients here, can probably turn into a dictionary w/ tuples
	if gradient_type == 'none':
		R = 0
		G = 0
		B = 0
	elif gradient_type == 'sunset':
		R = -1
		G = -1
		B = 1
	elif gradient_type == 'rain':
		R = -1
		G = 1
		B = 2
	
	#drawing bg color
	if gradient_type != 'none':
		for i in range(SCREEN_HEIGHT//32):
			pygame.draw.rect(screen, [bg_color[0]+ i*R, bg_color[1]+i*G, bg_color[2] + i*B], ((0,i*32), (SCREEN_WIDTH,(i+1)*32)))
	else:
		screen.fill(bg_color)


#instantiating player-------------------------------------------------------------------
#player0 = player(64, 127, 5)


#reading level data-----------------------------------------------------------------------------------------------------------------

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
	
    
def load_level_data(level, level_data_list, level_data_dict):
	
    #might want to turn this into a dictionary later
	if level == 0:
		BG_color = black
		gradient_type = 'none'
		rows = 15
		cols = 30
		level_transitions = []
		player_en = False
	elif level == 1:
		BG_color = maroonish
		gradient_type = 'rain'
		rows = 15
		cols = 200
		level_transitions = [(2, 15*32, 2, 44*32 -2, 288), (2, 15*32, 2, 2, 384)]
		player_en = True #(transition tile width, transition tile height, level, player new x, player new y)
	elif level == 2:
		BG_color = maroonish
		gradient_type = 'rain'
		rows = 15
		cols = 45
		level_transitions = [(2, 15*32, 1, 199*32 -2, 384), (2, 15*32, 1, 2, 288)]
		player_en = True #-2 to prevent an auto looping level change
	else:
		BG_color = orang
		gradient_type = 'sunset'
		rows = 15
		cols = 200
		level_transitions = []
		player_en = True

	#reading csv files 
	index = 0
	for level_data in level_data_list:
		read_level_data(level, rows, cols, level_data, level_data_dict[index])
		index += 1
  
	#world has self data lists that get cleared each time this is called
	world.process_data(level_data_list, the_sprite_group, SCREEN_WIDTH, SCREEN_HEIGHT, level_transitions)
	
	return [gradient_type, BG_color, player_en]



#instantiate sprite groups
class sprite_group():
    def __init__(self):
        self.enemy0_group = pygame.sprite.Group()
        self.enemy_bullet_group = pygame.sprite.Group()
        self.player_bullet_group = pygame.sprite.Group()
        self.particle_group = pygame.sprite.Group()
        self.particle_group_bg = pygame.sprite.Group()
        self.particle_group_fg = pygame.sprite.Group()
        self.button_group = pygame.sprite.Group()
    
    def purge_sprite_groups(self):
        self.enemy0_group.empty()
        self.enemy_bullet_group.empty()
        self.player_bullet_group.empty()
        self.particle_group.empty()
        self.particle_group_bg.empty()
        self.particle_group_fg.empty()
        self.button_group.empty()

the_sprite_group = sprite_group()
#create a hostiles group tuple
hostiles_group = (the_sprite_group.enemy0_group, the_sprite_group.enemy_bullet_group)


player0 = player(32, 128, 4, 6, 6, 0, 0)#6368 #5856 #6240
#a player needs to be instantiated every level, but a dead player can also be instantiated when one isn't needed
#good news is that the player's coordinates can go off screen and currently the camera's auto scroll will eventually correct it
normal_speed = player0.speed

#load initial level-------------------------------------------------------------------------------------------------
the_sprite_group.purge_sprite_groups()#does as the name suggests
color_n_BG = load_level_data(0, level_data_list, level_data_dict) 


#running the game----------------------------------------------------------------------------------------------------------------------
#https://www.youtube.com/watch?v=XPHDiibNiCM

run = True
player_new_x = 32
player_new_y = 32
ld_title_screen_en = True

while run:
	clock.tick(FPS)
	#reset temporary values
	text_box_on = False
 
	temp_move_R = False
	temp_move_L = False
	player0.gravity_on = color_n_BG[2] #disables player movement w/ accordance to enable signal
	
	if level != 0 and not show_controls_en:#delete mouse when out of the main menu
		pygame.mouse.set_visible(0)
	else:
		pygame.mouse.set_visible(1)
  
	if player0.lvl_transition_flag:#test for player collision w/ level transition rects
		next_level = player0.lvl_transition_data[0]
		player_new_x = player0.lvl_transition_data[1]
		player_new_y = player0.lvl_transition_data[2]
		player0.lvl_transition_flag = False
	
	#----------------------------------------------------------------------level changing-------------------------------------------------
	if level != next_level:
		the_sprite_group.purge_sprite_groups()
		clear_world_data(level_data_list)
		world.clear_data()
		level_transitioning = True
		level = next_level
		color_n_BG = load_level_data(level, level_data_list, level_data_dict)
		
		if move_L:
			temp_move_L = move_L
			move_L = False
		if move_R:
			temp_move_R = move_R
			move_R = False
		player0.rect.x = player_new_x #set player location
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
	
	
	#----------------------------------------------------------------------drawing level------------------------------------------------------------------
	draw_bg(screen, color_n_BG[0], color_n_BG[1])#this just draws the color
	#camera.draw(screen)#for camera debugging
	if world.x_scroll_en:
		camera.auto_correct(player0.rect, world.coords, world.world_limit, SCREEN_WIDTH, SCREEN_HEIGHT)
	world.draw(screen, scroll_x, 0)#this draws the world and scrolls it 
	#draw_filter(screen, color_n_BG[0], color_n_BG[1])
 
	player0.animate(the_sprite_group)
	#if player0.Alive:
	player0.move(move_L, move_R, world.solids, world.coords, world.world_limit, world.x_scroll_en, world.y_scroll_en, 
              	SCREEN_WIDTH, SCREEN_HEIGHT, the_sprite_group)
	
	scroll_x = player0.scrollx + camera.scrollx

	for particle in the_sprite_group.particle_group_bg:
		particle.draw(screen)
		particle.animate()
		particle.move(scroll_x)
		if particle.Active == False:
			the_sprite_group.particle_group_bg.remove(particle)

	for enemy0 in the_sprite_group.enemy0_group:
		enemy0.draw(screen)
		enemy0.animate(the_sprite_group)
		enemy0.move(player0.hitbox_rect, player0.atk_rect_scaled, world.solids, scroll_x, player0.action, player0.frame_index, the_sprite_group)
		if enemy0.Alive == False:
			the_sprite_group.enemy0_group.remove(enemy0)

	for enemy_bullet in the_sprite_group.enemy_bullet_group:
		enemy_bullet.draw(screen)
		enemy_bullet.animate()
		enemy_bullet.move(player0.hitbox_rect, player0.atk_rect_scaled, world.solids, scroll_x, player0.action, the_sprite_group, player0.direction)
		if enemy_bullet.Active == False:
			the_sprite_group.enemy_bullet_group.remove(enemy_bullet)
    
	for player_bullet in the_sprite_group.player_bullet_group:
		player_bullet.draw(screen)
		player_bullet.animate()
		player_bullet.move(player0.hitbox_rect, player0.atk_rect_scaled, world.solids, scroll_x, player0.action, the_sprite_group, player0.direction)
		if player_bullet.Active == False:
			the_sprite_group.player_bullet_group.remove(player_bullet)
   
	for particle in the_sprite_group.particle_group:
		particle.draw(screen)
		particle.animate()
		particle.move(scroll_x)
		if particle.Active == False:
			the_sprite_group.particle_group.remove(particle)
    
	player0.draw(screen)
 
	for particle in the_sprite_group.particle_group_fg:
		particle.draw(screen)
		particle.animate()
		particle.move(scroll_x)
		if particle.Active == False:
			the_sprite_group.particle_group_fg.remove(particle)
   
	status_bars.draw(screen, player0.get_status_bars(), font)
 
	#----------black screen while transitioning---------------------------------------------------------
	if level_transitioning:
		pygame.draw.rect(screen, (0,0,0), (0,0,SCREEN_WIDTH,SCREEN_HEIGHT))
 
	#--------------------------------------------------------------MAIN MENU CODE---------------------------------------------------------------------
	if level == 0: 
		draw_bg(screen, color_n_BG[0], color_n_BG[1])
		if ld_title_screen_en: #execute once signal
			new_game_img = pygame.image.load('sprites/new_game_btn.png').convert_alpha()
			quit_img = pygame.image.load('sprites/quit_btn.png').convert_alpha()
			ctrl_img = pygame.image.load('sprites/ctrl_btn.png').convert_alpha()
			title_screen = pygame.image.load('sprites/title_screen.png').convert_alpha()
			ts_rect = title_screen.get_rect()
			ts_rect.center = (SCREEN_WIDTH//2 -8, SCREEN_HEIGHT//2 +32)
			start_button = Button(SCREEN_WIDTH //2 -64, SCREEN_HEIGHT //2 +64, new_game_img, 1)
			ctrl_button = Button(SCREEN_WIDTH //2 -64, SCREEN_HEIGHT //2 +96, ctrl_img, 1)
			quit_button = Button(SCREEN_WIDTH //2 -64, SCREEN_HEIGHT //2 +128, quit_img, 1)
			ld_title_screen_en = False
			#these buttons get purged on level change dw

		screen.blit(title_screen, ts_rect)
  
		if start_button.highlight:
			pygame.draw.rect(screen, (255,0,86), start_button.rect, 2)
			#button shaking lol
			if pygame.time.get_ticks()%2 == 0:
				start_button.rect.x += 1
			elif pygame.time.get_ticks()%3 == 0:
				start_button.rect.x -= 2
			else:
				start_button.rect.x = SCREEN_WIDTH //2 -64
		else:
			start_button.rect.x = SCREEN_WIDTH //2 -64
		if ctrl_button.highlight:
			pygame.draw.rect(screen, (255,0,86), ctrl_button.rect, 2)
		if quit_button.highlight:
			pygame.draw.rect(screen, (255,0,86), quit_button.rect, 2)
   
		if not show_controls_en:
			if start_button.draw(screen):
				next_level = 1
			if ctrl_button.draw(screen):
				show_controls_en = True
				m_player.play_sound(m_player.sfx[1])
			if quit_button.draw(screen):
				run = False

			if start_button.clicked or quit_button.clicked:
				m_player.play_sound(m_player.sfx[1])
		#you need to add saves and volume controls, and probably control controls too later
	else:
		ld_title_screen_en = True
	
	#--------------------------------------showing controls----------------------------
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
 
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------
    #handling enemy player collisions------------------------------------------------------------------------------------
    
	if player0.hits_tanked >= player0.hp:#killing the player------------------------------------------------
		player0.Alive = False
		text = (
			'',
			'		You Died.',
			'(ESC to Restart)'
		)
		text_box_on =text_manager0.disp_text_box(screen, font_larger, text, black, white, (0, SCREEN_HEIGHT//2 -24, SCREEN_WIDTH, 72), 
                                           False, type_out_en, 'centered')

    
    #the outermost if basically states: 
    #if the player is not meleeing or rolling or is going through the hurt animation/has i frames
	if (player0.rolling == False and player0.action != 7 and player0.action != 8 and player0.action != 10
     	and player0.i_frames_en == False and player0.hurting == False and player0.Alive):
		#loops thru toople of sprite groups that can damage the player
		#	allows player to take damage from different kinds of sprite groups in a single tick (each enemy collision has its own value)
		#	does not take in account collisions of multiple of the same sprite group in a single tick
		for enemy in enumerate(hostiles_group):
			if pygame.sprite.spritecollide(player0, enemy[1], False, collided= pygame.sprite.collide_rect_ratio(0.8)):
				enemy_collision = True #this is a 1 tick variable
				if enemy[1] == the_sprite_group.enemy0_group:
					damage += 1.5
					# for enemy0_ in enumerate(the_sprite_group.enemy0_group):
					# 	if enemy0_[1].inundated == False:
					# 		print(enemy0_[1].inundated)
					# 		damage += 0.75
					# 	else:
					# 		print(enemy0_[1].inundated)
				if enemy[1] == the_sprite_group.enemy_bullet_group:
					damage += 3
					
				player0.take_damage(damage)
				#print(damage)
			damage = 0
			

	#update player action for animation
	if player0.Alive:
		if (enemy_collision == True or player0.hurting == True):
			enemy_collision = False
			player0.update_action(5) #hurting
		else:
			if player0.shoot:
				player0.update_action(11)
			
			elif player0.atk1:
				# if player0.rolling:
				# 	player0.update_action(9)#rolling
				# 	player0.atk1_alternate = False
				if player0.atk1_alternate == True:# and player0.in_air == False:
					player0.update_action(7)
				else:
					#player0.update_action(8)#8: atk1, yes they are ordered in the way you loaded them
					if player0.crit:
						player0.update_action(10)
					else:
						player0.update_action(8)#8: atk1, yes they are ordered in the way you loaded them
				
			else:
				if player0.rolling:
					player0.update_action(9)#rolling
					player0.atk1_alternate = False
					#hold_jump = False
				elif player0.in_air:
					player0.update_action(2)#2: jump
					#hold_jump = False
					if player0.vel_y < -2:# and player0.speed == normal_speed: -1
						player0.atk1_alternate = True
					else:
						player0.atk1_alternate = False
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
  

	for event in pygame.event.get():
		#quit game
		if(event.type == pygame.QUIT):
			run = False
		#key press
		
		if(event.type == pygame.KEYDOWN):
			if player0.Alive and color_n_BG[2]:
				if event.key == pygame.K_a:
					move_L = True
				if event.key == pygame.K_d:
					move_R = True
				if event.key == pygame.K_w and event.key == pygame.K_i and player0.stamina_used + 2 <= player0.stamina:
					#player0.squat = True
					#player0.squat_done = True
					player0.atk1_alternate = False
					player0.atk1 = True
				elif event.key == pygame.K_w:# and player0.in_air == False:# : #and event.key != pygame.K_i and event.key != pygame.K_s
					
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
     
				if event.key == pygame.K_i and player0.stamina_used + 2 <= player0.stamina and event.key != pygame.K_w:
					player0.atk1 = True
					hold_jump = False
				elif event.key == pygame.K_i and player0.stamina_used + 2 > player0.stamina:
					status_bars.warning = True
				
				if event.key == pygame.K_o and player0.stamina_used + 2 <= player0.stamina:
					player0.shot_charging = True
				elif event.key == pygame.K_o and player0.stamina_used + 2 > player0.stamina:
					status_bars.warning = True
				
				if event.key == pygame.K_s and player0.roll_count == 0 and player0.stamina_used + 2 <= player0.stamina:
					#player0.rolling = True
					if hold_roll == False:
						hold_roll = True
						hold_roll_update = pygame.time.get_ticks()
					hold_jump = False
				elif event.key == pygame.K_s and player0.roll_count == 0 and player0.stamina_used + 2 > player0.stamina:
					status_bars.warning = True
     
				if event.key == pygame.K_RALT or event.key == pygame.K_LALT:
					player0.speed = normal_speed + 1
					player0.sprint = True
			if event.key == pygame.K_m:
				m_player.play_song('newsong18.wav')
			if event.key == pygame.K_c:
				show_controls_en = True
			if event.key == pygame.K_f:
				if flags == pygame.SHOWN: #windowed mode
					flags = pygame.DOUBLEBUF|pygame.FULLSCREEN #full screen mode
					screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
				else:
					flags = pygame.SHOWN #windowed mode
					screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
			# if event.key == pygame.K_l and player0.action < 5:
			# 	if level < 2:
			# 		next_level = level + 1
			# 	else:
			# 		next_level = 0

			if event.key == pygame.K_ESCAPE:
				#run = False
				if level != 0:
					m_player.stop_sound()
					m_player.play_sound(m_player.sfx[1])
				elif level == 0 and show_controls_en:
					m_player.play_sound(m_player.sfx[1])
					show_controls_en = False
				else:
					run = False
				next_level = 0
				player0 = player(32, 128, 4, 6, 6, 0, 0)
				player_new_x = 32
				player_new_y = 32
    
			if event.key == pygame.K_RETURN:
				if level == 0 and not show_controls_en:
					m_player.play_sound(m_player.sfx[1])
					next_level = 1
				if (text_manager0.str_list_rebuilt != text_manager0.current_str_list):
					if type_out:
						m_player.play_sound(m_player.sfx[1])
					type_out = False #kill type_out signal while it's typing
				#else load next dialogue bubble
					#print(type_out)
				
				#shit you need to be able to reset the player back to level 1 and restore their health!
    
			#temp bg adjustment
			amnt = 1
			if event.key == pygame.K_5:
				amnt = -1
				print(amnt)
			elif event.key == pygame.K_6:
				amnt = 1
				print(amnt)
			if event.key == pygame.K_1 or event.key == pygame.K_2 or event.key == pygame.K_3:
				pygame.key.set_repeat(5,60)
				if event.key == pygame.K_1 and BG_color[0] < 256 and BG_color[0] > 0:
					BG_color[0] += amnt
					#print(BG_color[0])
				if event.key == pygame.K_2 and BG_color[1] < 256 and BG_color[1] > 0:
					BG_color[1] += amnt
				if event.key == pygame.K_3 and BG_color[2] < 256 and BG_color[2] > 0:
					BG_color[2] += amnt
			else:
				pygame.key.set_repeat(0,0)
			
			if event.key == pygame.K_4:
				print(BG_color)
			


		if(event.type == pygame.KEYUP):
			if event.key == pygame.K_a:
				move_L = False
			if event.key == pygame.K_d:
				move_R = False

			# if event.key == pygame.K_w and player0.squat == False:#variable height jumping, has a bug that results in an echo
			# 	# if player0.action == 2 and player0.rolling == False and player0.vel_y < 0:
					
			# 	# 	hold_jump = False
			# 	if player0.vel_y <= -5:
			# 		player0.vel_y *= 0.5
			# 		hold_jump = False
			# 		print(player0.vel_y)
			# 	# else:
			# 	# 	print(player0.vel_y)
					
			if event.key == pygame.K_i:
				status_bars.warning = False
			if event.key == pygame.K_s:#s
				status_bars.warning = False
			if event.key == pygame.K_o:
				status_bars.warning = False
				player0.frame_updateBP = 150
				if player0.shot_charging == True:
					player0.shoot = True
					player0.shot_charging = False
					#player0.squat = False
					#player0.squat_done = False
			if event.key == pygame.K_RALT or event.key == pygame.K_LALT:
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

		if hold_roll:
			if  player0.stamina_used + 2 <= player0.stamina:
				player0.rolling = True
			if pygame.time.get_ticks() - hold_roll_time > hold_roll_update or player0.rolled_into_wall:
				hold_roll_update = pygame.time.get_ticks()
				hold_roll = False
			else:
				hold_roll = True

				
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

