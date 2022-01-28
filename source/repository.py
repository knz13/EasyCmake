from dataclasses import dataclass,field
from typing import List,Dict
from PyQt5.QtWidgets import *

@dataclass
class Repository:
    name : str = ""
    git_repo : str = ""
    git_tag : str = ""
    should_build : bool = False
    includes : List[str] = field(default_factory=list)
    libraries : List[str] = field(default_factory=list)
    cmake_args : List[str] = field(default_factory=list)
    
    #advanced 
    
    
    
    
    def get_as_string(self):
        mystr = "Name: {}\n".format(self.name)
        mystr += "Git-Repo: {}\n".format(self.git_repo)
        mystr += "Git-Tag: {}\n".format(self.git_tag)
        mystr += "Should-Build: {}\n".format(self.should_build)
        mystr += "includes:\n"
        for item in self.includes:
            mystr += "\t-{}\n".format(item)
        mystr += "libraries:\n"
        for item in self.libraries:
            mystr += "\t-{}\n".format(item)
        mystr += "cmake args:\n"
        for item in self.cmake_args:
            mystr += "\t-{}\n".format(item)
            
        mystr += "source_subdir: {}\n".format(self.source_subdir)
        
        return mystr
    

class RepositoryDialog(QDialog):
    
    
    def __init__(self,repository : Repository):
        super().__init__()
        
        self.setWindowTitle("New External Repository")
        
        self._repository = repository
        self.name = QLineEdit(repository.name)
        self.repo = QLineEdit(repository.git_repo)
        self.tag = QLineEdit(repository.git_tag)
        self.should_build = QCheckBox()
        self.should_build.setCheckState(repository.should_build)
        self.includes = QTextEdit()
        self.includes.setText("\n".join(repository.includes))
        
        self.libraries = QTextEdit()
        self.libraries.setText("\n".join(repository.libraries))
        
        self.cmake_args = QTextEdit()
        self.cmake_args.setText("\n".join(repository.cmake_args))
        
        self.end_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        
        self.name.editingFinished.connect(self._update_name)
        self.repo.editingFinished.connect(self._repo_validation_func)
        self.tag.editingFinished.connect(self._update_tag)
        self.should_build.clicked.connect(self._update_build)
        self.includes.textChanged.connect(self._update_includes)
        self.libraries.textChanged.connect(self._update_libraries)
        self.cmake_args.textChanged.connect(self._update_cmake_args)
        self.end_buttons.accepted.connect(self._finishing_check_callback)
        self.end_buttons.rejected.connect(self.reject)
        
        layout = QFormLayout()
        
        self._add_to_layout(layout)
        
        self.setLayout(layout)
        
    def _finishing_check_callback(self):
        if not self.is_filled():
            message = QMessageBox(icon=QMessageBox.Warning,text="Please fill all required fields.")
            message.setWindowTitle("Error in Easy Cmake!")
            message.exec_()
            return

        if self._repository.git_repo[:8] != "https://":
                self._repository.git_repo = "https://" + self._repository.git_repo
       
        if self._repository.git_tag == "":
            self._repository.git_tag = "origin/master"
        
    
        self.accept()
        
        

    def _repo_validation_func(self):
        self._repository.git_repo = self.repo.text()
    
    def _update_includes(self):
        self._repository.includes = self.includes.toPlainText().split()
        
    def _update_libraries(self):
        self._repository.libraries = self.libraries.toPlainText().split()
        
    def _update_cmake_args(self):
        self._repository.cmake_args = self.cmake_args.toPlainText().split()  
    
    def _update_build(self):
        self._repository.should_build = self.should_build.isChecked()
            
    def _update_tag(self):
        self._repository.git_tag = self.tag.text()
            
    def _update_name(self):
        self._repository.name = self.name.text()
    
    def _add_to_layout(self,layout : QFormLayout):
        layout.addRow("Name*",self.name)
        layout.addRow("Git Repo*",self.repo)
        layout.addRow("Git Tag",self.tag)
        layout.addRow("Should Build",self.should_build)
        layout.addRow("Include Paths",self.includes)
        layout.addRow("Libraries",self.libraries)
        layout.addRow("Cmake Args",self.cmake_args)
        layout.addRow(QLabel("* = Required"),self.end_buttons)
        
    
    
    def is_filled(self):
        if self.name.text() == "" or self.repo.text() == "":  
            return False

        return True

