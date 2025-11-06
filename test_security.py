"""Test security module functionality."""

from src.security import (
    validate_part_number,
    validate_component_id,
    sanitize_string,
    RateLimiter,
    validate_file_size,
    validate_file_extension
)
from pathlib import Path

print("="*60)
print("SECURITY MODULE TEST")
print("="*60)

# Test 1: Part Number Validation
print("\n1. Part Number Validation:")
print(f"  Valid 'ABC-123': {validate_part_number('ABC-123')}")
print(f"  Valid 'LM5166': {validate_part_number('LM5166')}")
print(f"  Invalid 'DROP TABLE': {validate_part_number('DROP TABLE')}")
print(f"  Invalid '../../../etc/passwd': {validate_part_number('../../../etc/passwd')}")
print(f"  Invalid '; DELETE FROM--': {validate_part_number('; DELETE FROM--')}")

# Test 2: Component ID Validation  
print("\n2. Component ID Validation:")
print(f"  Valid '123-456': {validate_component_id('123-456')}")
print(f"  Valid 'ABC_123': {validate_component_id('ABC_123')}")
print(f"  Invalid '../test': {validate_component_id('../test')}")
print(f"  Invalid 'test/path': {validate_component_id('test/path')}")

# Test 3: String Sanitization
print("\n3. String Sanitization:")
print(f"  'Test String   ' -> '{sanitize_string('Test String   ')}'")
print(f"  'A' * 600 -> '{sanitize_string('A' * 600)[:50]}...' (length: {len(sanitize_string('A' * 600))})")

# Test 4: Rate Limiter
print("\n4. Rate Limiter (max 3 requests per 60s):")
limiter = RateLimiter(max_requests=3, time_window_seconds=60)
for i in range(5):
    allowed = limiter.allow_request('test_api')
    print(f"  Request {i+1}: {'ALLOWED' if allowed else 'BLOCKED (rate limited)'}")
    if not allowed:
        wait_time = limiter.get_wait_time('test_api')
        print(f"    Wait time: {wait_time:.1f}s")

# Test 5: File Extension Validation
print("\n5. File Extension Validation:")
print(f"  'document.pdf': {validate_file_extension(Path('document.pdf'))}")
print(f"  'malware.exe': {validate_file_extension(Path('malware.exe'))}")
print(f"  'script.sh': {validate_file_extension(Path('script.sh'))}")

print("\n" + "="*60)
print("ALL SECURITY TESTS COMPLETED")
print("="*60)
