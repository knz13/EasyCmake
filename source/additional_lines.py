from dataclasses import dataclass,field
from typing import List,Dict
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from copy import deepcopy


@dataclass
class AdditionalLines:
    alias: str= ""
    lines: List[str] = field(default_factory=list)
    
    def get_from_dict(self,dict):
        self.alias = dict["alias"]
        self.lines = dict["lines"]
    
    def add_to_dict(self,dict):
        dict["alias"] = self.alias
        dict["lines"] = self.lines
    
    def get_dialog(self,master,lines_already_added):
        
        dialog = QDialog(master)
        
        main_layout = QVBoxLayout()
        
        accept_button = QPushButton("Ok")
        accept_button.clicked.connect(lambda: self._check_before_ending_dialog(dialog,lines_already_added))
        end_button = QPushButton("Cancel")
        end_button.clicked.connect(dialog.reject)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(accept_button)
        buttons_layout.addWidget(end_button)
        
        layout = QFormLayout()
        
        alias_text = QLineEdit(self.alias)
        alias_text.textChanged.connect(lambda: self._get_alias(alias_text))
        
        lines_text = QTextEdit()
        lines_text.setText("\n".join(self.lines))
        lines_text.textChanged.connect(lambda: self._get_lines(lines_text))
        
        layout.addRow("Alias",alias_text)
        layout.addRow("Lines",lines_text)
        
        main_layout.addLayout(layout)
        main_layout.addLayout(buttons_layout)
        
        dialog.setLayout(main_layout)
        
        return dialog
    
    def _check_before_ending_dialog(self,dialog: QDialog,lines_already_added):
        if self.alias == "":
            
            QMessageBox.warning(dialog,"Warning",f'''Please choose an alias.''')
            
            return
        
        if self.lines == []:
            QMessageBox.warning(dialog,"Warning",f'''Please add a line before applying.''')
                        
            return
    
        if self.alias in lines_already_added:
            QMessageBox.warning(dialog,"Warning",f'''Alias '{self.alias}' is already in use.\nPlease choose another one.''')
            
            return
        
        dialog.accept()
        
    def _get_alias(self,text : QLineEdit):
        self.alias = text.text()
        
    def _get_lines(self,text : QTextEdit):
        self.lines = text.toPlainText().split("\n")