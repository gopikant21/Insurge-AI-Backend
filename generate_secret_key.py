#!/usr/bin/env python3
"""
Generate secure secret key for JWT tokens
Run this script to generate a cryptographically secure secret key
"""

import secrets
import string
import base64
from datetime import datetime


def generate_secret_key(length=64):
    """Generate a secure random secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    secret_key = "".join(secrets.choice(alphabet) for _ in range(length))
    return secret_key


def generate_base64_key(length=32):
    """Generate a base64 encoded secret key"""
    key_bytes = secrets.token_bytes(length)
    return base64.b64encode(key_bytes).decode("utf-8")


def main():
    print("🔐 Insurge AI Backend - Secret Key Generator")
    print("=" * 50)
    print()

    # Generate different types of keys
    standard_key = generate_secret_key(64)
    base64_key = generate_base64_key(32)
    simple_key = generate_secret_key(32)

    print("📋 Generated Secret Keys:")
    print()
    print("1. Standard Secret Key (64 characters):")
    print(f"   SECRET_KEY={standard_key}")
    print()
    print("2. Base64 Encoded Key (32 bytes):")
    print(f"   SECRET_KEY={base64_key}")
    print()
    print("3. Simple Key (32 characters):")
    print(f"   SECRET_KEY={simple_key}")
    print()

    print("🔒 Security Recommendations:")
    print("- Use the standard key for production")
    print("- Never commit secret keys to version control")
    print("- Store keys securely in environment variables")
    print("- Rotate keys regularly (every 3-6 months)")
    print("- Use different keys for different environments")
    print()

    print("📝 How to use:")
    print("1. Copy one of the keys above")
    print("2. Update your .env file:")
    print("   SECRET_KEY=<paste-your-key-here>")
    print("3. Restart your application")
    print()

    print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
