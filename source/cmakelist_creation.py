from dataclasses import dataclass,field
from msilib.schema import Icon
from sqlite3 import Cursor
from typing import List,Dict
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator,QDoubleValidator
from PyQt5.QtCore import Qt
from copy import deepcopy
import json
import sys
import os



def get_cmake_lists_text(app,directory : str):
        source_globs_to_add = []
        source_files = []
        include_directories = []
        libraries_to_link = {}
        any_dependencies = False
        
        
        string_to_use = f'''
#setting cmake version
        
cmake_minimum_required(VERSION {app._cmake_version_text.text()})

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
project("{app._executable_name.text()}")
        
        '''
        if len(app.repositories) > 0:
            for repo in app.repositories:
                repo_name = repo.name
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
                        libraries_to_link[repo_name] = f'''${{PROJECT_SOURCE_DIR}}/vendor/{repo_name.lower()}/{lib_location}/${{CMAKE_STATIC_LIBRARY_PREFIX}}{lib_name}$<$<CONFIG:Debug>:d>${{CMAKE_STATIC_LIBRARY_SUFFIX}}'''
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
        for source_file in app.sources:
            if os.path.isdir(source_file):
                path = os.path.relpath(source_file,directory).replace("\\","/")
                string_to_use += f'''
file(GLOB SRC_FILES_{index} ${{PROJECT_SOURCE_DIR}}/{path} *.cpp *.cc *.c)'''
                source_globs_to_add.append(f'''${{SRC_FILES_{index}}}''')
                index += 1
            else:
                source_files.append(f'''${{PROJECT_SOURCE_DIR}}/''' + os.path.relpath(source_file,directory).replace("\\","/"))
        
        source_files_string = "\n\t".join(source_files)
        source_file_globs = "\n\t".join(source_globs_to_add)
        string_to_use += f'''
        
#creating executable
add_executable(${{PROJECT_NAME}} 
    
    #source globs...
    {source_file_globs}
    
    #source files...
    {source_files_string}
)
        
#setting c/cpp standard

set_property(TARGET ${{PROJECT_NAME}} PROPERTY CXX_STANDARD {app._cpp_standard_text.currentText()[3:]})
        
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
        
        include_directories += [f'''${{PROJECT_SOURCE_DIR}}/{os.path.relpath(i,directory)}''' for i in app.includes]
        
        if len(include_directories) > 0:
            string_to_use += f'''
#include directories
            
            '''    
            
            for item in include_directories:
                string_to_use += f'''
target_include_directories(${{PROJECT_NAME}} PRIVATE {item})'''
        
        
        return string_to_use
    
    
def generate_cmake_lists(app):
        
        if app._creating_directory == "":
            QMessageBox.warning(app,"Warning!","Please choose a valid creating directory")
            return
        
        if app._executable_name.text() == "":
            QMessageBox.warning(app,"Executable Name Warning!","Please add the executable name")
            return
        
        if app._cmake_version_text.text() == "":
            QMessageBox.warning(app,"Cmake Version Warning!","Please fill the cmake version")
            return
        
        if len(app.sources) == 0:
            QMessageBox.warning(app,"Sources Warning!","Please add at least one source file")
            return
    
    
        
        directory = app._creating_directory
        
        
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
                
        
        string_to_use = app._get_cmake_lists_text(directory)
        
        file = open(directory + "/" + "CMakeLists.txt","w")
        
        file.write(string_to_use)
        
        
        file.close()
        
        
        app._save_to_cache()
        
        
        QMessageBox.warning(app,"Finish","Writing Done!")
