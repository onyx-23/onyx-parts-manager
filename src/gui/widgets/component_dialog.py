from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QLineEdit, QComboBox, QSpinBox, QPushButton,
                           QDialogButtonBox)

class ComponentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Component")
        self.setModal(True)
        self.setup_ui()
        # Initialize units based on default component type
        self.update_units(self.type_input.currentText())
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Create input fields
        self.pn_input = QLineEdit()
        self.type_input = QComboBox()
        self.type_input.setEditable(True)
        self.type_input.addItems([
            "Resistor", "Capacitor", "Inductor", "IC", "Transistor",
            "Diode", "LED", "Connector", "Switch", "Crystal/Oscillator"
        ])
        
        # Create value input with unit selection
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter numeric value")
        self.unit_input = QComboBox()
        
        # Set up different unit options based on component type
        self.resistor_units = ["Ω", "kΩ", "MΩ", "GΩ"]
        self.capacitor_units = ["pF", "nF", "µF", "mF", "F"]
        self.inductor_units = ["nH", "µH", "mH", "H"]
        self.frequency_units = ["Hz", "kHz", "MHz", "GHz"]
        
        # Package and footprint inputs
        self.package_input = QComboBox()
        self.package_input.setEditable(True)
        self.package_input.addItems([
            "SMD", "Through-Hole", "DIP", "SOIC", "SOT-23", "QFN", "QFP", "BGA",
            "0201", "0402", "0603", "0805", "1206", "1210", "2512"
        ])
        
        self.footprint_input = QLineEdit()
        self.footprint_input.setPlaceholderText("e.g., 3mm x 3mm")
        
        # Voltage rating input with units
        self.voltage_input = QLineEdit()
        self.voltage_input.setPlaceholderText("Enter voltage")
        self.voltage_unit = QComboBox()
        self.voltage_unit.addItems(["V", "mV", "kV"])
        
        # Connect type selection to unit update
        self.type_input.currentTextChanged.connect(self.update_units)
        
        self.desc_input = QLineEdit()
        self.mfg_input = QLineEdit()
        self.mpn_input = QLineEdit()
        self.stock_input = QSpinBox()
        
        # Create layouts for fields with units
        value_layout = QHBoxLayout()
        value_layout.addWidget(self.value_input)
        value_layout.addWidget(self.unit_input)
        
        voltage_layout = QHBoxLayout()
        voltage_layout.addWidget(self.voltage_input)
        voltage_layout.addWidget(self.voltage_unit)
        
        # Add fields to form
        form_layout.addRow("Company Part Number:", self.pn_input)
        form_layout.addRow("Type:", self.type_input)
        form_layout.addRow("Value:", value_layout)
        form_layout.addRow("Package Type:", self.package_input)
        form_layout.addRow("Footprint Size:", self.footprint_input)
        form_layout.addRow("Voltage Rating:", voltage_layout)
        form_layout.addRow("Description:", self.desc_input)
        form_layout.addRow("Manufacturer:", self.mfg_input)
        form_layout.addRow("Manufacturer P/N:", self.mpn_input)
        form_layout.addRow("Stock:", self.stock_input)
        
        # Add form to main layout
        layout.addLayout(form_layout)
        
        # Add OK/Cancel buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def update_units(self, component_type):
        """Update the available units based on the selected component type."""
        self.unit_input.clear()
        
        if component_type == "Resistor":
            self.unit_input.addItems(self.resistor_units)
        elif component_type == "Capacitor":
            self.unit_input.addItems(self.capacitor_units)
        elif component_type == "Inductor":
            self.unit_input.addItems(self.inductor_units)
        elif component_type == "Crystal/Oscillator":
            self.unit_input.addItems(self.frequency_units)
        
        # Set a default unit if available
        if self.unit_input.count() > 0:
            self.unit_input.setCurrentIndex(0)

    def get_component_data(self):
        """Return the component data as a dictionary."""
        # Combine value and unit
        value = self.value_input.text()
        if value and self.unit_input.currentText():
            value = f"{value}{self.unit_input.currentText()}"
            
        # Combine voltage and unit
        voltage = self.voltage_input.text()
        if voltage and self.voltage_unit.currentText():
            voltage = f"{voltage}{self.voltage_unit.currentText()}"
            
        return {
            "company_part_number": self.pn_input.text(),
            "type": self.type_input.currentText(),
            "value": value,
            "package_type": self.package_input.currentText(),
            "footprint_size": self.footprint_input.text(),
            "voltage_rating": voltage,
            "description": self.desc_input.text(),
            "manufacturer": self.mfg_input.text(),
            "mpn": self.mpn_input.text(),
            "stock": self.stock_input.value()
        }