"""
Module for retrieving fields data from TerraCLIM API.
"""

import requests
from .auth import TerraCLIMAuth
from .utils import get_api_url, response_to_dataframe, handle_error_response

class Fields:
    def __init__(self, auth_client=None):
        """
        Initialize the Fields client.
        
        Args:
            auth_client (TerraCLIMAuth, optional): Authentication client. If not provided, creates new one.
        """
        self.auth = auth_client if auth_client else TerraCLIMAuth()
        if not self.auth.is_authenticated():
            raise ValueError("Authentication required. Please login first.")

    def get_fields(self, farm_id=None, portion_id=None):
        """
        Retrieve fields data.
        
        Args:
            farm_id (int, optional): Filter fields by farm ID
            portion_id (int, optional): Filter fields by farm portion ID
            
        Returns:
            pandas.DataFrame: Fields data
        """
        endpoint = "fields/"
        url = get_api_url(endpoint)
        
        params = {}
        if farm_id:
            params['farm_id'] = farm_id
        if portion_id:
            params['portion_id'] = portion_id
            
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting fields: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe(data)
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve fields: {str(e)}")
            return None

    def get_field(self, field_id):
        """
        Retrieve specific field by ID.
        
        Args:
            field_id (int): ID of the field to retrieve
            
        Returns:
            pandas.DataFrame: Single field data
        """
        endpoint = f"fields/{field_id}/"
        url = get_api_url(endpoint)
        
        try:
            response = requests.get(
                url,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting field {field_id}: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe([data])  # Wrap in list for DataFrame
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve field {field_id}: {str(e)}")
            return None

    def get_field_statistics(self, field_id, start_date=None, end_date=None):
        """
        Retrieve statistics for a specific field.
        
        Args:
            field_id (int): ID of the field
            start_date (str, optional): Start date for statistics (YYYY-MM-DD)
            end_date (str, optional): End date for statistics (YYYY-MM-DD)
            
        Returns:
            pandas.DataFrame: Field statistics data
        """
        endpoint = f"fields/{field_id}/statistics/"
        url = get_api_url(endpoint)
        
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting field statistics for {field_id}: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe(data, flatten=True)
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve field statistics for {field_id}: {str(e)}")
            return None

def show_help():
    """
    Display help message for command-line usage.
    """
    print("""
TerraCLIM Fields Script Usage:
-----------------------------
Basic Usage:
    python fields.py [command] [options]

Commands:
    list                    List all fields
    list-farm [farm_id]     List fields for a specific farm
    get [field_id]         Get details for a specific field
    stats [field_id]       Get statistics for a specific field

Options for 'stats' command:
    --start-date YYYY-MM-DD  Start date for statistics (optional)
    --end-date YYYY-MM-DD    End date for statistics (optional)

Examples:
    python fields.py list
    python fields.py list-farm 123
    python fields.py get 456
    python fields.py stats 456 --start-date 2025-01-01 --end-date 2025-12-31

All data will be saved to CSV files in the current directory.
    """)

def main():
    """
    Command-line interface for the Fields client.
    """
    import sys
    from datetime import datetime, timedelta

    # Show help if no arguments or help requested
    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        return

    # Initialize authentication
    auth = TerraCLIMAuth()
    if not auth.login():
        print("Failed to authenticate")
        return

    # Create client
    client = Fields(auth)
    
    command = sys.argv[1]

    try:
        if command == 'list':
            # List all fields
            print("\nGetting all fields...")
            df = client.get_fields()
            
            if df is not None:
                print(f"Total number of fields: {len(df)}")
                print("\nSample of fields data:")
                print(df.head())
                
                output_file = "all_fields.csv"
                df.to_csv(output_file, index=False)
                print(f"All fields data saved to {output_file}")

        elif command == 'list-farm':
            if len(sys.argv) < 3:
                print("Error: Farm ID required")
                show_help()
                return
                
            farm_id = int(sys.argv[2])
            print(f"\nGetting fields for farm {farm_id}...")
            df = client.get_fields(farm_id=farm_id)
            
            if df is not None:
                print(f"Number of fields for farm {farm_id}: {len(df)}")
                print("\nSample of farm's fields data:")
                print(df.head())
                
                output_file = f"farm_{farm_id}_fields.csv"
                df.to_csv(output_file, index=False)
                print(f"Farm's fields data saved to {output_file}")

        elif command == 'get':
            if len(sys.argv) < 3:
                print("Error: Field ID required")
                show_help()
                return
                
            field_id = int(sys.argv[2])
            print(f"\nGetting details for field {field_id}...")
            df = client.get_field(field_id)
            
            if df is not None:
                print("\nField details:")
                print(df)
                
                output_file = f"field_{field_id}_details.csv"
                df.to_csv(output_file, index=False)
                print(f"Field details saved to {output_file}")

        elif command == 'stats':
            if len(sys.argv) < 3:
                print("Error: Field ID required")
                show_help()
                return
                
            field_id = int(sys.argv[2])
            
            # Parse date options if provided
            start_date = None
            end_date = None
            
            args = sys.argv[3:]
            for i in range(0, len(args), 2):
                if i + 1 >= len(args):
                    break
                    
                if args[i] == '--start-date':
                    start_date = args[i + 1]
                elif args[i] == '--end-date':
                    end_date = args[i + 1]
            
            print(f"\nGetting statistics for field {field_id}...")
            df = client.get_field_statistics(field_id, start_date, end_date)
            
            if df is not None:
                print("\nField statistics:")
                print(df)
                
                output_file = f"field_{field_id}_stats.csv"
                df.to_csv(output_file, index=False)
                print(f"Field statistics saved to {output_file}")

        else:
            print(f"Unknown command: {command}")
            show_help()

    except ValueError as e:
        print(f"Error: Invalid number format - {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()