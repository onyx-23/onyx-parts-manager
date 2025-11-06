"""
Security utilities for the Onyx Parts Manager application.
Provides input validation, rate limiting, and secure API client functionality.
"""

import re
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logger = logging.getLogger(__name__)

# Security constants
MAX_PART_NUMBER_LENGTH = 100
MAX_STRING_LENGTH = 500
MAX_FILE_SIZE_MB = 50
MAX_API_REQUESTS_PER_MINUTE = 10
REQUEST_TIMEOUT_SECONDS = 30

# Allowed file extensions
ALLOWED_FILE_EXTENSIONS = {'.pdf'}

# Pattern for safe part numbers (alphanumeric, hyphens, underscores, periods, forward slashes)
PART_NUMBER_PATTERN = re.compile(r'^[A-Za-z0-9\-_./ ]+$')

# Pattern for safe component IDs (alphanumeric, hyphens, underscores)
COMPONENT_ID_PATTERN = re.compile(r'^[A-Za-z0-9\-_]+$')

# Pattern for safe strings (no special SQL/script characters)
SAFE_STRING_PATTERN = re.compile(r'^[A-Za-z0-9\s\-_.,:;()\[\]]+$')


def validate_part_number(part_number: str) -> bool:
    """
    Validate a part number to prevent injection attacks.
    
    Args:
        part_number: The part number to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not part_number:
        return False
    
    if not isinstance(part_number, str):
        return False
    
    # Check length
    if len(part_number) > MAX_PART_NUMBER_LENGTH:
        logger.warning(f"Part number exceeds maximum length: {len(part_number)}")
        return False
    
    # Check for SQL injection patterns
    sql_patterns = ['--', ';', '/*', '*/', 'xp_', 'sp_', 'DROP', 'INSERT', 'DELETE', 'UPDATE', 
                    'EXEC', 'EXECUTE', 'SCRIPT', 'UNION', 'SELECT']
    part_upper = part_number.upper()
    for pattern in sql_patterns:
        if pattern in part_upper:
            logger.warning(f"Potential SQL injection detected in part number: {part_number}")
            return False
    
    # Check against safe pattern
    if not PART_NUMBER_PATTERN.match(part_number):
        logger.warning(f"Part number contains invalid characters: {part_number}")
        return False
    
    return True


def validate_component_id(component_id: str) -> bool:
    """
    Validate a component ID for file operations.
    
    Args:
        component_id: The component ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not component_id:
        return False
    
    if not isinstance(component_id, str):
        return False
    
    # Check length
    if len(component_id) > MAX_PART_NUMBER_LENGTH:
        logger.warning(f"Component ID exceeds maximum length: {len(component_id)}")
        return False
    
    # Check for path traversal attempts
    if '..' in component_id or '/' in component_id or '\\' in component_id:
        logger.warning(f"Path traversal attempt detected in component ID: {component_id}")
        return False
    
    # Check against safe pattern
    if not COMPONENT_ID_PATTERN.match(component_id):
        logger.warning(f"Component ID contains invalid characters: {component_id}")
        return False
    
    return True


def validate_file_path(file_path: Path, base_directory: Path) -> bool:
    """
    Validate that a file path is within the allowed base directory (prevents path traversal).
    
    Args:
        file_path: The file path to validate
        base_directory: The base directory that files must be within
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Resolve to absolute paths
        file_path = Path(file_path).resolve()
        base_directory = Path(base_directory).resolve()
        
        # Check if file is within base directory
        if not str(file_path).startswith(str(base_directory)):
            logger.warning(f"Path traversal attempt detected: {file_path} outside {base_directory}")
            return False
        
        return True
    except (ValueError, OSError) as e:
        logger.error(f"Error validating file path: {e}")
        return False


def sanitize_string(input_string: str, max_length: int = MAX_STRING_LENGTH) -> str:
    """
    Sanitize a string for safe database storage and display.
    
    Args:
        input_string: The string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not input_string:
        return ""
    
    # Convert to string if not already
    input_string = str(input_string)
    
    # Truncate to max length
    if len(input_string) > max_length:
        input_string = input_string[:max_length]
        logger.warning(f"String truncated to {max_length} characters")
    
    # Remove null bytes
    input_string = input_string.replace('\x00', '')
    
    # Strip leading/trailing whitespace
    input_string = input_string.strip()
    
    return input_string


def validate_file_size(file_path: Path, max_size_mb: int = MAX_FILE_SIZE_MB) -> bool:
    """
    Validate that a file is not too large.
    
    Args:
        file_path: Path to the file
        max_size_mb: Maximum allowed size in megabytes
        
    Returns:
        True if valid, False otherwise
    """
    try:
        file_size = file_path.stat().st_size
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_size > max_size_bytes:
            logger.warning(f"File exceeds maximum size: {file_size / 1024 / 1024:.2f}MB > {max_size_mb}MB")
            return False
        
        return True
    except (OSError, ValueError) as e:
        logger.error(f"Error checking file size: {e}")
        return False


def validate_file_extension(file_path: Path, allowed_extensions: set = ALLOWED_FILE_EXTENSIONS) -> bool:
    """
    Validate that a file has an allowed extension.
    
    Args:
        file_path: Path to the file
        allowed_extensions: Set of allowed extensions (e.g., {'.pdf'})
        
    Returns:
        True if valid, False otherwise
    """
    extension = file_path.suffix.lower()
    
    if extension not in allowed_extensions:
        logger.warning(f"Invalid file extension: {extension}")
        return False
    
    return True


class RateLimiter:
    """Rate limiter to prevent API abuse."""
    
    def __init__(self, max_requests: int = MAX_API_REQUESTS_PER_MINUTE, time_window_seconds: int = 60):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in time window
            time_window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = timedelta(seconds=time_window_seconds)
        self.requests: Dict[str, list] = defaultdict(list)
        logger.info(f"RateLimiter initialized: {max_requests} requests per {time_window_seconds}s")
    
    def allow_request(self, identifier: str) -> bool:
        """
        Check if a request is allowed for the given identifier.
        
        Args:
            identifier: Identifier for the requester (e.g., supplier name)
            
        Returns:
            True if request is allowed, False if rate limited
        """
        now = datetime.now()
        
        # Clean old requests outside the time window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.time_window
        ]
        
        # Check if limit is exceeded
        if len(self.requests[identifier]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for {identifier}")
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True
    
    def get_wait_time(self, identifier: str) -> float:
        """
        Get the time to wait before next request is allowed.
        
        Args:
            identifier: Identifier for the requester
            
        Returns:
            Seconds to wait, or 0 if request is allowed now
        """
        if self.allow_request(identifier):
            # Remove the request we just added for checking
            self.requests[identifier].pop()
            return 0.0
        
        # Calculate wait time until oldest request expires
        if self.requests[identifier]:
            oldest_request = min(self.requests[identifier])
            wait_until = oldest_request + self.time_window
            wait_seconds = (wait_until - datetime.now()).total_seconds()
            return max(0.0, wait_seconds)
        
        return 0.0


class SecureAPIClient:
    """Secure HTTP client for API requests."""
    
    def __init__(self, timeout: int = REQUEST_TIMEOUT_SECONDS):
        """
        Initialize secure API client.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = self._create_session()
        logger.info("SecureAPIClient initialized")
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with security best practices.
        
        Returns:
            Configured requests.Session
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        # Configure adapter with retry
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session
    
    def get(self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        """
        Perform a secure GET request.
        
        Args:
            url: URL to request
            headers: Optional headers
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: On request failure
        """
        # Ensure HTTPS
        if not url.startswith('https://'):
            logger.warning(f"Non-HTTPS URL requested: {url}")
            raise ValueError("Only HTTPS URLs are allowed")
        
        # Set default headers
        if headers is None:
            headers = {}
        
        # Add security headers
        headers.setdefault('User-Agent', 'OnyxPartsManager/1.0')
        
        # Perform request with SSL verification and timeout
        try:
            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout,
                verify=True,  # Always verify SSL certificates
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL verification failed: {e}")
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def post(self, url: str, headers: Optional[Dict[str, str]] = None, data: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """
        Perform a secure POST request.
        
        Args:
            url: URL to request
            headers: Optional headers
            data: Optional data payload
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: On request failure
        """
        # Ensure HTTPS
        if not url.startswith('https://'):
            logger.warning(f"Non-HTTPS URL requested: {url}")
            raise ValueError("Only HTTPS URLs are allowed")
        
        # Set default headers
        if headers is None:
            headers = {}
        
        # Add security headers
        headers.setdefault('User-Agent', 'OnyxPartsManager/1.0')
        headers.setdefault('Content-Type', 'application/json')
        
        # Perform request with SSL verification and timeout
        try:
            response = self.session.post(
                url,
                headers=headers,
                json=data,
                timeout=self.timeout,
                verify=True,  # Always verify SSL certificates
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL verification failed: {e}")
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise


def validate_api_keys() -> Dict[str, bool]:
    """
    Validate that API keys are present and properly formatted.
    
    Returns:
        Dictionary mapping API key names to validation status
    """
    api_keys = {
        'DIGIKEY_API_KEY': os.getenv('DIGIKEY_API_KEY'),
        'MOUSER_API_KEY': os.getenv('MOUSER_API_KEY'),
        'LCSC_API_KEY': os.getenv('LCSC_API_KEY')
    }
    
    validation_results = {}
    
    for key_name, key_value in api_keys.items():
        # Check if key exists and is not empty
        if not key_value or not key_value.strip():
            logger.warning(f"API key not set: {key_name}")
            validation_results[key_name] = False
            continue
        
        # Check if key is not a placeholder
        if 'your_' in key_value.lower() or 'placeholder' in key_value.lower() or 'api_key_here' in key_value.lower():
            logger.warning(f"API key appears to be placeholder: {key_name}")
            validation_results[key_name] = False
            continue
        
        # Check minimum length (most API keys are at least 20 characters)
        if len(key_value) < 20:
            logger.warning(f"API key appears too short: {key_name}")
            validation_results[key_name] = False
            continue
        
        validation_results[key_name] = True
        logger.info(f"API key validated: {key_name}")
    
    return validation_results


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive data for logging (e.g., API keys).
    
    Args:
        data: The sensitive data to mask
        visible_chars: Number of characters to leave visible at the end
        
    Returns:
        Masked string
    """
    if not data or len(data) <= visible_chars:
        return "****"
    
    return "*" * (len(data) - visible_chars) + data[-visible_chars:]
