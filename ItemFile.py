import pygame
import os
import math
from button import Button 
from textManager import text_manager 
from music_player import music_player 

from textfile_handler import textfile_formatter
import random

config_path = 'config_textfiles/item_config'
item_sprites_path = 'sprites/items'

#Items exist in 2 spaces: level spaces and inventory spaces
#This file contains code to support an item existing in the level space and being able to interact with the player.
#Behaviors in inventory space involve keeping track of item count and apply status effects.

class Item(pygame.sprite.Sprite): #helper class with logic for item behavior outside of player inventory
    def __init__(self, id, x, y, count):
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
        
        self.is_key_item = False
        self.life_span = 5000
        self.initial_time = pygame.time.get_ticks()
        
        self.flip = False
        self.flicker = False
        
        self.gravitation_rect = pygame.rect.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
        self.gravitation_rect.scale_by_ip(6)

        
    def enable(self, player_rect, pause_game):
        #THE ORDER OF EXECUTION MATTERS FOR THIS METHOD
        disable = False
        
        #align rects
        self.gravitation_rect.center = self.rect.center
        
        #picking up item, might need to moved to a separate class
        if self.rect.colliderect(player_rect):# and pick_up_confirmation: #picking up item is not affected by pause game
            #disable = True
            pass
            
        elif not pause_game and not self.gravitate(player_rect):#bob up and down
            self.rect.centery = self.ini_y - 9*math.sin(self.increment)

            if self.increment > 2*math.pi:
                self.rect.centery = self.ini_y
                self.increment = 0
                
            self.increment += math.pi/24
                
        #player can get item data from the sprite group
        
        #despawning
        if not pause_game and not self.is_key_item and pygame.time.get_ticks() > self.initial_time + int(self.life_span):
            disable = True
        elif not pause_game and not self.is_key_item and pygame.time.get_ticks() > self.initial_time + int(0.8*self.life_span):
            self.flicker = True
        elif pause_game and not self.is_key_item:
            #self.life_span *= 0.7 #decreases the lifespan everytime game is paused otherwise items' lifespans will be restored by the line below
            self.initial_time = pygame.time.get_ticks()
            
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
            
    #will probably need a csv reader for this one somewhere along the process
    #used for loading inventory from save file        
    def load_saved_inventory(self, inventory):
        self.inventory = inventory
    
    def find_available_slot(self, item_id):
        slot_index = 0
        stacked = False
        allocated = False
        
        #first check if there's a slot with a matching item ID (item can stack) and that the max count (99) hasn't been reshced
        for slot in self.inventory:
            if slot[0] == item_id and slot[1] < 99:
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
        self.instant_heal_items_dict = t.str_list_to_dict(t.read_text_from_file(os.path.join(config_path, 'instant_heal_items_config.txt')), 'int')
        self.st_reduction_factor_dict = t.str_list_to_dict(t.read_text_from_file(os.path.join(config_path, 'st_reduction_factor_config.txt')), 'float')
        
        #make a separate dict for particles and sfx for each item used
    
    #make a signal processing function that will process an item usage request from inventory UI in game_window
    #have it be called in game window
    #possibly have it wrapped in an if statement for if the item usage request is being sent to avoid having to constantly pass the pointer to the player
    def process_use_signal(self, use_item_flag, item_id, player):
        #print(use_item_flag)
        item_was_used = False
        if use_item_flag: #and some internal variable in player indicating the animation finished
            item_was_used = self.use_item(item_id, player)
            use_item_flag = False
            
        return (use_item_flag, item_was_used)
        
    #I'm gonna have the player pass itself into this function to avoid having a huge amount of parameters
    #The drawback is a loss of modularity since I'll have to reference the specific variables in 'player'
    
    #note this can only deal with instant effects, persistent status effects probably need a separate class or function
    
    #however, another perk of passing the player is that this class has access to the player's music player, particles, and sounds
    
    #plain text file game/ game modular
    #recode this a little bit so that it uses more dictionaries with values that can be initially loaded thru a text file
    
    def use_item(self, item_id, player):
        if item_id in self.sub_function_dict:
            sub_function_tuple = self.sub_function_dict[item_id]
            item_was_used = True
        else:
            sub_function_tuple = ('nothing', 'nothing')
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

#=============================================================================================================================================  
#note: due to the implementation of a delay in the button file, the game will slow down whenever a button is pressed
#this is so for general menu navigating the mechanical signal of a click doesn't carry on when the next set of buttons is loaded in        
                
class inventory_UI(): #handles displaying inventory, item description and counts, and slot selection
    def __init__(self, rows, cols, fontlist, SCREEN_WIDTH, SCREEN_HEIGHT, ini_vol):
        m_player_sfx_list_main = ['roblox_oof.wav', 'hat.wav', 'woop.wav']
        self.m_player = music_player(m_player_sfx_list_main, ini_vol)

        self.rows = rows
        self.cols = cols
        self.size = 0
        self.trigger_once = True
        self.inventory_grid = []
        
        self.fontlist = fontlist
        self.button_list = []
        self.button_list2 = [] #for displaying inventory items
        
        self.S_W = SCREEN_WIDTH
        self.S_H = SCREEN_HEIGHT
        
        self.temp_inventory = []
        
        self.slot = 0
        
        self.generic_img = pygame.image.load('sprites/generic_btn.png').convert_alpha()
        self.inventory_btn = pygame.image.load('sprites/inventory_btn.png').convert_alpha()
        self.inv_bg = pygame.image.load('sprites/pause_bg.png').convert_alpha()
        self.aria_frame_list = []
        for i in range (len(os.listdir(f'sprites/misc_art/aria'))):
            self.aria_frame_list.append(pygame.image.load(f'sprites/misc_art/aria/{i}.png').convert_alpha())
        
        self.inv_disp = (160,128) #inventory displacement for displaying slot
        self.isolated_slot_pos = (192, self.inv_disp[1] + self.rows*32 + 32)
        self.text_manager0 = text_manager()
     
        
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
        
    def clear_inventory(self, inventory):
        temp_inventory = inventory 
        for i in range(self.size):
            temp_inventory[i] = ['empty', 0]
            
        return temp_inventory
        
    def press_use_item_btn(self, inventory):
        #print(self.slot)
        item_can_be_used = False
        if (inventory[self.slot][1] > 0 
            and not self.item_details0.is_key_item(inventory[self.slot][0]) 
            and inventory[self.slot][0] in self.item_details0.sub_function_dict
            ):#add some additional logic for key items
            #self.use_item_flag = True#sets internal flag to true
            self.item_to_use = inventory[self.slot][0]
            item_can_be_used = True
        #elif self.item_details0.is_key_item(inventory[self.slot][0]:
        
        return item_can_be_used
            
    def discard_item(self, inventory):
        if inventory[self.slot][1] > 0:
            inventory[self.slot][1] -= 1
            
        if inventory[self.slot][1] == 0:
            inventory[self.slot][0] = 'empty'
        
    #will be called constantly   
    def open_inventory(self, inventory, screen, inv_key):
        
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
                    #self.item_img_dict[inventory[i*self.cols + j][0]]
                    self.size += 1
                    
            #create a final inventory slot that's set out from the rest
            self.button_list.append(Button(self.isolated_slot_pos[0], self.isolated_slot_pos[1], self.inventory_btn, 1))
            self.button_list2.append(Button(self.isolated_slot_pos[0] + 8, self.isolated_slot_pos[1] + 8, self.item_img_dict[inventory[len(inventory) - 1][0]], 1))
            self.size += 1
                            
            self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 +64 +16, self.generic_img, 1))
            self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 +64 +56, self.generic_img, 1))
            
            self.trigger_once = False
            
        if not self.trigger_once:
            #draw shaded bg
            screen.blit(self.inv_bg, (0,0))
            screen.blit(self.aria_frame_list[0], (-40,0))
            
            #draw item description box
            pygame.draw.rect(screen, (24,23,25), (self.S_W//2, self.S_H//2 - 128, 224, 192))
            pygame.draw.rect(screen, (38,37,41), (self.S_W//2 + 2, self.S_H//2 - 126, 220, 188))
            
            #set up and draw text
            # print(len(inventory))
            # print(self.slot)
            is_key_item = self.item_details0.is_key_item(inventory[self.slot][0])

            item_details = ['Slot: ' + inventory[self.slot][0],
                            'Count: ' + str(inventory[self.slot][1]),
                            'Is Key Item: ' + str(is_key_item),
                            'Description: ',
                            ' '
                            ]
            
            item_description = self.item_details0.get_formatted_description(inventory[self.slot][0])#string list
            for line in item_description:
                item_details.append(line)#add to the established stringlist
                
            
            self.text_manager0.disp_text_box(screen, self.fontlist[1], item_details,
                                             (-1,-1,-1), (200,200,200), (self.S_W//2 + 4, self.S_H//2 - 124, 220, 188), False, False, 'none')
            
            self.text_manager0.disp_text_box(screen, self.fontlist[1], ('Exit:(' + pygame.key.name(inv_key) + ') or (esc)', ''), 
                                             (-1,-1,-1), (100,100,100), ((480 - 8*len(pygame.key.name(inv_key))), 456, 32, 32), False, False, 'none')
            
            #buttons and drawing buttons--------------------------------------------------------------------------------------
            
            #highlighting selected inventory slot
            self.button_list[self.slot].draw_border(screen)
            
            #selecting the current slot
            for slot in self.button_list[0:self.size]:
                if slot.draw(screen):
                    self.m_player.play_sound(self.m_player.sfx[1])
                    self.slot = self.button_list.index(slot)
                    #print(self.slot)
                    
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
            if self.button_list[len(self.button_list)-2].draw(screen):
                self.m_player.play_sound(self.m_player.sfx[1])
                #self.press_use_item_btn(inventory)
                self.use_item_btn_output = True

            self.button_list[len(self.button_list)-2].show_text(screen, self.fontlist[1], ('','Use Item'))
            
            #discard button
            if self.button_list[len(self.button_list)-1].draw(screen):
                self.m_player.play_sound(self.m_player.sfx[1])
                self.discard_item(inventory)

            self.button_list[len(self.button_list)-1].show_text(screen, self.fontlist[1], ('','Discard'))
        
        #test for if the items in inventory changed
        for i in range(len(inventory)):
            if inventory[i][0] != self.temp_inventory[i][0]:
                self.trigger_once = True
        
        
    def close_inventory(self):
        self.use_item_btn_output = False
        self.temp_inventory *= 0
        self.button_list *= 0
        self.trigger_once = True

class item_details():#helper class for getting and formatting item descriptions and attributes
    def __init__(self):
        self.t = textfile_formatter()
        self.sub_function_dict = self.t.str_list_to_dict(self.t.read_text_from_file(os.path.join(config_path, 'item_subfunctions.txt')), 'list')
        self.key_items = self.t.read_text_from_file(os.path.join(config_path, 'keyitems_list.txt')) #list of strings that are id's of key items
        self.item_desc_dict = self.t.str_list_to_dict(self.t.read_text_from_file(os.path.join(config_path, 'item_descriptions.txt')), 'none')
        
        self.f_item_desc_dict = self.format_into_str_list(self.item_desc_dict, 26)
        
    def format_into_str_list(self, input_dict, limit):
        temp_list = []
        for key in input_dict:
            str_list = self.t.split_string(input_dict[key], limit, (',', '.', ' ', ':', ';', '-'))
            temp_list.append([key, str_list])
            
        return dict(temp_list)
        
    def is_key_item(self, item_id):
        return item_id in self.key_items
    
    def get_formatted_description(self, item_id):
        if item_id in self.f_item_desc_dict:
            f_description = self.f_item_desc_dict[item_id]
        else:
            f_description = ('')
            
        return f_description
            

            
# item_details0 = item_details()
# print(item_details0.f_item_desc_dict)
# print(item_details0.get_formatted_description('test2'))

