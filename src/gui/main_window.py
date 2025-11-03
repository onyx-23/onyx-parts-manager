from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from src.gui.widgets.search_panel import SearchPanel
from src.gui.widgets.parts_list import PartsList
from src.database.db import Database

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Onyx Parts Manager")
        self.setMinimumSize(1200, 800)
        
        # Initialize database
        self.db = Database()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Set dark theme styling
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2D2D2D;
                color: #E0E0E0;
            }
            QWidget#centralWidget {
                background-color: #2D2D2D;
            }
            QHeaderView {
                background-color: #2D2D2D;
            }
            QTableCornerButton::section {
                background-color: #2D2D2D;
                border: none;
            }
        """)
        main_widget.setObjectName("centralWidget")
        
        # Remove margins to make it look more modern
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Add widgets
        self.search_panel = SearchPanel()
        self.parts_list = PartsList()
        
        layout.addWidget(self.search_panel)
        layout.addWidget(self.parts_list)
        
        # Connect signals
        self.search_panel.search_triggered.connect(self.perform_search)
        self.parts_list.database_updated.connect(lambda: self.perform_search("All", ""))
        
        # Initial search to populate the list
        self.perform_search("All", "")
    
    def perform_search(self, type_filter, value_filter):
        """Search for components and update the parts list."""
        # Clear filters if searching for "All" with no value
        if type_filter == "All" and not value_filter.strip():
            # Show all components
            results = self.db.search_components()
        else:
            # Search with filters
            results = self.db.search_components(type_filter, value_filter)
            
        self.parts_list.update_parts_list(results)