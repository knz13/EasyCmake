from dataclasses import dataclass,field
from msilib.schema import InstallExecuteSequence
from typing import List,Dict
from PyQt5.QtWidgets import *


@dataclass
class InstalledPackage:
    name: str =""
    includes: List[str] = field(default_factory=list)
    libraries: List[str] = field(default_factory=list)
    
    
class InstalledPackageDialog(QDialog):

    
    
    def __init__(self,package: InstalledPackage):
        super().__init__()
        
        self.setWindowTitle("New Installed Package")
        
        self._package = package
        self.package_name = QLineEdit(package.name)
        self.includes = QTextEdit()
        self.includes.setText("\n".join(package.includes))
        self.libraries = QTextEdit()
        self.libraries.setText("\n".join(package.libraries))
        
        end_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        end_buttons.accepted.connect(self.accept)
        end_buttons.rejected.connect(self.reject)
        
        
        layout = QFormLayout()

        layout.addRow("Package Name",self.package_name)
        layout.addRow("Includes",self.includes)
        layout.addRow("libraries",self.libraries)
        layout.addRow("* = Required",end_buttons)
        
        self.setLayout(layout)
        
    
        
        