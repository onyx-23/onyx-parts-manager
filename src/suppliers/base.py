import abc
from typing import Dict, Optional, Tuple

class SupplierBase(abc.ABC):
    """Base class for supplier integrations."""
    
    @abc.abstractmethod
    def get_part_info(self, part_number: str) -> Optional[Tuple[float, int]]:
        """
        Get price and stock information for a part number.
        Returns: Tuple of (price, stock) or None if not found
        """
        pass