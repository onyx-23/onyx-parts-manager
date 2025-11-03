import pytest
import tempfile
from pathlib import Path
from src.database.datasheet_manager import DatasheetManager

@pytest.fixture
def temp_datasheet_manager():
    """Create a temporary datasheet manager for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = DatasheetManager(base_path=tmpdir)
        yield manager

def test_store_datasheet(temp_datasheet_manager, tmp_path):
    """Test storing a datasheet file."""
    # Create a test PDF file
    test_pdf = tmp_path / "test.pdf"
    test_pdf.write_bytes(b"%PDF-1.4\n%EOF")  # Minimal valid PDF content
    
    # Store the datasheet
    stored_path = temp_datasheet_manager.store_datasheet(
        component_id="ONX-CAP-001",
        file_path=test_pdf
    )
    
    assert stored_path is not None
    assert stored_path.exists()
    assert stored_path.name == "test.pdf"

def test_get_datasheet_path(temp_datasheet_manager):
    """Test getting the datasheet path."""
    path = temp_datasheet_manager.get_datasheet_path(
        component_id="ONX-CAP-001",
        filename="test.pdf"
    )
    
    assert path is not None
    assert "ONX-CAP-001" in str(path)
    assert path.name == "test.pdf"
    assert path.parent.name == "ONX-CAP-001"