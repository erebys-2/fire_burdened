class textfile_formatter():
    def __init__(self) -> None:
        pass
    
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
                        value = self.format_line_to_list(line[line.index(char)+2: len(line)], ',')
                    elif format_mode == 'int':
                        value = int(line[line.index(char)+2: len(line)])
                    elif format_mode == 'float':
                        value = float(line[line.index(char)+2: len(line)])
                    else:
                        value = line[line.index(char)+2: len(line)]
                    
            rtn_dict[key] = value
            
        return rtn_dict
    
    def str_list_to_dialogue_list(self, str_list):
        rtn_list = []
        for str_ in str_list:
            rtn_list.append(self.format_line_to_list(str_, '#'))
        
        return tuple(rtn_list)
        
    
    #takes a formatted string and returns a list, ints and floats will be automatically processed
    #appropriate formatting: 
    # 'this, is, the, future, of, many, parameters.'
    # '1, 2, 4, 45345, 1234!, -90, .807, -.0008.'
    #note the space after ',' and ending with '.'
    def format_line_to_list(self, line, delimiter): 
        start_index = 0
        end_index = 0
        str_list = []
        for i in range(len(line)):
            char = line[i]
            if char == delimiter or i == len(line) - 1:
                end_index = i
                str_list.append(self.auto_string_to_number(line[start_index: end_index]))
                start_index = end_index + 2

        return tuple(str_list)
    
    #takes string, converts to float or int when possible
    def auto_string_to_number(self, str_):
        rtn_val = str_ #stay a string by default
        is_int = True
        is_float = False
        
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
            
        if is_int:
            rtn_val = int(str_)
        elif is_float:
            rtn_val = float(str_)
            
        return rtn_val
            