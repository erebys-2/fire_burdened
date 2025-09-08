import csv
import os
from textfile_handler import textfile_formatter
#DEPRECIATED

t1 = textfile_formatter()
path = 'assets/config_textfiles/level_config/'
level_sizes_dict = t1.str_list_to_dict(t1.read_text_from_file(os.path.join(path + 'level_sizes_dict.txt')), 'list')

layer_desc_dict = {
    0:'coord_data',
    1:'fg_data',
    2:'fg_1_data',
    3:'data',
    4:'bg1_data',
    5:'bg3_data',
    6:'bg2_data',
    7:'bg2_1_data',
    8:'bg4_data',
    9:'bg5_data',
    10: 'bg6_data'
}

path2 = 'assets/config_textfiles/level_config/'
ROWS = 0
MAX_COLS = 0
layer_list = []

#-------Reading and writing level data for loading---------------------------------------
def read_level_data(level, data_str):
    rtn_list = []
    with open(f'assets/level_files/level{level}_{data_str}.csv', newline= '') as csvfile:
        reader = csv.reader(csvfile, delimiter= ',') #what separates values = delimiter
        for x, current_row in enumerate(reader):
            row_list = []
            for y, tile in enumerate(current_row):
                row_list.append(int(tile))
            rtn_list.append(row_list)

    return rtn_list

def write_level_data(level, data_, data_str):
    with open(f'assets/level_files/level{level}_{data_str}.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter = ',')
            for row in data_:
                writer.writerow(row)
                
print("Input level to extend")
input_level = int(input('enter level: '))
level = -1

if input_level in level_sizes_dict:
    ROWS = level_sizes_dict[input_level][0]
    MAX_COLS = level_sizes_dict[input_level][1]
    level = input_level
else:
    print("Level not found\n")
    level = 9/0
    
for layer in layer_desc_dict:
    layer_list.append(read_level_data(level, layer_desc_dict[layer]))

print("Loaded level into list of lists")

#handling extension
extension = int(input('enter the x extension: '))

rtn_layer_list = []#3d list of lists
for layer in layer_list:#layer is 2d
    templist = []
    for i in range(ROWS):
        if extension > 0:
            templist.append(layer[i] + [-1]*extension)
        else:
            templist.append(layer[i][:MAX_COLS+extension])
    rtn_layer_list.append(templist)
    
#saving csvs and txt file
for layer in layer_desc_dict:
    write_level_data(level, rtn_layer_list[layer], layer_desc_dict[layer])
    
str_list = list(t1.read_text_from_file((path2 + 'level_sizes_dict.txt')))
str_list[level] = f'{level}: {ROWS}, {MAX_COLS+extension}'
output_str = ''
for str_ in str_list:
    output_str = output_str + str_ + '\n'
output_str = output_str[0:len(output_str)-1]
t1.overwrite_file((path2 + 'level_sizes_dict.txt'), output_str)
print("Operation completed.")