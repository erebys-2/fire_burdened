class textfile_formatter():
    def __init__(self):
        self.endcase_char = (',', '.', ' ', ':', ';', '-')
    
    def read_text_from_file(self, file_path):
        file = open(file_path, "r")
        str_list = []
        for line in file:
            if line[len(line)-1] == '\n':
                str_to_append = line[0:len(line)-1]
            else:
                str_to_append = line
            str_list.append(str_to_append)

        return tuple(str_list)
    
    #takes string list output from reading a text file and formats into a dictionary
    #the values of the dictionary can be further formatted if correctly typed out
    def str_list_to_dict(self, str_list, format_mode):
        rtn_dict = {}
        
        for line in str_list:
            for char in line:
                if char == ':':
                    key = self.auto_string_to_number(line[0:line.index(char)])
                    if format_mode == 'list':
                        value = tuple(self.format_line_to_list(line[line.index(char)+2: len(line)], ','))
                    elif format_mode == 'true_list':
                        value = self.format_line_to_list(line[line.index(char)+2: len(line)], ',')
                    elif format_mode == 'list_list':#used exclusively for player choice stuff
                        value = []
                        temp_value = self.format_line_to_list(line[line.index(char)+2: len(line)], ';')
                        for element in temp_value:
                            value.append(self.format_line_to_list(element, '#'))
                        value = tuple(value)
                    elif format_mode == 'text_box':
                        value = tuple(self.split_string(line[line.index(char)+2: len(line)], 60, self.endcase_char))
                    elif format_mode == 'int':
                        value = int(line[line.index(char)+2: len(line)])
                    elif format_mode == 'float':
                        value = float(line[line.index(char)+2: len(line)])
                    else:
                        value = line[line.index(char)+2: len(line)]
                    
            rtn_dict[key] = value
            
        return rtn_dict
    
    def str_list_to_dialogue_list(self, str_list, limit, endcase_char):
        rtn_list = []
        temp_list = []
        for str_ in str_list:
            temp_list.append(self.format_line_to_list(str_, '#'))
            
        for item in temp_list:
            str_list = self.split_string(item[1], limit, endcase_char)
            rtn_list.append((item[0], tuple(str_list), item[2], item[3]))

        return tuple(rtn_list)
    
    def str_list_to_list_list(self, str_list):
        rtn_list = []
        for str_ in str_list:
            rtn_list.append(list(self.format_line_to_list(str_, ',')))
            
        return rtn_list
    
    def str_list_to_list(self, str_list):
        rtn_list = []
        for str_ in str_list:
            rtn_list.append(self.auto_string_to_number(str_))
        
        return rtn_list
        
    
    #takes a formatted string and returns a list, ints and floats will be automatically processed
    #appropriate formatting: 
    # 'this, is, the, future, of, many, parameters'
    # '1, 2, 4, 45345, 1234!, -90, .807, -.0008'
    #note the space after ','
    def format_line_to_list(self, line, delimiter): 
        start_index = 0
        end_index = 0
        str_list = []
        for i in range(len(line)):
            char = line[i]
            if char == delimiter or i == len(line) - 1:
                end_index = i
                if i == len(line) - 1:
                    end_index += 1
                str_list.append(self.auto_string_to_number(line[start_index: end_index]))
                start_index = end_index + 2

        return str_list
    
    #takes string, converts to float or int when possible
    def auto_string_to_number(self, str_):
        rtn_val = str_ #stay a string by default
        is_int = True
        is_float = False
        dot_count = 0
        
        for i in range(0, len(str_)):
            char = str_[i]
            if char not in ('1','2','3','4','5','6','7','8','9','0','-','.'): #letter found, abort
                is_int = False
                is_float = False
                break
            if char == '-' and i != 0: #minus sign must be in the front
                is_int = False
                is_float = False
                break
            if char == '.': #switch to float conversion
                is_int = False
                is_float = True
                dot_count += 1
            if dot_count > 1:
                is_int = False
                is_float = False
                break
            
        if is_int:
            rtn_val = int(str_)
        elif is_float:
            rtn_val = float(str_)
            
        return rtn_val
    
    def add_line_to_file(self, line, path):
        with open(path, 'a') as file:
            file.write('\n' + line)
            file.close()
    
    
    #takes list of strings, splits each string into another list of strings that will fit a box
    def str_to_str_list(self, input_list, limit, endcase_char):
        destination_list = []
        for item in input_list:
           
            str_list = self.split_string(item[0], limit, endcase_char)
            destination_list.append((tuple(str_list),item[1],item[2]))
        
        return destination_list
            
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
    
    def overwrite_file(self, path, data):
        text_file = open(path, 'w')
        text_file.write(data)
        text_file.close()