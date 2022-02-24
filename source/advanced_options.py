from dataclasses import dataclass,field
from typing import List,Dict
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from copy import deepcopy
from extra_command import *
from additional_lines import *
from public_user_options import *

@dataclass
class AdvancedOptions:
    extra_commands: Dict[str,ExtraCommand]= field(default_factory=dict)
    additional_lines: List[AdditionalLines] = field(default_factory=list)
    public_user_options : Dict[str,PublicUserOption] = field(default_factory=dict)
    
    def get_from_dict(self,dict):
        if "extra_commands" in dict:
            for item in dict["extra_commands"]:
                command = ExtraCommand()
                command.get_from_dict(item)
                self.extra_commands[command.alias] = command
                
        if "additional_lines" in dict:
            for item in dict["additional_lines"]:
                lines = AdditionalLines()
                lines.get_from_dict(item)
                self.additional_lines.append(lines)
        
        if "public_user_options" in dict:
            for item in dict["public_user_options"]:
                user_option = PublicUserOption()
                user_option.get_from_dict(item)
                
                self.public_user_options[user_option.alias] = user_option
    
    def add_to_dict(self,dict):
        dict["extra_commands"] = []
        for item in self.extra_commands.values():
            my_dict = {}
            item.add_to_dict(my_dict)
            dict["extra_commands"].append(my_dict)
        dict["additional_lines"] = []
        for item in self.additional_lines:
            my_dict = {}
            item.add_to_dict(my_dict)
            dict["additional_lines"].append(my_dict)
            
        dict["public_user_options"] = []
        for item in self.public_user_options:
            inside_dict = {}
            self.public_user_options[item].add_to_dict(inside_dict)
            dict["public_user_options"].append(inside_dict)
        
        
            
    def clear(self):
        self.extra_commands.clear()
        self.additional_lines.clear()

    
