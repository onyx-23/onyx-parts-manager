# Security Implementation - Onyx Parts Manager

## Overview
This document outlines the comprehensive security measures implemented in the Onyx Parts Manager application.

## Security Updates - November 5, 2025

### Critical Security Features Implemented

#### 1. Input Validation & Sanitization
**Location:** `src/security/security_utils.py`

- **Part Number Validation**: Prevents SQL injection and XSS attacks
  - Alphanumeric characters, hyphens, underscores, periods, forward slashes only
  - Maximum length: 100 characters
  - SQL keyword detection and blocking
  
- **Component ID Validation**: Prevents path traversal attacks
  - No directory traversal characters (../, /, \)
  - Alphanumeric with hyphens and underscores only
  
- **String Sanitization**: All user inputs are sanitized
  - Null byte removal
  - Length limits enforced
  - Whitespace trimming

#### 2. API Security
**Location:** `src/suppliers/*.py`

- **Rate Limiting**: Prevents API abuse and DOS attacks
  - Maximum 10 requests per minute per supplier
  - Automatic request queuing and backoff
  
- **SSL/TLS Enforcement**:
  - HTTPS-only connections
  - Certificate verification enabled
  - No fallback to HTTP
  
- **Request Timeouts**: Prevents hanging connections
  - 30-second timeout on all API requests
  - Automatic retry with exponential backoff
  
- **API Key Protection**:
  - Keys never logged or displayed
  - Validation on initialization
  - Masked in logs (only last 4 characters shown)

#### 3. Database Security
**Location:** `src/database/db.py`

- **Parameterized Queries**: All SQL queries use parameters
  - No string concatenation in SQL
  - Protection against SQL injection
  
- **Input Validation**: All inputs validated before database operations
  - Type checking (integers, strings, floats)
  - Length validation
  - Pattern matching for special fields

#### 4. File Operation Security
**Location:** `src/database/datasheet_manager.py`

- **Path Traversal Protection**:
  - All paths validated against base directory
  - No ../ or absolute path access allowed
  
- **File Size Limits**:
  - Maximum file size: 50MB per datasheet
  - Prevents DOS attacks via large files
  
- **File Type Validation**:
  - Only PDF files accepted
  - Extension and MIME type checking
  
- **Filename Sanitization**:
  - Special characters removed
  - Path separators blocked

## Security Constants

```python
MAX_PART_NUMBER_LENGTH = 100
MAX_STRING_LENGTH = 500
MAX_FILE_SIZE_MB = 50
MAX_API_REQUESTS_PER_MINUTE = 10
REQUEST_TIMEOUT_SECONDS = 30
ALLOWED_FILE_EXTENSIONS = {'.pdf'}
```

## Security Classes

### RateLimiter
Prevents API abuse by limiting request frequency.

**Usage:**
```python
from src.security import RateLimiter

limiter = RateLimiter(max_requests=10, time_window_seconds=60)
if limiter.allow_request('api_name'):
    # Make API call
    pass
else:
    wait_time = limiter.get_wait_time('api_name')
    print(f"Rate limited. Wait {wait_time}s")
```

### SecureAPIClient
Provides secure HTTP requests with SSL verification and timeouts.

**Usage:**
```python
from src.security import SecureAPIClient

client = SecureAPIClient(timeout=30)
response = client.get('https://api.example.com/endpoint')
```

## Validation Functions

### validate_part_number(part_number: str) -> bool
Validates part numbers for safe database and API usage.

**Checks:**
- Not empty
- String type
- Length <= 100 characters
- No SQL injection patterns
- Matches safe character pattern

### validate_component_id(component_id: str) -> bool
Validates component IDs for file operations.

**Checks:**
- Not empty
- String type
- Length <= 100 characters
- No path traversal attempts
- Matches safe character pattern

### validate_file_path(file_path: Path, base_directory: Path) -> bool
Ensures files are within allowed directory.

**Checks:**
- Path resolves within base directory
- No directory traversal
- Valid path structure

### validate_file_size(file_path: Path, max_size_mb: int) -> bool
Validates file is not too large.

### validate_file_extension(file_path: Path, allowed_extensions: set) -> bool
Validates file has allowed extension.

## Logging Security

All security-related events are logged:
- Invalid input attempts
- Rate limit violations
- Path traversal attempts
- API errors (without exposing keys)
- File validation failures

**Log Levels:**
- `WARNING`: Suspicious activity detected
- `ERROR`: Security validation failures
- `INFO`: Normal security operations

## Best Practices Enforced

1. **Never Trust User Input**: All inputs validated and sanitized
2. **Principle of Least Privilege**: Files only accessible within designated directories
3. **Defense in Depth**: Multiple layers of validation
4. **Fail Securely**: Operations fail safely with proper error handling
5. **No Sensitive Data in Logs**: API keys and passwords never logged
6. **HTTPS Only**: No unencrypted communications
7. **Regular Expression Validation**: Pattern matching for all critical inputs

## API Key Security

### Storage
- API keys stored in `.env` file (excluded from git)
- Never hardcoded in source code
- Environment variables recommended for production

### Validation
```python
from src.security import validate_api_keys

validation_results = validate_api_keys()
# Returns: {'DIGIKEY_API_KEY': True, 'MOUSER_API_KEY': False, ...}
```

### Masking
```python
from src.security import mask_sensitive_data

masked = mask_sensitive_data(api_key, visible_chars=4)
# Returns: "****************key1"
```

## Threat Model

### Threats Mitigated

1. **SQL Injection**: Parameterized queries + input validation
2. **Path Traversal**: Path validation + sanitization
3. **XSS Attacks**: Input sanitization + output encoding
4. **DOS Attacks**: File size limits + rate limiting
5. **API Key Theft**: Secure storage + masking
6. **Man-in-the-Middle**: SSL/TLS enforcement
7. **Request Timeout**: Timeout protection
8. **Malicious File Upload**: Type + size validation

### Residual Risks

1. **PDF Malware**: No active malware scanning (consider adding)
2. **API Rate Limit Exhaustion**: Client-side only (server limits still apply)
3. **Brute Force**: No authentication system yet

## Compliance

This security implementation follows:
- OWASP Top 10 security practices
- CWE (Common Weakness Enumeration) guidelines
- PCI DSS data protection standards (where applicable)

## Testing Security Features

### Unit Tests Recommended

```python
def test_part_number_validation():
    from src.security import validate_part_number
    
    assert validate_part_number("ABC-123") == True
    assert validate_part_number("ABC'; DROP TABLE--") == False
    assert validate_part_number("../" + "A" * 100) == False

def test_rate_limiting():
    from src.security import RateLimiter
    
    limiter = RateLimiter(max_requests=2, time_window_seconds=60)
    assert limiter.allow_request('test') == True
    assert limiter.allow_request('test') == True
    assert limiter.allow_request('test') == False  # Rate limited
```

## Maintenance

### Regular Updates Required

1. **Dependencies**: Keep all packages updated
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Security Audit**: Review logs regularly
   ```bash
   grep -i "warning\|error" logs/*.log
   ```

3. **Vulnerability Scanning**: Use safety
   ```bash
   pip install safety
   safety check
   ```

## Incident Response

If a security issue is discovered:

1. **Isolate**: Disable affected API integrations
2. **Document**: Log all details of the incident
3. **Patch**: Apply fixes from `src/security/`
4. **Test**: Verify fix doesn't break functionality
5. **Deploy**: Update all installations
6. **Review**: Conduct post-incident review

## Security Contact

For security issues, please report via:
- GitHub Issues (for public vulnerabilities)
- Direct contact (for critical/private issues)

## Changelog

### 2025-11-05: Initial Security Implementation
- Created comprehensive security module
- Added input validation for all user inputs
- Implemented rate limiting for API calls
- Added file operation security (size, type, path validation)
- Enhanced database security with parameterized queries
- Added SSL/TLS enforcement for all API calls
- Implemented secure logging (no sensitive data)

## Future Enhancements

1. **Authentication System**: User login with password hashing
2. **Encryption at Rest**: Encrypt sensitive data in database
3. **Audit Trail**: Comprehensive action logging
4. **Two-Factor Authentication**: For critical operations
5. **PDF Malware Scanning**: Integration with antivirus APIs
6. **API Request Signing**: HMAC-based request signing
7. **Content Security Policy**: For web-based interfaces
