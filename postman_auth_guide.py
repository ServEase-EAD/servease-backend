#!/usr/bin/env python3
"""
ServEase Postman-Ready Authentication Test
==========================================
This script provides example requests that can be used in Postman or any HTTP client
to test the JWT authentication flow.
"""

import json


def print_postman_collection():
    """Print Postman-ready request examples"""

    print("="*70)
    print(" SERVEASE JWT AUTHENTICATION - POSTMAN TEST COLLECTION")
    print("="*70)

    print("\n📋 Copy these examples into Postman for testing:")

    # Registration
    print("\n" + "─"*50)
    print("1️⃣  USER REGISTRATION")
    print("─"*50)
    print("Method: POST")
    print("URL: http://localhost:8001/api/v1/auth/register/")
    print("Headers:")
    print("  Content-Type: application/json")
    print("\nBody (JSON):")
    registration_body = {
        "email": "john.doe@servease.com",
        "password1": "SecurePass123!",
        "password2": "SecurePass123!",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "1234567890"
    }
    print(json.dumps(registration_body, indent=2))
    print("\nExpected Response: 201 Created with user data and tokens")

    # Login
    print("\n" + "─"*50)
    print("2️⃣  USER LOGIN")
    print("─"*50)
    print("Method: POST")
    print("URL: http://localhost:8001/api/v1/auth/login/")
    print("Headers:")
    print("  Content-Type: application/json")
    print("\nBody (JSON):")
    login_body = {
        "email": "john.doe@servease.com",
        "password": "SecurePass123!"
    }
    print(json.dumps(login_body, indent=2))
    print("\nExpected Response: 200 OK with access and refresh tokens")
    print("💡 Save the 'access' token from response for next requests!")

    # Protected endpoint without token
    print("\n" + "─"*50)
    print("3️⃣  PROTECTED ENDPOINT (Without Token)")
    print("─"*50)
    print("Method: GET")
    print("URL: http://localhost:8002/api/v1/customers/")
    print("Headers: (none)")
    print("\nExpected Response: 403 Forbidden")
    print(
        "Response Body: {\"detail\": \"Authentication credentials were not provided.\"}")

    # Protected endpoint with token
    print("\n" + "─"*50)
    print("4️⃣  PROTECTED ENDPOINT (With Token)")
    print("─"*50)
    print("Method: GET")
    print("URL: http://localhost:8002/api/v1/customers/")
    print("Headers:")
    print("  Authorization: Bearer YOUR_ACCESS_TOKEN_HERE")
    print("  Content-Type: application/json")
    print("\nExpected Response: 200 OK with customer data")
    print("💡 Replace YOUR_ACCESS_TOKEN_HERE with the token from login response")

    # Token validation
    print("\n" + "─"*50)
    print("5️⃣  TOKEN VALIDATION")
    print("─"*50)
    print("Method: POST")
    print("URL: http://localhost:8001/api/v1/auth/validate-token/")
    print("Headers:")
    print("  Content-Type: application/json")
    print("\nBody (JSON):")
    validation_body = {
        "token": "YOUR_ACCESS_TOKEN_HERE"
    }
    print(json.dumps(validation_body, indent=2))
    print("\nExpected Response: 200 OK if token is valid")
    print("💡 Replace YOUR_ACCESS_TOKEN_HERE with actual token")

    # User profile
    print("\n" + "─"*50)
    print("6️⃣  USER PROFILE")
    print("─"*50)
    print("Method: GET")
    print("URL: http://localhost:8001/api/v1/auth/profile/")
    print("Headers:")
    print("  Authorization: Bearer YOUR_ACCESS_TOKEN_HERE")
    print("  Content-Type: application/json")
    print("\nExpected Response: 200 OK with user profile data")

    # Token refresh
    print("\n" + "─"*50)
    print("7️⃣  TOKEN REFRESH")
    print("─"*50)
    print("Method: POST")
    print("URL: http://localhost:8001/api/v1/auth/token/refresh/")
    print("Headers:")
    print("  Content-Type: application/json")
    print("\nBody (JSON):")
    refresh_body = {
        "refresh": "YOUR_REFRESH_TOKEN_HERE"
    }
    print(json.dumps(refresh_body, indent=2))
    print("\nExpected Response: 200 OK with new access token")
    print("💡 Replace YOUR_REFRESH_TOKEN_HERE with the refresh token from login")

    # Logout
    print("\n" + "─"*50)
    print("8️⃣  USER LOGOUT")
    print("─"*50)
    print("Method: POST")
    print("URL: http://localhost:8001/api/v1/auth/logout/")
    print("Headers:")
    print("  Authorization: Bearer YOUR_ACCESS_TOKEN_HERE")
    print("  Content-Type: application/json")
    print("\nBody (JSON):")
    logout_body = {
        "refresh": "YOUR_REFRESH_TOKEN_HERE"
    }
    print(json.dumps(logout_body, indent=2))
    print("\nExpected Response: 200 OK - tokens are blacklisted")

    print("\n" + "="*70)
    print(" TESTING WORKFLOW")
    print("="*70)
    print("\n📝 Recommended Testing Order:")
    print("1. Register a new user (Request #1)")
    print("2. Login with those credentials (Request #2)")
    print("3. Copy the access token from login response")
    print("4. Test protected endpoint without token (Request #3) - should fail")
    print("5. Test protected endpoint with token (Request #4) - should work")
    print("6. Validate the token (Request #5)")
    print("7. Get user profile (Request #6)")
    print("8. Refresh the token (Request #7)")
    print("9. Logout (Request #8)")

    print("\n💡 Tips for Postman:")
    print("• Create a new Collection called 'ServEase Auth'")
    print("• Add each request as a separate item in the collection")
    print("• Use Environment Variables for tokens:")
    print("  - {{access_token}} for access tokens")
    print("  - {{refresh_token}} for refresh tokens")
    print("• Set up Tests in Postman to automatically extract tokens:")
    print("  pm.environment.set('access_token', pm.response.json().tokens.access);")

    print("\n🎯 Authentication Flow Confirmed:")
    print("✅ Customer must be logged in → Server generates token → Token sent with requests → Server validates")


if __name__ == "__main__":
    print_postman_collection()
