import pygame
import os
import math
from button import Button 
from textManager import text_manager 
from music_player import music_player 

from textfile_handler import textfile_formatter
import random

config_path = 'assets/config_textfiles/item_config/'
item_sprites_path = 'assets/sprites/items/'
max_item_count = 999

#Items exist in 2 spaces: level spaces and inventory spaces
#This file contains code to support an item existing in the level space and being able to interact with the player.
#Behaviors in inventory space involve keeping track of item count and apply status effects.

class Item(pygame.sprite.Sprite): #helper class with logic for item behavior outside of player inventory
    def __init__(self, id, x, y, count, is_immortal):
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.image = pygame.image.load(os.path.join(item_sprites_path, f'{self.id}.png')).convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        self.count = count
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        #self.rect.centery = y
        self.ini_y = y

        self.increment = 3*random.random()
        
        self.is_immortal = is_immortal
        self.life_span = 10000
        self.initial_time = pygame.time.get_ticks()
        
        self.flip = False
        self.flicker = False
        
        self.gravitation_rect = pygame.rect.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
        self.gravitation_rect.scale_by_ip(8)
        
        weight_dict = {
            'Rock': 5,
            'Talisman of Salted Earth': 3
        }
        self.weight = 9
        if self.id in weight_dict:
            self.weight = weight_dict[self.id]

        
    def enable(self, player_rect, the_sprite_group, pause_game):
        #THE ORDER OF EXECUTION MATTERS FOR THIS METHOD
        disable = False
        
        #align rects
        self.gravitation_rect.center = self.rect.center
        
        #picking up item, might need to moved to a separate class
        if self.rect.colliderect(player_rect):# and pick_up_confirmation: #picking up item is not affected by pause game
            #disable = True
            pass
            
        elif not pause_game and not self.gravitate(player_rect):#bob up and down
            self.rect.centery = self.ini_y - self.weight*math.sin(self.increment)

            if self.increment > 2*math.pi:
                self.rect.centery = self.ini_y
                self.increment = 0
                
            self.increment += math.pi/24
                
        #player can get item data from the sprite group
        
        #despawning
        if not pause_game and not self.is_immortal and pygame.time.get_ticks() > self.initial_time + int(self.life_span):
            disable = True
        elif not pause_game and not self.is_immortal and pygame.time.get_ticks() > self.initial_time + int(0.8*self.life_span):
            self.flicker = True
        elif pause_game and not self.is_immortal:
            #self.life_span *= 0.7 #decreases the lifespan everytime game is paused otherwise items' lifespans will be restored by the line below
            self.initial_time = pygame.time.get_ticks()
            
        if not pause_game and self.is_immortal:
            if pygame.time.get_ticks()%50 == 0:
                the_sprite_group.particle_group_fg.sprite.add_particle('sparkle_white', 
                                                                        self.rect.centerx + random.randrange(-16,16), 
                                                                        self.rect.centery + random.randrange(-16,16), 
                                                                        1, 1, False, 0)
                
        if disable:
            self.disable()
            
    def gravitate(self, player_rect):
        if self.gravitation_rect.colliderect(player_rect):
            gravitating = True
            if self.rect.centerx < player_rect.centerx:
                self.rect.x += 3
            elif self.rect.centerx > player_rect.centerx:
                self.rect.x -= 3
        
            if self.rect.centery < player_rect.centery:
                self.rect.y += 3
            elif self.rect.centery > player_rect.centery:
                self.rect.y -= 3    
            self.ini_y = self.rect.y
        else:
            gravitating = False
            
        return gravitating
            
    def disable(self):
        self.rect = (0,0,0,0)
        self.kill()

    def scroll_along(self, scrollx):
        self.rect.x += ( - scrollx)
        
    def force_ini_position(self, scrollx):
        self.rect.x -= scrollx
        
    def draw(self, screen):
        if self.rect.x > -self.width and self.rect.x < 640:
            if self.flicker:
                if pygame.time.get_ticks() % 2 == 0:
                    screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
            else:
                #pygame.draw.rect(screen, (255,0,255), self.gravitation_rect)
                screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
                

#============================================================================================================================================ 
            
class inventory_handler(): #handles setting up inventory, picking up items, and storing items; is instantiated in player

    def __init__(self, slot_count):
        self.slot_count = slot_count
        
        #create a limited list of lists
        self.inventory = []
        for i in range(self.slot_count):
            self.inventory.append(['empty', 0]) #[ID, count]
            i += 1

        self.item_usage_hander0 = item_usage_hander()
        #print(self.inventory)
            
    #used for loading inventory from save file        
    def load_saved_inventory(self, inventory):
        self.inventory = inventory
        
    def check_for_item(self, item_name):
        # item_found = False
        # for slot in self.inventory:
        #     if slot[0] == item_name:
        #         item_found = True
        #         break
        
        return item_name in [x[0] for x in self.inventory]#item_found
    
    def discard_item_by_name(self, item_name):
        empty = False
        for slot in self.inventory:
            if slot[0] == item_name:
                slot_index = self.inventory.index(slot)
                if self.inventory[slot_index][1] > 0:
                    self.inventory[slot_index][1] -= 1
                    
                if self.inventory[slot_index][1] == 0:
                    self.inventory[slot_index][0] = 'empty'
                    empty = True
                break
            
        return empty
    
    def find_available_slot(self, item_id):
        slot_index = 0
        stacked = False
        allocated = False
        
        #first check if there's a slot with a matching item ID (item can stack) and that the max count hasn't been reshced
        for slot in self.inventory:
            if slot[0] == item_id and slot[1] < max_item_count:
                slot_index = self.inventory.index(slot)
                stacked = True
                break
                
        #then check for the next available slot (item can be allocated to another slot)
        if slot_index == 0 and not stacked: #slot with matching item id not found
            for slot in self.inventory:
                if slot == ['empty', 0] and self.inventory.index(slot) != len(self.inventory) - 1: #last slot is off reserved
                    slot_index = self.inventory.index(slot)
                    allocated = True
                    break
        
        #then check if there's any empty slots at all, or if there's no items
        if slot_index == 0 and not allocated and not stacked:
            slot_index = -1 #do not pick up item, inventory full
                
        return slot_index
                
    def include_exclude(self, exclude, id_, list_):
        if exclude:
            boolean = id_ not in list_ #if an item is not in the exclude list
        else:
            boolean = id_ in list_ #if an item is in the include list
            
        return boolean
                
    #call this whenever the player collides with an item
    def pick_up_item(self, player_rect, item_group, item_id_list, exclude):
        picked_up = False

        for item in item_group:
            if player_rect.colliderect(item.rect):
                slot_index = self.find_available_slot(item.id)
                if slot_index != -1 and self.include_exclude(exclude, item.id, item_id_list): #inventory not full
                    self.inventory[slot_index][0] = item.id
                    self.inventory[slot_index][1] += item.count
                    item.disable() #item is deleted on the player side by calling an internal method
                    picked_up = True
                elif self.include_exclude(not exclude, item.id, item_id_list): #if item is included in the item_id_list then put it in the special slot
                    self.inventory[len(self.inventory) - 1][0] = item.id
                    self.inventory[len(self.inventory) - 1][1] += item.count
                    item.disable()
                    picked_up = True
                #print(self.inventory)
        
        return picked_up
      
#using items:
#signal comes from inventory_UI probably in the form of a string: item_id
#items can only have one function, but that function can be composed of sub functions
#ex. using Cursed Flesh will 1. heal the player, 2. decrease player max stamina
#
#Make a class called item_usage_handler, which will be instantiated under inventory_handler
#It will have a dictionary formatted like item_id: (tuple of strings that are id's for sub functions)
#
#use item will probably have a for loop that iterates through the sub functions id tuple and a
#big if else chain (if sub_function_id == "heal"... etc) that calls sub functions
#
#will need a case for using empty, where empty: nothing

class item_usage_hander():  #helper class with logic for item usage and applying status effects directly to player, instantiated within inventory_handler
    def __init__ (self):
        t = textfile_formatter()
        self.sub_function_dict = t.str_list_to_dict(t.read_text_from_file(os.path.join(config_path, 'item_subfunctions.txt')), 'list')
        self.instant_heal_items_dict = t.str_list_to_dict(t.read_text_from_file(os.path.join(config_path, 'instant_heal_items_config.txt')), 'float')
        self.st_reduction_factor_dict = t.str_list_to_dict(t.read_text_from_file(os.path.join(config_path, 'st_reduction_factor_config.txt')), 'float')
        self.char_reduction_factor_dict = t.str_list_to_dict(t.read_text_from_file(os.path.join(config_path, 'char_reduction_factor_config.txt')), 'float')
        #make a separate dict for particles and sfx for each item used
    
    #make a signal processing function that will process an item usage request from inventory UI in game_window
    #have it be called in game window
    #possibly have it wrapped in an if statement for if the item usage request is being sent to avoid having to constantly pass the pointer to the player
    
    #add sprite group access here via a 2nd use_item function that handles instantiating objects
    def process_use_signal(self, use_item_flag, item_id, player):
        #print(use_item_flag)
        item_was_used = False
        if use_item_flag: #and some internal variable in player indicating the animation finished, trigger once signal
            item_was_used = (self.use_item(item_id, player) or False)#controls whether or not to discard the item
            use_item_flag = False
            
        return (use_item_flag, item_was_used)
        
    #I'm gonna have the player pass itself into this function to avoid having a huge amount of parameters
    #The drawback is a loss of modularity since I'll have to reference the specific variables in 'player'
    
    #note this can only deal with instant effects, persistent status effects probably need a separate class or function
    
    #however, another perk of passing the player is that this class has access to the player's music player, particles, and sounds
    
    #plain text file game/ game modular
    #recode this a little bit so that it uses more dictionaries with values that can be initially loaded thru a text file
    
    def use_item(self, item_id, player):
        if item_id in self.sub_function_dict:#basically check to see if the item has a subfunction
            sub_function_tuple = self.sub_function_dict[item_id]
            item_was_used = True
        else:#do nothing if no subfunction
            sub_function_tuple = ('nothing',)
            item_was_used = False
        
        for function in sub_function_tuple:
            if function == 'nothing':
                break
            elif function == 'heal':
                self.heal(item_id, player)
            elif function == 'reduce_stamina':
                self.reduce_stamina(item_id, player)
            elif function == 'restore_stamina':
                self.restore_stamina(player)
            elif function == 'reduce_char':
                self.reduce_char(item_id, player)
        
        return item_was_used
        
            
    def heal(self, item_id, player):
        #player hp works with hits tanked getting added up
        hp_increment = 0
        hp_increment = self.instant_heal_items_dict[item_id]
        
        if player.hits_tanked - hp_increment < 0: #if healing overflows set player hp to max
            player.hits_tanked = 0
        else:
            player.hits_tanked -= hp_increment
      
    def reduce_stamina(self, item_id, player):
        #this is how stamina works: there's this thing called stamina_used and it's incremented with each move that costs stamina
        #in game window, whenever the player uses stamina, it tests if the stamina_used will be greater than player stamina (which is essentially max stamina)
        #so effectively player stamina is the limit for how much the player can use

        player.stamina_usage_cap += (player.stamina - player.stamina_usage_cap)*self.st_reduction_factor_dict[item_id] #exponentially decreases stamina regen cap

        if player.stamina_used < player.stamina_usage_cap: #set stamina to new cap
            player.stamina_used = player.stamina_usage_cap
    
    def restore_stamina(self, player):
        player.stamina_usage_cap = 0
        
    def reduce_char(self, item_id, player):
        if self.char_reduction_factor_dict[item_id] < 1:
            player.char_level = int(player.char_level*self.char_reduction_factor_dict[item_id])
        else:
            player.char_level -= self.char_reduction_factor_dict[item_id]
            if player.char_level < 1:
                player.char_level = 1
        
    

#=============================================================================================================================================  
#note: due to the implementation of a delay in the button file, the game will slow down whenever a button is pressed
#this is so for general menu navigating the mechanical signal of a click doesn't carry on when the next set of buttons is loaded in        
                
class inventory_UI(): #handles displaying inventory, item description and counts, and slot selection
    def __init__(self, rows, cols, fontlist, SCREEN_WIDTH, SCREEN_HEIGHT, ts, ini_vol):
        m_player_sfx_list_main = ['roblox_oof.mp3', 'hat.mp3', 'woop.mp3']
        self.m_player = music_player(m_player_sfx_list_main, ini_vol)

        self.rows = rows
        self.cols = cols
        self.size = 0
        self.total_slots = rows*cols + 1
        self.trigger_once = True
        
        self.fontlist = fontlist
        self.button_list = []
        self.button_list2 = [] #for displaying inventory items
        
        self.S_W = SCREEN_WIDTH
        self.S_H = SCREEN_HEIGHT
        
        self.temp_inventory = []
        self.slot_pos_list = []
        for row in range(rows):
            for col in range(cols):
                self.slot_pos_list.append((row,col))
        #print(self.slot_pos_list)
        
        self.slot = 0
        self.inv_toggle_timer = pygame.time.get_ticks()
        
        self.generic_img = pygame.image.load('assets/sprites/generic_btn.png').convert_alpha()
        self.invisible_img = pygame.image.load('assets/sprites/invisible_btn.png').convert_alpha()
        self.inventory_btn = pygame.image.load('assets/sprites/inventory_btn.png').convert_alpha()
        self.inv_bg = pygame.image.load('assets/sprites/pause_bg.png').convert_alpha()
        self.aria_frame_list = []
        for i in range (len(os.listdir(f'assets/sprites/misc_art/aria'))):
            self.aria_frame_list.append(pygame.image.load(f'assets/sprites/misc_art/aria/{i}.png').convert_alpha())
        
        self.inv_disp = (160,128) #inventory displacement for displaying slot
        self.isolated_slot_pos = (192, self.inv_disp[1] + self.rows*32 + 32)
        self.text_manager0 = text_manager(SCREEN_WIDTH, SCREEN_HEIGHT, ts)
     
        
        #load all items into a list
        item_img_list = []
        for item in os.listdir(item_sprites_path):
            item_img_list.append([item[0:len(item)-4], pygame.image.load(os.path.join(item_sprites_path, f'{item}')).convert_alpha()])#-4 to remove '.png'
            
        #create dictionary
        #dictionaries are mutable btw!
        self.item_img_dict = dict(item_img_list)
        self.item_details0 = item_details()
        
        self.use_item_flag = False
        self.item_to_use = 'empty'
        self.use_item_btn_output = False
        
        self.help_btn_str = '[Open Tips]'
        self.help_open = False
        
    def clear_inventory(self, inventory):
        temp_inventory = inventory 
        for i in range(self.size):
            temp_inventory[i] = ['empty', 0]
            
        return temp_inventory
    
    def play_click_sound(self):
        self.m_player.play_sound(self.m_player.sfx[1], None)
    
    def move_item(self, inv_directions, move_enable, inventory):#using kbd to move around inventory and manipulate items
        if self.slot != self.total_slots - 1:#make sure the last slot is never reached
            moveR = inv_directions[0]
            moveL = inv_directions[1]
            moveUp = inv_directions[2]
            moveDown = inv_directions[3]
            discard = inv_directions[4]
            
            slot_data_temp = inventory[self.slot]
            
            current_pos = self.slot_pos_list[self.slot]#get initial slot position
            row = current_pos[0]
            col = current_pos[1]
            if moveR:#set new position
                if col < self.cols - 1:
                    col += 1
                else:
                    col = 0
            elif moveL:
                if col > 0:
                    col -= 1
                else:
                    col = self.cols - 1
            elif moveDown:
                if row < self.rows - 1:
                    row += 1
                else:
                    row = 0
            elif moveUp:
                if row > 0:
                    row -= 1
                else:
                    row = self.rows - 1
            elif discard and not move_enable:
                self.discard_item(inventory)
            
            new_slot = self.slot_pos_list.index((row,col))
            
            if move_enable: #move items to new positions
                inventory[self.slot] = inventory[new_slot]
                inventory[new_slot] = slot_data_temp
                
                if discard:
                    self.discard_slot(inventory)
            
            self.slot = new_slot
        elif True in inv_directions: #if the last slot is currently selected, default to the first slot
            self.slot = 0
            
        return inventory
        
    
    def show_selected_item(self, inventory, screen):#draws currently selected item over status bar
        blit_coord = (11, 453)
        count_coord = (17, 461)
        if inventory[self.slot][0] != 'empty':
            screen.blit(self.item_img_dict[inventory[self.slot][0]], blit_coord)
            item_count = str(inventory[self.slot][1])
            if int(item_count) < 10:
                item_count = ' ' + item_count
            screen.blit(self.fontlist[1].render(item_count, True, (255,255,255)), count_coord)
            
    def toggle_inv_slot(self, rate):#hold toggle inv key
        if self.inv_toggle_timer + rate < pygame.time.get_ticks():
            self.toggle_inv_slot_once()
            
    def toggle_inv_slot_once(self):#press toggle inv key once
        if self.slot < self.total_slots - 1:
            self.slot += 1
        else:
            self.slot = 0
        self.inv_toggle_timer = pygame.time.get_ticks()
        
    def press_use_item_btn(self, inventory):
        item_can_be_used = False
        if (inventory[self.slot][1] > 0 
            and self.item_details0.get_item_class(inventory[self.slot][0]) != 'Key'
            and inventory[self.slot][0] in self.item_details0.sub_function_dict
            ):#add some additional logic for key items
            self.item_to_use = inventory[self.slot][0]
            item_can_be_used = True

        return item_can_be_used
            
    def discard_item(self, inventory):
        if inventory[self.slot][1] > 0:
            inventory[self.slot][1] -= 1
            
        if inventory[self.slot][1] == 0:
            inventory[self.slot][0] = 'empty'
            
    def discard_slot(self, inventory):
        inventory[self.slot] = ['empty', 0]
        
    #will be called constantly   
    def open_inventory(self, inventory, charring, screen, ctrl_list):
        
        if self.trigger_once:#will be set to true again by either escape or inventory key
            self.temp_inventory = []
            
            #CREATE A DEEP COPY OF INVENTORY
            #for lists in lists you have to copy each sub list by element as well
            for slot in inventory:
                temp_list = []
                for element in slot:
                    temp_list.append(element)
                self.temp_inventory.append(temp_list)
                
            #set current item to use
            self.item_to_use = inventory[self.slot][0]

            #deploy buttons
            self.size = 0
            self.button_list *= 0
            self.button_list2 *= 0
            
            for i in range(self.rows):
                for j in range(self.cols):
                    self.button_list.append(Button(32*j + self.inv_disp[0], 32*i + self.inv_disp[1], self.inventory_btn, 1))
                    self.button_list2.append(Button(32*j + 8 + self.inv_disp[0], 32*i + 8 + self.inv_disp[1], self.item_img_dict[inventory[i*self.cols + j][0]], 1))
                    self.size += 1
                    
            #create a final inventory slot that's set out from the rest
            self.button_list.append(Button(self.isolated_slot_pos[0], self.isolated_slot_pos[1], self.inventory_btn, 1))
            self.button_list2.append(Button(self.isolated_slot_pos[0] + 8, self.isolated_slot_pos[1] + 8, self.item_img_dict[inventory[len(inventory) - 1][0]], 1))
            self.size += 1
            
            for btn in self.button_list2: #disable hover button highlighting for items
                btn.img_highlight_en = False
                            
            self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 +64 +16, self.generic_img, 1))
            self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 +64 +56, self.generic_img, 1))
            self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 +64 +96, self.generic_img, 1))
            self.button_list.append(Button(2, 2, self.invisible_img, 1))
            
            self.trigger_once = False
            
        if not self.trigger_once:
            #draw shaded bg
            screen.blit(self.inv_bg, (0,0))
            screen.blit(self.aria_frame_list[0], (-40,0))
            
            #draw item description box
            pygame.draw.rect(screen, (24,23,25), (self.S_W//2, self.S_H//2 - 160, 304, 224))
            pygame.draw.rect(screen, (38,37,41), (self.S_W//2 + 2, self.S_H//2 - 158, 300, 220))
            
            #draw char box
            self.text_manager0.disp_text_box(screen, self.fontlist[1], ('Bodily Charring: ' + str(100*charring)[0:8] + '%',),
                                             (-1,-1,-1), (200,200,200), (self.S_W//2 + 4, self.S_H//2 - 226, 0, 0), False, False, 'none')
            pygame.draw.rect(screen, (24,23,25), (self.S_W//2, self.S_H//2 - 208, 304, 34))
            pygame.draw.rect(screen, (38,37,41), (self.S_W//2 + 2, self.S_H//2 - 206, 300, 30))
            pygame.draw.rect(screen, (0,0,0), (self.S_W//2 + 3, self.S_H//2 - 204, 298, 26))
            pygame.draw.rect(screen, (255,0,86), (self.S_W//2 + 3, self.S_H//2 - 204, 298*charring, 26))
            
            #draw 2nd textbox
            status_str = [f'Sprint Unlocked: {'Worn Knee Socks' in [x[0] for x in inventory]}',]
            self.text_manager0.disp_text_box(screen, self.fontlist[1], status_str, 
                                             (-1,-1,-1), (200,200,200), (self.S_W//2 + 64 + 16, self.S_H//2 +64 +24,0,0), False, False, 'none')
            
            #set up and draw text
            item_class = self.item_details0.get_item_class(inventory[self.slot][0])

            item_details = ['Slot: ' + inventory[self.slot][0],
                            'Count: ' + str(inventory[self.slot][1]),
                            'Item Class: ' + item_class,
                            'Description: ',
                            ' '
                            ]
            
            item_description = self.item_details0.get_formatted_description(inventory[self.slot][0])#string list
            for line in item_description:
                item_details.append(line)#add to the established stringlist
                
            
            self.text_manager0.disp_text_box(screen, self.fontlist[1], item_details,
                                             (-1,-1,-1), (200,200,200), (self.S_W//2 + 4, self.S_H//2 - 158, 220, 188), False, False, 'none')
            
            self.text_manager0.disp_text_box(screen, self.fontlist[1], ('Exit:[' + pygame.key.name(ctrl_list[8]) + '] or [Esc]', ''), 
                                             (-1,-1,-1), (100,100,100), ((480 - 8*len(pygame.key.name(ctrl_list[8]))), 456, 32, 32), False, False, 'none')
            
            #buttons and drawing buttons--------------------------------------------------------------------------------------
            
            #highlighting selected inventory slot
            self.button_list[self.slot].draw_border(screen)
            
            if not self.help_open:
                #selecting the current slot
                for slot in self.button_list[0:self.size]:
                    if slot.draw(screen):
                        self.play_click_sound()
                        self.slot = self.button_list.index(slot)
                        
                #draw items in slots
                for btn in self.button_list2:
                    btn.draw(screen)
                    if inventory[self.button_list2.index(btn)][0] != 'empty':
                        item_count = str(inventory[self.button_list2.index(btn)][1])
                        if int(item_count) < 10:
                            item_count = ' ' + item_count
                        btn.show_text(screen, self.fontlist[1], ('', item_count))
                
                #use button
                self.use_item_btn_output = False
                if self.button_list[len(self.button_list)-4].draw(screen):
                    self.play_click_sound()
                    self.use_item_btn_output = True

                self.button_list[len(self.button_list)-4].show_text(screen, self.fontlist[1], ('','Use Item'))
                
                #discard button
                if self.button_list[len(self.button_list)-3].draw(screen):
                    self.play_click_sound()
                    self.discard_item(inventory)

                self.button_list[len(self.button_list)-3].show_text(screen, self.fontlist[1], ('','Discard'))
                
                #discard slot button
                if self.button_list[len(self.button_list)-2].draw(screen):
                    self.play_click_sound()
                    self.discard_slot(inventory)

                self.button_list[len(self.button_list)-2].show_text(screen, self.fontlist[1], ('','Discard Slot'))
            
            #blit help screen here
            else:
                pygame.draw.rect(screen, (0,0,0), (0, 0, self.S_W, self.S_H))
                ctrl_listk = []
                for key in ctrl_list:
                    ctrl_listk.append(pygame.key.name(key))
                inventory_tips = (
                    '',
                    '',
                    '',
                    'Toggle selected inventory slot:',
                    f'   -Press or hold [{ctrl_listk[8]}] while holding [{ctrl_listk[7]}].',
                    '',
                    '   OR while inventory is open:',
                    '      -Click any inventory slot.',
                    f'      -Use directional keys [UP, LEFT, DOWN, RIGHT].',
                    '',
                    'Moving Items:',
                    f'   -Use directional keys [UP, LEFT, DOWN, RIGHT] while holding [{ctrl_listk[7]}].',
                    '',
                    'Using Items:',
                    '   -Click Use Item button.',
                    f'   -Press [{ctrl_listk[9]}].',
                    '',
                    'Discarding Items:',
                    '   -Click Discard or Discard Slot button.',
                    f'   -Press [{ctrl_listk[4]}] to discard 1 item.', 
                    f'   -Press [{ctrl_listk[4]}] while holding [{ctrl_listk[7]}] to discard a whole slot.'
                )
                
                self.text_manager0.disp_text_box(screen, self.fontlist[1], inventory_tips,
                                             (-1,-1,-1), (200,200,200), (32, 32, 630, 480), False, False, 'none')
                
            
            
            #help button
            if self.button_list[len(self.button_list)-1].draw(screen):
                self.play_click_sound()
                self.help_open = not self.help_open
                if self.help_open:
                    self.help_btn_str = '[Close Tips]'
                else:
                    self.help_btn_str = '[Open Tips]'

            self.button_list[len(self.button_list)-1].show_text(screen, self.fontlist[1], ('',self.help_btn_str))
        
        #test for if the items in inventory changed
        for i in range(len(inventory)):
            if inventory[i][0] != self.temp_inventory[i][0]:
                self.trigger_once = True
        
        
    def close_inventory(self):
        self.help_open = False
        self.help_btn_str = '[Open Tips]'
        self.use_item_btn_output = False
        self.temp_inventory *= 0
        self.button_list *= 0
        self.trigger_once = True

class item_details():#helper class for getting and formatting item descriptions and attributes
    def __init__(self):
        self.t = textfile_formatter()
        self.sub_function_dict = self.t.str_list_to_dict(self.t.read_text_from_file(os.path.join(config_path, 'item_subfunctions.txt')), 'list')
        self.item_desc_dict = self.t.str_list_to_dict(self.t.read_text_from_file(os.path.join(config_path, 'item_descriptions.txt')), 'true_list')
        
        self.f_item_desc_dict = self.format_desc_dict(self.item_desc_dict, 36)
        
    def format_desc_dict(self, input_dict, limit):
        temp_list = []
        for key in input_dict:
            str_list = self.t.split_string(input_dict[key][1], limit, (',', '.', ' ', ':', ';', '-'))
            temp_list.append([key, str_list])
            
        return dict(temp_list)
        
    def get_item_class(self, item_id):
        if item_id in self.item_desc_dict:
            item_class = self.item_desc_dict[item_id][0]
        else:
            item_class = ' '
        return item_class
    
    def get_formatted_description(self, item_id):
        if item_id in self.f_item_desc_dict:
            f_description = self.f_item_desc_dict[item_id]
        else:
            f_description = ('')
            
        return f_description
            

class trade_menu_ui():
    #LIMITATIONS:
    #CANNOT HAVE 2 DIFFERENT PRICES FOR THE SAME ITEM
    def __init__(self, total_slots, fontlist, SCREEN_WIDTH, SCREEN_HEIGHT, ts, ini_vol):
        m_player_sfx_list_main = ['roblox_oof.mp3', 'hat.mp3', 'woop.mp3']
        self.m_player = music_player(m_player_sfx_list_main, ini_vol)

        self.total_slots = total_slots
        self.trigger_once = True
        
        self.fontlist = fontlist
        self.button_list = []
        self.button_list2 = [] #for displaying inventory items
        self.button_list3 = []
        self.button_list4 = [] #for displaying inventory items
        
        self.btn_list_list = [
            self.button_list,
            self.button_list2,
            self.button_list3,
            self.button_list4
        ]
        
        self.S_W = SCREEN_WIDTH
        self.S_H = SCREEN_HEIGHT
        
        self.temp_inventory = []
        
        self.slot = 0
        self.selected_group = 0
        
        #load ui images
        self.generic_img = pygame.image.load('assets/sprites/generic_btn.png').convert_alpha()
        self.invisible_img = pygame.image.load('assets/sprites/invisible_btn.png').convert_alpha()
        self.inventory_btn = pygame.image.load('assets/sprites/inventory_btn.png').convert_alpha()
        self.inv_bg = pygame.image.load('assets/sprites/pause_bg.png').convert_alpha()
        
        self.frame_index = 0
        self.frame_list = []
        self.all_frame_list = []
        for i in range (len(os.listdir(f'assets/sprites/misc_art/trade'))):
            self.all_frame_list.append(pygame.image.load(f'assets/sprites/misc_art/trade/{i}.png').convert_alpha())
        
        self.inv_disp = (16,370) #initial position for first slot
        self.text_manager0 = text_manager(SCREEN_WIDTH, SCREEN_HEIGHT, ts)
     
        
        #loading item images into a dictionary
        item_img_list = []
        for item in os.listdir(item_sprites_path):
            item_img_list.append([item[0:len(item)-4], pygame.image.load(os.path.join(item_sprites_path, f'{item}')).convert_alpha()])#-4 to remove '.png'
            
        self.item_img_dict = dict(item_img_list)
        
        self.item_details0 = item_details()
        
        self.t = textfile_formatter()
        path2 = 'assets/config_textfiles/item_config'
        self.base_prices_dict = self.t.str_list_to_dict(self.t.read_text_from_file(os.path.join(path2, 'item_base_prices.txt')), 'list_list')
        
        self.transaction_msg = ''
        self.transaction_msg_timer = pygame.time.get_ticks()
        
        self.show_prices = True
        self.wares = [
            ['a', 'none'], 
            ['b', 'none'], 
            ['c', 'none'],
            ['d', 'none'],
            ['e', 'none'],
            ['f', 'none'],
            ['g', 'none'],
            ['i', 'none'],
            ['empty', 'none'],
            ['empty', 'none']
        ]
        self.next_dialogue_index = -3
        self.exit_index = 0
        self.enabled = False
        
    def play_click_sound(self):
        self.m_player.play_sound(self.m_player.sfx[1], None)
        
    def adjust_cost(self, cost, curr_product_ct, pricing_type):
        if pricing_type == 'double':
            cost = cost*(2**curr_product_ct)
        return cost
        
    #Disclaimer: won't stack if the get_tot_itm_ct + product_amnt is just bigger than max edge case
    def trade_item(self, inventory, product, pricing_type):
        #implement on-spot price changing here
        #returns signals for why the player cannot afford something, defaults below
        target_slot = -1
        too_expensive = 1
        product_amnt = 0
        if product in self.base_prices_dict:
            product_amnt = self.base_prices_dict[product][0][1]
        
        #check if player has space in inventory, change the slot accordingly
        #check for stacking
        slot_list_p = self.sort_list(self.check_for_item2(product, inventory), -1)
        curr_product_ct = self.get_tot_itm_ct(slot_list_p)

        if (len(slot_list_p) * max_item_count) >= (curr_product_ct + product_amnt):
            target_slot = -2 #signal to stack
        else:#check for empty space
            target_slot = self.find_empty_slot()
        
        #check for item price
        if product_amnt > 0:
            #search for if the player has the items needed
            can_afford = []
            for payment_partition in self.base_prices_dict[product]:
                if payment_partition[0] != 'amount':
                    cost = self.adjust_cost(payment_partition[1], curr_product_ct, pricing_type)
                    can_afford.append(self.get_tot_itm_ct(self.check_for_item2(payment_partition[0], inventory)) >= cost) #player can afford  
                
            #charge player and give the player the product
            if False not in can_afford: 
                too_expensive = -1
                
            if target_slot != -1 and too_expensive != 1:
                #charge items
                for payment_partition in self.base_prices_dict[product]:
                    if payment_partition[0] != 'amount':
                        cost = self.adjust_cost(payment_partition[1], curr_product_ct, pricing_type)
                        for slot_pair in self.sort_list(self.check_for_item2(payment_partition[0], inventory), 1):
                            #discard items from slots where the target item was found until cost is met
                            while inventory[slot_pair[0]][1] > 0 and cost > 0:
                                self.discard_item(inventory, slot_pair[0])
                                cost -= 1
                            if cost == 0:
                                break

                #give item 
                if target_slot != -2:#no stacking
                    inventory[target_slot][0] = product
                    inventory[target_slot][1] += product_amnt
                else:#stacking
                    amnt_to_give = product_amnt
                    for slot_pair in [slot_pair for slot_pair in slot_list_p if slot_pair[1] < max_item_count]:#exclude full slots
                        #fill the first stackable slot until unable or amnt runs out
                        while inventory[slot_pair[0]][1] < max_item_count and amnt_to_give > 0: 
                            inventory[slot_pair[0]][1] += 1
                            amnt_to_give -= 1
                        if amnt_to_give == 0:#finish
                            break

        else:
            target_slot = -1

        return (target_slot, too_expensive)
    
    def get_transaction_msg(self, transaction_output):
        if transaction_output[0] == -1 and transaction_output[1] == 1:
            rtn_str = 'Item Not Available!'
        elif transaction_output[0] == -1:
            rtn_str = 'Inventory Full!!'
        elif transaction_output[1] == 1:
            rtn_str = 'Insufficient Funds!!'
        else:
            rtn_str = 'Transaction Success!'
            
        return rtn_str
        
    def check_for_item2(self, item_name, inventory):#returns how many of an item the player has in their inventory, default/item not found is 0
        # count = 0
        # slot_index = -1
        
        #slot_candidates = []#fill list of inventory slots with matching item names
        # for slot in enumerate(inventory):
        #     if slot[1][0] == item_name:
        #         slot_index = slot[0]
        #         count = slot[1][1]
        #         slot_candidates.append((slot_index, count))
        
        return [(slot[0], slot[1][1]) for slot in enumerate(inventory) if slot[1][0] == item_name]#slot_candidates
    
    def get_tot_itm_ct(self, slot_list):
        total_items = 0
        for slot in slot_list:
            total_items += slot[1]
        return total_items
    
    #bubble sort
    def sort_list(self, input_list, direction):#this destroys the original list
        sorted_l = []#create temp list
        runs = len(input_list)#get number of runs
        for i in range(runs):
            target = input_list[0]
            for i in range(len(input_list)):
                if direction > 0 and input_list[i][1] < target[1]:
                    target = input_list[i]
                elif direction < 0 and input_list[i][1] > target[1]:
                    target = input_list[i]
            sorted_l.append(target)
            input_list.pop(input_list.index(target))#remove the target element from the original list
            
        return sorted_l
        
    
    def find_empty_slot(self):
        rtn_slot = -1
        for slot in enumerate(self.temp_inventory):
            if slot[0] < self.total_slots and slot[1][0] == 'empty':#not the last slot
                rtn_slot = slot[0]
        return rtn_slot
        
    def discard_item(self, inventory, slot):
        if inventory[slot][1] > 0:
            inventory[slot][1] -= 1
            
        if inventory[slot][1] == 0:
            inventory[slot][0] = 'empty'
            
    def discard_slot(self, inventory, slot):
        inventory[slot] = ['empty', 0]
    
    def open_trade_ui(self, inventory, trade_key, screen, ctrl_list):
        
        if self.trigger_once:#will be set to true again by either escape or inventory key
            self.enabled = True
            #set wares
            if trade_key != 'test':
                path2 = 'assets/config_textfiles/trade_config'
                trade_data = self.t.str_list_to_list_list(self.t.read_text_from_file(os.path.join(path2, trade_key + '.txt')))
                #first sublist in trade data is reserved for ordered non-item data:
                #[exit index, start frame, end frame]
                self.wares = trade_data[1: len(trade_data)]
                self.exit_index = trade_data[0][0]
                self.frame_list = self.all_frame_list[trade_data[0][1]:trade_data[0][2] + 1]
                #print(self.wares)
            else:
                self.frame_list = self.all_frame_list[0:3]#default to mars' frames
                
            self.temp_inventory = []
            
            #CREATE A DEEP COPY OF INVENTORY
            #for lists in lists you have to copy each sub list by element as well
            for slot in inventory:
                temp_list = []
                for element in slot:
                    temp_list.append(element)
                self.temp_inventory.append(temp_list)
                
            #set current item to use
            self.item_to_use = inventory[self.slot][0]

            #deploy buttons
            for btn_list in self.btn_list_list:
                btn_list *= 0
            
           
            for i in range(self.total_slots):
                #button lists for inventory
                self.button_list.append(Button(32*i + self.inv_disp[0], self.inv_disp[1], self.inventory_btn, 1))
                self.button_list2.append(Button(32*i + 8 + self.inv_disp[0], 8 + self.inv_disp[1], self.item_img_dict[inventory[i][0]], 1))
                
                #button lists for self.wares
                self.button_list3.append(Button(32*i + self.inv_disp[0], self.inv_disp[1] - 48, self.inventory_btn, 1))
                self.button_list4.append(Button(32*i + 8 + self.inv_disp[0], 8 + self.inv_disp[1] - 48, self.item_img_dict[self.wares[i][0]], 1))
                
            for btn in self.button_list2: #disable hover button highlighting for items
                btn.img_highlight_en = False
                
            for btn in self.button_list4: 
                btn.img_highlight_en = False
                            
            self.button_list.append(Button(self.S_W//2 +88, self.S_H//2 +64 +16, self.generic_img, 1)) #trade button
            self.button_list.append(Button(self.S_W//2 +88, self.S_H//2 +64 +56, self.generic_img, 1))
            self.button_list.append(Button(self.S_W//2 +88, self.S_H//2 +64 +96, self.generic_img, 1))
            self.button_list.append(Button(self.S_W//2 - 8, self.S_H//2 -160 - 28, self.invisible_img, 1))
            self.button_list.append(Button(self.S_W//2 - 64, self.S_H - 48, self.generic_img, 1))
            
            self.next_dialogue_index = -3
            
            self.trigger_once = False
            
                    
        if not self.trigger_once:
            #draw shaded bg
            screen.blit(self.inv_bg, (0,0))
            #draw frame
            screen.blit(self.frame_list[self.frame_index], (0,0))
            
            #draw item description box
            pygame.draw.rect(screen, (24,23,25), (self.S_W//2, self.S_H//2 - 160, 304, 224))
            pygame.draw.rect(screen, (38,37,41), (self.S_W//2 + 2, self.S_H//2 - 158, 300, 220))
            
            #set up and draw text
            if self.selected_group == 0: #get description for the right group
                item_interface = inventory
                item_btn_list = self.button_list
                item_count = str(inventory[self.slot][1])
                cost_str = []
                item_type_str = 'Slot: '
            else:
                item_interface = self.wares
                item_btn_list = self.button_list3
                item_type_str = 'Product: '
                if self.wares[self.slot][0] not in self.base_prices_dict:
                    cost_str = []
                    item_count = '0'
                else:
                    cost_str = []
                    item_count = str(self.base_prices_dict[self.wares[self.slot][0]][0][1])
                    for sublist in self.base_prices_dict[self.wares[self.slot][0]]:
                        if sublist[0] == 'amount':
                            cost_str.append('')
                            cost_str.append('Price:')
                        else:
                            cost = self.adjust_cost(sublist[1], self.get_tot_itm_ct(self.check_for_item2(self.wares[self.slot][0], inventory)), self.wares[self.slot][1])
                            cost_str.append(f'  {sublist[0]}: {str(cost)}')
               
            item_details = [item_type_str + item_interface[self.slot][0],
                            'Count: ' + item_count
                            ]
            
            if not self.show_prices or self.selected_group == 0:
                item_details = item_details + ['Item Class: ' + self.item_details0.get_item_class(item_interface[self.slot][0]),
                                                'Description: ',
                                                ' '
                                                ]
                item_description = self.item_details0.get_formatted_description(item_interface[self.slot][0])#string list
                for line in item_description:
                    item_details.append(line)#add to the established stringlist
            else:
                item_details = item_details + cost_str
                
            self.text_manager0.disp_text_box(screen, self.fontlist[1], item_details,
                                             (-1,-1,-1), (200,200,200), (self.S_W//2 + 4, self.S_H//2 - 158, 220, 188), False, False, 'none')
            
            self.text_manager0.disp_text_box(screen, self.fontlist[1], ('Exit:[Esc]', ''), 
                                             (-1,-1,-1), (100,100,100), ((548), 456, 32, 32), False, False, 'none')
            
            self.text_manager0.disp_text_box(screen, self.fontlist[1], ('My Wares',),
                                             (-1,-1,-1), (200,200,200), (16, 296, 32, 32), False, False, 'none')
            
            self.text_manager0.disp_text_box(screen, self.fontlist[1], ('Your Stuff',),
                                            (-1,-1,-1), (200,200,200), (16, 410, 32, 32), False, False, 'none')
            
            if self.transaction_msg_timer + 2500 > pygame.time.get_ticks():
                if self.transaction_msg_timer + 2000 > pygame.time.get_ticks():#flicker
                    self.text_manager0.disp_text_box(screen, self.fontlist[2], (self.transaction_msg,),
                                                (-1,-1,-1), (200,200,200), (16, 8, 32, 32), False, False, 'none')
                else:
                    if pygame.time.get_ticks()%3 == 0:
                        self.text_manager0.disp_text_box(screen, self.fontlist[2], (self.transaction_msg,),
                                                (-1,-1,-1), (200,200,200), (16, 8, 32, 32), False, False, 'none')
            
            #buttons and drawing buttons--------------------------------------------------------------------------------------
            
            #highlighting selected inventory slot
            item_btn_list[self.slot].draw_border(screen)
            
            #selecting the current slot
            for btn_list in enumerate((self.button_list, self.button_list3)):
                for slot in btn_list[1][0:self.total_slots]:
                    if slot.draw(screen):
                        self.play_click_sound()
                        self.slot = btn_list[1].index(slot)
                        self.selected_group = btn_list[0]
                    
            #draw items in slots
            for btn in self.button_list2:
                btn.draw(screen)
                if inventory[self.button_list2.index(btn)][0] != 'empty':
                    item_count = str(inventory[self.button_list2.index(btn)][1])
                    if int(item_count) < 10:
                        item_count = ' ' + item_count
                    btn.show_text(screen, self.fontlist[1], ('', item_count))
                    
            for btn in self.button_list4:
                btn.draw(screen)
                if self.wares[self.button_list4.index(btn)][0] != 'empty':
                    item_count = str(self.wares[self.button_list4.index(btn)][1])
                    # if int(item_count) < 10:
                    #     item_count = ' ' + item_count
                    # btn.show_text(screen, self.fontlist[1], ('', item_count))
            
            #trade button
            if self.button_list[len(self.button_list)-5].draw(screen): #need to check for both inventory space and if the cost can be paid
                self.play_click_sound()
                if self.selected_group == 1:
                    self.transaction_msg = self.get_transaction_msg(self.trade_item(inventory, self.wares[self.slot][0], self.wares[self.slot][1]))
                    #reset timer for drawing transaction_msg
                    self.transaction_msg_timer = pygame.time.get_ticks()
                #change frame
                if self.frame_index < len(self.frame_list) - 1:
                    self.frame_index += 1
                else:
                    self.frame_index = 0

            self.button_list[len(self.button_list)-5].show_text(screen, self.fontlist[1], ('','Trade'))        

            #discard button
            if self.button_list[len(self.button_list)-4].draw(screen):
                self.play_click_sound()
                if self.selected_group == 0:
                    self.discard_item(inventory, self.slot)
            self.button_list[len(self.button_list)-4].show_text(screen, self.fontlist[1], ('','Discard'))
            
            #discard slot button
            if self.button_list[len(self.button_list)-3].draw(screen):
                self.play_click_sound()
                if self.selected_group == 0:
                    self.discard_slot(inventory, self.slot)
            self.button_list[len(self.button_list)-3].show_text(screen, self.fontlist[1], ('','Discard Slot'))
            
            #toggle description vs cost button
            if self.selected_group != 0:
                if self.show_prices:
                    btn_str = '[Show Description]'
                else:
                    btn_str = '[Show Cost]'
                if self.button_list[len(self.button_list)-2].draw(screen):
                    self.play_click_sound()
                    self.show_prices = not self.show_prices
                self.button_list[len(self.button_list)-2].show_text(screen, self.fontlist[1], ('', btn_str))
                
            #back button
            if self.button_list[len(self.button_list)-1].draw(screen):
                self.exit_to_dialogue()
            self.button_list[len(self.button_list)-1].show_text(screen, self.fontlist[1], ('','Back'))
            
        
        #test for if the items in inventory changed
        for i in range(len(inventory)):
            if inventory[i][0] != self.temp_inventory[i][0]:
                self.trigger_once = True
                
        return self.next_dialogue_index
    
    def exit_to_dialogue(self):
        self.next_dialogue_index = self.exit_index
                
    def close_trade_ui(self):
        self.temp_inventory *= 0
        self.trigger_once = True
        self.enabled = False
        self.next_dialogue_index = -3
        for btn_list in self.btn_list_list:
            btn_list *= 0

            
# item_details0 = item_details()
# print(item_details0.f_item_desc_dict)
# print(item_details0.get_formatted_description('test2'))

