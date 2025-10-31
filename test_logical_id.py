#!/usr/bin/env python3
"""
Test script for logical ID consolidation
"""
import requests
import json

# Test endpoints
base_url = "http://localhost/api/v1/customers"

# Test data (using existing customer data)
test_user_id = "6dab4597-a154-413f-86b9-0745a6474b5c"
test_customer_id = "390e7070-b329-4e87-a75e-9b6e0ca4e502"

print("=== Testing Logical ID Consolidation ===")
print(f"Test User ID: {test_user_id}")
print(f"Test Customer ID: {test_customer_id}")
print()

# Test 1: Check profile endpoint
print("1. Testing profile endpoint...")
try:
    response = requests.get(f"{base_url}/profile/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response ID: {data.get('id')}")
        print(f"Response User ID field: {data.get('user_id')}")
        print(f"ID matches user_id: {data.get('id') == test_user_id}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")
print()

# Test 2: Check logical ID endpoint
print("2. Testing logical ID endpoint...")
try:
    response = requests.get(f"{base_url}/logical/{test_user_id}/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response ID: {data.get('id')}")
        print(f"Response User ID field: {data.get('user_id')}")
        print(f"ID matches user_id: {data.get('id') == test_user_id}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")
print()

# Test 3: Check legacy customer ID endpoint
print("3. Testing legacy customer ID endpoint...")
try:
    response = requests.get(f"{base_url}/{test_customer_id}/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response ID: {data.get('id')}")
        print(f"Response User ID field: {data.get('user_id')}")
        print(f"ID matches user_id: {data.get('id') == test_user_id}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Test Complete ===")
