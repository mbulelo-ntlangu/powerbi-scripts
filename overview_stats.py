"""
Module for retrieving overview statistics from TerraCLIM API.
"""

import requests
from auth import TerraCLIMAuth
from utils import get_api_url, response_to_dataframe, handle_error_response, format_date

class OverviewStats:
    def __init__(self, auth_client=None):
        """
        Initialize the Overview Stats client.
        
        Args:
            auth_client (TerraCLIMAuth, optional): Authentication client. If not provided, creates new one.
        """
        self.auth = auth_client if auth_client else TerraCLIMAuth()
        if not self.auth.is_authenticated():
            raise ValueError("Authentication required. Please login first.")

    def get_overview_stats(self, start_date=None, end_date=None, field_id=None, farm_id=None):
        """
        Retrieve overview statistics data.
        
        Args:
            start_date (str, optional): Start date for statistics (YYYY-MM-DD)
            end_date (str, optional): End date for statistics (YYYY-MM-DD)
            field_id (int, optional): Filter by field ID
            farm_id (int, optional): Filter by farm ID
            
        Returns:
            pandas.DataFrame: Overview statistics data
        """
        endpoint = "overview-stats/"
        url = get_api_url(endpoint)
        
        params = {}
        if start_date:
            params['start_date'] = format_date(start_date)
        if end_date:
            params['end_date'] = format_date(end_date)
        if field_id:
            params['field_id'] = field_id
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
                print(f"Error getting overview stats: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe(data)
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve overview stats: {str(e)}")
            return None

    def get_summary(self):
        """
        Retrieve summary overview statistics.
        
        Returns:
            pandas.DataFrame: Summary statistics data
        """
        endpoint = "overview-stats/summary/"
        url = get_api_url(endpoint)
        
        try:
            response = requests.get(
                url,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting overview summary: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe([data])  # Wrap in list for DataFrame
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve overview summary: {str(e)}")
            return None

def main():
    """
    Example usage of the Overview Stats client.
    """
    # Initialize authentication
    auth = TerraCLIMAuth()
    if not auth.login():
        print("Failed to authenticate")
        return

    # Create client
    client = OverviewStats(auth)
    
    # Example: Get overall summary
    summary_df = client.get_summary()
    if summary_df is not None:
        print("Overview Summary:")
        print(summary_df)
        
        # Save summary to CSV for Power BI
        summary_file = "overview_summary.csv"
        summary_df.to_csv(summary_file, index=False)
        print(f"Summary saved to {summary_file}")
    
    # Example: Get detailed overview stats for a date range
    stats_df = client.get_overview_stats(
        start_date="2025-01-01",
        end_date="2025-12-31"
    )
    
    if stats_df is not None:
        print("\nDetailed Overview Statistics:")
        print(stats_df.head())
        
        # Save detailed stats to CSV for Power BI
        stats_file = "overview_stats.csv"
        stats_df.to_csv(stats_file, index=False)
        print(f"Statistics saved to {stats_file}")

if __name__ == "__main__":
    main()