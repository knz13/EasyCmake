from posixpath import dirname
import string
from xml.etree.ElementInclude import include
from main_app_containers import *


@dataclass
class EasyCmakeApp(QMainWindow):
    
    #main stuff
    
    container : MainAppData = field(default_factory= MainAppData)

    _instance_cache_location: str = ""
    _cache_location : str = ""
    _creating_directory: str = ""
    _repository_window : QDialog = field(default_factory=QDialog)
    _saved_configurations :Dict = field(default_factory=dict)
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
    _advanced_button : QPushButton = field(default_factory=QPushButton)
    _cmake_version_text : QLineEdit = field(default_factory=QLineEdit)

    
    
    
    
    
    def __post_init__(self):
        super().__init__()
        
        
        current_dir = os.path.normpath(os.getcwd()).replace("\\","/")
        self._creating_directory = current_dir
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
        
        self._advanced_button = QPushButton("Advanced")
        self._advanced_button.clicked.connect(self._advanced_button_callback)
        self._advanced_button.setMaximumWidth(80)
        
        
        self._generate_button = QPushButton("Generate")
        self._generate_button.clicked.connect(self._generate_cmake_lists)
        self._generate_button.setMaximumWidth(80)
        
        self._repo_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self._repo_list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self._repo_list_widget.customContextMenuRequested.connect(self._repo_list_context_menu_callback)
        
        
        #source buttons
        
        source_button_layout = QVBoxLayout()
        source_button_add_0 = QPushButton("Add Files")
        source_button_add_0.setContextMenuPolicy(Qt.CustomContextMenu)
        source_button_add_0.customContextMenuRequested.connect(lambda pos: self._custom_context_menu_for_option_addition(source_button_add_0,pos,lambda: self._add_source_files(True)))
        source_button_add_0.clicked.connect(self._add_source_files)
        
        source_button_add_1 = QPushButton("Add Directories")
        source_button_add_1.setContextMenuPolicy(Qt.CustomContextMenu)
        source_button_add_1.customContextMenuRequested.connect(lambda pos: self._custom_context_menu_for_option_addition(source_button_add_1,pos,lambda: self._add_source_dirs(True)))
        source_button_add_1.clicked.connect(self._add_source_dirs)
        
        source_button_layout.addWidget(source_button_add_0)
        source_button_layout.addWidget(source_button_add_1)
        
        #include buttons
        include_button_layout = QVBoxLayout()
        include_button_add = QPushButton("Add Includes")
        include_button_add.setContextMenuPolicy(Qt.CustomContextMenu)
        include_button_add.customContextMenuRequested.connect(lambda pos: self._custom_context_menu_for_option_addition(include_button_add,pos,lambda: self._add_include_dirs(True)))
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
        
        end_buttons_layout = QHBoxLayout()
        end_buttons_layout.addWidget(self._generate_button)
        end_buttons_layout.addStretch()
        end_buttons_layout.addWidget(self._advanced_button)
        
        self._layout.addRow(end_buttons_layout)
        
        
        
        box = QGroupBox()
        box.setLayout(self._layout)
        scroll = QScrollArea()
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(box)
        scroll.setWidgetResizable(True)
        
        
        menuBar = self.menuBar()
        
        menu = menuBar.addMenu("File")
        save_action = menu.addAction("Save Configuration")
        save_action.triggered.connect(self._save_custom_config)
        load_action = menu.addAction("Load Configuration")
        load_action.triggered.connect(self._load_custom_config)
    
        
        self.setCentralWidget(scroll)
        
    def _get_from_dict(self,dict):
        if "create_library" in dict: 
            self._create_library_checkbox.setChecked(dict["create_library"])
        if "executable_name" in dict:
            self._executable_name.setText(dict["executable_name"])
        if "cpp_version" in dict:
            self._cpp_standard_text.setCurrentIndex(self._cpp_standard_text.findText(dict["cpp_version"]))
        if "cmake_version" in dict:
            self._cmake_version_text.setText(dict["cmake_version"])
            
        self.container.get_from_dict(dict)
        
        self._update_all()
        
    def _add_to_dict(self,dict):
        dict["executable_name"] = self._executable_name.text()
        
        dict["create_library"] = self._create_library_checkbox.isChecked()

        dict["cpp_version"] = self._cpp_standard_text.currentText()
        
        dict["cmake_version"] = self._cmake_version_text.text()     
                
        self.container.add_to_dict(dict)
    
    def _load_custom_config(self): #todo
        if len(self._saved_configurations) == 0:
            
            QMessageBox.warning(self,"Error!","No save configurations were found")
            
            return
            
        
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Load Choice")
        dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        
        widget = QListWidget()

        for config_name in self._saved_configurations:
            widget.addItem(config_name)
        
        
        dialog.layout().addWidget(widget,0,0,1,dialog.layout().columnCount())

        if dialog.exec() == QMessageBox.Ok:
            self._get_from_dict(self._saved_configurations[widget.selectedItems()[0].text()])
            
            
        
        
        

    def _save_custom_config(self): #todo
        
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Save Location")
        dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        
        layout = QFormLayout()
        text = QLineEdit()
        widget = QWidget()
        
        layout.addRow("Save Name:",text)
        
        widget.setLayout(layout)
        
        dialog.layout().addWidget(widget,0,0,1,dialog.layout().columnCount())
        
        if dialog.exec_() == QMessageBox.Ok:
            
            saving_dict = {}
            self._add_to_dict(saving_dict)
            
            self._saved_configurations[text.text()] = saving_dict
            
        else:
            pass
            
            
        
    def _custom_context_menu_for_option_addition(self,caller,position,function):
        
        if len(self.container.advanced_options.public_user_options) == 0:
            return
        
        menu = QMenu(self)
        
        action = menu.addAction("Add for specific options")
        action.triggered.connect(function)
        
        menu.exec_(caller.mapToGlobal(position))
        
        
    def _advanced_button_callback(self):
        dialog = AdvancedOptionsDialog(deepcopy(self.container.advanced_options),self.container)
        if dialog.exec_():
            self.container.advanced_options = dialog.advanced_options
            self._update_all()
    
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
        
        self._source_text.clear()
        
        self._includes_text.clear()
        
        self.container.clear()
        
        self._update_all()
        
        
    def _get_creating_dir(self):
        
        if self._creating_directory != "":
            if not os.path.exists(self._instance_cache_location):
                open(self._instance_cache_location,"x").close()
            self._save_to_cache(self._instance_cache_location)

            self._clear_fields()
        
        dir = QFileDialog.getExistingDirectory(self,"Choose a Directory",os.curdir)
        if dir == "":
            return

        self._creating_directory = dir
        
        
        self._creating_directory_text.setText("Creating Directory: " + dir)
        
        if not self._check_if_creating_dir_in_cache(self._instance_cache_location):
            self._check_if_creating_dir_in_cache(self._cache_location)
        
        
    def _create_options_dialog_for_addition(self):
        
        dialog = QMessageBox(self)
        
        dialog.setWindowTitle("Options Message")
        dialog.setText("Choose all the options that you want this choice to depend on.")
        
        list_of_choices = [False for i in self.container.advanced_options.public_user_options]
        list_of_options = list(self.container.advanced_options.public_user_options.keys())
        widget = create_clickable_list_widget(list_of_options,list_of_choices)
        widget.itemChanged.connect(lambda item: create_options_dialog_for_addition_callback(item,list_of_options,list_of_choices))
        
        dialog.layout().addWidget(widget,0,0,1,dialog.layout().columnCount())
        
        return dialog,list_of_options,list_of_choices
        
                
    def _add_source_files(self,search_for_options=False):
        
        if self._creating_directory == "":
            QMessageBox.warning(self,"Warning!","Please choose a valid creating directory")
            return
        
        files = QFileDialog.getOpenFileNames(self,"Choose files to add",self._creating_directory,"C/C++ files (*.cpp *.cc *.c)")
        
        if files[0] == []:
            return
        
        
        
        
        file_names = [os.path.relpath(i,self._creating_directory).replace("\\","/") for i in files[0]]
        
        
        
        
        if search_for_options:
            
            dialog,options,choices = self._create_options_dialog_for_addition()
            
            dialog.exec_()
            
            for file in file_names:
                file += "*depends_on="
                for option,choice in zip(options,choices):
                    if choice:
                        file += option
                        file += ","
                file = file[:-1]
                file += "*"
        
        self.container.sources = self.container.sources + file_names
        self._source_text.setText("\n".join(self.container.sources))
        
    def _add_source_dirs(self,search_for_options=False):
        
        if self._creating_directory == "":
            QMessageBox.warning(self,"Warning!","Please choose a valid creating directory")
            return
        
        dir = QFileDialog.getExistingDirectory(self,"Choose a directory",self._creating_directory)
        
        if dir == "":
            return
        
        dir_name = os.path.relpath(dir,self._creating_directory).replace("\\","/")
        
        
        
        if search_for_options:
            
            dialog,options,choices = self._create_options_dialog_for_addition()
            
            dialog.exec_()
            
            dir_name += "*depends_on="
            for option,choice in zip(options,choices):
                if choice:
                    dir_name += option
                    dir_name += ","
            dir_name = dir_name[:-1]
            dir_name += "*"
        
        
        self.container.sources.append(dir_name)
        self._source_text.setText("\n".join(self.container.sources))
        
        
        
    
    def _add_include_dirs(self,search_for_options=False):
        if self._creating_directory == "":
            QMessageBox.warning(self,"Warning!","Please choose a valid creating directory")
            return
        
        files = QFileDialog.getExistingDirectory(self,"Choose a directory to include",self._creating_directory)
        
        if files == "":
            return
        
        include_dir = os.path.relpath(files,self._creating_directory).replace("\\","/")
        
        if search_for_options:
            
            dialog,options,choices = self._create_options_dialog_for_addition()
            
            dialog.exec_()
            
            include_dir += "*depends_on="
            for option,choice in zip(options,choices):
                if choice:
                    include_dir += option
                    include_dir += ","
            include_dir = include_dir[:-1]
            include_dir += "*" 
        self.container.includes.append(include_dir)
        
        self._includes_text.setText("\n".join(self.container.includes))
        
    def _add_new_installed_package(self):
        installed_package = InstalledPackage()
        dialog = InstalledPackageDialog(installed_package)
        
        if dialog.exec_():
            self.container.installed_packages[installed_package.name] = installed_package
            self.container.list_of_external_repo_names[installed_package.name] = "package"
            self._update_repo_list()
        
    def _create_new_repo_callback(self):
        repo = Repository()
        dialog = RepositoryDialog(repo,self.container.advanced_options.public_user_options)
        
        if dialog.exec_():
            self.container.repositories[repo.name] = repo
            self.container.list_of_external_repo_names[repo.name] = "repository"
            self._update_repo_list()

    def _repo_modify_callback(self):
        text = self._repo_list_widget.selectedItems()[0].text()
        if "*" in text:
            text = text[:text.index("*")-1]
        if self.container.list_of_external_repo_names[text] == "repository":
            repo = deepcopy(self.container.repositories[text])
            repo_name = repo.name
            dialog = RepositoryDialog(repo,self.container.advanced_options.public_user_options)
            
            if dialog.exec_():
                self.container.repositories.pop(repo_name)
                self.container.repositories[repo.name] = repo
                self.container.list_of_external_repo_names.pop(repo_name)
                self.container.list_of_external_repo_names[repo.name] = "repository"
                self._update_repo_list()
                
        if self.container.list_of_external_repo_names[text] == "package":
            installed_package = deepcopy(self.container.installed_packages[text])
            old_name = installed_package.name
            dialog = InstalledPackageDialog(installed_package)
            
            if dialog.exec_():
                self.container.installed_packages.pop(old_name)
                self.container.installed_packages[installed_package.name] = installed_package
                self.container.list_of_external_repo_names.pop(old_name)
                self.container.list_of_external_repo_names[installed_package.name] = "package"
                self._update_repo_list()
            

    def _repo_delete_callback(self):
        repo_name = self._repo_list_widget.selectedItems()[0].text()
        if "*" in repo_name:
            repo_name = repo_name[:repo_name.index("*")-1]
        if self.container.list_of_external_repo_names[repo_name] == "repository":
            self.container.repositories.pop(repo_name)
        if self.container.list_of_external_repo_names[repo_name] == "package":
            self.container.installed_packages.pop(repo_name)
            
        self.container.list_of_external_repo_names.pop(repo_name)
        self._update_repo_list()
        
    def _update_repo_list(self):
        self._repo_list_widget.clear()
        for item in self.container.list_of_external_repo_names:
            this_item = QListWidgetItem()
            if self.container.list_of_external_repo_names[item] == "repository":
                if self.container.repositories[item].depends_on != "":
                    this_item.setText(item + f''' *{self.container.repositories[item].depends_on}*''')
                else:
                    this_item.setText(item)
            else:    
                this_item.setText(item)
            this_item.setToolTip(self.container.list_of_external_repo_names[item])
            self._repo_list_widget.addItem(this_item)
            
    def _update_source_text(self):
        if "\n".join(self.container.sources) != self._source_text.toPlainText():
            self.container.sources = self._source_text.toPlainText().split()

            
    def _update_include_text(self):
        if "\n".join(self.container.includes) != self._includes_text.toPlainText():
            self.container.includes = self._includes_text.toPlainText().split()
            
    def closeEvent(self, event) -> None:
        
        if os.path.exists(self._instance_cache_location):
            os.remove(self._instance_cache_location)

        self._save_to_cache(self._cache_location)

        return super().closeEvent(event)
    
    def _update_all(self):
        self._source_text.setText("\n".join(self.container.sources))
        self._includes_text.setText("\n".join(self.container.includes))
        
        self._update_repo_list()
        
    
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
        
        
        if self._creating_directory in saved_files_dict["Files"]:
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
        
        #clearing fields
        
        self._repo_list_widget.clear()
        self.container.clear()
            
        my_settings = saved_files_dict["Files"][self._creating_directory]
        
        self._get_from_dict(my_settings)
           
        self._update_all()
        
        if "Configurations" in saved_files_dict:
            my_configs = saved_files_dict["Configurations"]
            
            for config_name,my_dict in my_configs.items():
                self._saved_configurations[config_name] = my_dict
        
        
        return True
    
    def _save_to_cache(self,location):
        
        saving_dict = {
            
        }
        
        self._add_to_dict(saving_dict)
        
        
        file = open(location,"r")
        
        try:
            current_dict = json.load(file)
            
            current_dict["Configurations"] = self._saved_configurations
            
            current_dict["Files"][self._creating_directory] = saving_dict
            
            file.close()
            
             
            file = open(location,"w")
            
            file.write(json.dumps(current_dict))
            
            file.close()
            
        
        except json.JSONDecodeError:
            
            current_dict = {"Files":{},"Configurations":{}}
            current_dict["Configurations"] = self._saved_configurations
            
            current_dict["Files"][self._creating_directory] = saving_dict
            
            
            file.close()
            
            
            file = open(location,"w")
            
            file.write(json.dumps(current_dict))
            
            file.close()
           
    def _read_text_options(self,text: str):
        
        if not "*" in text:
            return False,{}
        
        
        options = text[text.index("*"):len(text)-1]
            
    def _get_cmake_lists_text(self,directory : str):
        source_globs_to_add = []
        source_files = []
        include_directories = []
        libraries_to_link = {}
        list_of_commands_per_option = {"":[]}
        
        for item in self.container.advanced_options.public_user_options:
            list_of_commands_per_option[item] = []
        
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
include(GNUInstallDirs)
include(ExternalProject)
include(FetchContent)

'''

        if len(self.container.advanced_options.public_user_options) > 0:
            string_to_use += f'''
#adding options       
     
'''
            for option in self.container.advanced_options.public_user_options.values():
                if len(option.depends_on) > 0:
                    string_to_use += f'''
cmake_dependent_option("{option.option_name.upper()}" '''
                else:
                    string_to_use += f'''
option("{option.option_name.upper()}" '''

                if option.description != "":
                    string_to_use += f'''"{option.description}" '''
                
                if option.default_value:
                    string_to_use += f'''ON '''
                else:
                    string_to_use += f'''OFF '''
                
                if len(option.depends_on) > 0:
                    string_to_use += f'''"'''
                    for item in option.depends_on:
                        string_to_use += item
                        string_to_use += ";"
                    string_to_use = string_to_use[:-1] 
                    string_to_use += f'''" '''
                    if not option.default_value:
                        string_to_use += f'''ON'''
                    else:
                        string_to_use += f'''OFF'''
                
                if string_to_use[-1] == " ":
                    string_to_use = string_to_use[:-1]
                
                string_to_use += f''')

'''

                
        string_to_use += f'''
#project name
project("{self._executable_name.text()}")

#creating variables for ease of adding libraries
set(${{PROJECT_NAME}}_DEPS_TO_BUILD )
set(${{PROJECT_NAME}}_SOURCE_FILES )
set(${{PROJECT_NAME}}_INCLUDES )
set(${{PROJECT_NAME}}_LIBRARIES )

        
        '''
        if len(self.container.repositories) > 0:
            
            
            for repo_name in self.container.repositories:
                repo = self.container.repositories[repo_name]
                
                has_options,options_dict = self._read_text_options(repo_name)
                repo_has_option = has_options and "depends_on" in options_dict
                
                if repo.depends_on == "":
                    list_of_lines = list_of_commands_per_option[""]
                    
                else:
                    list_of_lines = list_of_commands_per_option[repo.depends_on]
                
                list_of_lines.append(f'''

# repository download and settings for {repo_name.lower()}...

    dir_exists({repo_name.lower()}_exists ${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()})
''')
                
                library_locations = []
                
                if len(repo.includes) > 0:
                    
                    list_of_lines.append(f'''

    # adding includes:

''')
                    
                    for item in repo.includes:
                        if item == "./":
                            list_of_lines.append(f'''
        list(APPEND ${{PROJECT_NAME}}_INCLUDES ${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()})
''')
                        else:
                            list_of_lines.append(f'''
        list(APPEND ${{PROJECT_NAME}}_INCLUDES ${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()}/{item})
''')
                            
                if len(repo.sources_to_add) > 0:
                    list_of_lines.append(f'''
    
    # adding sources

''')
                    for source in repo.sources_to_add:
                        list_of_lines.append(f'''
        list(APPEND ${{PROJECT_NAME}}_SOURCE_FILES ${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()}/source)
''')
                            
                if len(repo.libraries) > 0:
                    
                    list_of_lines.append(f'''

    # adding libraries

''')
                    
                    libraries_to_link[repo_name] = []
                    index = 0
                    for lib_file in repo.libraries:
                        
                        lib_name = lib_file[lib_file.rfind("/")+1:]
                        lib_location = lib_file[:lib_file.rfind("/")]
                        if lib_file[len(lib_file) - 1] == "*":
                            lib_name = lib_name[:len(lib_name)-1]
                            file_name = f'''${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()}/{lib_location}/${{CMAKE_STATIC_LIBRARY_PREFIX}}{lib_name}$<$<CONFIG:Debug>:d>${{CMAKE_STATIC_LIBRARY_SUFFIX}}'''
                            libraries_to_link[repo_name].append(file_name)
                            list_of_lines.append(f'''
        list(APPEND ${{PROJECT_NAME}}_LIBRARIES {file_name})
''')
                            library_locations.append(file_name)
                            
                        else:
                            file_name = f'''${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()}/{lib_location}/${{CMAKE_STATIC_LIBRARY_PREFIX}}{lib_name}${{CMAKE_STATIC_LIBRARY_SUFFIX}}'''
                            libraries_to_link[repo_name].append(file_name)
                            list_of_lines.append(f'''
        list(APPEND ${{PROJECT_NAME}}_LIBRARIES {file_name})
''')
                            library_locations.append(file_name)
                        
                        index += 1
                        
                        
                if repo.should_build:
                    list_of_lines.append(f'''

    if(NOT ${{{repo_name.lower()}_exists}} OR NOT ${{${{PROJECT_NAME}}_BUILD_TYPE}} STREQUAL ${{CMAKE_BUILD_TYPE}})
        ExternalProject_Add({repo_name.upper()}
        GIT_REPOSITORY {repo.git_repo}
        GIT_TAG {repo.git_tag}
        CMAKE_ARGS  -DCMAKE_INSTALL_PREFIX:PATH=${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()}
                    -DCMAKE_BUILD_TYPE=${{CMAKE_BUILD_TYPE}}''')
                    for arg in repo.cmake_args:
                        list_of_lines.append(f'''
                    -D{arg}
                        ''')
                    list_of_lines.append(f'''
        BUILD_BYPRODUCTS {" ".join(library_locations)}
        )

        list(APPEND ${{PROJECT_NAME}}_DEPS_TO_BUILD {repo_name.upper()})

    endif()


''')
                    any_dependencies = True
                    
                else:
                    list_of_lines.append(f'''

    if(NOT ${{{repo_name.lower()}_exists}})
        FetchContent_Declare({repo_name.upper()}
        GIT_REPOSITORY {repo.git_repo}
        GIT_TAG {repo.git_tag}
        SOURCE_DIR ${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()}
        )

        FetchContent_MakeAvailable({repo_name.upper()})

    endif()
                    
''')
        
        if len(self.container.installed_packages) > 0:
            pass
        
        for package_name in self.container.installed_packages:
            package = self.container.installed_packages[package_name]
            
            has_options,options_dict = self._read_text_options(package.name)
            package_has_option = has_options and "depends_on" in options_dict
            
            if package_has_option:
                
                list_of_lines = list_of_commands_per_option[options_dict["depends_on"]]
            else:
                list_of_lines = list_of_commands_per_option[""]
            
            list_of_lines.append(f'''

# finding package and adding settings for alias {package.name}...

''')
            
            addition_string = f'''find_package({package_name}'''
            if len(package.extra_args) > 0:
                addition_string += f''' {package.extra_args}'''
            if package.required:
                addition_string += " REQUIRED"
            addition_string += ")"
            list_of_lines.append(f'''
    {addition_string}

''')

            if len(package.includes) > 0:
                list_of_lines.append(f'''
    # adding includes:

''')
                for item in package.includes:
                    list_of_lines.append(f'''
        list(APPEND ${{PROJECT_NAME}}_INCLUDES {item})
''')
            if len(package.libraries) > 0:
                list_of_lines.append(f'''
    # adding libraries:

''')
                libraries_to_link[package.name] = []
                for item in package.libraries:
                    list_of_lines.append(f'''
        list(APPEND ${{PROJECT_NAME}}_LIBRARIES {item})
''')
        
        
        
        
        index = 1
        
        
        
        
        for source_file in self.container.sources:
            
            has_options,options_dict = self._read_text_options(source_file)
            file_has_option = has_options and "depends_on" in options_dict
            
            if file_has_option:
                
                list_of_lines = list_of_commands_per_option[options_dict["depends_on"]]
            else:
                list_of_lines = list_of_commands_per_option[""]
            
            list_of_lines.append(f'''
''')
            
            if os.path.isdir(source_file):
                path = os.path.relpath(source_file,directory).replace("\\","/")
                list_of_lines.append(f'''
file(GLOB SRC_FILES_{index} ${{PROJECT_SOURCE_DIR}}/{path} *.cpp *.cc *.c)
list(APPEND ${{PROJECT_NAME}}_SOURCE_FILES ${{SRC_FILES_{index}}})
''')
                source_globs_to_add.append(f'''${{SRC_FILES_{index}}}''')
                index += 1
            else:
                list_of_lines.append(f'''
list(APPEND ${{PROJECT_NAME}}_SOURCE_FILES ${{PROJECT_SOURCE_DIR}}/''' + source_file.replace("\\","/") + f''')
''')

        for name,commands in list_of_commands_per_option.items():
            if name != "":
                list_of_commands_additions = []
                for command in commands:
                    if command == commands[0]:
                        command = "\t" + command
                    command = command.replace("\n","\n\t")
                    list_of_commands_additions.append(command)
                
                list_of_source_additions = []
                for source_file in self.container.advanced_options.public_user_options[name].option_specific_source_files:
                    list_of_source_additions.append(f'''
    list(APPEND ${{PROJECT_NAME}}_SOURCE_FILES ${{PROJECT_SOURCE_DIR}}/{source_file})

''')
                    

                tab = "\t"
                newline = "\n"
                string_to_use += f'''

if({self.container.advanced_options.public_user_options[name].option_name.upper()})

    #adding compiler definition for this option
    
    add_compile_definitions({self.container.advanced_options.public_user_options[name].option_name.upper()})

    #adding sources specific to this option
    
    {(newline).join(list_of_source_additions)}

{(newline).join(list_of_commands_additions)}

endif()

'''
            
        for command in list_of_commands_per_option[""]:
            string_to_use += command
        
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
        
        string_to_use += f'''
        ${{${{PROJECT_NAME}}_SOURCE_FILES}}
)
        
#setting c/cpp standard

set_property(TARGET ${{PROJECT_NAME}} PROPERTY CXX_STANDARD {self._cpp_standard_text.currentText()[3:]})

        '''
        
        if self._create_library_checkbox.isChecked():
            string_to_use += f'''

#installing library
install(TARGETS ${{PROJECT_NAME}} DESTINATION lib RUNTIME_DEPENDENCIES)

#installing includes
'''
            for item in self.container.includes:
                if item.endswith("*"):
                    installation_location = item[item.index("*")+1:]
                    installation_location = installation_location.replace("*","")
                    
                    string_to_use += f'''

install(DIRECTORY {item[:item.index("*")]} DESTINATION {installation_location} FILES_MATCHING PATTERN "*.h" PATTERN "*.hpp" PATTERN "*.inl")
'''
 
            if len(libraries_to_link) > 0:
                string_to_use += f'''
#installing libraries from dependencies...

'''

            for item in libraries_to_link:
                if item not in self.container.installed_packages:
                    for lib_file in libraries_to_link[item]:
                        string_to_use += f'''
    install(FILES {lib_file} DESTINATION lib)
'''
            string_to_use += f'''
include(CPack)        
'''
        
        if any_dependencies:
            string_to_use += f'''
#adding dependencies

foreach(X ${{${{PROJECT_NAME}}_DEPS_TO_BUILD}})

    add_dependencies(${{PROJECT_NAME}} ${{X}})

endforeach()


            '''
            
        if len(libraries_to_link) > 0:
            string_to_use += f'''
# ------------- linking libraries -------------

    target_link_libraries(${{PROJECT_NAME}} PUBLIC ${{${{PROJECT_NAME}}_LIBRARIES}})

'''
            
        
        include_directories += [i for i in self.container.includes]
        
        if len(include_directories) > 0:
            
            
            
            string_to_use += f'''

#------------ include directories -------------

'''         

            for item in self.container.includes:
                 if "*" in item:
                    string_to_use += f'''
    list(APPEND ${{PROJECT_NAME}}_INCLUDES ${{PROJECT_SOURCE_DIR}}/{item[:item.index("*")]})

'''
                 else:
                    string_to_use +=  f'''
    list(APPEND ${{PROJECT_NAME}}_INCLUDES ${{PROJECT_SOURCE_DIR}}/{item})

''' 


            string_to_use += f'''
    target_include_directories(${{PROJECT_NAME}} PUBLIC ${{${{PROJECT_NAME}}_INCLUDES}})

'''

        if len(self.container.advanced_options.extra_commands) > 0:
            string_to_use += f'''
#------------ custom commands ----------------

'''
            for item in self.container.advanced_options.extra_commands.values():
                string_to_use += f'''
    #custom command for alias {item.alias}...
                
    add_custom_command(TARGET ${{PROJECT_NAME}}
                       {item.execute_time}'''
                for command in item.command:
                    string_to_use += f'''
                       COMMAND {command}'''
                string_to_use += f'''
                       )
    
'''


        if len(self.container.advanced_options.additional_lines) > 0:
            string_to_use += f'''
#------------ additional lines ---------------

'''
            for item in self.container.advanced_options.additional_lines:
                my_str = "\n\t".join(item.lines)
                string_to_use += f'''
    # additional lines for alias "{item.alias}"...

    {my_str}

'''
                
        string_to_use += f'''

# cacheing the build type

set(${{PROJECT_NAME}}_BUILD_TYPE ${{CMAKE_BUILD_TYPE}} CACHE INTERNAL "")
        
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
        
        if len(self.container.sources) == 0:
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

def create_options_dialog_for_addition_callback(item:QListWidgetItem,list_of_options,list_of_choices):
    list_of_choices[list_of_options.index(item.text())] = item.checkState()