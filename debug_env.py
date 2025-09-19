#!/usr/bin/env python
import os

print("=== Environment Variables Debug ===")
print(f"DEBUG: {os.environ.get('DEBUG', 'NOT SET')}")
print(f"SECRET_KEY: {os.environ.get('SECRET_KEY', 'NOT SET')[:20]}...")
print(f"ALLOWED_HOSTS: {os.environ.get('ALLOWED_HOSTS', 'NOT SET')}")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'NOT SET')[:50]}...")
print("==================================")
