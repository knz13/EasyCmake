from dataclasses import dataclass,field
from typing import List,Dict
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator,QDoubleValidator
from PyQt5.QtCore import Qt
from copy import deepcopy
import json
import sys
import os

from git import Repo
from repository import*
from installed_packages import *
from cmakelist_creation import *


@dataclass
class EasyCmakeApp(QWidget):
    
    #main stuff
    
    sources : List[str] = field(default_factory=list)
    includes : List[str] = field(default_factory=list)
    list_of_external_repo_names: Dict[str,str] = field(default_factory=list)
    
    installed_packages: Dict[str,InstalledPackage] = field(default_factory=dict)
    repositories : Dict[str,Repository] = field(default_factory=dict)
    

    _instance_cache_location: str = ""
    _cache_location : str = ""
    _creating_directory: str = ""
    _repository_window : QDialog = field(default_factory=QDialog)
    _layout : QFormLayout = field(default_factory=QFormLayout)
    _added_modify_parts: bool = False
    _last_item_in_modifying: str = ""
    
    #main widgets
    
    _creating_directory_button : QPushButton = field(default_factory=QPushButton)
    _creating_directory_text : QLabel = field(default_factory=QLabel)
    _executable_name : QLineEdit = field(default_factory=QLineEdit)
    _cpp_standard_text : QComboBox= field(default_factory=QComboBox)
    _source_text : QTextEdit = field(default_factory=QTextEdit)
    _includes_text : QTextEdit = field(default_factory=QTextEdit)
    _repo_list_widget : QListWidget = field(default_factory=QListWidget)
    _generate_button : QPushButton = field(default_factory=QPushButton)
    _cmake_version_text : QLineEdit = field(default_factory=QLineEdit)

    
    
    
    
    
    def __post_init__(self):
        super().__init__()
        
        self._cache_location = os.getcwd().replace("\\","/") + "/cache.json"
        self._instance_cache_location = os.getcwd().replace("\\","/") + "/instance_cache.json"
        
        self.setWindowTitle("Easy Cmake")
        self.setFixedSize(700,600)
        
        self._creating_directory_text.setText("Creating Directory: ")
        self._creating_directory_button.setText("Modify")
        self._creating_directory_button.clicked.connect(self._get_creating_dir)
        
        self._cpp_standard_text.addItem("C++20")
        self._cpp_standard_text.addItem("C++17")
        self._cpp_standard_text.addItem("C++14")
        self._cpp_standard_text.addItem("C++11")
        self._cpp_standard_text.addItem("C++03")
        self._cpp_standard_text.addItem("C++98")
        
        self._cmake_version_text.setValidator(QDoubleValidator())
        
        self._source_text.textChanged.connect(self._update_source_text)
        self._source_text.setMinimumSize(400,0)
        
        self._includes_text.textChanged.connect(self._update_include_text)
        self._includes_text.setMinimumSize(400,0)
        
        
        self._generate_button = QPushButton("Generate")
        self._generate_button.clicked.connect(lambda: generate_cmake_lists(self))
        self._generate_button.setMaximumWidth(80)
        
        self._repo_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self._repo_list_widget.customContextMenuRequested.connect(self._repo_list_context_menu_callback)
        
        
        #source buttons
        
        source_button_layout = QVBoxLayout()
        source_button_add_0 = QPushButton("Add Files")
        source_button_add_0.clicked.connect(self._add_source_files)
        
        source_button_add_1 = QPushButton("Add Directories")
        source_button_add_1.clicked.connect(self._add_source_dirs)
        
        source_button_layout.addWidget(source_button_add_0)
        source_button_layout.addWidget(source_button_add_1)
        
        #include buttons
        include_button_layout = QVBoxLayout()
        include_button_add = QPushButton("Add Includes")
        include_button_add.clicked.connect(self._add_include_dirs)
        
        include_button_layout.addWidget(include_button_add)
        
        #main widget
        
        self._layout.addRow(self._creating_directory_text,self._creating_directory_button)
        
        self._layout.addRow(QLabel("Executable Name*"),self._executable_name)
        
        self._layout.addRow(QLabel("C++ Standard"),self._cpp_standard_text)
        
        self._layout.addRow(QLabel("Cmake Version*"),self._cmake_version_text)
        
        self._layout.addRow(QLabel("Source Files*"))
        self._layout.addRow(self._source_text,source_button_layout)
        
        self._layout.addRow(QLabel("Include Directories"))
        self._layout.addRow(self._includes_text,include_button_layout)
        
        
        self._layout.addRow(QLabel("External Repositories\n(Right click on the white screen on the right for more options)"),self._repo_list_widget)
        
        
        self._layout.addRow(self._generate_button)
        
        
        
        box = QGroupBox()
        box.setLayout(self._layout)
        scroll = QScrollArea()
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(box)
        scroll.setWidgetResizable(True)
        
        layout = QVBoxLayout()
        layout.addWidget(scroll)
        
        
        
        self.setLayout(layout)
        
    
    def _repo_list_context_menu_callback(self,position):
        
        menu = QMenu(self)
        add_action = menu.addMenu("Add")
        repo_add_action = add_action.addAction("Repository")
        installed_package_add_action = add_action.addAction("Installed Package")
        
        
        repo_add_action.triggered.connect(self._create_new_repo_callback)
        installed_package_add_action.triggered.connect(self._add_new_installed_package)
        
        if len(self._repo_list_widget.selectedItems()) == 1:
            modify_action = menu.addAction("Modify")
            modify_action.triggered.connect(self._repo_modify_callback)
        if len(self._repo_list_widget.selectedItems()) >= 1:
            delete_action = menu.addAction("Delete")
            delete_action.triggered.connect(self._repo_delete_callback)
        
        
        menu.exec_(self._repo_list_widget.mapToGlobal(position))
        
    def _clear_fields(self):
        self._executable_name.setText("")
        self._cpp_standard_text.setCurrentIndex(self._cpp_standard_text.findText("C++20"))
        self._cmake_version_text.setText("")
        self.sources.clear()
        self._source_text.clear()
        self.includes.clear()
        self._includes_text.clear()
        self.repositories.clear()
        self.installed_packages.clear()
        self.list_of_external_repo_names.clear()
        
        self._update_source_text()
        self._update_include_text()
        self._update_repo_list()
        
        
    def _get_creating_dir(self):
        
        if self._creating_directory != "":
            self._save_to_cache(self._instance_cache_location)

            self._clear_fields()
        
        dir = QFileDialog.getExistingDirectory(self,"Choose a Directory",os.curdir)
        if dir == "":
            return

        self._creating_directory = dir
        
        
        self._creating_directory_text.setText("Creating Directory: " + dir)
        
        if not self._check_if_creating_dir_in_cache(self._instance_cache_location):
            self._check_if_creating_dir_in_cache(self._cache_location)
                
    def _add_source_files(self):
        
        if self._creating_directory == "":
            QMessageBox.warning(self,"Warning!","Please choose a valid creating directory")
            return
        
        files = QFileDialog.getOpenFileNames(self,"Choose files to add",self._creating_directory,"C/C++ files (*.cpp *.cc *.c)")
        
        if files[0] == []:
            return
        
        self.sources = self.sources + files[0]
        
        self._source_text.setText("\n".join(self.sources))
        
    def _add_source_dirs(self):
        
        if self._creating_directory == "":
            QMessageBox.warning(self,"Warning!","Please choose a valid creating directory")
            return
        
        files = QFileDialog.getExistingDirectory(self,"Choose a directory",self._creating_directory)
        
        if files == "":
            return
        
        self.sources.append(files)
        
        self._source_text.setText("\n".join(self.sources))
        
    
    def _add_include_dirs(self):
        if self._creating_directory == "":
            QMessageBox.warning(self,"Warning!","Please choose a valid creating directory")
            return
        
        files = QFileDialog.getExistingDirectory(self,"Choose a directory to include",self._creating_directory)
        
        if files == "":
            return
        
        self.includes.append(files)
        
        self._includes_text.setText("\n".join(self.includes))
        
    def _add_new_installed_package(self):
        installed_package = InstalledPackage()
        dialog = InstalledPackageDialog(installed_package)
        
        if dialog.exec_():
            self.installed_packages[installed_package.name] = installed_package
            self.list_of_external_repo_names[installed_package.name] = "package"
            self._update_repo_list()
        
    def _create_new_repo_callback(self):
        repo = Repository()
        dialog = RepositoryDialog(repo)
        
        if dialog.exec_():
            self.repositories[repo.name] = repo
            self.list_of_external_repo_names[repo.name] = "repository"
            self._update_repo_list()

    def _repo_modify_callback(self):
        text = self._repo_list_widget.selectedItems()[0].text()
        if self.list_of_external_repo_names[text] == "repository":
            repo = deepcopy(self.repositories[text])
            repo_name = repo.name
            dialog = RepositoryDialog(repo)
            
            if dialog.exec_():
                self.repositories.pop(repo_name)
                self.repositories[repo.name] = repo
                self.list_of_external_repo_names.pop(repo_name)
                self.list_of_external_repo_names[repo.name] = "repository"
                self._update_repo_list()
                
        if self.list_of_external_repo_names[text] == "package":
            installed_package = deepcopy(self.installed_packages[text])
            old_name = installed_package.name
            dialog = InstalledPackageDialog(installed_package)
            
            if dialog.exec_():
                self.installed_packages.pop(old_name)
                self.installed_packages[installed_package.name] = installed_package
                self.list_of_external_repo_names.pop(old_name)
                self.list_of_external_repo_names[installed_package.name] = "package"
                self._update_repo_list()
            

    def _repo_delete_callback(self):
        repo_name = self._repo_list_widget.selectedItems()[0].text()
        if self.list_of_external_repo_names[repo_name] == "repository":
            self.repositories.pop(repo_name)
        if self.list_of_external_repo_names[repo_name] == "package":
            self.installed_packages.pop(repo_name)
            
        self.list_of_external_repo_names.pop(repo_name)
        self._update_repo_list()
        
    def _update_repo_list(self):
        self._repo_list_widget.clear()
        for item in self.list_of_external_repo_names:
            this_item = QListWidgetItem()
            this_item.setText(item)
            this_item.setToolTip(self.list_of_external_repo_names[item])
            

        
        
    def _update_source_text(self):
        if "\n".join(self.sources) != self._source_text.toPlainText():
            self.sources = self._source_text.toPlainText().split()

            
    def _update_include_text(self):
        if "\n".join(self.includes) != self._includes_text.toPlainText():
            self.includes = self._includes_text.toPlainText().split()
            
    def closeEvent(self, event) -> None:
        
        if os.path.exists(self._instance_cache_location):
            os.remove(self._instance_cache_location)

        return super().closeEvent(event)
    
    def _check_if_creating_dir_in_cache(self,cache_location):
        
        if not os.path.exists(cache_location):
            file = open(cache_location,"x")
            file.close()
            return False
        
        file = open(cache_location,"r")
        try:
            saved_files_dict = json.load(file)
            
        except json.JSONDecodeError:
            file.close()
            return False
            
            
        file.close()
        
        
        
        
        if self._creating_directory in saved_files_dict:
            if cache_location == self._cache_location:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Question)
                msg.setWindowTitle("Creating Directory Conflict")
                msg.setText("An EasyCmake instance was already used on this directory,\nWould you like to load its settings?")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                
                exec_code = msg.exec_()
                
                if exec_code == QMessageBox.No:
                    return False
        else:
            return False
            
        my_settings = saved_files_dict[self._creating_directory]    
        
        self._executable_name.setText(my_settings["executable_name"])
        self._cpp_standard_text.setCurrentIndex(self._cpp_standard_text.findText(my_settings["cpp_version"]))
        self._cmake_version_text.setText(my_settings["cmake_version"])
        self._source_text.setText("\n".join(my_settings["sources"]))
        self._includes_text.setText("\n".join(my_settings["includes"]))
        
        self._repo_list_widget.clear()
        for item in my_settings["repositories"]:
            repo = Repository()
            repo.name = item
            repo.git_repo = my_settings["repositories"][item]["repo"]
            repo.git_tag = my_settings["repositories"][item]["tag"]
            repo.should_build = my_settings["repositories"][item]["should_build"]
            repo.includes = my_settings["repositories"][item]["includes"]
            repo.libraries = my_settings["repositories"][item]["libraries"]
            repo.cmake_args = my_settings["repositories"][item]["cmake_args"]
            
            self.repositories[item] = repo
            
            self.list_of_external_repo_names[item] = "repository"
           
        for item in my_settings["installed_packages"]:
            installed_package = InstalledPackage()
            installed_package.name = item
            installed_package.includes = my_settings["installed_packages"][item]["includes"]
            installed_package.libraries = my_settings["installed_packages"][item]["libraries"]
           
            self.list_of_external_repo_names[item] = "package"
           
        self._update_repo_list()
        
        return True
            
            
    
    def _save_to_cache(self,location):
        
        saving_dict = {
            "executable_name":self._executable_name.text(),
            "cpp_version":self._cpp_standard_text.currentText(),
            "cmake_version":self._cmake_version_text.text(),
            "sources":self.sources,
            "includes":self.includes,
            "repositories":{},
            "installed_packages":{}
        }
        
        for item in self.repositories:
            saving_dict["repositories"][item] = {
                "repo":self.repositories[item].git_repo,
                "tag":self.repositories[item].git_tag,
                "should_build":self.repositories[item].should_build,
                "includes":self.repositories[item].includes,
                "libraries":self.repositories[item].libraries,
                "cmake_args":self.repositories[item].cmake_args
            }
        for item in self.installed_packages:
            installed_package = self.installed_packages[item]
            saving_dict["installed_packages"][item] = {
                "package_name":installed_package.name,
                "includes":installed_package.includes,
                "libraries":installed_package.libraries
            }
        
        file = open(location,"r")
        
        try:
            current_dict = json.load(file)
            
            current_dict[self._creating_directory] = saving_dict
            
            file.close()
            
             
            file = open(location,"w")
            
            file.write(json.dumps(current_dict))
            
            file.close()
            
        
        except json.JSONDecodeError:
            
            current_dict = {}
            
            current_dict[self._creating_directory] = saving_dict
            
            
            file.close()
            
            
            file = open(location,"w")
            
            file.write(json.dumps(current_dict))
            
            file.close()
            
    