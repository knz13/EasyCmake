from dataclasses import dataclass,field
from msilib.schema import Icon
from sqlite3 import Cursor
import string
from typing import List,Dict
from urllib.error import HTTPError
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator,QDoubleValidator
from PyQt5.QtCore import Qt
from tkinter import filedialog
from copy import deepcopy
import appdirs
import json
import sys
import requests
import os
import git
        
        

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
    
    _repository : Repository
    name : QLineEdit = field(default_factory=QLineEdit)
    repo : QLineEdit = field(default_factory=QLineEdit)
    tag : QLineEdit = field(default_factory=QLineEdit)
    should_build : QCheckBox =  field(default_factory=QCheckBox)
    includes : QTextEdit = field(default_factory=QTextEdit)
    libraries : QTextEdit = field(default_factory=QTextEdit)
    cmake_args : QTextEdit = field(default_factory=QTextEdit)
    
    
    def __init__(self,repository : Repository):
        super().__init__()
        
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
            
    
    def _check_if_repo_exists(self):
        
        text = self.repo.text()
        
        if text[:8] == "https://":
            text = text[8:]
        
        if text[:11] == "github.com/":
            text = text[11:]
        
        
        response = requests.get("https://api.github.com/repos/" + text).json()
        if "message" in response:
            if response["message"] == "Not Found":
                return False
        return True
    
        
    
    def _add_to_layout(self,layout : QFormLayout):
        layout.addRow("Name*",self.name)
        layout.addRow("Git Repo*",self.repo)
        layout.addRow("Git Tag",self.tag)
        layout.addRow("Should Build",self.should_build)
        layout.addRow("Include Paths",self.includes)
        layout.addRow("Libraries",self.libraries)
        layout.addRow("Cmake Args",self.cmake_args)
        layout.addRow(QLabel("* = Required"),self.end_buttons)
        
    
    def set_fields(self,repository: Repository):
        self.name.setText(repository.name)
        self.repo.setText(repository.git_repo)
        self.tag.setText(repository.git_tag)
        self.should_build.setCheckState(repository.should_build)
        self.includes.setText("\n".join(repository.includes))
        self.libraries.setText("\n".join(repository.libraries))
        self.cmake_args.setText("\n".join(repository.cmake_args))
        
    def is_filled(self):
        if self.name.text() == "" or self.repo.text() == "":  
            return False

        return True
        
        
        
    def get_results(self):
        repository = Repository()
        repository.name = self.name.text()
        repository.git_repo = self.repo.text()
        if self.tag.text() == "":
            repository.git_tag = "origin/master"
        else:
            repository.git_tag = self.tag.text()
        repository.should_build = self.should_build.isChecked()
        repository.libraries = self.libraries.toPlainText().split()
        repository.includes = self.includes.toPlainText().split()
        repository.cmake_args = self.cmake_args.toPlainText().split()
        
        return repository
    


    
    
    
@dataclass
class EasyCmakeApp(QWidget):
    
    #main stuff
    
    sources : List[str] = field(default_factory=list)
    includes : List[str] = field(default_factory=list)
    repositories : Dict[str,Repository] = field(default_factory=dict)
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
        self._generate_button.clicked.connect(self._generate_cmake_lists)
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
        add_action = menu.addAction("Add")
        add_action.triggered.connect(self._repo_create_new_callback)
        
        if len(self._repo_list_widget.selectedItems()) == 1:
            modify_action = menu.addAction("Modify")
            modify_action.triggered.connect(self._repo_modify_callback)
        if len(self._repo_list_widget.selectedItems()) >= 1:
            delete_action = menu.addAction("Delete")
            delete_action.triggered.connect(self._repo_delete_callback)
        
        
        menu.exec_(self._repo_list_widget.mapToGlobal(position))
        
        
    def _get_creating_dir(self):
        dir = QFileDialog.getExistingDirectory(self,"Choose a Directory",os.curdir)
        if dir == "":
            return

        self._creating_directory = dir
        
        
        self._creating_directory_text.setText("Creating Directory: " + dir)
        
        self._check_if_creating_dir_in_cache()
                
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
        
    def _repo_create_new_callback(self):
        repo = Repository()
        dialog = RepositoryDialog(repo)
        
        if dialog.exec_():
            self.repositories[repo.name] = repo
            self._update_repo_list()

    def _repo_modify_callback(self):
        
        repo = deepcopy(self.repositories[self._repo_list_widget.selectedItems()[0].text()])
        repo_name = repo.name
        dialog = RepositoryDialog(repo)
        
        if dialog.exec_():
            self.repositories.pop(repo_name)
            self.repositories[repo.name] = repo
            self._update_repo_list()

    def _repo_delete_callback(self):
        repo_name = self._repo_list_widget.selectedItems()[0].text()
        self.repositories.pop(repo_name)
        self._update_repo_list()
        
    def _update_repo_list(self):
        self._repo_list_widget.clear()
        for item in self.repositories:
            self._repo_list_widget.addItem(item)

        
        
    def _update_source_text(self):
        if "\n".join(self.sources) != self._source_text.toPlainText():
            self.sources = self._source_text.toPlainText().split()

            
    def _update_include_text(self):
        if "\n".join(self.includes) != self._includes_text.toPlainText():
            self.includes = self._includes_text.toPlainText().split()
            
    def _get_cmake_lists_text(self,directory):
        source_globs_to_add = []
        source_files = []
        include_directories = []
        libraries_to_link = {}
        any_dependencies = False
        
        
        string_to_use = f'''
#setting cmake version
        
cmake_minimum_required(VERSION {self._cmake_version_text.text()})

#adding useful functions

function(DIR_EXISTS variable dir_path)

file(GLOB ${{variable}}_check ${{dir_path}}/*)

list(LENGTH ${{variable}}_check ${{variable}}_len)

if(${{${{variable}}_len}} EQUAL 0)

set(${{variable}} FALSE PARENT_SCOPE)

else()

set(${{variable}} TRUE PARENT_SCOPE)

endif()

endfunction()

        
#adding extra cmake libs
include(ExternalProject)
include(FetchContent)
        
#creating variables for ease of adding libraries
set(DEPS_TO_BUILD )
        
#project name
project("{self._executable_name.text()}")
        
        '''
        if len(self.repositories) > 0:
            for repo_name in self.repositories:
                repo = self.repositories[repo_name]
                library_locations = []
                for item in repo.includes:
                    if item == "./":
                       include_directories.append(f'''${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()}''')
                    else:
                        include_directories.append(f'''${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()}/{item}''')
                for lib_file in repo.libraries:
                    
                    lib_name = lib_file[lib_file.rfind("/")+1:]
                    lib_location = lib_file[:lib_file.rfind("/")]
                    if lib_file[len(lib_file) - 1] == "*":
                        lib_name = lib_name[:len(lib_name)-1]
                        libraries_to_link[repo_name] = f'''${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()}/{lib_location}/${{CMAKE_STATIC_LIBRARY_PREFIX}}{lib_name}$<IF:$<CONFIG:Debug>,d,"">${{CMAKE_STATIC_LIBRARY_SUFFIX}}'''
                    else:
                        libraries_to_link[repo_name] = f'''${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()}/{lib_location}/${{CMAKE_STATIC_LIBRARY_PREFIX}}{lib_name}${{CMAKE_STATIC_LIBRARY_SUFFIX}}'''
                    library_locations.append(libraries_to_link[repo_name])
                
                if repo.should_build:
                    string_to_use += f'''
dir_exists({repo_name.lower()}_exists ${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()})

if(NOT ${{{repo_name.lower()}_exists}})
    ExternalProject_Add({repo_name.upper()}
    GIT_REPOSITORY {repo.git_repo}
    GIT_TAG {repo.git_tag}
    CMAKE_ARGS  -DCMAKE_INSTALL_PREFIX:PATH=${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()}'''
                    for arg in repo.cmake_args:
                        string_to_use += f'''
                {arg}
                        '''
                    string_to_use += f'''
    BUILD_BYPRODUCTS {" ".join(library_locations)}
)
    
    list(APPEND DEPS_TO_BUILD {repo_name.upper()})

endif()


                    '''
                    any_dependencies = True
                    
                else:
                    string_to_use += f'''
                    
dir_exists({repo_name.lower()}_exists ${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()})
                    
                    
if(NOT ${{{repo_name.lower()}_exists}})
    FetchContent_Declare({repo_name.upper()}
    GIT_REPOSITORY {repo.git_repo}
    GIT_TAG {repo.git_tag}
    SOURCE_DIR ${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()}
    )

    FetchContent_MakeAvailable({repo_name.upper()})

endif()
                    
                    '''
                    
        index = 1
        for source_file in self.sources:
            if os.path.isdir(source_file):
                path = os.path.relpath(source_file,directory).replace("\\","/")
                string_to_use += f'''
file(GLOB SRC_FILES_{index} ${{PROJECT_SOURCE_DIR}}/{path} *.cpp *.cc *.c)'''
                source_globs_to_add.append(f'''${{SRC_FILES_{index}}}''')
                index += 1
            else:
                source_files.append(f'''${{PROJECT_SOURCE_DIR}}/''' + os.path.relpath(source_file,directory).replace("\\","/"))
        
        string_to_use += f'''
        
#creating executable
add_executable(${{PROJECT_NAME}} {" ".join(source_globs_to_add)}
{" ".join(source_files)})
        
#setting c/cpp standard

set_property(TARGET ${{PROJECT_NAME}} PROPERTY CXX_STANDARD {self._cpp_standard_text.currentText()[3:]})
        
        '''
        
        if any_dependencies:
            string_to_use += f'''
#adding dependencies

foreach(X ${{DEPS_TO_BUILD}})

    add_dependencies(${{PROJECT_NAME}} ${{X}})

endforeach()


            '''

        if len(libraries_to_link) > 0:
            string_to_use += f'''
#linking libraries
            '''
            
            for item in libraries_to_link:
                string_to_use += f'''
                
#linking for {item}...

target_link_libraries(${{PROJECT_NAME}} PRIVATE {libraries_to_link[item]})
                '''
        
        include_directories += [f'''${{PROJECT_SOURCE_DIR}}/{os.path.relpath(i,directory)}''' for i in self.includes]
        
        if len(include_directories) > 0:
            string_to_use += f'''
#include directories
            
            '''    
            
            for item in include_directories:
                string_to_use += f'''
target_include_directories(${{PROJECT_NAME}} PRIVATE {item})'''
        
        
        return string_to_use
    
    def _check_if_creating_dir_in_cache(self):
        
        if not os.path.exists(self._cache_location):
            file = open(self._cache_location,"x")
            file.close()
            return
        
        file = open(self._cache_location,"r")
        try:
            saved_files_dict = json.load(file)
            
        except json.JSONDecodeError:
            file.close()
            return
            
            
        file.close()
        
        
        
        
        if self._creating_directory in saved_files_dict:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle("Creating Directory Conflict")
            msg.setText("An EasyCmake instance was already used on this directory,\nWould you like to load its settings?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            
            exec_code = msg.exec_()
            
            if exec_code == QMessageBox.No:
                return
        else:
            return
            
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
            
            
            self._repo_list_widget.addItem(item)
            
    
    def _save_to_cache(self):
        
        saving_dict = {
            "executable_name":self._executable_name.text(),
            "cpp_version":self._cpp_standard_text.currentText(),
            "cmake_version":self._cmake_version_text.text(),
            "sources":self.sources,
            "includes":self.includes,
            "repositories":{}
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
        
        file = open(self._cache_location,"r")
        
        try:
            current_dict = json.load(file)
            
            current_dict[self._creating_directory] = saving_dict
            
            file.close()
            
             
            file = open(self._cache_location,"w")
            
            file.write(json.dumps(current_dict))
            
            file.close()
            
        
        except json.JSONDecodeError:
            
            current_dict = {}
            
            current_dict[self._creating_directory] = saving_dict
            
            
            file.close()
            
            
            file = open(self._cache_location,"w")
            
            file.write(json.dumps(current_dict))
            
            file.close()
        
        
            
    def _generate_cmake_lists(self):
        
        if self._creating_directory == "":
            QMessageBox.warning(self,"Warning!","Please choose a valid creating directory")
            return
        
        if self._executable_name.text() == "":
            QMessageBox.warning(self,"Executable Name Warning!","Please add the executable name")
            return
        
        if self._cmake_version_text.text() == "":
            QMessageBox.warning(self,"Cmake Version Warning!","Please fill the cmake version")
            return
        
        if len(self.sources) == 0:
            QMessageBox.warning(self,"Sources Warning!","Please add at least one source file")
            return
    
    
        
        directory = self._creating_directory
        
        
        if os.path.isfile(directory + "/CMakeLists.txt"):
            msg = QMessageBox()
            msg.setWindowTitle("Check")
            msg.setText("A CMakeLists.txt file was found in the specified directory,\nare you sure you'd like to overwrite it?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            val = msg.exec_()
            if val == QMessageBox.No:
                return
            else:
                os.remove(directory + "/CMakeLists.txt")
                
        
        string_to_use = self._get_cmake_lists_text(directory)
        
        file = open(directory + "/" + "CMakeLists.txt","w")
        
        file.write(string_to_use)
        
        
        file.close()
        
        
        self._save_to_cache()
        
        
        QMessageBox.warning(self,"Finish","Writing Done!")

        
    



application = QApplication(sys.argv)
        
app = EasyCmakeApp()

app.show()

sys.exit(application.exec_())