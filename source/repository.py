from dataclasses import dataclass,field
from typing import List,Dict
from PyQt5.QtWidgets import *
from click import option

@dataclass
class Repository:
    name : str = ""
    git_repo : str = ""
    git_tag : str = ""
    should_build : bool = False
    depends_on : str = ""
    sources_to_add: List[str] = field(default_factory=list)
    includes : List[str] = field(default_factory=list)
    libraries : List[str] = field(default_factory=list)
    cmake_args : List[str] = field(default_factory=list)
    
    #advanced 
    
    def add_to_dict(self,dict):
        dict["name"] = self.name
        dict["repo"] = self.git_repo
        dict["tag"] = self.git_tag
        dict["should_build"] = self.should_build
        dict["sources"] = self.sources_to_add
        dict["includes"] = self.includes
        dict["libraries"] = self.libraries
        dict["depends_on"] = self.depends_on
        dict["cmake_args"] = self.cmake_args
        
    def get_from_dict(self,dict):
        if "name" in dict:
            self.name = dict["name"]
        if "repo" in dict:
            self.git_repo = dict["repo"]
        if "tag" in dict:
            self.git_tag = dict["tag"]
        if "should_build" in dict:
            self.should_build = dict["should_build"]
        if "sources" in dict:
            self.sources_to_add = dict["sources"]
        if "includes" in dict:
            self.includes = dict["includes"]
        if "libraries" in dict:
            self.libraries = dict["libraries"]
        if "cmake_args" in dict:
            self.cmake_args = dict["cmake_args"]
        if "depends_on" in dict:
            self.depends_on = dict["depends_on"]
    
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
    
    
    def __init__(self,repository : Repository,dict_of_options: Dict):
        super().__init__()
        
        self.setWindowTitle("New External Repository")
        
        self._repository = repository
        self.name = QLineEdit(repository.name)
        self.repo = QLineEdit(repository.git_repo)
        self.tag = QLineEdit(repository.git_tag)
        self.should_build = QCheckBox()
        self.should_build.setCheckState(repository.should_build)
        
        if len(dict_of_options) > 0:
            options_combo = QComboBox()
            options_combo.addItem("None")
            for item in dict_of_options:
                options_combo.addItem(item)
                if item == repository.depends_on:
                    options_combo.setCurrentIndex(options_combo.findText(item))
            options_combo.currentIndexChanged.connect(lambda index: self._update_options(options_combo,index))
            
        self.sources = QTextEdit()
        self.sources.setText("\n".join(repository.sources_to_add))
            
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
        self.sources.textChanged.connect(self._update_source)
        self.includes.textChanged.connect(self._update_includes)
        self.libraries.textChanged.connect(self._update_libraries)
        self.cmake_args.textChanged.connect(self._update_cmake_args)
        self.end_buttons.accepted.connect(self._finishing_check_callback)
        self.end_buttons.rejected.connect(self.reject)
        
        layout = QFormLayout()
        
        layout.addRow("Name*",self.name)
        layout.addRow("Git Repo*",self.repo)
        layout.addRow("Git Tag",self.tag)
        layout.addRow("Should Build",self.should_build)
        if len(dict_of_options) > 0:
            layout.addRow("Depends on",options_combo)
        layout.addRow("Sources to add",self.sources)
        layout.addRow("Include Paths",self.includes)
        layout.addRow("Libraries",self.libraries)
        layout.addRow("Cmake Args",self.cmake_args)
        layout.addRow(QLabel("* = Required"),self.end_buttons)
        
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
    
    def _update_options(self,object: QComboBox,index):
        if object.itemText(index) == "None":
            self._repository.depends_on = ""
        else:
            self._repository.depends_on = object.itemText(index)
    
    def _update_source(self):
        self._repository.sources_to_add = self.sources.toPlainText().split()
    
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
    
    
        
    
    
    def is_filled(self):
        if self.name.text() == "" or self.repo.text() == "":  
            return False

        return True

