"""
Module for retrieving climate filter table data from TerraCLIM API.
"""

import requests
from auth import TerraCLIMAuth
from utils import get_api_url, response_to_dataframe, handle_error_response, format_date

class ClimateFilter:
    def __init__(self, auth_client=None):
        """
        Initialize the Climate Filter client.
        
        Args:
            auth_client (TerraCLIMAuth, optional): Authentication client. If not provided, creates new one.
        """
        self.auth = auth_client if auth_client else TerraCLIMAuth()
        if not self.auth.is_authenticated():
            raise ValueError("Authentication required. Please login first.")

    def get_climate_data(self, field_id=None, start_date=None, end_date=None, variable=None):
        """
        Retrieve climate filter table data.
        
        Args:
            field_id (int, optional): Filter data by field ID
            start_date (str, optional): Start date for data range (YYYY-MM-DD)
            end_date (str, optional): End date for data range (YYYY-MM-DD)
            variable (str, optional): Climate variable to filter by
            
        Returns:
            pandas.DataFrame: Climate filter table data
        """
        endpoint = "filter-table/climate/"
        url = get_api_url(endpoint)
        
        params = {}
        if field_id:
            params['field_id'] = field_id
        if start_date:
            params['start_date'] = format_date(start_date)
        if end_date:
            params['end_date'] = format_date(end_date)
        if variable:
            params['variable'] = variable
            
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting climate data: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe(data, flatten=True)
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve climate data: {str(e)}")
            return None

    def get_available_variables(self):
        """
        Retrieve list of available climate variables.
        
        Returns:
            pandas.DataFrame: Available climate variables data
        """
        endpoint = "filter-table/climate/variables/"
        url = get_api_url(endpoint)
        
        try:
            response = requests.get(
                url,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting climate variables: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe(data)
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve climate variables: {str(e)}")
            return None

def show_help():
    """
    Display help message for command-line usage.
    """
    print("""
TerraCLIM Climate Filter Script Usage:
-----------------------------------
Basic Usage:
    python climate_filter.py [command] [options]

Commands:
    variables              List available climate variables
    data                  Get climate data with optional filters
    help                  Show this help message

Options for 'data' command:
    --field ID            Filter by field ID
    --variable VAR        Filter by climate variable
    --start-date DATE     Start date (YYYY-MM-DD)
    --end-date DATE      End date (YYYY-MM-DD)
    --output FILE        Output CSV filename (default: climate_data.csv)

Examples:
    python climate_filter.py variables
    python climate_filter.py data --variable temperature
    python climate_filter.py data --field 123 --start-date 2025-01-01 --end-date 2025-12-31
    python climate_filter.py data --variable rainfall --output rainfall_data.csv
    """)

def main():
    """
    Command-line interface for Climate Filter client.
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
    client = ClimateFilter(auth)
    
    command = sys.argv[1]

    try:
        if command == 'variables':
            print("\nFetching available climate variables...")
            df = client.get_available_variables()
            
            if df is not None:
                print("\nAvailable Climate Variables:")
                print(df)
                
                # Save variables to CSV
                output_file = "climate_variables.csv"
                df.to_csv(output_file, index=False)
                print(f"\nVariables saved to {output_file}")

        elif command == 'data':
            # Parse command options
            field_id = None
            variable = None
            start_date = None
            end_date = None
            output_file = "climate_data.csv"
            
            args = sys.argv[2:]
            for i in range(0, len(args), 2):
                if i + 1 >= len(args):
                    break
                    
                if args[i] == '--field':
                    field_id = int(args[i + 1])
                elif args[i] == '--variable':
                    variable = args[i + 1]
                elif args[i] == '--start-date':
                    start_date = args[i + 1]
                elif args[i] == '--end-date':
                    end_date = args[i + 1]
                elif args[i] == '--output':
                    output_file = args[i + 1]
            
            # Build description of what we're fetching
            print("\nFetching climate data with filters:")
            if field_id:
                print(f"Field ID: {field_id}")
            if variable:
                print(f"Variable: {variable}")
            if start_date:
                print(f"Start date: {start_date}")
            if end_date:
                print(f"End date: {end_date}")
            
            df = client.get_climate_data(
                field_id=field_id,
                variable=variable,
                start_date=start_date,
                end_date=end_date
            )
            
            if df is not None:
                print(f"\nTotal records: {len(df)}")
                print("\nSample of climate data:")
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