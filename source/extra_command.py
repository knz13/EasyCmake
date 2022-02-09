from dataclasses import dataclass
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt





@dataclass
class ExtraCommand:
    alias : str= ""
    command : str = ""
    execute_time : str = ""
    
    def get_from_dict(self,dict):
        self.alias = dict["alias"]
        self.command = dict["command"]
        self.execute_time = dict["execute_time"]
    
    def add_to_dict(self,dict):
        dict["alias"] = self.alias
        dict["command"] = self.command
        dict["execute_time"] = self.execute_time
    
    def get_dialog(self,master,current_used_commands):
        dialog = QDialog(master)
        
        dialog.setWindowTitle("Extra Command")
        
        main_layout = QVBoxLayout()
        
        accept_button = QPushButton("Ok")
        accept_button.clicked.connect(lambda: self._check_before_ending_dialog(dialog,current_used_commands))
        end_button = QPushButton("Cancel")
        end_button.clicked.connect(dialog.reject)
        
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(accept_button)
        buttons_layout.addWidget(end_button)
        
        layout = QFormLayout()
        
        alias_text = QLineEdit(self.alias)
        alias_text.textChanged.connect(lambda: self._get_alias(alias_text))
        
        execute_time_combobox = QComboBox()
        execute_time_combobox.addItem("PRE_BUILD")
        execute_time_combobox.addItem("POST_BUILD")
        execute_time_combobox.addItem("PRE_LINK")
        if self.execute_time != "":
            execute_time_combobox.setCurrentIndex(execute_time_combobox.findText(self.execute_time))
        else:
            self.execute_time = execute_time_combobox.itemText(execute_time_combobox.currentIndex())
        
        execute_time_combobox.currentTextChanged.connect(lambda: self._get_execute_time(execute_time_combobox))
        
        command_text = QLineEdit(self.command)
        command_text.textChanged.connect(lambda: self._get_command_text(command_text))
        
        layout.addRow("Alias",alias_text)
        layout.addRow("Execution Time",execute_time_combobox)
        layout.addRow("Command",command_text)
        
        main_layout.addLayout(layout)
        main_layout.addLayout(buttons_layout)
        
        dialog.setLayout(main_layout)
        
        return dialog
    
    
        
    def _check_before_ending_dialog(self,dialog : QDialog,current_used_commands):
        
        if self.alias == "":
            
            QMessageBox.warning(dialog,"Warning",f'''Please choose an alias.''')
            
            return
        if self.command == "":
            QMessageBox.warning(dialog,"Warning",f'''Please define a command to execute.''')
            
            return
        
        if self.alias in current_used_commands:
            QMessageBox.warning(dialog,"Warning",f'''Alias {self.alias} was already used,\nplease choose another one.''')
            
            return
        dialog.accept()
        

    
        
    def _get_alias(self,text : QLineEdit):
        self.alias = text.text()
        
    def _get_execute_time(self,combobox : QComboBox):
        self.execute_time = combobox.currentText()

    def _get_command_text(self,text : QLineEdit):
        self.command = text.text()
        