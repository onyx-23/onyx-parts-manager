from typing import Dict, List, Optional, Tuple
from .digikey import DigiKeySupplier
from .mouser import MouserSupplier
from .lcsc import LCSCSupplier

class SupplierManager:
    def __init__(self):
        self.suppliers = {
            'digikey': DigiKeySupplier(),
            'mouser': MouserSupplier(),
            'lcsc': LCSCSupplier()
        }
    
    def get_all_prices(self, part_number: str) -> Dict[str, Optional[Tuple[float, int]]]:
        """Get prices and stock levels from all suppliers for a part number."""
        results = {}
        for supplier_name, supplier in self.suppliers.items():
            try:
                results[supplier_name] = supplier.get_part_info(part_number)
            except Exception as e:
                print(f"Error getting price from {supplier_name}: {e}")
                results[supplier_name] = None
        return results