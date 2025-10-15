"""
Module for retrieving crop type data from TerraCLIM API.
"""

import requests
from auth import TerraCLIMAuth
from utils import get_api_url, response_to_dataframe, handle_error_response

class CropType:
    def __init__(self, auth_client=None):
        """
        Initialize the Crop Type client.
        
        Args:
            auth_client (TerraCLIMAuth, optional): Authentication client. If not provided, creates new one.
        """
        self.auth = auth_client if auth_client else TerraCLIMAuth()
        if not self.auth.is_authenticated():
            raise ValueError("Authentication required. Please login first.")

    def get_crop_types(self):
        """
        Retrieve all crop types data.
        
        Returns:
            pandas.DataFrame: Crop types data
        """
        endpoint = "cropType/"
        url = get_api_url(endpoint)
        
        try:
            response = requests.get(
                url,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting crop types: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe(data)
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve crop types: {str(e)}")
            return None

    def get_crop_type(self, crop_id):
        """
        Retrieve specific crop type by ID.
        
        Args:
            crop_id (int): ID of the crop type to retrieve
            
        Returns:
            pandas.DataFrame: Single crop type data
        """
        endpoint = f"cropType/{crop_id}/"
        url = get_api_url(endpoint)
        
        try:
            response = requests.get(
                url,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting crop type {crop_id}: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe([data])  # Wrap in list for DataFrame
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve crop type {crop_id}: {str(e)}")
            return None

def main():
    """
    Example usage of the Crop Type client.
    """
    # Initialize authentication
    auth = TerraCLIMAuth()
    if not auth.login():
        print("Failed to authenticate")
        return

    # Create client
    client = CropType(auth)
    
    # Example: Get all crop types
    df = client.get_crop_types()
    
    if df is not None:
        print("Crop Types Data:")
        print(df.head())
        
        # Optionally save to CSV for Power BI
        output_file = "crop_types.csv"
        df.to_csv(output_file, index=False)
        print(f"Data saved to {output_file}")
        
        # Example: Get specific crop type if we have data
        if not df.empty and 'id' in df.columns:
            first_crop_id = df.iloc[0]['id']
            single_crop = client.get_crop_type(first_crop_id)
            if single_crop is not None:
                print(f"\nSingle Crop Type (ID: {first_crop_id}):")
                print(single_crop)

if __name__ == "__main__":
    main()