from dataclasses import dataclass,field
from typing import List,Dict
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

def create_clickable_list_widget(list_of_names,list_of_states):
    list = QListWidget()
    
    index = 0
    for item in list_of_names:
        list_item = QListWidgetItem()
        list_item.setText(item)
        list_item.setFlags(list_item.flags() | Qt.ItemIsUserCheckable)
        if list_of_states[index]:
            list_item.setCheckState(True)
        else:
            list_item.setCheckState(False)
        list.addItem(list_item)
        index +=1
    return list


@dataclass
class PublicUserOption:
    alias: str=""
    option_name: str=""
    description: str=""
    option_specific_source_files: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    default_value: bool=True
    
    def add_to_dict(self,dict):
        
        dict["alias"] = self.alias
        dict["option_name"] = self.option_name
        dict["description"] = self.description
        dict["default_value"] = self.default_value
        dict["depends_on"] = self.depends_on
        dict["option_specific_sources"] = self.option_specific_source_files
        
    def get_from_dict(self,dict):
        if "alias" in dict:
            self.alias = dict["alias"]
        if "option_name" in dict:
            self.option_name = dict["option_name"]
        if "default_value" in dict:
            self.default_value = dict["default_value"]
        if "description" in dict:
            self.description = dict["description"]
        if "depends_on" in dict:
            self.depends_on = dict["depends_on"]
        if "option_specific_sources" in dict:
            self.option_specific_source_files = dict["option_specific_sources"]
    
    
    
    def get_dialog(self,master,options_already_added):
        dialog = QDialog(master)
        
        main_layout = QVBoxLayout()
        
        accept_button = QPushButton("Ok")
        accept_button.clicked.connect(lambda: self._check_before_ending_dialog(dialog,options_already_added))
        end_button = QPushButton("Cancel")
        end_button.clicked.connect(dialog.reject)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(accept_button)
        buttons_layout.addWidget(end_button)
        
        layout = QFormLayout()
        
        alias_text = QLineEdit(self.alias)
        alias_text.textChanged.connect(lambda: self._get_alias(alias_text))
        
        option_name_text = QLineEdit(self.option_name)
        option_name_text.textChanged.connect(lambda: self._get_name(option_name_text))
        
        description_text = QTextEdit(self.description)
        description_text.textChanged.connect(lambda: self._get_description(description_text))
        
        option_sources_text = QTextEdit("\n".join(self.option_specific_source_files))
        option_sources_text.textChanged.connect(lambda: self._get_sources(option_sources_text))
        
        depends_on_list = create_clickable_list_widget(options_already_added.keys(),[True if x == y else False for x,y in zip(options_already_added.keys(),self.depends_on)])
        depends_on_list.itemChanged.connect(self._get_depends_on)
        
        default_value_combo = QComboBox()
        default_value_combo.addItem("ON")
        default_value_combo.addItem("OFF")
        default_value_combo.currentIndexChanged.connect(lambda index: self._get_value(default_value_combo,index))
        
        if self.default_value:
            default_value_combo.setCurrentIndex(0)
        else:
            default_value_combo.setCurrentIndex(1)
        
        
        layout.addRow("Alias*",alias_text)
        layout.addRow("Option Name*",option_name_text)
        layout.addRow("Default Value",default_value_combo)
        layout.addRow("Description",description_text)
        layout.addRow("Option Specific\nSource Files",option_sources_text)
        layout.addRow("Depends on",depends_on_list)
        
        
        main_layout.addLayout(layout)
        main_layout.addLayout(buttons_layout)
        
        dialog.setLayout(main_layout)
        
        return dialog
    
    def _check_before_ending_dialog(self,dialog,options):
        if self.alias == "":
             QMessageBox.warning(dialog,"Warning",f'''Please choose an alias.''')
             
             return

        if self.option_name == "":
            QMessageBox.warning(dialog,"Warning",f'''Please choose an options name.''')

            return
        
        if self.alias in options:
            QMessageBox.warning(dialog,"Warning",f'''Alias '{self.alias}' is already in use.\nPlease choose another one.''')

            return
        
        
        for item in options.values():
            if self.option_name == item.option_name:
                QMessageBox.warning(dialog,"Warning",f'''Option name '{self.option_name}' is already in use.\nPlease choose another one.''')
                
                return
            
        dialog.accept()

    def _get_sources(self,text : QTextEdit):
        self.option_specific_source_files = text.toPlainText().split()

    def _get_alias(self,text : QLineEdit):
        self.alias = text.text()
    def _get_name(self,text: QLineEdit):
        self.option_name = text.text()
    def _get_value(self,combobox : QComboBox,index):
        if combobox.itemText(index) == "ON":
            self.default_value = True
        else:
            self.default_value = False
    def  _get_description(self,text: QTextEdit):
        self.description = text.toPlainText()
        
    def _get_depends_on(self,item : QListWidgetItem):
        if item.text() in self.depends_on:
            self.depends_on.pop(self.depends_on.index(item.text()))
        else:
            self.depends_on.append(item.text())