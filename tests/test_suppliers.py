import pytest
from unittest.mock import MagicMock, patch
from src.suppliers.base import SupplierBase
from src.suppliers.digikey import DigiKeySupplier
from src.suppliers.mouser import MouserSupplier
from src.suppliers.lcsc import LCSCSupplier

def test_supplier_base_interface():
    """Test that supplier base class enforces interface."""
    with pytest.raises(TypeError):
        SupplierBase()  # Should fail as it's abstract

@pytest.fixture
def mock_supplier():
    """Create a mock supplier for testing."""
    class TestSupplier(SupplierBase):
        def get_part_info(self, part_number):
            return (1.23, 100)  # price, stock
    return TestSupplier()

def test_digikey_supplier():
    """Test DigiKey supplier with mocked API."""
    supplier = DigiKeySupplier()
    with patch.object(supplier, 'api_key', 'test_key'):
        # Mock the API response
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                'UnitPrice': 1.23,
                'QuantityAvailable': 100
            }
            price, stock = supplier.get_part_info('TEST123')
            assert price == 1.23
            assert stock == 100

def test_mouser_supplier():
    """Test Mouser supplier with mocked API."""
    supplier = MouserSupplier()
    with patch.object(supplier, 'api_key', 'test_key'):
        # Mock the API response
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                'Price': 1.23,
                'Stock': 100
            }
            price, stock = supplier.get_part_info('TEST123')
            assert price == 1.23
            assert stock == 100

def test_lcsc_supplier():
    """Test LCSC supplier with mocked API."""
    supplier = LCSCSupplier()
    with patch.object(supplier, 'api_key', 'test_key'):
        # Mock the API response
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                'price': 1.23,
                'stock': 100
            }
            price, stock = supplier.get_part_info('TEST123')
            assert price == 1.23
            assert stock == 100