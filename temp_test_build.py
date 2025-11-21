#!/usr/bin/env python3
"""Test build de slave"""

from app.distributed.build_d8_slave import BuildD8Slave
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('GITHUB_TOKEN')

print("="*60)
print("🧪 PRUEBA DE BUILD D8 SLAVE")
print("="*60)
print(f"Token: {token[:20]}...")
print()

builder = BuildD8Slave('192.168.4.38', 7600, token=token)
result = builder.build('slave-192-168-4-38', token)

print("\n" + "="*60)
print("RESULTADO FINAL:")
print("="*60)
print(f"Success: {result['success']}")
print(f"Strategy: {result['strategy']}")
print(f"Message: {result['message']}")
print(f"Log File: {result.get('log_file', 'N/A')}")
print("="*60)
