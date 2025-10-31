#!/usr/bin/env python3
"""
Test Auth Service Integration with Customer Service
"""
import requests
import json

# Test data
base_url = "http://localhost/api/v1"
test_credentials = {
    "email": "customer@example.com",
    "password": "password123"
}

print("=== Testing Auth Service Integration ===")
print()

# Step 1: Login to get a valid token
print("1. Logging in to get authentication token...")
try:
    login_response = requests.post(f"{base_url}/auth/login/", json=test_credentials)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        access_token = login_data.get('access_token')
        print(f"Login successful! Token length: {len(access_token) if access_token else 0}")
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Step 2: Test auth profile endpoint
        print("\n2. Testing auth profile endpoint...")
        auth_profile_response = requests.get(f"{base_url}/auth/profile/", headers=headers)
        print(f"Auth profile status: {auth_profile_response.status_code}")
        
        if auth_profile_response.status_code == 200:
            auth_data = auth_profile_response.json()
            print("Auth profile data:")
            for key, value in auth_data.items():
                print(f"  {key}: {value}")
        else:
            print(f"Auth profile error: {auth_profile_response.text}")
        
        # Step 3: Test customer profile endpoint (with auth integration)
        print("\n3. Testing customer profile endpoint (with auth integration)...")
        customer_profile_response = requests.get(f"{base_url}/customers/profile/", headers=headers)
        print(f"Customer profile status: {customer_profile_response.status_code}")
        
        if customer_profile_response.status_code == 200:
            customer_data = customer_profile_response.json()
            print("Customer profile data (should include auth data):")
            print(f"  id: {customer_data.get('id')}")
            print(f"  email: {customer_data.get('email')}")
            print(f"  first_name: {customer_data.get('first_name')}")
            print(f"  last_name: {customer_data.get('last_name')}")
            print(f"  full_name: {customer_data.get('full_name')}")
            print(f"  phone_number: {customer_data.get('phone_number')}")
            
            # Check if auth data is properly integrated
            has_auth_data = all([
                customer_data.get('email') != 'N/A',
                customer_data.get('first_name') != 'N/A',
                customer_data.get('last_name') != 'N/A'
            ])
            print(f"\n✅ Auth data integration working: {has_auth_data}")
            
        else:
            print(f"Customer profile error: {customer_profile_response.text}")
    
    else:
        print(f"Login failed: {login_response.text}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n=== Test Complete ===")