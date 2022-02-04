from dataclasses import dataclass,field
from typing import List,Dict
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator,QDoubleValidator
from PyQt5.QtCore import Qt
from copy import deepcopy
import json
import sys
import os
from repository import*
from installed_packages import *


@dataclass
class EasyCmakeApp(QWidget):
    
    #main stuff
    
    sources : List[str] = field(default_factory=list)
    includes : List[str] = field(default_factory=list)
    list_of_external_repo_names: Dict[str,str] = field(default_factory=dict)
    
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
    _create_library_checkbox : QCheckBox = field(default_factory=QCheckBox)
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
        
        
        current_dir = os.path.normpath(os.getcwd()).replace("\\","/")
        self._cache_location = current_dir + "/cache.json"
        self._instance_cache_location = current_dir + "/instance_cache.json"
        
        self.setWindowTitle("Easy Cmake")
        self.setFixedSize(700,600)
        
        self._creating_directory_text.setText(f'''Creating Directory: {current_dir}''')
        self._creating_directory_button.setText("Modify")
        self._creating_directory_button.clicked.connect(self._get_creating_dir)
        
        #self._create_library_checkbox.toggled.connect()
        
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
        
        self._layout.addRow(QLabel("Create Library"),self._create_library_checkbox)
        
        self._layout.addRow(QLabel("Target Name*"),self._executable_name)
        
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
        
        self.sources = self.sources + [os.path.relpath(i,self._creating_directory).replace("\\","/") for i in files[0]]
        
        self._source_text.setText("\n".join(self.sources))
        
    def _add_source_dirs(self):
        
        if self._creating_directory == "":
            QMessageBox.warning(self,"Warning!","Please choose a valid creating directory")
            return
        
        files = QFileDialog.getExistingDirectory(self,"Choose a directory",self._creating_directory)
        
        if files == "":
            return
        
        self.sources.append(os.path.relpath(files,self._creating_directory).replace("\\","/"))
        
        self._source_text.setText("\n".join(self.sources))
        
    
    def _add_include_dirs(self):
        if self._creating_directory == "":
            QMessageBox.warning(self,"Warning!","Please choose a valid creating directory")
            return
        
        files = QFileDialog.getExistingDirectory(self,"Choose a directory to include",self._creating_directory)
        
        if files == "":
            return
        
        self.includes.append(os.path.relpath(files,self._creating_directory).replace("\\","/"))
        
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
            self._repo_list_widget.addItem(this_item)
            

        
        
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
        if "create_library" in my_settings: 
            self._create_library_checkbox.setChecked(my_settings["create_library"])
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
            installed_package.required = my_settings["installed_packages"][item]["required"]
            installed_package.includes = my_settings["installed_packages"][item]["includes"]
            installed_package.libraries = my_settings["installed_packages"][item]["libraries"]
           
            self.installed_packages[item] = installed_package
            self.list_of_external_repo_names[item] = "package"
           
        self._update_repo_list()
        
        return True
            
            
    
    def _save_to_cache(self,location):
        
        saving_dict = {
            "create_library":self._create_library_checkbox.isChecked(),
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
                "required":installed_package.required,
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
            
    def _get_cmake_lists_text(self,directory : str):
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
            
            string_to_use += f'''
            
#-------------- external repositories ---------------
            
            '''
            for repo_name in self.repositories:
                repo = self.repositories[repo_name]
                library_locations = []
                for item in repo.includes:
                    if item == "./":
                       include_directories.append(f'''${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()}''')
                    else:
                        include_directories.append(f'''${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()}/{item}''')
                if len(repo.libraries) > 0:
                    libraries_to_link[repo_name] = []
                    index = 0
                    for lib_file in repo.libraries:
                        
                        lib_name = lib_file[lib_file.rfind("/")+1:]
                        lib_location = lib_file[:lib_file.rfind("/")]
                        if lib_file[len(lib_file) - 1] == "*":
                            lib_name = lib_name[:len(lib_name)-1]
                            libraries_to_link[repo_name].append(f'''${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()}/{lib_location}/${{CMAKE_STATIC_LIBRARY_PREFIX}}{lib_name}$<$<CONFIG:Debug>:d>${{CMAKE_STATIC_LIBRARY_SUFFIX}}''')
                        else:
                            libraries_to_link[repo_name].append(f'''${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()}/{lib_location}/${{CMAKE_STATIC_LIBRARY_PREFIX}}{lib_name}${{CMAKE_STATIC_LIBRARY_SUFFIX}}''')
                        library_locations.append(libraries_to_link[repo_name][index])
                        index += 1
                        
                        
                if repo.should_build:
                    string_to_use += f'''

# repository download for {repo_name.lower()}...
                    
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

# repository download for {repo_name.lower()}...
                    
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
        
        if len(self.installed_packages) > 0:
            string_to_use += f'''
#finding packages...            
'''
        
        for package_name in self.installed_packages:
            package = self.installed_packages[package_name]
            if package.required:
                string_to_use += f'''
    find_package({package.name} REQUIRED)
'''
            else:
                string_to_use += f'''
find_package({package.name})
'''
            if len(package.includes) > 0:
                for item in package.includes:
                    include_directories.append(item)
            if len(package.libraries) > 0:
                libraries_to_link[package.name] = []
                for item in package.libraries:
                    libraries_to_link[package.name].append(item)
        
        
        index = 1
        for source_file in self.sources:
            if os.path.isdir(source_file):
                path = os.path.relpath(source_file,directory).replace("\\","/")
                string_to_use += f'''
file(GLOB SRC_FILES_{index} ${{PROJECT_SOURCE_DIR}}/{path} *.cpp *.cc *.c)'''
                source_globs_to_add.append(f'''${{SRC_FILES_{index}}}''')
                index += 1
            else:
                source_files.append(f'''${{PROJECT_SOURCE_DIR}}/''' + source_file.replace("\\","/"))
        
        source_files_string = "\n\t".join(source_files)
        source_file_globs = "\n\t".join(source_globs_to_add)
        if not self._create_library_checkbox.isChecked():
            string_to_use += f'''

#creating executable
add_executable(${{PROJECT_NAME}}
'''
        else:
            string_to_use += f'''

#creating library
add_library(${{PROJECT_NAME}}
'''
        if len(source_file_globs) > 0:
            string_to_use += f'''
    #source globs...
    {source_file_globs}
    
'''     
        string_to_use += f'''
    #source files...
    {source_files_string}
)
        
#setting c/cpp standard

set_property(TARGET ${{PROJECT_NAME}} PROPERTY CXX_STANDARD {self._cpp_standard_text.currentText()[3:]})

        '''
        
        if self._create_library_checkbox.isChecked():
            string_to_use += f'''

#installing library
install(TARGETS ${{PROJECT_NAME}} DESTINATION lib)

#installing includes
'''
            for item in self.includes:
                if item.endswith("*"):
                    string_to_use += f'''

install(DIRECTORY {item.replace("*","")}/ DESTINATION include)                
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
# ------------- linking libraries -------------
            '''
            
            for item in libraries_to_link:
                string_to_use += f'''

    #linking for {item}...

'''
                for library in libraries_to_link[item]:
                    string_to_use += f'''
    target_link_libraries(${{PROJECT_NAME}} PRIVATE {library})
                '''
        
        include_directories += [f'''${{PROJECT_SOURCE_DIR}}/{i.replace("*","")}''' for i in self.includes]
        
        if len(include_directories) > 0:
            string_to_use += f'''

#------------ include directories -------------

            '''    
            
            for item in include_directories:
                string_to_use += f'''
    target_include_directories(${{PROJECT_NAME}} PRIVATE {item})
    
'''


        return string_to_use
    
    
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
        
        
        self._save_to_cache(self._cache_location)
        
        
        QMessageBox.warning(self,"Finish","Writing Done!")

    