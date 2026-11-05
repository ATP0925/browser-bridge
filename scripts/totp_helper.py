"""
Autonomous TOTP (Time-based One-Time Password) Generator.
Compliant with RFC 6238 and RFC 4226.
Uses pure Python standard library (hmac, hashlib, struct, time, base64) with zero external dependencies.
"""
import hmac
import hashlib
import time
import struct
import base64
import re

def clean_secret(secret: str) -> str:
    """Normalize base32 secret (remove spaces, hyphens, and convert to uppercase)."""
    return re.sub(r'[\s\-]', '', secret).strip().upper()

def generate_totp(secret: str, digits: int = 6, time_step: int = 30) -> str:
    """
    Generate the current TOTP 6-digit (or 8-digit) authentication code.
    
    :param secret: Base32-encoded secret key provided by the service (e.g. Google Authenticator seed).
    :param digits: Number of digits in output (default 6).
    :param time_step: Validity window in seconds (standard 30s).
    :return: Formatted numeric OTP string with leading zeroes if needed.
    """
    secret = clean_secret(secret)
    
    # Pad base32 string to multiple of 8 if needed
    missing_padding = len(secret) % 8
    if missing_padding:
        secret += '=' * (8 - missing_padding)

    try:
        key = base64.b32decode(secret, casefold=True)
    except Exception as e:
        raise ValueError(f"Invalid Base32 TOTP secret: {e}")

    # Calculate 8-byte counter value based on unix time
    counter = int(time.time()) // time_step
    counter_bytes = struct.pack(">Q", counter)

    # Compute HMAC-SHA1
    mac = hmac.new(key, counter_bytes, hashlib.sha1).digest()

    # Dynamic truncation algorithm
    offset = mac[-1] & 0x0F
    code_int = struct.unpack(">I", mac[offset:offset + 4])[0] & 0x7FFFFFFF

    otp = code_int % (10 ** digits)
    return str(otp).zfill(digits)

def get_remaining_seconds(time_step: int = 30) -> int:
    """Returns how many seconds remain before the current TOTP token expires."""
    return time_step - (int(time.time()) % time_step)

if __name__ == "__main__":
    import sys
    # Standard RFC 6238 test secret
    test_secret = sys.argv[1] if len(sys.argv) > 1 else "JBSWY3DPEHPK3PXP"
    code = generate_totp(test_secret)
    rem = get_remaining_seconds()
    print(f"Generated TOTP: {code} (Valid for {rem}s)")

