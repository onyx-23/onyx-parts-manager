import os
import logging
from typing import Optional, Tuple
from .base import SupplierBase
from dotenv import load_dotenv
from src.security import (
    validate_part_number,
    RateLimiter,
    SecureAPIClient,
    mask_sensitive_data
)

load_dotenv()

logger = logging.getLogger(__name__)


class MouserSupplier(SupplierBase):
    """Secure Mouser API integration with rate limiting and input validation."""
    
    def __init__(self):
        self.api_key = os.getenv('MOUSER_API_KEY')
        self.base_url = "https://api.mouser.com/api/v1"
        self.rate_limiter = RateLimiter(max_requests=10, time_window_seconds=60)
        self.client = SecureAPIClient(timeout=30)
        
        # Validate API key on initialization
        if not self.api_key or 'your_' in self.api_key.lower():
            logger.warning("Mouser API key not configured properly")
        else:
            logger.info(f"Mouser API initialized with key: {mask_sensitive_data(self.api_key)}")
        
    def get_part_info(self, part_number: str) -> Optional[Tuple[float, int]]:
        """
        Get price and stock information from Mouser.
        
        Args:
            part_number: The part number to search for
            
        Returns:
            Tuple of (price, stock) or None if not found or error
            
        Security:
            - Input validation to prevent injection
            - Rate limiting to prevent abuse
            - SSL certificate verification
            - Timeout protection
        """
        # SECURITY: Validate input
        if not validate_part_number(part_number):
            logger.error(f"Invalid part number format: {part_number}")
            return None
        
        # SECURITY: Check API key
        if not self.api_key or 'your_' in self.api_key.lower():
            logger.error("Mouser API key not configured")
            return None
        
        # SECURITY: Rate limiting
        if not self.rate_limiter.allow_request('mouser'):
            wait_time = self.rate_limiter.get_wait_time('mouser')
            logger.warning(f"Mouser rate limit exceeded. Wait {wait_time:.1f}s")
            return None
        
        try:
            # Prepare secure API request
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Accept': 'application/json'
            }
            
            # SECURITY: Use HTTPS-only client with SSL verification
            url = f"{self.base_url}/search/partnumber"
            
            # Note: This is a placeholder - actual implementation will depend on Mouser API documentation
            # For now, return None as API is not fully implemented
            logger.info(f"Mouser API call prepared for: {part_number}")
            
            # Actual implementation would be:
            # data = {'SearchByPartRequest': {'mouserPartNumber': part_number}}
            # response = self.client.post(url, headers=headers, data=data)
            # result = response.json()
            # return (result['price'], result['stock'])
            
            return None
            
        except Exception as e:
            # SECURITY: Never expose API keys or sensitive data in errors
            logger.error(f"Mouser API error for part lookup: {str(e)}")
            return None