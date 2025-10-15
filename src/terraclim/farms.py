"""
Module for retrieving farm data from TerraCLIM API.
"""

import requests
from auth import TerraCLIMAuth
from utils import get_api_url, response_to_dataframe, handle_error_response

class Farms:
    def __init__(self, auth_client=None):
        """
        Initialize the Farms client.
        
        Args:
            auth_client (TerraCLIMAuth, optional): Authentication client. If not provided, creates new one.
        """
        self.auth = auth_client if auth_client else TerraCLIMAuth()
        if not self.auth.is_authenticated():
            raise ValueError("Authentication required. Please login first.")

    def get_farms(self):
        """
        Retrieve all farms data.
        
        Returns:
            pandas.DataFrame: Farms data
        """
        endpoint = "farms/"
        url = get_api_url(endpoint)
        
        try:
            response = requests.get(
                url,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting farms: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe(data)
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve farms: {str(e)}")
            return None

    def get_farm(self, farm_id):
        """
        Retrieve specific farm by ID.
        
        Args:
            farm_id (int): ID of the farm to retrieve
            
        Returns:
            pandas.DataFrame: Single farm data
        """
        endpoint = f"farms/{farm_id}/"
        url = get_api_url(endpoint)
        
        try:
            response = requests.get(
                url,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting farm {farm_id}: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe([data])  # Wrap in list for DataFrame
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve farm {farm_id}: {str(e)}")
            return None

    def get_farm_statistics(self, farm_id, start_date=None, end_date=None):
        """
        Retrieve statistics for a specific farm.
        
        Args:
            farm_id (int): ID of the farm
            start_date (str, optional): Start date for statistics (YYYY-MM-DD)
            end_date (str, optional): End date for statistics (YYYY-MM-DD)
            
        Returns:
            pandas.DataFrame: Farm statistics data
        """
        endpoint = f"farms/{farm_id}/statistics/"
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
                print(f"Error getting farm statistics for {farm_id}: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe(data, flatten=True)
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve farm statistics for {farm_id}: {str(e)}")
            return None

def show_help():
    """
    Display help message for command-line usage.
    """
    print("""
TerraCLIM Farms Script Usage:
---------------------------
Basic Usage:
    python farms.py [command] [options]

Commands:
    list                    List all farms
    get [farm_id]          Get details for a specific farm
    stats [farm_id]        Get statistics for a specific farm
    extract-ids            Extract farm IDs to a separate CSV file
    help                   Show this help message

Options for 'list' and 'get' commands:
    --output FILE          Output CSV filename (default: farms.csv or farm_[id].csv)

Options for 'stats' command:
    --start-date DATE      Start date (YYYY-MM-DD)
    --end-date DATE       End date (YYYY-MM-DD)
    --output FILE         Output CSV filename (default: farm_[id]_stats.csv)

Examples:
    python farms.py list
    python farms.py get 123
    python farms.py stats 123 --start-date 2025-01-01 --end-date 2025-12-31
    python farms.py extract-ids
    """)

def main():
    """
    Command-line interface for Farms client.
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
    client = Farms(auth)
    
    command = sys.argv[1]

    try:
        if command == 'list':
            # Parse output filename
            output_file = "farms.csv"
            args = sys.argv[2:]
            for i in range(0, len(args), 2):
                if i + 1 >= len(args):
                    break
                if args[i] == '--output':
                    output_file = args[i + 1]
            
            # Get all farms
            print("\nFetching all farms...")
            df = client.get_farms()
            
            if df is not None:
                print(f"Total farms: {len(df)}")
                print("\nSample of farms data:")
                print(df.head())
                
                df.to_csv(output_file, index=False)
                print(f"\nData saved to {output_file}")

        elif command == 'get':
            if len(sys.argv) < 3:
                print("Error: Farm ID required")
                show_help()
                return
                
            farm_id = int(sys.argv[2])
            
            # Parse output filename
            output_file = f"farm_{farm_id}.csv"
            args = sys.argv[3:]
            for i in range(0, len(args), 2):
                if i + 1 >= len(args):
                    break
                if args[i] == '--output':
                    output_file = args[i + 1]
            
            print(f"\nFetching details for farm {farm_id}...")
            df = client.get_farm(farm_id)
            
            if df is not None:
                print("\nFarm details:")
                print(df)
                
                df.to_csv(output_file, index=False)
                print(f"\nData saved to {output_file}")

        elif command == 'stats':
            if len(sys.argv) < 3:
                print("Error: Farm ID required")
                show_help()
                return
                
            farm_id = int(sys.argv[2])
            
            # Parse command options
            start_date = None
            end_date = None
            output_file = f"farm_{farm_id}_stats.csv"
            
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
            
            print(f"\nFetching statistics for farm {farm_id}...")
            if start_date:
                print(f"Start date: {start_date}")
            if end_date:
                print(f"End date: {end_date}")
                
            df = client.get_farm_statistics(farm_id, start_date, end_date)
            
            if df is not None:
                print("\nFarm statistics:")
                print(df.head())
                
                df.to_csv(output_file, index=False)
                print(f"\nData saved to {output_file}")

        elif command == 'extract-ids':
            print("\nFetching farms to extract IDs...")
            df = client.get_farms()
            
            if df is not None and 'id' in df.columns:
                farm_ids_df = df[['id']].copy()
                output_file = "farm_ids.csv"
                farm_ids_df.to_csv(output_file, index=False)
                print(f"\nFarm IDs saved to {output_file}")
            else:
                print("Error: Could not extract farm IDs")

        else:
            print(f"Unknown command: {command}")
            show_help()

    except ValueError as e:
        print(f"Error: Invalid number format - {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()