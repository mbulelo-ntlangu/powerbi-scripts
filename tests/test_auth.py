"""
Test script for authentication module.
"""

from terraclim.auth import TerraCLIMAuth

def test_auth():
    print("\nTesting TerraCLIM Authentication")
    print("--------------------------------")
    
    # Initialize auth client
    auth = TerraCLIMAuth()
    print(f"Base URL: {auth.base_url}")
    
    # Test login
    print("\nTesting login...")
    success = auth.login()
    if success:
        print("✓ Login successful")
        print(f"Access token: {auth.access_token[:20]}..." if auth.access_token else "None")
        print(f"Refresh token: {auth.refresh_token[:20]}..." if auth.refresh_token else "None")
    else:
        print("✗ Login failed")
    
    # Test headers
    print("\nTesting headers...")
    headers = auth.get_headers()
    print("Authorization header:", headers.get('Authorization', 'Not set'))
    
    # Test is_authenticated
    print("\nTesting is_authenticated...")
    if auth.is_authenticated():
        print("✓ Client is authenticated")
    else:
        print("✗ Client is not authenticated")
    
    # Test token refresh if we have a refresh token
    if auth.refresh_token:
        print("\nTesting token refresh...")
        refresh_success = auth.refresh_tokens()
        if refresh_success:
            print("✓ Token refresh successful")
            print(f"New access token: {auth.access_token[:20]}...")
        else:
            print("✗ Token refresh failed")

if __name__ == "__main__":
    test_auth()