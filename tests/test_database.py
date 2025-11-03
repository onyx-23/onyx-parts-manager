import os
import tempfile
import pytest
from pathlib import Path
from src.database.db import Database

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(db_path)
        yield db

def test_add_component(temp_db):
    """Test adding a component to the database."""
    component_id = temp_db.add_component(
        company_part_number="ONX-CAP-001",
        type_name="Capacitor",
        value="100nF",
        description="Ceramic capacitor, 100nF, 50V",
        manufacturer="TDK",
        mpn="C0805C104K5RACTU",
        datasheet_path="",
        stock=100,
        minimum_stock=20
    )
    
    # Verify the component was added
    assert component_id is not None
    assert isinstance(component_id, int)

def test_search_components(temp_db):
    """Test searching components."""
    # Add test components
    temp_db.add_component(
        company_part_number="ONX-CAP-001",
        type_name="Capacitor",
        value="100nF",
        description="Test capacitor 1",
        manufacturer="TDK",
        mpn="C0805C104K5RACTU",
        datasheet_path="",
        stock=100
    )
    temp_db.add_component(
        company_part_number="ONX-RES-001",
        type_name="Resistor",
        value="10k",
        description="Test resistor 1",
        manufacturer="Yageo",
        mpn="RC0805FR-0710KL",
        datasheet_path="",
        stock=50
    )
    
    # Test search by type
    results = temp_db.search_components(type_filter="Capacitor")
    assert len(results) == 1
    assert results[0][2] == "Capacitor"  # type is at index 2
    
    # Test search by value
    results = temp_db.search_components(value_filter="10k")
    assert len(results) == 1
    assert results[0][3] == "10k"  # value is at index 3
    
    # Test search by part number
    results = temp_db.search_components(part_number="ONX-CAP")
    assert len(results) == 1
    assert results[0][1] == "ONX-CAP-001"  # company_part_number is at index 1