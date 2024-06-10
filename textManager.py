import pygame
from music_player import music_player #type: ignore
#methods regarding text boxes live here

class text_manager():
    def __init__(self):#constructor
        self.combined_str = ' '
        self.current_str_list = []
        self.run_once = False

        self.word_split_indice = [0]
        self.empty_str = ''
        self.internal_index = 0
        
        self.str_list_rebuilt = []
        self.disp_text_box_quit = False
        
        self.m_player_sfx_list = ['roblox_oof.wav', 'hat.wav']
        self.m_player = music_player(self.m_player_sfx_list)
        self.finished_typing = False
        
    #reset internal variables
    def reset_internals(self):
        self.combined_str = ' '

        self.word_split_indice = [0]
        self.empty_str = ''
        self.internal_index = 0

        self.str_list_rebuilt = []
        
        
    #create combined string from string list
    def build_combined_str(self, str_list, close_text_box):
        if not self.run_once:#only build the combined string once
            self.current_str_list = str_list
            
            for line in str_list:
                self.combined_str = self.combined_str + line + '\n' 
                  
            self.run_once = True
        
        if self.current_str_list != str_list or close_text_box: #reset signal is triggered by inputting a different string list
            self.run_once = False
            self.reset_internals()
        
        return self.combined_str
    
    
    #rebuilds a list of strings from a combined string by character each call
    def copy_by_char2(self, str, break_):
        if str != self.empty_str and not break_:
            self.empty_str = self.empty_str + str[self.internal_index]#build self.empty_str by 1 char every cycle
            
            self.str_list_rebuilt = []
            
            if self.empty_str[self.internal_index] == '\n':
                self.word_split_indice.append(self.internal_index)
                
            #plays sound for letters
            if self.empty_str[self.internal_index] != '\n' and self.empty_str[self.internal_index] != ' ': 
                self.m_player.play_sound(self.m_player.sfx[1])
            
            for i in range(len(self.word_split_indice)-1):#separating full words
                tup = (self.word_split_indice[i]+1, self.word_split_indice[i+1])
                self.str_list_rebuilt.append(self.empty_str[tup[0]:tup[1]])
            
            tup2 = (self.word_split_indice[len(self.word_split_indice)-1]+1, self.internal_index)#trailing characters
            if tup2[0] != tup2[1]:
                self.str_list_rebuilt.append(self.empty_str[tup2[0]:tup2[1]])
                
            self.internal_index += 1
            
        elif break_:
            self.str_list_rebuilt = self.current_str_list
            
        return self.str_list_rebuilt
    
    
    #displays a list of strings
    def disp_text_box(self, screen, font, text, color, text_color, box, type_out, type_out_en, alignment): #box contains the coords in the first 2 variables
        self.disp_text_box_quit = False
        #this needs to be set to True after this method is finished being called during its duration
        #though it isn't functional right now, what happens is that text boxes only get typed out once if the same text is fed in
        #...which isn't a bad thing
        
        #textbox bg
        if color != (-1,-1,-1):
            pygame.draw.rect(screen, color, box)

        #text positioning
        if alignment == 'centered': #not actually centered LMAO
            x = screen.get_width()//2 -64
        else:
            x = box[0]
        y = box[1]


        if type_out:
            if type_out_en:#this is set to true per several game ticks
                str_list = self.copy_by_char2(self.build_combined_str(text, self.disp_text_box_quit), not type_out)# kind of redundant to set str_list but it does the job
            str_list = self.str_list_rebuilt
        else:
            str_list = text
        #draws text here

        dx = x
        dy = y
        
        for line in str_list:
            #process characters
            # if type_out:#by character #can be further investigated for text effects like shaking or smth
            #     dx = x#resets x coord of letter per line when typing by character
                
            #     for char in line:
            #         screen.blit(font.render(char, True, text_color), (dx, dy))
            #         dx += 8 #dependent on font size and type, change later maybe

            # else:#by line
            screen.blit(font.render(line, True, text_color), (dx, dy))
            dy += 17

        return True

    
    
# #comment out later
# #----------------------variables for testing
# str_list = [
#     'hello',
#     'world',
#     'mofo',
#     ]
# str_list2 = [
#     'suck',
#     'my fat',
#     'cock'    
# ]

# #---------------------------------main-------------------------------------
# text_manager0 = text_manager()

# for i in range(20):
#     print(text_manager0.copy_by_char2(text_manager0.build_combined_str(str_list, False), False))
# print("switching string list")
# for i in range(20):
#     if i < 10:
#         break_ = False
#     else:
#         break_ = True
#     print(text_manager0.copy_by_char2(text_manager0.build_combined_str(str_list2, False), break_))
