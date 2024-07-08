import pygame
import os
# from bullet import bullet_ #type: ignore
from particle import particle_ #type: ignore
from music_player import music_player #type: ignore
import random
 
#traps and puzzles and items

class npc(pygame.sprite.Sprite):
    #constructor
    def __init__(self, x, y, scale, direction, name, ini_vol, enabled, dialogue_array, index):
        pygame.sprite.Sprite.__init__(self)
        self.direction = direction
        self.name = name
        self.enabled = enabled
        self.scale = scale
        
        self.m_player = music_player(['mc_anvil.wav'], ini_vol)
        self.ini_vol = ini_vol
        
        start_index = dialogue_array.index((self.name, '-1'))
        self.dialogue_array = dialogue_array[start_index[0]]
        self.index = index