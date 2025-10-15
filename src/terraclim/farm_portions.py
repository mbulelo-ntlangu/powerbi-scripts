"""
Module for retrieving farm portions data from TerraCLIM API.
"""

import requests
from auth import TerraCLIMAuth
from utils import get_api_url, response_to_dataframe, handle_error_response

class FarmPortions:
    def __init__(self, auth_client=None):
        """
        Initialize the Farm Portions client.
        
        Args:
            auth_client (TerraCLIMAuth, optional): Authentication client. If not provided, creates new one.
        """
        self.auth = auth_client if auth_client else TerraCLIMAuth()
        if not self.auth.is_authenticated():
            raise ValueError("Authentication required. Please login first.")

    def get_farm_portions(self, farm_id=None):
        """
        Retrieve farm portions data.
        
        Args:
            farm_id (int, optional): Filter portions by farm ID
            
        Returns:
            pandas.DataFrame: Farm portions data
        """
        endpoint = "farms/portions/"
        url = get_api_url(endpoint)
        
        params = {}
        if farm_id:
            params['farm_id'] = farm_id
            
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting farm portions: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe(data)
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve farm portions: {str(e)}")
            return None

    def get_farm_portion(self, portion_id):
        """
        Retrieve specific farm portion by ID.
        
        Args:
            portion_id (int): ID of the farm portion to retrieve
            
        Returns:
            pandas.DataFrame: Single farm portion data
        """
        endpoint = f"farms/portions/{portion_id}/"
        url = get_api_url(endpoint)
        
        try:
            response = requests.get(
                url,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting farm portion {portion_id}: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe([data])  # Wrap in list for DataFrame
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve farm portion {portion_id}: {str(e)}")
            return None

    def get_portion_statistics(self, portion_id, start_date=None, end_date=None):
        """
        Retrieve statistics for a specific farm portion.
        
        Args:
            portion_id (int): ID of the farm portion
            start_date (str, optional): Start date for statistics (YYYY-MM-DD)
            end_date (str, optional): End date for statistics (YYYY-MM-DD)
            
        Returns:
            pandas.DataFrame: Farm portion statistics data
        """
        endpoint = f"farms/portions/{portion_id}/statistics/"
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
                print(f"Error getting portion statistics for {portion_id}: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe(data, flatten=True)
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve portion statistics for {portion_id}: {str(e)}")
            return None

def show_help():
    """
    Display help message for command-line usage.
    """
    print("""
TerraCLIM Farm Portions Script Usage:
----------------------------------
Basic Usage:
    python farm_portions.py [command] [options]

Commands:
    list                    List all farm portions
    list-farm [farm_id]     List portions for a specific farm
    get [portion_id]       Get details for a specific portion
    stats [portion_id]     Get statistics for a specific portion
    help                   Show this help message

Options for 'list' and 'get' commands:
    --output FILE         Output CSV filename (default: farm_portions.csv or portion_[id].csv)

Options for 'stats' command:
    --start-date DATE     Start date (YYYY-MM-DD)
    --end-date DATE      End date (YYYY-MM-DD)
    --output FILE        Output CSV filename (default: portion_[id]_stats.csv)

Examples:
    python farm_portions.py list
    python farm_portions.py list-farm 123
    python farm_portions.py get 456
    python farm_portions.py stats 456 --start-date 2025-01-01 --end-date 2025-12-31
    """)

def main():
    """
    Command-line interface for Farm Portions client.
    """
    import sys

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
    client = FarmPortions(auth)
    
    command = sys.argv[1]

    try:
        if command == 'list':
            # Parse output filename
            output_file = "farm_portions.csv"
            args = sys.argv[2:]
            for i in range(0, len(args), 2):
                if i + 1 >= len(args):
                    break
                if args[i] == '--output':
                    output_file = args[i + 1]
            
            # Get all portions
            print("\nFetching all farm portions...")
            df = client.get_farm_portions()
            
            if df is not None:
                print(f"Total portions: {len(df)}")
                print("\nSample of portions data:")
                print(df.head())
                
                df.to_csv(output_file, index=False)
                print(f"\nData saved to {output_file}")

        elif command == 'list-farm':
            if len(sys.argv) < 3:
                print("Error: Farm ID required")
                show_help()
                return
                
            farm_id = int(sys.argv[2])
            
            # Parse output filename
            output_file = f"farm_{farm_id}_portions.csv"
            args = sys.argv[3:]
            for i in range(0, len(args), 2):
                if i + 1 >= len(args):
                    break
                if args[i] == '--output':
                    output_file = args[i + 1]
            
            print(f"\nFetching portions for farm {farm_id}...")
            df = client.get_farm_portions(farm_id=farm_id)
            
            if df is not None:
                print(f"Total portions for farm {farm_id}: {len(df)}")
                print("\nSample of portions data:")
                print(df.head())
                
                df.to_csv(output_file, index=False)
                print(f"\nData saved to {output_file}")

        elif command == 'get':
            if len(sys.argv) < 3:
                print("Error: Portion ID required")
                show_help()
                return
                
            portion_id = int(sys.argv[2])
            
            # Parse output filename
            output_file = f"portion_{portion_id}.csv"
            args = sys.argv[3:]
            for i in range(0, len(args), 2):
                if i + 1 >= len(args):
                    break
                if args[i] == '--output':
                    output_file = args[i + 1]
            
            print(f"\nFetching details for portion {portion_id}...")
            df = client.get_farm_portion(portion_id)
            
            if df is not None:
                print("\nPortion details:")
                print(df)
                
                df.to_csv(output_file, index=False)
                print(f"\nData saved to {output_file}")

        elif command == 'stats':
            if len(sys.argv) < 3:
                print("Error: Portion ID required")
                show_help()
                return
                
            portion_id = int(sys.argv[2])
            
            # Parse command options
            start_date = None
            end_date = None
            output_file = f"portion_{portion_id}_stats.csv"
            
            args = sys.argv[3:]
            for i in range(0, len(args), 2):
                if i + 1 >= len(args):
                    break
                if args[i] == '--start-date':
                    start_date = args[i + 1]
                elif args[i] == '--end-date':
                    end_date = args[i + 1]
                elif args[i] == '--output':
                    output_file = args[i + 1]
            
            print(f"\nFetching statistics for portion {portion_id}...")
            if start_date:
                print(f"Start date: {start_date}")
            if end_date:
                print(f"End date: {end_date}")
                
            df = client.get_portion_statistics(portion_id, start_date, end_date)
            
            if df is not None:
                print("\nPortion statistics:")
                print(df.head())
                
                df.to_csv(output_file, index=False)
                print(f"\nData saved to {output_file}")

        else:
            print(f"Unknown command: {command}")
            show_help()

    except ValueError as e:
        print(f"Error: Invalid number format - {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()