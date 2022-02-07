from dataclasses import dataclass,field
from typing import List,Dict
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator,QDoubleValidator
from PyQt5.QtCore import Qt
from copy import deepcopy
import json
import sys
import os
from main_app import *

        
        
if __name__ == "__main__":

    application = QApplication(sys.argv)
    application.setAttribute(Qt.AA_DisableWindowContextHelpButton)
    
    app = EasyCmakeApp()

    app.show()

    sys.exit(application.exec_())