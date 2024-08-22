import os
import csv

class csv_extracter():
    
    def __init__(self, cut_off_length):
        self.cut_off_length = cut_off_length
        self.endcase_char = (',', '.', ' ', ':', ';', '-')

    #reads csv file and fills a list with entries as strings    
    def read_npc_data(self, data_name):
        temp_list = []
        with open(f'npc_dialogue_files/{data_name}.csv', newline= '') as csvfile:
            reader = csv.reader(csvfile, delimiter= ',') #what separates values = delimiter
            for row in reader:
                for entry in row:
                    temp_list.append((entry))
                    
        return temp_list
    
    #takes a list of strings and converts it into a list of lists, splitting it at the splitter character '#'
    #in this case, an int will always follow a string after #, the int being the index to the next dialogue
    def format_to_listoflistoflists(self, str_list):
        destination_list = []
        temp_list = []
        start_index = 0
        end_index = 0
        
        #split strings into lists of strings and ints by the divider '#'
        for string in str_list:
            if string != '':
                
                break_index = self.get_break_index('#', string)
                list = [string[0:break_index], string[break_index+1:len(string)]]
                
                break_index2 = self.get_break_index('#', list[1])    
                list2 = [list[0], int(list[1][0:break_index2]), int(list[1][break_index2+1:len(list[1])])]
                
                temp_list.append(list2)
            
        #split list of lists by boundary ints -1 and -2
        for list in temp_list:
            if list[1] == -1:
                start_index = temp_list.index(list)
            if list[1] == -2:
                end_index = temp_list.index(list)
                
            if temp_list[start_index:end_index] != []:
                destination_list.append(temp_list[start_index:end_index])
            
        return destination_list
    
    #selects a listoflists from the listoflistoflists by character name and removes first element
    def select_npc_dialogue(self, name, input_list):
        destination_list = []
        for list in input_list:
            if list[0][0] == name:
                destination_list = list
                break
        destination_list.pop(0)
        return destination_list
    
    def get_break_index(self, special_char, string):
        break_index = 0
        for char in string:
            if char == special_char:
                break
            break_index+= 1
        
        return break_index
    
    def split_string(self, string_, limit, endcase_char):
        str_list = []
        if len(string_) > limit:
            #cut string into limit sized pieces and append them into a str list
            num_strings = len(string_)//limit
            i = 0
            for i in range(num_strings):
                string_to_append = string_[0+limit*(i):limit*(i+1)]
                
                #check against list of sentence splitting chars to add '-' when a word is split
                if (limit*(i+1) != len(string_) and 
                    all(string_[limit*(i+1)-1] != char and string_[limit*(i+1)] != char for char in endcase_char)
                    ):
                    string_to_append = string_to_append + '-'
                
                if string_to_append[0] == ' ':
                    string_to_append = string_to_append[1:len(string_to_append)]
                str_list.append(string_to_append)
            
            #append final length of string into the str list
            if limit*(i+1) != len(string_):
                string_to_append = string_[limit*(i+1):len(string_)]
                if string_to_append[0] == ' ':
                    string_to_append = string_to_append[1:len(string_to_append)]
                
                str_list.append(string_to_append)
        else:
            str_list.append(string_[0:len(string_)])
        str_list.append('')
        
        return str_list

    #formats the string in the list of lists into a string list that is compatible with textManager's methods 
    #will split a large string into segments as long as the provided length of the text box (in units of chars)
    #words have '-' added if split in the middle
    def str_to_str_list(self, input_list):
        destination_list = []
        for item in input_list:
           
            str_list = self.split_string(item[0], self.cut_off_length, self.endcase_char)
            destination_list.append((tuple(str_list),item[1],item[2]))
            
        return destination_list
        
    #used to format a raw csv reading into a list of npc dialogue lists
    #called once when processing a new level
    def get_all_npc_data(self, data_name):
        destination_list = self.format_to_listoflistoflists(self.read_npc_data(data_name))
        return destination_list

    #used to isolate a specific npc dialogue list and format it into a useable form for the textManager
    #called once per npc instantiation
    def get_specific_npc_data(self, name, input_array):
        destination_list = self.str_to_str_list(self.select_npc_dialogue(name, input_array))
        return destination_list
    
#there will be a single master dialogue csv loaded by the world world manager in its constructor
#it will be loaded and processed into individual lists for characters in the constructor

#each time a character is processed by the world, they are passed their individual dialogue list
                    
#there will be a single universal plot index csv where the first column is character names, and the second column is the index
#each character will take in their index as an plot index then process it through a method called in the npcFile's constructor
#that takes plot index and current level and npc name to determine the current index

#plot index will have nothing to do with actual dialogue index

#universal plot index csv will be updated if the player passes through a key dialogue box

#on new game, the second column will be reset to all 0's

#Player choices will also be handled through the npc file as well, (each npc will have to be passed the player dialogue list as a consequence)
#NPC dialogue will be displayed ontop the screen, player reponses in the bottom
    
    def csv_nonformatted(self, file_name):
        temp_list = self.read_npc_data(file_name)
        return temp_list
 
    #create separate file and class for player choices with independent methods
    #choice processing will happen in the NPC file, current dialogue and frame will have to be suspended during a player choice
    #choice processing will have a structure like: [[[message, next_index]...]....] where both are ints
    #message will refer to an index in temp_list above, next_index will be the return value when a choiee is selected
    #the actual buttons will have to be instantiated in the text box subclass
    #if there were to be a single instantiation of a player choice handler, it'd probably be in the textbox subclass
    #an NPC just needs to pass a player choice int to access the choice processing structure
    
# csv0 = csv_extracter(1)

# print(csv0.decode_player_choice())