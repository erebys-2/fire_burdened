import pygame
import os
import math
import copy
from button import Button 
from textManager import text_manager 
from music_player import music_player 

#Items exist in 2 spaces: level spaces and inventory spaces
#This file contains code to support an item existing in the level space and being able to interact with the player.
#Behaviors in inventory space involve keeping track of item count and apply status effects.

class Item(pygame.sprite.Sprite):
    def __init__(self, id, x, y, count):
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.image = pygame.image.load(f'sprites/items/{self.id}.png').convert_alpha()
        
        self.count = count
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        #self.rect.centery = y
        self.ini_y = y

        self.increment = 0
        
        self.is_key_item = False
        self.life_span = 5000
        self.initial_time = pygame.time.get_ticks()
        
        self.flip = False
        self.flicker = False
        
    def enable(self, player_rect, pause_game):
        #THE ORDER OF EXECUTION MATTERS FOR THIS METHOD
        disable = False
        
        #picking up item, might need to moved to a separate class
        if self.rect.colliderect(player_rect):# and pick_up_confirmation: #picking up item is not affected by pause game
            #disable = True
            pass
            
        elif not pause_game:#bob up and down
            self.rect.y -= math.sin(self.increment)
            #print(2*math.sin(self.increment))
            if self.increment < 6.283:
                self.increment += 0.1
            else:#reset position
                self.increment = 0
                self.rect.y = self.ini_y
                
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
            
            
    def disable(self):
        self.rect = (0,0,0,0)
        self.kill()

    def scroll_along(self, scrollx):
        self.rect.x += ( - scrollx)
        
    def draw(self, screen):
        if self.flicker:
            if pygame.time.get_ticks() % 2 == 0:
                screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        else:
            screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
            
            
class inventory_handler(): #handles setting up inventory, picking up items, and storing items
    #add on for player file
    def __init__(self, slot_count):
        self.slot_count = slot_count
        
        #create a limited list of lists
        self.inventory = []
        for i in range(self.slot_count):
            self.inventory.append(['empty', 0]) #[ID, count]
            i += 1

        #print(self.inventory)
            
    #will probably need a csv reader for this one somewhere along the process
    #used for loading inventory from save file        
    def load_saved_inventory(self, inventory):
        self.inventory = inventory
    
    def find_available_slot(self, item_id):
        slot_index = 0
        stacked = False
        allocated = False
        
        #first check if there's a slot with a matching item ID (item can stack)
        for slot in self.inventory:
            if slot[0] == item_id:
                slot_index = self.inventory.index(slot)
                stacked = True
                break
                
        #then check for the next available slot (item can be allocated to another slot)
        if slot_index == 0 and not stacked: #slot with matching item id not found
            for slot in self.inventory:
                if slot == ['empty', 0]:
                    slot_index = self.inventory.index(slot)
                    allocated = True
                    break
        
        #then check if there's any empty slots at all, or if there's no items
        if slot_index == 0 and not allocated and not stacked:
            slot_index = -1 #do not pick up item, inventory full
                
        return slot_index
                
                
    #call this whenever the player collides with an item
    def pick_up_item(self, player_rect, item_group):
        for item in item_group:
            if player_rect.colliderect(item.rect):
                slot_index = self.find_available_slot(item.id)
                if slot_index != -1: #inventory not full
                    self.inventory[slot_index][0] = item.id
                    self.inventory[slot_index][1] += item.count
                    item.disable() #item is deleted on the player side by calling an internal method
                print(self.inventory)
                
                
class inventory_UI(): #handles displaying inventory and 
    def __init__(self, rows, cols, fontlist, SCREEN_WIDTH, SCREEN_HEIGHT, ini_vol):
        m_player_sfx_list_main = ['roblox_oof.wav', 'hat.wav']
        self.m_player = music_player(m_player_sfx_list_main, ini_vol)
        
        self.current_item_index = 0
        self.rows = rows
        self.cols = cols
        self.size = rows * cols
        self.trigger_once = True
        self.inventory_grid = []
        
        self.fontlist = fontlist
        self.button_list = []
        
        self.S_W = SCREEN_WIDTH
        self.S_H = SCREEN_HEIGHT
        
        self.temp_inventory = []
        self.temp_inv_2 = []
        self.slot = 0
        
        self.generic_img = pygame.image.load('sprites/generic_btn.png').convert_alpha()
        
        #load all items into a list
        item_img_list = []
        for item in os.listdir(f'sprites/items'):
            item_img_list.append([item[0:len(item)-4], pygame.image.load(f'sprites/items/{item}').convert_alpha()])
            
        #create dictionary
        #dictionaries are mutable btw!
        self.item_img_dict = dict(item_img_list)
        #print(self.item_img_dict)
        
        self.text_manager0 = text_manager()
        
    def clear_inventory(self, inventory):
        temp_inventory = inventory 
        for i in range(self.size):
            temp_inventory[i] = ['empty', 0]
            
        return temp_inventory
        
    #might not be used
    def format_into_grid(self, inventory):
        inventory_grid = []
        for i in range(self.rows):
            inventory_grid.append(inventory[i * self.cols: (i + 1) * self.cols])
            
        return inventory_grid
        
    #will be called constantly   
    def open_inventory(self, inventory, screen):
        
        if self.trigger_once:#will be set to true again by either escape or inventory key
            print("true")
            #self.temp_inventory = copy.deepcopy(inventory)
            self.temp_inventory = []
            
            #CREATE A DEEP COPY OF INVENTORY
            #for lists in lists you have to copy each sub list by element as well
            for slot in inventory:
                temp_list = []
                for element in slot:
                    temp_list.append(element)
                self.temp_inventory.append(temp_list)
            

                
            #self.slot = 0 #set current inventory slot to 0
            #deploy buttons
            #the locations of these buttons are probably gonna be giga fucked first execution
            self.button_list *= 0
            
            for i in range(self.rows):
                for j in range(self.cols):
                    self.button_list.append(Button(32*j , 24*i*self.cols, self.item_img_dict[inventory[i*self.cols + j][0]], 1))
                    
            self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 +64 +36, self.generic_img, 1))
            self.button_list.append(Button(self.S_W//2 -64, self.S_H//2 +64 +64, self.generic_img, 1))
            
            self.trigger_once = False
            
        if not self.trigger_once:
            
            #selecting the current slot
            for slot in self.button_list[0:self.size]:
                if slot.draw(screen):
                    self.slot = self.button_list.index(slot)
            
            #use button---------------------------------------------------------------------------------------------
            if self.button_list[len(self.button_list)-2].draw(screen):
                self.m_player.play_sound(self.m_player.sfx[1])
                if inventory[self.slot][1] > 0:
                    inventory[self.slot][1] -= 1
                    
                if inventory[self.slot][1] == 0:
                    inventory[self.slot][0] = 'empty'
                print(inventory)

            self.button_list[len(self.button_list)-2].show_text(screen, self.fontlist[1], ('','Use Item'))
            
            #discard button-----------------------------------------------------------------------------------
            if self.button_list[len(self.button_list)-1].draw(screen):
                self.m_player.play_sound(self.m_player.sfx[1])
                if inventory[self.slot][1] > 0:
                    inventory[self.slot][1] -= 1
                    
                if inventory[self.slot][1] == 0:
                    inventory[self.slot][0] = 'empty'
                print(self.slot)
            
            self.button_list[len(self.button_list)-1].show_text(screen, self.fontlist[1], ('','Discard'))
        
        #test for if the items in inventory changed
        for i in range(len(inventory)):
            if inventory[i][0] != self.temp_inventory[i][0]:
                self.trigger_once = True
        
        
    def close_inventory(self):
        self.temp_inventory *= 0
        self.button_list *= 0
        self.trigger_once = True

