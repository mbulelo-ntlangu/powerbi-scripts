"""
Module for retrieving analysis statistics from TerraCLIM API.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Union
from auth import TerraCLIMAuth
from utils import get_api_url, response_to_dataframe, handle_error_response, format_date

class AnalysisStats:
    def __init__(self, auth_client=None):
        """
        Initialize the Analysis Stats client.
        
        Args:
            auth_client (TerraCLIMAuth, optional): Authentication client. If not provided, creates new one.
        """
        self.auth = auth_client if auth_client else TerraCLIMAuth()
        if not self.auth.is_authenticated():
            raise ValueError("Authentication required. Please login first.")

    def get_analysis_stats(self, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None,
                         field_ids: Optional[Union[List[int], int]] = None) -> Optional[pd.DataFrame]:
        """
        Retrieve analysis statistics data.
        
        Args:
            start_date (str, optional): Start date for analysis (YYYY-MM-DD).
                                      If not provided, defaults to 60 days ago.
            end_date (str, optional): End date for analysis (YYYY-MM-DD).
                                    If not provided, defaults to today.
            field_ids (Union[List[int], int], optional): List of field IDs or single field ID to analyze
            
        Returns:
            pandas.DataFrame: Analysis statistics data
        """
        endpoint = "analysis-stats/"
        url = get_api_url(endpoint)
        
        # Set default dates if not provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=60)).strftime('%Y-%m-%d')
            
        params = {
            'start_date': format_date(start_date),
            'end_date': format_date(end_date)
        }
        
        # Handle field_ids parameter
        if field_ids is not None:
            if isinstance(field_ids, (list, tuple)):
                params['field_id'] = ','.join(map(str, field_ids))
            else:
                params['field_id'] = str(field_ids)
            
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting analysis stats: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe(data, flatten=True)
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve analysis stats: {str(e)}")
            return None

def show_help():
    """
    Display help message for command-line usage.
    """
    print("""
TerraCLIM Analysis Stats Script Usage:
-----------------------------------
Basic Usage:
    python analysis_stats.py [command] [options]

Commands:
    get                     Get analysis statistics (defaults to last 60 days)
    help                    Show this help message

Options for 'get' command:
    --start-date DATE      Start date (YYYY-MM-DD)
    --end-date DATE       End date (YYYY-MM-DD)
    --fields IDS          Comma-separated list of field IDs (e.g., 1,2,3)
    --output FILE         Output CSV filename (default: analysis_stats.csv)

Examples:
    python analysis_stats.py get
    python analysis_stats.py get --start-date 2025-01-01 --end-date 2025-12-31
    python analysis_stats.py get --fields 1,2,3
    python analysis_stats.py get --output custom_stats.csv
    """)

def main():
    """
    Command-line interface for Analysis Stats.
    """
    import sys

    # Show help if no arguments or help requested
    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        return

    command = sys.argv[1]

    try:
        if command == 'get':
            # Initialize authentication
            auth = TerraCLIMAuth()
            if not auth.login():
                print("Failed to authenticate")
                return

            # Create client
            client = AnalysisStats(auth)
            
            # Parse command options
            start_date = None
            end_date = None
            field_ids = None
            output_file = "analysis_stats.csv"
            
            args = sys.argv[2:]
            for i in range(0, len(args), 2):
                if i + 1 >= len(args):
                    break
                    
                if args[i] == '--start-date':
                    start_date = args[i + 1]
                elif args[i] == '--end-date':
                    end_date = args[i + 1]
                elif args[i] == '--fields':
                    field_ids = [int(f.strip()) for f in args[i + 1].split(',')]
                elif args[i] == '--output':
                    output_file = args[i + 1]

            # Get the stats
            print(f"\nFetching analysis statistics...")
            if start_date:
                print(f"Start date: {start_date}")
            if end_date:
                print(f"End date: {end_date}")
            if field_ids:
                print(f"Fields: {field_ids}")
                
            df = client.get_analysis_stats(
                start_date=start_date,
                end_date=end_date,
                field_ids=field_ids
            )
            
            if df is not None:
                print(f"\nAnalysis Statistics Data:")
                print(f"Total records: {len(df)}")
                print("\nSample of data:")
                print(df.head())
                
                # Save to CSV
                df.to_csv(output_file, index=False)
                print(f"\nData saved to {output_file}")
            else:
                print("Failed to retrieve analysis statistics")

        else:
            print(f"Unknown command: {command}")
            show_help()

    except ValueError as e:
        print(f"Error: Invalid number format - {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()