#!/usr/bin/env python3
"""
🔑 JWT Test Token Generator
==========================

This script generates a valid JWT token that matches your Django authentication service
configuration. Use this token to test your authentication requirement when services
are experiencing database connectivity issues.
"""

import jwt
from datetime import datetime, timedelta, timezone

def generate_test_token():
    """Generate a valid JWT token for testing"""
    
    # Your Django SECRET_KEY (matches the working secret from earlier tests)
    secret_key = "django-insecure-dev-key-please-change-this-in-production-12345"
    
    # Create token payload with all required claims
    payload = {
        'user_id': 1,
        'email': 'test.customer@example.com',
        'user_role': 'customer',
        'first_name': 'Test',
        'last_name': 'Customer',
        'exp': datetime.now(timezone.utc) + timedelta(hours=2),  # Valid for 2 hours
        'iat': datetime.now(timezone.utc),
        'token_type': 'access'
    }
    
    # Generate JWT token
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    
    print("🔑 JWT TEST TOKEN GENERATOR")
    print("=" * 50)
    print(f"\n✅ Generated Test Token:")
    print(f"{token}")
    print(f"\n📋 Token Details:")
    print(f"   User ID: {payload['user_id']}")
    print(f"   Email: {payload['email']}")
    print(f"   Role: {payload['user_role']}")
    print(f"   Expires: {payload['exp']}")
    print(f"   Algorithm: HS256")
    
    print(f"\n🚀 Use in Postman:")
    print(f"   Authorization: Bearer {token}")
    
    print(f"\n📝 Test URLs:")
    print(f"   GET http://localhost/api/v1/customers/profile/")
    print(f"   GET http://localhost/api/v1/customers/stats/")
    print(f"   (Add Authorization header with the token above)")
    
    return token

if __name__ == "__main__":
    generate_test_token()