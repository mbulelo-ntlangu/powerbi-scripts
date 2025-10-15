"""
Module for retrieving overview statistics from TerraCLIM API.
"""

import requests
from .auth import TerraCLIMAuth
from .utils import get_api_url, response_to_dataframe, handle_error_response, format_date

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

    def get_overview_stats(self, farm_id=None, field_id=None):
        """
        Retrieve overview statistics data.
        
        Args:
            farm_id (int): Filter by farm ID. Required if field_id is not provided.
            field_id (int, optional): Filter by field ID. If provided, must be a field within the farm.
            
        Returns:
            pandas.DataFrame: Overview statistics data
        """
        if farm_id is None and field_id is None:
            raise ValueError("Either farm_id or field_id must be provided")
            
        endpoint = "overview-stats/"
        url = get_api_url(endpoint)
        
        params = {}
        if field_id is not None:
            params['fieldID'] = field_id
        if farm_id is not None:
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