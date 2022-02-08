from dataclasses import dataclass,field
from typing import List,Dict
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from enum import Enum
from copy import deepcopy




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
    
    def get_dialog(self,master,extra_commands):
        dialog = QDialog(master)
        
        dialog.setWindowTitle("Extra Command")
        
        main_layout = QVBoxLayout()
        
        accept_button = QPushButton("Ok")
        accept_button.clicked.connect(lambda: self._check_before_ending_dialog(dialog,extra_commands))
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
        
    def _check_before_ending_dialog(self,dialog : QDialog,extra_commands):
        
        if self.alias == "":
            
            QMessageBox.warning(dialog,"Warning",f'''Please choose an alias.''')
            
            return
        if self.command == "":
            QMessageBox.warning(dialog,"Warning",f'''Please define a command to execute.''')
            
            return
        
        if self.alias in extra_commands:
            QMessageBox.warning(dialog,"Warning",f'''Alias {self.alias} was already used,\nplease choose another one.''')
            
            return
        dialog.accept()
        

        
    def _get_alias(self,text : QLineEdit):
        self.alias = text.text()
        
    def _get_execute_time(self,combobox : QComboBox):
        self.execute_time = combobox.currentText()

    def _get_command_text(self,text : QLineEdit):
        self.command = text.text()
        
        
        
        
        
        
        
        

@dataclass
class AdvancedOptions:
    extra_commands: Dict[str,ExtraCommand]= field(default_factory=dict)
    
    def get_from_dict(self,dict):
        for item in dict["extra_commands"]:
            command = ExtraCommand()
            command.get_from_dict(item)
            self.extra_commands[command.alias] = command
    
    def add_to_dict(self,dict):
        dict["extra_commands"] = []
        for item in self.extra_commands.values():
            my_dict = {}
            item.add_to_dict(my_dict)
            dict["extra_commands"].append(my_dict)
            
    def clear(self):
        self.extra_commands.clear()

    
class AdvancedOptionsDialog(QDialog):
    
    
    
    def __init__(self,options: AdvancedOptions):
        super().__init__()
        
        self.advanced_options_ref = options
        
        self._layout = QVBoxLayout()
        
        self._extra_commands = QListWidget()
        self._extra_commands.setSelectionMode(QAbstractItemView.SingleSelection)
        self._extra_commands.setContextMenuPolicy(Qt.CustomContextMenu)
        self._extra_commands.customContextMenuRequested.connect(self._extra_commands_context_menu)
        self._update_extra_commands_list()
        
        extra_commands_layout = QFormLayout()
        extra_commands_layout.addRow("Extra Commands",self._extra_commands)
        
        end_buttons_layout = QHBoxLayout()
        accept_button = QPushButton("Apply")
        accept_button.clicked.connect(self.accept)
        
        reject_button = QPushButton("Cancel")
        reject_button.clicked.connect(self.reject)
        
        end_buttons_layout.addStretch()
        end_buttons_layout.addWidget(accept_button)
        end_buttons_layout.addWidget(reject_button)
        
        self._layout.addLayout(extra_commands_layout)
        self._layout.addLayout(end_buttons_layout)
        
        self.setLayout(self._layout)
        
        
        
        
    def _extra_commands_context_menu(self,position):
        
        menu = QMenu()
        menu.addAction("Add").triggered.connect(self._extra_commands_context_menu_add)
        
        if len(self._extra_commands.selectedItems()) == 1:
            menu.addAction("Modify").triggered.connect(self._extra_commands_context_menu_modify)
            menu.addAction("Delete").triggered.connect(self._extra_commands_context_menu_delete)
        
        menu.exec_(self._extra_commands.mapToGlobal(position))
        
    
    def _update_extra_commands_list(self):
        self._extra_commands.clear()
        
        for item in self.advanced_options_ref.extra_commands.values():
            self._extra_commands.addItem(item.alias)
        
    def _extra_commands_context_menu_modify(self):
        command = deepcopy(self.advanced_options_ref.extra_commands[self._extra_commands.selectedItems()[0].text()])
        original_command = deepcopy(command)
        command_name = command.alias
        self.advanced_options_ref.extra_commands.pop(command_name)
        
        
        dialog = command.get_dialog(self,self.advanced_options_ref.extra_commands)
        
        if dialog.exec_():
            self.advanced_options_ref.extra_commands[command.alias] = command
            self._update_extra_commands_list()
        else:
            self.advanced_options_ref.extra_commands[original_command.alias] = original_command
            self._update_extra_commands_list()
        
    def _extra_commands_context_menu_add(self):
        
        command = ExtraCommand()
        
        dialog = command.get_dialog(self,self.advanced_options_ref.extra_commands)
        
        if dialog.exec_():
            self.advanced_options_ref.extra_commands[command.alias] = command
            
            
            self._update_extra_commands_list()
            
    def _extra_commands_context_menu_delete(self):
        self.advanced_options_ref.extra_commands.pop(self._extra_commands.selectedItems()[0].text())
        self._update_extra_commands_list()
        
        