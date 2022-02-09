from dataclasses import dataclass,field
from typing import List,Dict
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from copy import deepcopy
from extra_command import *
from additional_lines import *

@dataclass
class AdvancedOptions:
    extra_commands: Dict[str,ExtraCommand]= field(default_factory=dict)
    additional_lines: List[AdditionalLines] = field(default_factory=list)
    
    def get_from_dict(self,dict):
        for item in dict["extra_commands"]:
            command = ExtraCommand()
            command.get_from_dict(item)
            self.extra_commands[command.alias] = command
        for item in dict["additional_lines"]:
            lines = AdditionalLines()
            lines.get_from_dict(item)
            self.additional_lines.append(lines)
    
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
            
            
    def clear(self):
        self.extra_commands.clear()
        self.additional_lines.clear()

    
