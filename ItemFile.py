import pygame
import os
import math

#Items exist in 2 spaces: level spaces and inventory spaces
#This file contains code to support an item existing in the level space and being able to interact with the player.
#Behaviors in inventory space involve keeping track of item count and apply status effects.

class Item(pygame.sprite.Sprite):
    def __init__(self, id, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.image = pygame.image.load(f'sprites/items/{self.id}.png')
        
        
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        #self.rect.centery = y
        self.ini_y = y

        self.increment = 0
        
        self.is_key_item = False
        self.life_span = 5000
        self.initial_time = pygame.time.get_ticks()
        
        self.flip = False
        
    def enable(self, player_rect, pick_up_confirmation, pause_game):
        #THE ORDER OF EXECUTION MATTERS FOR THIS METHOD
        
        #picking up item, might need to moved to a separate class
        if self.rect.colliderect(player_rect):# and pick_up_confirmation:#picking up item is not affected by pause game
            self.disable()
            
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
            self.disable()
        elif pause_game and not self.is_key_item:
            self.life_span *= 0.7 #decreases the lifespan everytime game is paused otherwise items' lifespans will be restored by the line below
            self.initial_time = pygame.time.get_ticks()
            
            
    def disable(self):
        self.rect = (0,0,0,0)
        self.kill()

    def scroll_along(self, scrollx):
        self.rect.x += ( - scrollx)
        
    def draw(self, screen):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)