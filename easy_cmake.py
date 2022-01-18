from dataclasses import dataclass,field
from msilib.schema import Icon
import string
from tracemalloc import start
from typing import List,Dict
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator,QDoubleValidator
from PyQt5.QtCore import Qt
from tkinter import filedialog
import sys
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
    
@dataclass
class RepositoryDialog:
    name : QLineEdit = field(default_factory=QLineEdit)
    repo : QLineEdit = field(default_factory=QLineEdit)
    tag : QLineEdit = field(default_factory=QLineEdit)
    should_build : QCheckBox =  field(default_factory=QCheckBox)
    includes : QTextEdit = field(default_factory=QTextEdit)
    libraries : QTextEdit = field(default_factory=QTextEdit)
    cmake_args : QTextEdit = field(default_factory=QTextEdit)
    rows_used : List[int] = field(default_factory=list)
    
    def __post_init__(self):
        self.repo.editingFinished.connect(self._repo_validation_func)

    def _repo_validation_func(self):
        if not self._check_if_repo_exists():
            self.repo.setStyleSheet("background-color: red")
        else:
            self.repo.setStyleSheet("")
            
    
    def _check_if_repo_exists(self):
        git_command = git.cmd.Git()
        try:
            git_command.ls_remote(self.repo.text())
            return True
        except git.GitCommandError:
            return False
    
    def add_to_layout(self,layout : QFormLayout):
        layout.addRow("Name*",self.name)
        layout.addRow("Git Repo*",self.repo)
        layout.addRow("Git Tag",self.tag)
        layout.addRow("Should Build",self.should_build)
        layout.addRow("Include Paths",self.includes)
        layout.addRow("Libraries",self.libraries)
        layout.addRow("Cmake Args",self.cmake_args)
        layout.addRow(QLabel("* = Required"))
        
    def remove_from_layout(layout : QFormLayout,startingPos):
            for i in range(8):
                layout.removeRow(startingPos)
             
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
        repository.includes = self.libraries.toPlainText().split()
        repository.cmake_args = self.cmake_args.toPlainText().split()
        
        return repository
    
    
    
@dataclass
class EasyCmakeApp(QWidget):
    
    #main stuff
    
    sources : List[str] = field(default_factory=list)
    includes : List[str] = field(default_factory=list)
    repositories : Dict[str,Repository] = field(default_factory=dict)
    _repository_window : QWidget = field(default_factory=QWidget)
    _layout : QFormLayout = field(default_factory=QFormLayout)
    _added_modify_parts: bool = False
    _repo_dialog_for_modifying : RepositoryDialog = field(default_factory=RepositoryDialog)
    _last_item_in_modifying: str = ""
    
    #main widgets
    
    _executable_name : QLineEdit = field(default_factory=QLineEdit)
    _source_text : QTextEdit = field(default_factory=QTextEdit)
    _includes_text : QTextEdit = field(default_factory=QTextEdit)
    _repo_combobox : QComboBox = field(default_factory=QComboBox)
    _generate_button : QPushButton = field(default_factory=QPushButton)
    _cmake_version_text : QLineEdit = field(default_factory=QLineEdit)
    
    
    
    
    
    def __post_init__(self):
        super().__init__()
        
        
        self.setFixedSize(700,600)
        
        self._cmake_version_text.setValidator(QDoubleValidator())
        
        self._source_text.textChanged.connect(self._update_source_text)
        self._source_text.setMinimumSize(400,0)
        
        self._includes_text.textChanged.connect(self._update_include_text)
        self._includes_text.setMinimumSize(400,0)
        
        self._repo_combobox.activated.connect(self._repo_combobox_callback)
        self._repo_combobox.addItem("None")
        self._repo_combobox.addItem("Add Item")
        
        
        self._generate_button = QPushButton("Generate")
        self._generate_button.clicked.connect(self._generate_cmake_lists)
        self._generate_button.setMaximumWidth(80)
        
        
        
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
        self._layout.addRow(QLabel("Executable Name*"),self._executable_name)
        
        self._layout.addRow(QLabel("Cmake Version*"),self._cmake_version_text)
        
        self._layout.addRow(QLabel("Source Files*"))
        self._layout.addRow(self._source_text,source_button_layout)
        
        self._layout.addRow(QLabel("Include Directories"))
        self._layout.addRow(self._includes_text,include_button_layout)
        
        self._layout.addRow(QLabel("External Repositories"),self._repo_combobox)
        
        
        self._layout.addRow(self._generate_button)
        
        box = QGroupBox()
        box.setLayout(self._layout)
        scroll = QScrollArea()
        scroll.setWidget(box)
        scroll.setWidgetResizable(True)
        
        layout = QVBoxLayout()
        layout.addWidget(scroll)
        
        
        
        self.setLayout(layout)
        
        
    def _add_source_files(self):
        files = filedialog.askopenfilenames(initialdir=os.curdir,filetypes=[("C++ file",".cpp"),("C++ file",".cc"),("C++ file",".c")])
        
        if files == "":
            return
        
        self.sources = self.sources + list(files)
        
        self._source_text.setText("\n".join(self.sources))
        
    def _add_source_dirs(self):
        files = filedialog.askdirectory(initialdir=os.curdir)
        
        if files == "":
            return
        
        self.sources.append(files)
        
        self._source_text.setText("\n".join(self.sources))
        
    
    def _add_include_dirs(self):
        files = filedialog.askdirectory(initialdir=os.curdir)
        
        if files == "":
            return
        
        self.includes.append(files)
        
        self._includes_text.setText("\n".join(self.includes))
        
    def _repo_combobox_callback(self):
        current_item = self._repo_combobox.itemText(self._repo_combobox.currentIndex())
        if current_item == "Add Item":
            self._repository_window = QWidget()
            new_window_layout = QFormLayout()
            
            repo_dialog = RepositoryDialog()
            
            close_dialog = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            
            close_dialog.accepted.connect(lambda: self._repository_window_close_callback(close_dialog,repo_dialog))
            close_dialog.rejected.connect(self._repository_window.close)
            
            repo_dialog.add_to_layout(new_window_layout)
            
            new_window_layout.addRow(close_dialog)
            
            self._repository_window.setLayout(new_window_layout)
            
            self._repository_window.show()
        elif current_item == "None":
            if self._added_modify_parts:
                self._added_modify_parts = False
                
                self._save_repo_modification()
                
                RepositoryDialog.remove_from_layout(self._layout,self._layout.indexOf(self._layout.findChild(QLabel,"External Repositories"))+3)
                
                
            
        
        else:
            
            if self._added_modify_parts:    
                if(self._last_item_in_modifying != current_item):
                    self._save_repo_modification()
                RepositoryDialog.remove_from_layout(self._layout,self._layout.indexOf(self._layout.findChild(QLabel,"External Repositories"))+3)
                
            if not self._added_modify_parts:
                self._added_modify_parts = True
            
                
            self._repo_dialog_for_modifying = RepositoryDialog()
            self._repo_dialog_for_modifying.set_fields(self.repositories[current_item])
            
            self._repo_dialog_for_modifying.add_to_layout(self._layout)
            
            self._last_item_in_modifying = current_item
            
        
            
            
    def _save_repo_modification(self):
        repo = self._repo_dialog_for_modifying.get_results()
        self.repositories.pop(self._last_item_in_modifying)
        self.repositories[repo.name] = repo
        self._add_items_to_repos()
            
                
            
      
    def _repository_window_close_callback(self,close_button : QPushButton,repo_dialog : RepositoryDialog):
            if not repo_dialog.is_filled():
                message = QMessageBox(icon=QMessageBox.Warning,text="Please fill all required fields.")
                message.setWindowTitle("Error in Easy Cmake!")
                message.exec_()
                return
            
            repo = repo_dialog.get_results()
            self.repositories[repo.name] = repo
            self._repository_window.close()
            self._add_items_to_repos()
            
            
    def _add_items_to_repos(self):
        if len(self.repositories) > 0:
            self._repo_combobox.clear()
            self._repo_combobox.addItem("None")
            for item in self.repositories:
                self._repo_combobox.addItem(item)
            self._repo_combobox.addItem("Add Item")
    
        
        
    def _update_source_text(self):
        if "\n".join(self.sources) != self._source_text.toPlainText():
            self.sources = self._source_text.toPlainText().split()

            
    def _update_include_text(self):
        if "\n".join(self.includes) != self._includes_text.toPlainText():
            self.includes = self._includes_text.toPlainText().split()
            
    def _generate_cmake_lists(self):
        
        if self._executable_name.text() == "":
            QMessageBox.warning(self,"Executable Name Warning!","Please add the executable name")
            return
        
        if self._cmake_version_text.text() == "":
            QMessageBox.warning(self,"Cmake Version Warning!","Please fill the cmake version")
            return
        
        if len(self.sources) == 0:
            QMessageBox.warning(self,"Sources Warning!","Please add at least one source file")
            return
    
    
        
        directory = filedialog.askdirectory(initialdir=os.curdir,title="Choose generate location")
        
        if os.path.isfile(directory + "/CMakeLists.txt"):
            msg = QMessageBox()
            msg.setWindowTitle("Check")
            msg.setText("A CMakeLists.txt file was found in the specified directory,\nwould you like to overwrite it?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            val = msg.exec_()
            if val == QMessageBox.No:
                return
                
        
        source_globs_to_add = []
        source_files = []
        libraries_to_link = []
        dependencies = []
        
        
        string_to_use = f'''
cmake_minimum_required({self._cmake_version_text.text()})
        
#adding extra cmake libs
include(ExternalProject)
include(FetchContent)
        
#creating variables for ease of adding libraries
set(LIBRARIES_TO_BUILD )
set()
        
#project name
project("TestProj")
        
        '''
        if len(self.repositories) > 0:
            for repo_name in self.repositories:
                repo = self.repositories[repo_name]
                if repo.should_build:
                    string_to_use += f'''
                    
ExternalProject_Add({repo_name.upper()}
GIT_REPOSITORY {repo.git_repo}
GIT_TAG {repo.git_tag}
CMAKE_ARGS -DINSTALL_DIR=vendor/{repo_name.lower()}

'''
                    for arg in repo.cmake_args:
                        string_to_use += f'''
            {arg}
                        '''
                    string_to_use += ")"
                    dependencies.append(repo_name.upper())
                    
                else:
                    string_to_use += f'''
                    
FetchContent_Declare({repo_name.upper()}
GIT_REPOSITORY {repo.git_repo}
GIT_TAG {repo.git_tag}
INSTALL_DIR vendor/{repo_name.lower()}
)

FetchContent_MakeAvailable({repo_name.upper()})
                    
                    '''
                for item in repo.includes:
                    self.includes.append(f'''${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()}/{item}''')
                for lib_file in repo.libraries:
                    lib_name = lib_file[lib_file.rfind("/")+1:]
                    lib_location = lib_file[:lib_file.rfind("/")]
                    libraries_to_link.append(f'''${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()}/{lib_location}/${{CMAKE_STATIC_LIBRARY_PREFIX}}{lib_name}${{CMAKE_STATIC_LIBRARY_SUFFIX}}''')
                    
                    
                    
        
        
        index = 1
        for source_file in self.sources:
            if os.path.isdir(source_file):
                string_to_use += f'''
file(GLOB SRC_FILES_{index} ${source_file}/ *.cpp *.cc *.c)'''
                source_globs_to_add.append(f'''${{SRC_FILES_{index}}}''')
                index += 1
            else:
                source_files.append(source_file)
        
        

        if len(libraries_to_link) > 0:
            string_to_use += f'''
#linking libraries
            '''
            
            for item in libraries_to_link:
                string_to_use += f'''
target_link_libraries(${{PROJECT_NAME}} PRIVATE {item})
                '''
        
        if len(self.includes) > 0:
            string_to_use += f'''
#include directories
            
            '''    
            
            for item in self.includes:
                string_to_use += f'''
target_include_directories(${{PROJECT_NAME}} PRIVATE {item})'''
        
        string_to_use += f'''
        
#creating executable
add_executable(${{PROJECT_NAME}} {" ".join(source_globs_to_add)}
{" ".join(source_files)})
        
        '''
        
        if len(dependencies) > 0:
            for item in dependencies:
                
                string_to_use += f'''
add_dependencies(${{PROJECT_NAME}} {item})
                '''
        
        
        
        file = open(directory + "/" + "CMakeLists.txt","w")
        
        file.write(string_to_use)
        
        
        file.close()
        
        
        QMessageBox.warning(self,"Finish","Writing Done!")

        
    

        

    

application = QApplication(sys.argv)
        
app = EasyCmakeApp()

app.show()

sys.exit(application.exec_())