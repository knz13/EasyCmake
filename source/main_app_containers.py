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
from advanced_options_dialog import *


@dataclass
class MainAppData:
    sources : List[str] = field(default_factory=list)
    includes : List[str] = field(default_factory=list)
    list_of_external_repo_names: Dict[str,str] = field(default_factory=dict)
    installed_packages: Dict[str,InstalledPackage] = field(default_factory=dict)
    repositories : Dict[str,Repository] = field(default_factory=dict)
    advanced_options : AdvancedOptions = AdvancedOptions()
    
    
    def clear(self):
        self.sources.clear()
        self.includes.clear()
        self.list_of_external_repo_names.clear()
        self.installed_packages.clear()
        self.repositories.clear()
        self.advanced_options.clear()
        
    
    def add_to_dict(self,dict):
        dict["sources"] = self.sources
        dict["includes"] = self.includes
        
        dict["repositories"] = []
        for item in self.repositories:
            inside_dict = {}
            self.repositories[item].add_to_dict(inside_dict)
            dict["repositories"].append(inside_dict)
        
        dict["installed_packages"] = []
        for item in self.installed_packages:
            inside_dict = {}
            self.installed_packages[item].add_to_dict(inside_dict)
            dict["installed_packages"].append(inside_dict)
        
        dict["advanced_options"] = {}
        self.advanced_options.add_to_dict(dict["advanced_options"])
        
        
        
            
            
        
    def get_from_dict(self,dict):
        if "sources" in dict:
            self.sources = dict["sources"]
        
        if "includes" in dict:
            self.includes = dict["includes"]
        
        if "repositories" in dict:
            for item in dict["repositories"]:
                repo = Repository()
                repo.get_from_dict(item)
                
                self.repositories[repo.name] = repo
                
                self.list_of_external_repo_names[repo.name] = "repository"
                
        if "installed_packages" in dict:
            for item in dict["installed_packages"]:
                installed_package = InstalledPackage()
                installed_package.get_from_dict(item)
            
                self.installed_packages[installed_package.name] = installed_package
                self.list_of_external_repo_names[installed_package.name] = "package"
                
        
                 
        if "advanced_options" in dict and len(dict["advanced_options"]) > 0:
            self.advanced_options.get_from_dict(dict["advanced_options"])
        
        
            
            