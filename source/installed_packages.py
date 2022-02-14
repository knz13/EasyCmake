from dataclasses import dataclass,field
from msilib.schema import InstallExecuteSequence
from typing import List,Dict
from PyQt5.QtWidgets import *


@dataclass
class InstalledPackage:
    name: str =""
    extra_args: str = ""
    includes: List[str] = field(default_factory=list)
    libraries: List[str] = field(default_factory=list)
    required: bool = False
    
    def add_to_dict(self,dict):
        dict["package_name"] = self.name
        dict["extra_args"] = self.extra_args
        dict["required"] = self.required
        dict["includes"] = self.includes
        dict["libraries"] = self.libraries
        
    def get_from_dict(self,dict):
        self.name = dict["package_name"]
        self.extra_args = dict["extra_args"]
        self.required = dict["required"]
        self.includes = dict["includes"]
        self.libraries = dict["libraries"]
    
    
class InstalledPackageDialog(QDialog):

    
    
    def __init__(self,package: InstalledPackage):
        super().__init__()
        
        self.setWindowTitle("New Installed Package")
        
        self._package = package
        self.package_name = QLineEdit(package.name)
        self.package_name.editingFinished.connect(self._package_name_editing_callback)
        
        self.package_extra_args = QLineEdit(package.extra_args)
        self.package_extra_args.editingFinished.connect(self._package_extra_args_callback)
        
        self.is_required_check = QCheckBox()
        self.is_required_check.setCheckState(package.required)
        self.is_required_check.stateChanged.connect(self._required_check_state_callback)
        
        self.includes_text = QTextEdit()
        self.includes_text.setText("\n".join(package.includes))
        self.includes_text.textChanged.connect(self._includes_callback)
        
        self.libraries_text = QTextEdit()
        self.libraries_text.setText("\n".join(package.libraries))
        self.libraries_text.textChanged.connect(self._libraries_callback)
        
        end_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        end_buttons.accepted.connect(self._end_button_accept_callback)
        end_buttons.rejected.connect(self.reject)
        
        
        layout = QFormLayout()

        layout.addRow("Package Name*",self.package_name)
        layout.addRow("Extra Args",self.package_extra_args)
        layout.addRow("Required?",self.is_required_check)
        layout.addRow("Includes",self.includes_text)
        layout.addRow("libraries",self.libraries_text)
        layout.addRow("* = Required",end_buttons)
        
        self.setLayout(layout)
        
    def _package_extra_args_callback(self):
        self._package.extra_args = self.package_extra_args.text()
        
    def _package_name_editing_callback(self):
        
        self._package.name = self.package_name.text()
        
    def _includes_callback(self):
        self._package.includes = self.includes_text.toPlainText().split()
        
    def _libraries_callback(self):
        self._package.libraries = self.libraries_text.toPlainText().split()
        
    def _end_button_accept_callback(self):
        
        if self._package.name == "":
            dialog = QMessageBox()
            dialog.setIcon(QMessageBox.Warning)
            dialog.setText("Please specify a package name")
            dialog.setWindowTitle("Warning!")
            dialog.exec_()
            return
        
        self.accept()
        
    def _required_check_state_callback(self):
        self._package.required = self.is_required_check.checkState()
        
    