from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QMessageBox, QHeaderView,
                             QFileDialog, QStyledItemDelegate, QComboBox)
from PyQt6.QtCore import Qt, QMimeData, pyqtSignal, QPoint, QModelIndex
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QDragMoveEvent, QColor

class UnitDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems([
            "Ω", "kΩ", "MΩ", "mΩ",  # Resistor units
            "F", "mF", "µF", "nF", "pF",  # Capacitor units
            "H", "mH", "µH", "nH",  # Inductor units
            "Hz", "kHz", "MHz"  # Frequency units
        ])
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        editor.setCurrentText(value if value else "")
import os
from pathlib import Path
import sqlite3
from src.database.datasheet_manager import DatasheetManager
from src.gui.widgets.component_dialog import ComponentDialog
from src.database.db import Database

class PartsList(QWidget):
    # Signal emitted when the database is updated
    database_updated = pyqtSignal()

    # Define unit mappings
    UNIT_MAPPINGS = {
        "Resistor": {
            "Ω": 1,
            "kΩ": 1000,
            "MΩ": 1000000,
            "mΩ": 0.001
        },
        "Capacitor": {
            "F": 1,
            "mF": 0.001,
            "µF": 0.000001,
            "nF": 0.000000001,
            "pF": 0.000000000001
        },
        "Inductor": {
            "H": 1,
            "mH": 0.001,
            "µH": 0.000001,
            "nH": 0.000000001
        }
    }

    def __init__(self):
        super().__init__()
        self.datasheet_manager = DatasheetManager()
        self.db = Database()
        self.setAcceptDrops(True)  # Enable drag and drop
        self.last_highlighted_row = -1  # Track highlighted row
        self.normal_background = QColor(45, 45, 45)  # Dark theme background
        self.highlight_color = QColor(106, 76, 147, 100)  # Semi-transparent purple
        self.init_ui()
        
    def _parse_value_and_unit(self, value_str: str, component_type: str) -> tuple[float, str]:
        """
        Parse a value string into numeric value and unit.
        
        Args:
            value_str: The value string (e.g., "10k", "100n", "4.7µ")
            component_type: The type of component (Resistor, Capacitor, etc.)
            
        Returns:
            Tuple of (numeric_value, unit_string)
        """
        if not value_str:
            return 0.0, ""
            
        # Common multiplier prefixes
        multipliers = {
            'p': 1e-12,  # pico
            'n': 1e-9,   # nano
            'u': 1e-6,   # micro
            'µ': 1e-6,   # micro (alternative)
            'm': 1e-3,   # milli
            'k': 1e3,    # kilo
            'M': 1e6     # mega
        }
        
        try:
            # Extract numeric part and unit/multiplier
            numeric_part = ""
            unit_part = ""
            for char in value_str:
                if char.isdigit() or char == '.':
                    numeric_part += char
                else:
                    unit_part += char
                    
            numeric_value = float(numeric_part)
            
            # Apply multiplier if present
            if unit_part and unit_part[0] in multipliers:
                numeric_value *= multipliers[unit_part[0]]
            
            # Determine appropriate unit based on component type and value
            unit = ""
            if component_type == "Resistor":
                if numeric_value >= 1e6:
                    numeric_value /= 1e6
                    unit = "MΩ"
                elif numeric_value >= 1e3:
                    numeric_value /= 1e3
                    unit = "kΩ"
                else:
                    unit = "Ω"
            elif component_type == "Capacitor":
                if numeric_value >= 1e-6:
                    numeric_value *= 1e6
                    unit = "µF"
                elif numeric_value >= 1e-9:
                    numeric_value *= 1e9
                    unit = "nF"
                else:
                    numeric_value *= 1e12
                    unit = "pF"
            elif component_type == "Inductor":
                if numeric_value >= 1e-3:
                    numeric_value *= 1e3
                    unit = "mH"
                elif numeric_value >= 1e-6:
                    numeric_value *= 1e6
                    unit = "µH"
                else:
                    numeric_value *= 1e9
                    unit = "nH"
                    
            return round(numeric_value, 3), unit
            
        except (ValueError, TypeError):
            return 0.0, ""
        
    def init_ui(self):
        # Set up the main layout
        self.layout = QVBoxLayout(self)
        
        # Create button layout
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Component")
        self.add_button.clicked.connect(self.show_add_component_dialog)
        button_layout.addWidget(self.add_button)
        button_layout.addStretch()
        self.layout.addLayout(button_layout)
        
        # Create and set up the table
        self.setup_table()
        self.layout.addWidget(self.table)
        
    def add_datasheet_to_component(self, row: int, company_pn: str):
        """Show file dialog and add datasheet to component"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Datasheet",
            "",
            "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return
            
        try:
            # Store the datasheet
            stored_path = self.datasheet_manager.store_datasheet(company_pn, file_path)
            
            if stored_path:
                try:
                    # Update database
                    with self.db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE components SET datasheet_path = ? WHERE company_part_number = ?",
                            (str(stored_path), company_pn)
                        )
                        conn.commit()
                    
                    # Update UI with new datasheet controls
                    container = QWidget()
                    layout = QHBoxLayout(container)
                    layout.setContentsMargins(2, 2, 2, 2)
                    layout.setSpacing(4)
                    
                    # Add View button
                    view_btn = QPushButton("View")
                    view_btn.setMaximumWidth(60)
                    view_btn.clicked.connect(lambda checked, path=stored_path: self.open_datasheet(path))
                    
                    # Add Change button
                    change_btn = QPushButton("Change")
                    change_btn.setMaximumWidth(60)
                    change_btn.clicked.connect(
                        lambda checked, r=row, pn=company_pn: self.add_datasheet_to_component(r, pn)
                    )
                    
                    layout.addWidget(view_btn)
                    layout.addWidget(change_btn)
                    self.table.setCellWidget(row, 11, container)
                    
                    # Emit signal to refresh the display
                    self.database_updated.emit()
                    
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Datasheet added successfully for part {company_pn}"
                    )
                    
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Database Error",
                        f"Failed to update database: {str(e)}"
                    )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to store datasheet. Please check if the file is valid."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to add datasheet: {str(e)}"
            )
        
    def setup_table(self):
        """Create and configure the table widget"""
        self.table = QTableWidget()
        self.table.setColumnCount(12)  # Added Unit column
        self.table.setHorizontalHeaderLabels([
            "Part Number", "Type", "Value", "Unit", "Package", "Footprint", 
            "Voltage", "Description", "Manufacturer P/N", "Stock", 
            "Price", "Datasheet"
        ])
        
        # Style the header and table
        header = self.table.horizontalHeader()
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2D2D2D;
                color: #E0E0E0;
                gridline-color: #404040;
                selection-background-color: #6A4C93;
                selection-color: white;
                alternate-background-color: #353535;
            }
            QHeaderView::section {
                background-color: #4A2C6B;
                color: white;
                padding: 6px;
                font-weight: bold;
                border: none;
                border-right: 1px solid #563D7C;
            }
            QTableWidget::item {
                padding: 4px;
                border: none;
            }
            QPushButton {
                background-color: #6A4C93;
                color: white;
                border: none;
                padding: 6px 10px;
                border-radius: 2px;
                min-width: 70px;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #845EC2;
            }
            QPushButton:pressed {
                background-color: #563D7C;
            }
        """)
        
        # Enable alternating row colors
        self.table.setAlternatingRowColors(True)
        
        # Enable sorting and stretching
        self.table.setSortingEnabled(True)
        header.setStretchLastSection(True)  # Make last column fill remaining space
        
        # Set column widths and fixed sizes where appropriate
        column_widths = [
            (0, 120),  # Part Number
            (1, 100),  # Type
            (2, 80),   # Value
            (3, 60),   # Unit
            (4, 100),  # Package
            (5, 100),  # Footprint
            (6, 80),   # Voltage
            (7, 200),  # Description
            (8, 150),  # Manufacturer P/N
            (9, 80),   # Stock
            (10, 80),  # Price
            (11, 100)  # Datasheet
        ]
        
        # Apply column widths and fix sizes
        for col, width in column_widths:
            self.table.setColumnWidth(col, width)
            if col != 7:  # Allow only Description column to stretch
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            else:
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
                
        # Set up unit delegate for the Unit column
        unit_delegate = UnitDelegate(self.table)
        self.table.setItemDelegateForColumn(3, unit_delegate)
        
        # Make table editable
        self.table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked |
                                 QTableWidget.EditTrigger.EditKeyPressed)
        
        # Ensure gridlines are visible
        self.table.setShowGrid(True)
        self.table.setGridStyle(Qt.PenStyle.SolidLine)
        
        # Enable hover effect
        self.table.setMouseTracking(True)
        
    def update_parts_list(self, parts):
        self.table.setRowCount(0)  # Clear existing items
        
        for part in parts:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Unpack part data (matches updated database columns)
            (id, company_pn, type_, value, package_type, footprint_size,
             voltage_rating, description, manufacturer, mpn, datasheet_path,
             stock, min_stock, created, updated) = part
            
            # Parse value and unit
            numeric_value, unit = self._parse_value_and_unit(value or "", type_)
            
            # Create sortable items for numeric columns
            value_item = QTableWidgetItem()
            value_item.setData(Qt.ItemDataRole.DisplayRole, numeric_value)  # For display
            value_item.setData(Qt.ItemDataRole.UserRole, numeric_value)     # For sorting
            
            stock_item = QTableWidgetItem()
            stock_item.setData(Qt.ItemDataRole.DisplayRole, stock)
            stock_item.setData(Qt.ItemDataRole.UserRole, stock)
            
            # Create items with appropriate alignment
            items = [
                (QTableWidgetItem(company_pn), Qt.AlignmentFlag.AlignLeft),
                (QTableWidgetItem(type_), Qt.AlignmentFlag.AlignLeft),
                (value_item, Qt.AlignmentFlag.AlignRight),  # Numeric value
                (QTableWidgetItem(unit), Qt.AlignmentFlag.AlignLeft),  # Unit
                (QTableWidgetItem(package_type or ""), Qt.AlignmentFlag.AlignLeft),
                (QTableWidgetItem(footprint_size or ""), Qt.AlignmentFlag.AlignLeft),
                (QTableWidgetItem(voltage_rating or ""), Qt.AlignmentFlag.AlignRight),
                (QTableWidgetItem(description or ""), Qt.AlignmentFlag.AlignLeft),
                (QTableWidgetItem(mpn or ""), Qt.AlignmentFlag.AlignLeft),
                (stock_item, Qt.AlignmentFlag.AlignRight),  # Numeric stock
                (QTableWidgetItem("N/A"), Qt.AlignmentFlag.AlignRight)  # Price
            ]
            
            # Set items with alignment
            for col, (item, alignment) in enumerate(items):
                item.setTextAlignment(alignment | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, col, item)
            
            # Create datasheet controls in the last column
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 2, 0, 0)  # Add small top margin
            layout.setSpacing(1)  # Reduce spacing between buttons
            layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            
            button_style = """
                QPushButton {
                    background-color: #6A4C93;
                    color: white;
                    border: none;
                    border-top-left-radius: 2px;
                    border-top-right-radius: 2px;
                    border-bottom-left-radius: 0px;
                    border-bottom-right-radius: 0px;
                    padding: 0px 8px;
                    min-width: 60px;
                    height: 20px;
                    line-height: 20px;
                    margin: 0px;
                    text-align: center;
                    qproperty-alignment: AlignCenter;
                }
                QPushButton:hover {
                    background-color: #845EC2;
                }
                QPushButton:pressed {
                    background-color: #563D7C;
                }
            """
            
            if datasheet_path and os.path.exists(datasheet_path):
                # Add View button
                view_btn = QPushButton("View")
                view_btn.setStyleSheet(button_style)
                view_btn.clicked.connect(lambda checked, path=datasheet_path: self.open_datasheet(path))
                
                # Add Change button
                change_btn = QPushButton("Change")
                change_btn.setStyleSheet(button_style)
                change_btn.clicked.connect(
                    lambda checked, r=row, pn=company_pn: self.add_datasheet_to_component(r, pn)
                )
                
                layout.addWidget(view_btn)
                layout.addWidget(change_btn)
            else:
                # Add button
                add_btn = QPushButton("Add PDF")
                add_btn.setStyleSheet(button_style)
                add_btn.clicked.connect(
                    lambda checked, r=row, pn=company_pn: self.add_datasheet_to_component(r, pn)
                )
                layout.addWidget(add_btn)
            
            # Make container transparent
            container.setStyleSheet("background-color: transparent;")
            self.table.setCellWidget(row, 11, container)
    
    def open_datasheet(self, path):
        from src.gui.widgets.datasheet_viewer import DatasheetViewer
        viewer = DatasheetViewer(path, self)
        viewer.exec()

    def _clear_row_highlight(self):
        """Clear the highlight from the last highlighted row"""
        if self.last_highlighted_row >= 0:
            # Get the base color based on whether it's an odd or even row
            is_alternate_row = self.last_highlighted_row % 2 == 1
            base_color = QColor("#353535") if is_alternate_row else QColor("#2D2D2D")
            
            for col in range(self.table.columnCount()):
                item = self.table.item(self.last_highlighted_row, col)
                if item:
                    item.setBackground(base_color)
                    
                # Reset button styling if present
                widget = self.table.cellWidget(self.last_highlighted_row, col)
                if widget and isinstance(widget, QPushButton):
                    widget.setStyleSheet("""
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
                    
        self.last_highlighted_row = -1

    def _highlight_row(self, row: int):
        """Highlight a row to indicate it's a valid drop target"""
        self._clear_row_highlight()
        if row >= 0:
            # Use semi-transparent purple highlight for dark theme
            highlight_color = QColor(106, 76, 147, 120)  # Purple with alpha
            
            # Create items if they don't exist and set highlight
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item is None:
                    item = QTableWidgetItem()
                    self.table.setItem(row, col, item)
                item.setBackground(highlight_color)
                
                # Handle cells with widgets (like buttons)
                widget = self.table.cellWidget(row, col)
                if widget:
                    widget.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {highlight_color.name()};
                            color: white;
                            border: none;
                            padding: 4px 8px;
                            border-radius: 2px;
                        }}
                    """)
            
            self.last_highlighted_row = row

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event for PDF files"""
        if event.mimeData().hasUrls():
            # Check if any of the dragged files are PDFs
            urls = event.mimeData().urls()
            if any(url.toLocalFile().lower().endswith('.pdf') for url in urls):
                # Only accept if we're actually over the table widget
                pos = self.table.mapFromGlobal(self.mapToGlobal(event.position().toPoint()))
                if self.table.rect().contains(pos):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent):
        """Handle drag move to highlight the target row"""
        try:
            # Only handle if we're over the table widget
            pos = self.table.mapFromGlobal(self.mapToGlobal(event.position().toPoint()))
            if not self.table.rect().contains(pos):
                self._clear_row_highlight()
                event.ignore()
                return
            
            # Get the current row
            row = self.table.rowAt(pos.y())
            current_row = self.last_highlighted_row
            
            # Only update highlight if we've moved to a different row
            if row != current_row:
                if row >= 0:
                    self._highlight_row(row)
                    event.acceptProposedAction()
                else:
                    self._clear_row_highlight()
                    event.ignore()
            else:
                # Keep the event accepted if we're on a valid row
                if row >= 0:
                    event.acceptProposedAction()
                else:
                    event.ignore()
                    
        except Exception as e:
            print(f"Error in dragMoveEvent: {e}")
            self._clear_row_highlight()
            event.ignore()

    def dragLeaveEvent(self, event):
        """Clear highlighting when drag leaves the widget"""
        self._clear_row_highlight()

    def dropEvent(self, event: QDropEvent):
        """Handle dropping a PDF file onto a component row"""
        try:
            self._clear_row_highlight()  # Clear the highlight
            
            # Validate mime data
            if not event.mimeData():
                event.ignore()
                return
                
            urls = event.mimeData().urls()
            if not urls:
                event.ignore()
                return
                
            # Get PDF files from urls
            pdf_files = []
            for url in urls:
                try:
                    local_file = url.toLocalFile()
                    if local_file.lower().endswith('.pdf'):
                        pdf_files.append(local_file)
                except Exception:
                    continue
            
            if not pdf_files:
                QMessageBox.warning(self, "Error", "Please drop a PDF file.")
                event.ignore()
                return
                
            # Get drop position and validate
            pos = self.table.mapFromGlobal(self.mapToGlobal(event.position().toPoint()))
            if not self.table.rect().contains(pos):
                event.ignore()
                return
                
            # Get the row where the file was dropped
            row = self.table.rowAt(pos.y())
            if row < 0:
                QMessageBox.warning(self, "Error", "Please drop the datasheet on a specific component row.")
                event.ignore()
                return
                
            # Get the component ID and validate
            try:
                company_pn = self.table.item(row, 0).text()
                if not company_pn:
                    raise ValueError("Could not find component part number")
            except (AttributeError, ValueError) as e:
                QMessageBox.critical(self, "Error", str(e))
                event.ignore()
                return
                
            # Store the PDF file
            try:
                pdf_path = pdf_files[0]
                stored_path = self.datasheet_manager.store_datasheet(company_pn, pdf_path)
                
                if not stored_path:
                    raise ValueError("Failed to store the datasheet")
                    
                # Update database
                with self.db.get_connection() as conn:
                    conn.execute(
                        "UPDATE components SET datasheet_path = ?, updated = CURRENT_TIMESTAMP WHERE company_part_number = ?",
                        (str(stored_path), company_pn)
                    )
                    conn.commit()
                
                # Update UI
                datasheet_btn = QPushButton("View")
                datasheet_btn.clicked.connect(lambda checked, path=str(stored_path): self.open_datasheet(path))
                self.table.setCellWidget(row, 11, datasheet_btn)
                
                event.acceptProposedAction()
                QMessageBox.information(self, "Success", f"Datasheet added successfully for part {company_pn}")
                self.database_updated.emit()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to process datasheet: {str(e)}")
                event.ignore()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error: {str(e)}")
            event.ignore()
            self._clear_row_highlight()
            

            
    def show_add_component_dialog(self):
        """Show dialog to add a new component."""
        dialog = ComponentDialog(self)
        if dialog.exec():
            # Get the component data
            data = dialog.get_component_data()
            
            try:
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO components (
                            company_part_number, type_name, value, package_type,
                            footprint_size, voltage_rating, description,
                            manufacturer, mpn, datasheet_path, stock, minimum_stock
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        data["company_part_number"],
                        data["type"],
                        data["value"],
                        data["package_type"],
                        data["footprint_size"],
                        data["voltage_rating"],
                        data["description"],
                        data["manufacturer"],
                        data["mpn"],
                        None,  # datasheet_path
                        data["stock"],
                        0  # minimum_stock
                    ))
                    conn.commit()
                
                # Emit signal to update the display
                self.database_updated.emit()
                
                # Show success message
                QMessageBox.information(
                    self,
                    "Success",
                    "Component added successfully!"
                )
                
            except sqlite3.IntegrityError:
                QMessageBox.critical(
                    self,
                    "Error",
                    "A component with this part number already exists!"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to add component: {str(e)}"
                )