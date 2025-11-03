from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QComboBox, 
                             QLineEdit, QPushButton, QHBoxLayout, QLabel)
from PyQt6.QtCore import pyqtSignal

class SearchPanel(QWidget):
    search_triggered = pyqtSignal(str, str)  # type, value

    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        # Set dark theme for the panel
        self.setStyleSheet("""
            QWidget {
                background-color: #2D2D2D;
                color: #E0E0E0;
            }
            QLabel {
                color: #E0E0E0;
            }
            QLineEdit {
                background-color: #383838;
                color: #E0E0E0;
                border: 1px solid #404040;
                border-radius: 2px;
                padding: 2px 4px;
            }
            QComboBox {
                background-color: #383838;
                color: #E0E0E0;
                border: 1px solid #404040;
                border-radius: 2px;
                padding: 2px 4px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QPushButton {
                background-color: #6A4C93;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #845EC2;
            }
            QPushButton:pressed {
                background-color: #563D7C;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)  # Add some padding around the edges
        
        # Search filters
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(20)  # Add space between filter sections
        
        # Part number filter
        pn_layout = QVBoxLayout()
        pn_layout.setSpacing(5)  # Space between label and input
        pn_label = QLabel("Part Number")
        pn_layout.addWidget(pn_label)
        self.pn_edit = QLineEdit()
        self.pn_edit.setPlaceholderText("Enter Onyx part number")
        self.pn_edit.setMinimumWidth(200)  # Set minimum width
        pn_layout.addWidget(self.pn_edit)
        filters_layout.addLayout(pn_layout)
        
        # Component type filter
        type_layout = QVBoxLayout()
        type_layout.setSpacing(5)  # Space between label and input
        type_label = QLabel("Component Type")
        type_layout.addWidget(type_label)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["All", "Capacitor", "Resistor", "IC", "Transistor", "Diode", "Inductor"])
        self.type_combo.setMinimumWidth(150)  # Set minimum width
        type_layout.addWidget(self.type_combo)
        filters_layout.addLayout(type_layout)
        
        # Value filter
        value_layout = QVBoxLayout()
        value_layout.setSpacing(5)  # Space between label and input
        value_label = QLabel("Value")
        value_layout.addWidget(value_label)
        self.value_edit = QLineEdit()
        self.value_edit.setPlaceholderText("e.g., 100nF, 10k")
        self.value_edit.setMinimumWidth(150)  # Set minimum width
        value_layout.addWidget(self.value_edit)
        filters_layout.addLayout(value_layout)
        
        # Search button in a vertical layout for alignment
        button_layout = QVBoxLayout()
        button_layout.setSpacing(5)  # Match spacing with other sections
        button_layout.addWidget(QLabel(""))  # Empty label for spacing
        self.search_button = QPushButton("Search")
        self.search_button.setMinimumWidth(80)  # Set minimum width
        self.search_button.setFixedHeight(24)  # Match height with other inputs
        self.search_button.clicked.connect(self.on_search)
        button_layout.addWidget(self.search_button)
        filters_layout.addLayout(button_layout)
        filters_layout.addStretch(1)  # Add stretch at the end to keep everything left-aligned
        
        layout.addLayout(filters_layout)
    
    def on_search(self):
        component_type = self.type_combo.currentText()
        value = self.value_edit.text()
        self.search_triggered.emit(component_type, value)