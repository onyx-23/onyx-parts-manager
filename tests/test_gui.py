import pytest
from PyQt6.QtWidgets import QApplication
from src.gui.widgets.parts_list import PartsList
from src.gui.widgets.datasheet_viewer import DatasheetViewer

@pytest.fixture
def app(qtbot):
    """Create a Qt application."""
    return QApplication([])

@pytest.fixture
def parts_list(app, qtbot):
    """Create a parts list widget for testing."""
    widget = PartsList()
    qtbot.addWidget(widget)
    return widget

def test_parts_list_creation(parts_list):
    """Test that the parts list widget is created correctly."""
    assert parts_list.table is not None
    assert parts_list.table.columnCount() == 8
    headers = [parts_list.table.horizontalHeaderItem(i).text() 
              for i in range(parts_list.table.columnCount())]
    assert headers == [
        "Part Number", "Type", "Value", "Description",
        "Manufacturer P/N", "Stock", "Price", "Datasheet"
    ]

def test_parts_list_update(parts_list):
    """Test updating the parts list with data."""
    test_data = [(1, "ONX-CAP-001", "Capacitor", "100nF", 
                  "Test Cap", "TDK", "C0805C104K5RACTU", "", 
                  100, 20, "2023-01-01", "2023-01-01")]
    
    parts_list.update_parts_list(test_data)
    
    assert parts_list.table.rowCount() == 1
    assert parts_list.table.item(0, 0).text() == "ONX-CAP-001"
    assert parts_list.table.item(0, 1).text() == "Capacitor"
    assert parts_list.table.item(0, 2).text() == "100nF"