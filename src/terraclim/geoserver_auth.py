"""
Module for retrieving GeoServer authentication key from TerraCLIM API.
"""

import requests
from .auth import TerraCLIMAuth
from .utils import get_api_url, response_to_dataframe, handle_error_response

class GeoServerAuth:
    def __init__(self, auth_client=None):
        """
        Initialize the GeoServer Authentication client.
        
        Args:
            auth_client (TerraCLIMAuth, optional): Authentication client. If not provided, creates new one.
        """
        self.auth = auth_client if auth_client else TerraCLIMAuth()
        if not self.auth.is_authenticated():
            raise ValueError("Authentication required. Please login first.")

    def get_auth_key(self):
        """
        Retrieve GeoServer authentication key.
        
        Returns:
            pandas.DataFrame: GeoServer authentication key data
        """
        endpoint = "geoserver/authkey"
        url = get_api_url(endpoint)
        
        try:
            response = requests.get(
                url,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting GeoServer auth key: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe([data])  # Wrap in list for DataFrame
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve GeoServer auth key: {str(e)}")
            return None

def main():
    """
    Example usage of the GeoServer Authentication client.
    """
    # Initialize authentication
    auth = TerraCLIMAuth()
    if not auth.login():
        print("Failed to authenticate")
        return

    # Create client
    client = GeoServerAuth(auth)
    
    # Get GeoServer authentication key
    df = client.get_auth_key()
    
    if df is not None:
        print("GeoServer Authentication Key:")
        print(df)
        
        # Optionally save to CSV for Power BI
        output_file = "geoserver_auth.csv"
        df.to_csv(output_file, index=False)
        print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()