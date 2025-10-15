"""
Authentication module for TerraCLIM API.
Handles login and token management.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TerraCLIMAuth:
    def __init__(self):
        """Initialize the TerraCLIM authentication client."""
        self.base_url = "https://dashboard.staging.terraclim.co.za"
        self.access_token = None
        self.refresh_token = None
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def login(self, username=None, password=None):
        """
        Login to TerraCLIM API and obtain access token.
        
        Args:
            username (str, optional): Username for authentication. If not provided, reads from environment.
            password (str, optional): Password for authentication. If not provided, reads from environment.
            
        Returns:
            bool: True if login successful, False otherwise
        """
        username = username or os.getenv('TERRACLIM_USERNAME')
        password = password or os.getenv('TERRACLIM_PASSWORD')
        
        if not username or not password:
            raise ValueError("Username and password must be provided either as arguments or environment variables")

        login_url = f"{self.base_url}/api/token/"
        
        try:
            response = requests.post(
                login_url,
                json={
                    'username': username,
                    'password': password
                },
                headers=self.headers
            )
            
            # Check if response contains valid JSON data
            try:
                data = response.json()
            except ValueError:
                print(f"Invalid JSON response: {response.text}")
                return False

            # Check response status
            if not response.ok:
                error_msg = data.get('detail') if isinstance(data, dict) else str(data)
                print(f"Login failed: {error_msg}")
                return False
            
            # Extract tokens from response
            if isinstance(data, dict):
                self.access_token = data.get('access')
                self.refresh_token = data.get('refresh')

                if self.access_token:
                    self.headers['Authorization'] = f'Bearer {self.access_token}'
                    return True
                else:
                    print("No access token in response")
                    return False
                
        except requests.exceptions.RequestException as e:
            print(f"Login failed: {str(e)}")
            return False
            
        return False

    def get_headers(self):
        """
        Get the current headers with authentication token if available.
        
        Returns:
            dict: Headers dictionary
        """
        return self.headers

    def is_authenticated(self):
        """
        Check if the client is authenticated.
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return bool(self.access_token)

    def refresh_tokens(self):
        """
        Refresh access token using the refresh token.
        
        Returns:
            bool: True if refresh successful, False otherwise
        """
        if not self.refresh_token:
            print("No refresh token available. Please login first.")
            return False

        refresh_url = f"{self.base_url}/api/token/refresh/"
        
        try:
            response = requests.post(
                refresh_url,
                json={
                    'refresh': self.refresh_token
                },
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            response.raise_for_status()
            
            # Extract new tokens from response
            tokens = response.json()
            self.access_token = tokens.get('access')
            self.refresh_token = tokens.get('refresh')  # In case a new refresh token is provided
            
            if self.access_token:
                self.headers['Authorization'] = f'Bearer {self.access_token}'
                return True
                
        except requests.exceptions.RequestException as e:
            print(f"Token refresh failed: {str(e)}")
            return False
            
        return False

def show_help():
    """
    Display help message for command-line usage.
    """
    print("""
TerraCLIM Authentication Script Usage:
------------------------------------
Basic Usage:
    python auth.py [command] [options]

Commands:
    login               Login and get new tokens (uses environment variables by default)
    login --user USER --pass PASS  Login with specific credentials
    refresh            Refresh the current access token
    status             Check current authentication status
    help               Show this help message

Examples:
    python auth.py login
    python auth.py login --user myusername --pass mypassword
    python auth.py refresh
    python auth.py status

Note: It's recommended to use environment variables TERRACLIM_USERNAME and 
      TERRACLIM_PASSWORD instead of command line credentials for security.
    """)

def format_token(token):
    """Format token for display."""
    return token[:20] + "..." if token else "None"

def main():
    """
    Command-line interface for TerraCLIM authentication.
    """
    import sys
    import getpass

    # Show help if no arguments or help requested
    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        return

    command = sys.argv[1]
    auth = TerraCLIMAuth()

    try:
        if command == 'login':
            # Parse login options
            username = None
            password = None
            
            args = sys.argv[2:]
            for i in range(0, len(args), 2):
                if i + 1 >= len(args):
                    break
                    
                if args[i] == '--user':
                    username = args[i + 1]
                elif args[i] == '--pass':
                    password = args[i + 1]

            # If credentials not provided in command line, use environment or prompt
            if not username:
                username = os.getenv('TERRACLIM_USERNAME')
                if not username:
                    username = input("Username: ")
                    
            if not password:
                password = os.getenv('TERRACLIM_PASSWORD')
                if not password:
                    password = getpass.getpass("Password: ")

            # Attempt login
            if auth.login(username, password):
                print("Successfully logged in!")
                print(f"Access Token: {format_token(auth.access_token)}")
                print(f"Refresh Token: {format_token(auth.refresh_token)}")
            else:
                print("Login failed!")

        elif command == 'refresh':
            if not auth.is_authenticated():
                print("Error: Not authenticated. Please login first.")
                return

            if auth.refresh_tokens():
                print("Successfully refreshed tokens!")
                print(f"New Access Token: {format_token(auth.access_token)}")
                print(f"New Refresh Token: {format_token(auth.refresh_token)}")
            else:
                print("Token refresh failed!")

        elif command == 'status':
            if auth.is_authenticated():
                print("Status: Authenticated")
                print(f"Access Token: {format_token(auth.access_token)}")
                print(f"Refresh Token: {format_token(auth.refresh_token)}")
            else:
                print("Status: Not authenticated")

        else:
            print(f"Unknown command: {command}")
            show_help()

    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()