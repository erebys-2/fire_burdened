import pygame
pygame.init()
import os
#music player class used for both playing music and sfx
#There will be one instance for each level/ location
#probably another for each enemy/ the player
class music_player():
    
    def __init__(self, sfx_list, initial_vol):
        pygame.mixer.init()
        
        #all sfx files for the game will be in one directory, 
        #whenever you instantiate a music player you need to pass in an 'sfx_list'
        #containing the names of the sound effects you want to use for that instantiation
        #(loading in every sound effect every time would be inefficient)
        
        #ex. (instantiation name) = music_player([(sfx list)])
        
        #to play a sound is just: (instantiation name).play_sound((instantiation name).sfx[(index)])
        
        #index is index in the list of sfx's representing a specific one
        
        #finding out where to play sounds in the files might be challenging, usually if you want to find
        #a signal that only happens once per action, look for an update action method
        
        #also check the particles file for things like explosions, in there you'd probably want to play_sound
        #in the constructor
        
        #see https://www.pygame.org/docs/ref/mixer.html#pygame.mixer
        #and https://www.youtube.com/watch?v=xdkY6yhEccA
        
        self.sfx = []
        for sound in sfx_list:
            sfx = pygame.mixer.Sound(f'sfx/{sound}')
            self.sfx.append(sfx)
        
        self.channel_count = 8
        self.channel_list = []
        pygame.mixer.set_num_channels(self.channel_count)
        for i in range(self.channel_count):
            channel = pygame.mixer.Channel(i)
            self.channel_list.append(channel)
        # pygame.mixer.set_reserved(1)
        # self.reserved_channel = pygame.mixer.Channel(self.channel_count)

        self.concurrent_sounds = 0

        self.eq_regime = (10,9,9,8,8,7,7,6,6)
       
        #self.SONG_END = pygame.USEREVENT + 1
        self.playing_music = False
        
        #set volumes of sounds at end of constructor
        for sound in self.sfx:
            if initial_vol[0] < 10: 
                pygame.mixer.Sound.set_volume(sound, initial_vol[0]*0.1)
            elif initial_vol[0] == 10:
                pygame.mixer.Sound.set_volume(sound, 0.9921875)
        
        
    #-------------------------------------------------------------adjusting volume------------------------
    def set_vol_all_sounds(self, level):
        for sound in self.sfx:
            self.set_sound_vol(sound, level[0])
            
    #--------------------------------------------------------------------equalizing-----------------------------------------
    def auto_equalize(self): #for setting volume, self.equalization_regime will have to be turned into a parameter passed in from game_window
        #check how many channels are being used
        
        self.concurrent_sounds = 0
        for channel in self.channel_list: 
            if channel.get_busy():
                self.concurrent_sounds += 1
                
        #linear volume adjustment based on num channels used
        #pygame cannot test if there's music playing across different instances
        # num = 0
        # if pygame.mixer.music.get_busy: #also factor in music
        #     num = 1
            #print("there is music playing")
        self.set_vol_all_channels(self.eq_regime[self.concurrent_sounds]-2)
                
        #when too many sounds are trying to play (espcially during a bullet spam) free up one channel   
        #works 9 times out of 10?    
        if self.concurrent_sounds == self.channel_count:
            self.channel_list[0].stop()
        
        #print(self.concurrent_sounds)
        

    #-------------------------------------------------------------------------playing sounds---------------------------------

    def play_song(self, file_name):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(f'music/{file_name}')
            pygame.mixer.music.play()
        else:
            pygame.mixer.music.stop()
        #print(pygame.mixer.music.get_busy())
        
    def play_sound(self, sound):
        #if update_eq, read from the csv file
        self.auto_equalize()
        pygame.mixer.Sound.play(sound)
        
    def stop_sound(self):
        pygame.mixer.stop()
    
    #---------------------------------------------------------------------setting volume------------------------------------------    
    #volume levels 0-10
    
    #music has its own channels, or maybe it doesn't ??
    def set_music_vol(self, level):
        if level < 10: 
            pygame.mixer.music.set_volume(level*0.1)
        elif level == 10:
            pygame.mixer.music.set_volume(0.9921875)

    #for channels
    def set_channel_vol(self, channel, level):
        if level < 10 and level >= 0: 
            channel.set_volume(level*0.1)
        elif level == 10:
            channel.set_volume(0.9921875)
        else:
            channel.set_volume(0)
            
    def set_vol_all_channels(self, level):
        #print(level)
        for channel in self.channel_list: 
            if channel.get_busy():
                self.set_channel_vol(channel, level)
                
    def set_vol_all_channels2(self, factor): #doesn't quite work when paired with auto equalize
        #print(level)
        for channel in self.channel_list: 
            if channel.get_busy():
                level = channel.get_volume()*factor
                self.set_channel_vol(channel, level)
                
    #for specific sounds
    def set_sound_vol(self, sound, level):
        if level < 10: 
            pygame.mixer.Sound.set_volume(sound, level*0.1)
        elif level == 10:
            pygame.mixer.Sound.set_volume(sound, 0.9921875)
        
#uncomment to test this particular file
# m_player = music_player(['roblox_oof.wav'])
# # m_player.play_song('newsong15')
# m_player.set_sfx_vol(m_player.sfx[0], 10)
# m_player.play_sound(m_player.sfx[0]) #if you paste this underneath, you end up playing it at the same time
# input('any key to exit')