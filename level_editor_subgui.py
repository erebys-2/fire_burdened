import sys
from PyQt6.QtWidgets import QInputDialog, QApplication, QWidget, QGridLayout, QListWidget, QPushButton, QLabel, QMessageBox, QLineEdit
from cfg_handler0 import yaml_handler

class level_editor_subgui(QWidget):
    def __init__(self, level, data_dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(f'Editing Level {level} Config Data')
        self.setGeometry(100, 100, 1080, 0)
        self.y0 = yaml_handler()	
        
        self.y_ = 1
        self.data_dict = data_dict#{k:data_dict[k] for k in data_dict if k != 'trans_data'}
        self.export_data_dict = {}
        self.layout = QGridLayout(self)
        
        self.s_box_dict = {}
        self.lvl_trans_list = []
        self.build_window(self.data_dict, self.layout)
        self.build_transdata_dict(self.data_dict['trans_data'], self.layout)
        
        x3 = 4
        save_btn = QPushButton(self, text='save')
        save_btn.clicked.connect(self.export_data)
        self.layout.addWidget(save_btn, 0, 4)
        
        rst_btn = QPushButton(self, text='reset')
        rst_btn.clicked.connect(self.reset)
        self.layout.addWidget(rst_btn, 1, 4)
        

        # show the window
        self.show()
        
        
    def reset(self):
        self.build_window(self.data_dict, self.layout)
        self.build_transdata_dict(self.data_dict['trans_data'], self.layout)
        self.export_data_dict = {}
        
        
    def export_data(self):
        for key in self.s_box_dict:
            val = self.y0.format_complex_str(self.s_box_dict[key].text())
            #autocorrect bad entries
            if key == 'player_en':
                if val not in (True, False):
                    val = True
            elif key == 'color':
                if sum([1 for num in val if num > 255]) > 0:
                    val = self.data_dict['color']
            elif key == 'name':
                val = str(val)
                    
            self.export_data_dict[key] = val
            
        self.export_data_dict['trans_data'] = [self.y0.format_complex_str(str_.text(), force_none=True) for str_ in self.lvl_trans_list]

        #print(self.export_data_dict)
        print('saved config data')

    def build_transdata_dict(self, lvl_trans_list, layout):
        x = 1
        x2 = 2
        self.lvl_trans_list*=0
        layout.addWidget(QLabel(self, text='trans_data:'), self.y_, x)
        for i in range(len(lvl_trans_list)):
            
            self.lvl_trans_list.append(QLineEdit(
                self,
                text=str(lvl_trans_list[i]),
                clearButtonEnabled=True
            ))
            layout.addWidget(QLabel(self, text='transition tile '+str(i)+ f' at position ({lvl_trans_list[i]['x']}, {lvl_trans_list[i]['y']}):'), self.y_, x2)
            layout.addWidget(self.lvl_trans_list[i], self.y_, x2+1)
            
            self.y_+= 1
            
        self.setLayout(layout)
        
    def build_window(self, data_dict, layout):
        x = 1
        self.y_ = 1

        self.s_box_list = {}
        for key in data_dict:
            if key != 'trans_data':
                self.s_box_dict[key] = QLineEdit(
                    self,
                    text=str(data_dict[key]),
                    clearButtonEnabled=key!='size',
                    readOnly=key=='size'
                )
        
        for key in self.s_box_dict:
            layout.addWidget(self.s_box_dict[key], self.y_, x+1)
            layout.addWidget(QLabel(self, text=key+':'), self.y_, x)
            self.y_+= 1

        
        self.setLayout(layout)
        
# import os
# y1 = yaml_handler()	
# all_levels_dict = y1.get_data(os.path.join('assets', 'config_textfiles', 'world_config', 'level_dict.yaml'))
        
# #if __name__ == '__main__':
# app = QApplication(sys.argv)
# window = level_editor_subgui(all_levels_dict[4])
# window_closed = app.exec()
# print(window_closed)
# sys.exit(window_closed)