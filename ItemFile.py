import pygame
import os
import math

#Items exist in 2 spaces: level spaces and inventory spaces
#This file contains code to support an item existing in the level space and being able to interact with the player.
#Behaviors in inventory space involve keeping track of item count and apply status effects.

class Item(pygame.sprite.Sprite):
    def __init__(self, id, x, y, count):
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.image = pygame.image.load(f'sprites/items/{self.id}.png')
        
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
            
            
class inventory_handler():
    #add on for player file
    def __init__(self, slot_count):
        self.slot_count = slot_count
        
        #create a limited list of lists
        self.inventory = []
        for i in range(self.slot_count):
            self.inventory.append(['empty', 0]) #[ID, count]
            i += 1

        print(self.inventory)
            
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
                    