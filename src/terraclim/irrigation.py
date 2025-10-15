"""
Module for retrieving irrigation data from TerraCLIM API.
"""

import requests
from auth import TerraCLIMAuth
from utils import get_api_url, response_to_dataframe, handle_error_response, format_date

class Irrigation:
    def __init__(self, auth_client=None):
        """
        Initialize the Irrigation client.
        
        Args:
            auth_client (TerraCLIMAuth, optional): Authentication client. If not provided, creates new one.
        """
        self.auth = auth_client if auth_client else TerraCLIMAuth()
        if not self.auth.is_authenticated():
            raise ValueError("Authentication required. Please login first.")

    def get_irrigation_data(self, field_id=None, start_date=None, end_date=None):
        """
        Retrieve irrigation data.
        
        Args:
            field_id (int, optional): Filter by field ID
            start_date (str, optional): Start date for data range (YYYY-MM-DD)
            end_date (str, optional): End date for data range (YYYY-MM-DD)
            
        Returns:
            pandas.DataFrame: Irrigation data
        """
        endpoint = "irrigation/"
        url = get_api_url(endpoint)
        
        params = {}
        if field_id:
            params['field_id'] = field_id
        if start_date:
            params['start_date'] = format_date(start_date)
        if end_date:
            params['end_date'] = format_date(end_date)
            
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting irrigation data: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe(data)
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve irrigation data: {str(e)}")
            return None

    def get_irrigation_record(self, record_id):
        """
        Retrieve specific irrigation record by ID.
        
        Args:
            record_id (int): ID of the irrigation record to retrieve
            
        Returns:
            pandas.DataFrame: Single irrigation record data
        """
        endpoint = f"irrigation/{record_id}/"
        url = get_api_url(endpoint)
        
        try:
            response = requests.get(
                url,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting irrigation record {record_id}: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe([data])  # Wrap in list for DataFrame
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve irrigation record {record_id}: {str(e)}")
            return None

    def get_irrigation_summary(self, field_id, start_date=None, end_date=None):
        """
        Retrieve irrigation summary for a specific field.
        
        Args:
            field_id (int): ID of the field
            start_date (str, optional): Start date for summary period (YYYY-MM-DD)
            end_date (str, optional): End date for summary period (YYYY-MM-DD)
            
        Returns:
            pandas.DataFrame: Irrigation summary data
        """
        endpoint = f"irrigation/summary/{field_id}/"
        url = get_api_url(endpoint)
        
        params = {}
        if start_date:
            params['start_date'] = format_date(start_date)
        if end_date:
            params['end_date'] = format_date(end_date)
            
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting irrigation summary for field {field_id}: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe([data])  # Wrap in list for DataFrame
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve irrigation summary for field {field_id}: {str(e)}")
            return None

def main():
    """
    Example usage of the Irrigation client.
    """
    # Initialize authentication
    auth = TerraCLIMAuth()
    if not auth.login():
        print("Failed to authenticate")
        return

    # Create client
    client = Irrigation(auth)
    
    # Example: Get irrigation data for a date range
    df = client.get_irrigation_data(
        start_date="2025-01-01",
        end_date="2025-12-31"
    )
    
    if df is not None:
        print("Irrigation Data:")
        print(df.head())
        
        # Save to CSV for Power BI
        output_file = "irrigation_data.csv"
        df.to_csv(output_file, index=False)
        print(f"Data saved to {output_file}")
        
        # Example: Get specific irrigation record if we have data
        if not df.empty and 'id' in df.columns:
            first_record_id = df.iloc[0]['id']
            record = client.get_irrigation_record(first_record_id)
            if record is not None:
                print(f"\nIrrigation Record (ID: {first_record_id}):")
                print(record)
                
        # Example: Get irrigation summary for a field if we have field_id
        if not df.empty and 'field_id' in df.columns:
            first_field_id = df.iloc[0]['field_id']
            summary = client.get_irrigation_summary(
                first_field_id,
                start_date="2025-01-01",
                end_date="2025-12-31"
            )
            if summary is not None:
                print(f"\nIrrigation Summary for Field {first_field_id}:")
                print(summary)
                
                # Save summary to CSV
                summary_file = f"irrigation_summary_field_{first_field_id}.csv"
                summary.to_csv(summary_file, index=False)
                print(f"Summary saved to {summary_file}")

if __name__ == "__main__":
    main()