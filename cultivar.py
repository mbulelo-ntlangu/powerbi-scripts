"""
Module for retrieving cultivar data from TerraCLIM API.
"""

import requests
from auth import TerraCLIMAuth
from utils import get_api_url, response_to_dataframe, handle_error_response

class Cultivar:
    def __init__(self, auth_client=None):
        """
        Initialize the Cultivar client.
        
        Args:
            auth_client (TerraCLIMAuth, optional): Authentication client. If not provided, creates new one.
        """
        self.auth = auth_client if auth_client else TerraCLIMAuth()
        if not self.auth.is_authenticated():
            raise ValueError("Authentication required. Please login first.")

    def get_cultivars(self, crop_type_id=None):
        """
        Retrieve cultivar data.
        
        Args:
            crop_type_id (int, optional): Filter cultivars by crop type ID
            
        Returns:
            pandas.DataFrame: Cultivar data
        """
        endpoint = "cultivar/"
        url = get_api_url(endpoint)
        
        params = {}
        if crop_type_id:
            params['crop_type_id'] = crop_type_id
            
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting cultivars: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe(data)
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve cultivars: {str(e)}")
            return None

    def get_cultivar(self, cultivar_id):
        """
        Retrieve specific cultivar by ID.
        
        Args:
            cultivar_id (int): ID of the cultivar to retrieve
            
        Returns:
            pandas.DataFrame: Single cultivar data
        """
        endpoint = f"cultivar/{cultivar_id}/"
        url = get_api_url(endpoint)
        
        try:
            response = requests.get(
                url,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting cultivar {cultivar_id}: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe([data])  # Wrap in list for DataFrame
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve cultivar {cultivar_id}: {str(e)}")
            return None

def main():
    """
    Example usage of the Cultivar client.
    """
    # Initialize authentication
    auth = TerraCLIMAuth()
    if not auth.login():
        print("Failed to authenticate")
        return

    # Create client
    client = Cultivar(auth)
    
    # Example: Get all cultivars
    df = client.get_cultivars()
    
    if df is not None:
        print("Cultivars Data:")
        print(df.head())
        
        # Optionally save to CSV for Power BI
        output_file = "cultivars.csv"
        df.to_csv(output_file, index=False)
        print(f"Data saved to {output_file}")
        
        # Example: Get specific cultivar if we have data
        if not df.empty and 'id' in df.columns:
            first_cultivar_id = df.iloc[0]['id']
            single_cultivar = client.get_cultivar(first_cultivar_id)
            if single_cultivar is not None:
                print(f"\nSingle Cultivar (ID: {first_cultivar_id}):")
                print(single_cultivar)
                
        # Example: Get cultivars for a specific crop type
        if not df.empty and 'crop_type_id' in df.columns:
            first_crop_type = df.iloc[0]['crop_type_id']
            crop_cultivars = client.get_cultivars(crop_type_id=first_crop_type)
            if crop_cultivars is not None:
                print(f"\nCultivars for Crop Type {first_crop_type}:")
                print(crop_cultivars)

if __name__ == "__main__":
    main()