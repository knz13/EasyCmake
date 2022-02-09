
from select import select
from tokenize import maybe
from advanced_options import *







class AdvancedOptionsDialog(QDialog):
    
    
    
    def __init__(self,options: AdvancedOptions):
        super().__init__()
        
        self.advanced_options = options
        
        self._layout = QVBoxLayout()
        
        self._extra_commands = QListWidget()
        self._extra_commands.setSelectionMode(QAbstractItemView.SingleSelection)
        self._extra_commands.setContextMenuPolicy(Qt.CustomContextMenu)
        self._extra_commands.customContextMenuRequested.connect(self._extra_commands_context_menu)
        self._update_extra_commands_list()
        
        self._additional_lines = QListWidget()
        self._additional_lines.setSelectionMode(QAbstractItemView.SingleSelection)
        self._additional_lines.setContextMenuPolicy(Qt.CustomContextMenu)
        self._additional_lines.setDragDropMode(QAbstractItemView.InternalMove)
        self._additional_lines.model().rowsMoved.connect(self._additional_lines_order_changed)
        self._additional_lines.customContextMenuRequested.connect(self._additional_lines_context_menu)
        
        self._update_additional_lines()
        
        extra_commands_layout = QFormLayout()
        extra_commands_layout.addRow("Extra Commands\n(Right click for options)",self._extra_commands)
        extra_commands_layout.addRow("Additional Lines\n(Right click for options)\n(Drag and drop for ordering)",self._additional_lines)
        
        
        
        end_buttons_layout = QHBoxLayout()
        accept_button = QPushButton("Apply")
        accept_button.clicked.connect(self._ending_event)
        
        reject_button = QPushButton("Cancel")
        reject_button.clicked.connect(self.reject)
        
        end_buttons_layout.addStretch()
        end_buttons_layout.addWidget(accept_button)
        end_buttons_layout.addWidget(reject_button)
        
        self._layout.addLayout(extra_commands_layout)
        self._layout.addLayout(end_buttons_layout)
        
        self.setLayout(self._layout)
        
    def _ending_event(self):
        self._update_additional_lines()
        
        self.accept()
        
    def _additional_lines_order_changed(self):
        current_order = []
        for i in range(self._additional_lines.count()):
            current_order.append(self._additional_lines.item(i).text())
        
        reordered_list = [AdditionalLines() for i in current_order]
        
        for item in self.advanced_options.additional_lines:
            reordered_list[current_order.index(item.alias)] = item
        
        self.advanced_options.additional_lines = reordered_list
        
    def _additional_lines_context_menu(self,position):
        
        menu = QMenu()
        menu.addAction("Add").triggered.connect(self._additional_lines_context_menu_add)
        
        if len(self._additional_lines.selectedItems()) == 1:
            menu.addAction("Modify").triggered.connect(self._additional_lines_context_menu_modify)
            menu.addAction("Delete").triggered.connect(self._additional_lines_context_menu_delete)
        
        menu.exec_(self._additional_lines.mapToGlobal(position))
        
    def _additional_lines_context_menu_add(self):
        line = AdditionalLines()
        
        dialog = line.get_dialog(self,self.advanced_options.additional_lines)
        
        if dialog.exec_():
            self.advanced_options.additional_lines.append(line)
            
            self._update_additional_lines()
            
    def _additional_lines_context_menu_modify(self):
        selected_alias = self._additional_lines.selectedItems()[0].text()
        
        index = 0
        for item in self.advanced_options.additional_lines:
            if item.alias == selected_alias:
                break
            index += 1
            
        original_line = self.advanced_options.additional_lines[index]
        line = deepcopy(original_line)
        self.advanced_options.additional_lines.pop(index)
        
        dialog = line.get_dialog(self,self.advanced_options.additional_lines)
        
        if dialog.exec_():
            self.advanced_options.additional_lines.insert(index,line)
            
            self._update_additional_lines()
            
        else:
            self.advanced_options.additional_lines.insert(index,original_line)
            
            self._update_additional_lines()
            
    def _additional_lines_context_menu_delete(self):
        selected_alias = self._additional_lines.selectedItems()[0].text()
        
        index = 0
        for item in self.advanced_options.additional_lines:
            if item.alias == selected_alias:
                break
            index += 1
        
        self.advanced_options.additional_lines.pop(index)
        
        
        
        self._update_additional_lines()
        
        
            
            
    def _update_additional_lines(self):
        
                
        self._additional_lines.clear()
        
        
        for item in self.advanced_options.additional_lines:
            self._additional_lines.addItem(item.alias)
        
    def _extra_commands_context_menu(self,position):
        
        menu = QMenu()
        menu.addAction("Add").triggered.connect(self._extra_commands_context_menu_add)
        
        if len(self._extra_commands.selectedItems()) == 1:
            menu.addAction("Modify").triggered.connect(self._extra_commands_context_menu_modify)
            menu.addAction("Delete").triggered.connect(self._extra_commands_context_menu_delete)
        
        menu.exec_(self._extra_commands.mapToGlobal(position))
        
    
    def _update_extra_commands_list(self):
        self._extra_commands.clear()
        
        for item in self.advanced_options.extra_commands.values():
            self._extra_commands.addItem(item.alias)
        
    def _extra_commands_context_menu_modify(self):
        original_command = self.advanced_options.extra_commands[self._extra_commands.selectedItems()[0].text()]
        command = deepcopy(original_command)
        self.advanced_options.extra_commands.pop(original_command.alias)
        
        
        dialog = command.get_dialog(self,self.advanced_options.extra_commands)
        
        if dialog.exec_():
            self.advanced_options.extra_commands[command.alias] = command
            self._update_extra_commands_list()
        else:
            self.advanced_options.extra_commands[original_command.alias] = original_command
            self._update_extra_commands_list()
        
    def _extra_commands_context_menu_add(self):
        
        command = ExtraCommand()
        
        dialog = command.get_dialog(self,self.advanced_options.extra_commands)
        
        if dialog.exec_():
            self.advanced_options.extra_commands[command.alias] = command
            
            
            self._update_extra_commands_list()
            
    def _extra_commands_context_menu_delete(self):
        self.advanced_options.extra_commands.pop(self._extra_commands.selectedItems()[0].text())
        self._update_extra_commands_list()
        
        