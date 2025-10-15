"""
Module for handling clone operations from TerraCLIM API.
"""

import requests
from auth import TerraCLIMAuth
from utils import get_api_url, response_to_dataframe, handle_error_response

class CloneClient:
    def __init__(self, auth_client=None):
        """
        Initialize the Clone client.
        
        Args:
            auth_client (TerraCLIMAuth, optional): Authentication client. If not provided, creates new one.
        """
        self.auth = auth_client if auth_client else TerraCLIMAuth()
        if not self.auth.is_authenticated():
            raise ValueError("Authentication required. Please login first.")

    def get_clone_data(self, model_type=None, instance_id=None):
        """
        Retrieve clone data from the API.
        
        Args:
            model_type (str, optional): Type of model to clone
            instance_id (int, optional): ID of the instance to clone
            
        Returns:
            pandas.DataFrame: Clone data
        """
        endpoint = "clone/"
        url = get_api_url(endpoint)
        
        params = {}
        if model_type:
            params['model_type'] = model_type
        if instance_id:
            params['instance_id'] = instance_id
            
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting clone data: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe(data)
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve clone data: {str(e)}")
            return None

def main():
    """
    Example usage of the Clone client.
    """
    # Initialize authentication
    auth = TerraCLIMAuth()
    if not auth.login():
        print("Failed to authenticate")
        return

    # Create client and get clone data
    client = CloneClient(auth)
    
    # Example: Get all clone data
    df = client.get_clone_data()
    
    if df is not None:
        print("Clone Data:")
        print(df.head())
        
        # Optionally save to CSV for Power BI
        output_file = "clone_data.csv"
        df.to_csv(output_file, index=False)
        print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()