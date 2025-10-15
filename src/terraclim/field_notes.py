"""
Module for retrieving field notes data from TerraCLIM API.
"""

import requests
from .auth import TerraCLIMAuth
from .utils import get_api_url, response_to_dataframe, handle_error_response, format_date

class FieldNotes:
    def __init__(self, auth_client=None):
        """
        Initialize the Field Notes client.
        
        Args:
            auth_client (TerraCLIMAuth, optional): Authentication client. If not provided, creates new one.
        """
        self.auth = auth_client if auth_client else TerraCLIMAuth()
        if not self.auth.is_authenticated():
            raise ValueError("Authentication required. Please login first.")

    def get_field_notes(self, field_id=None, start_date=None, end_date=None):
        """
        Retrieve field notes data.
        
        Args:
            field_id (int, optional): Filter notes by field ID
            start_date (str, optional): Start date filter (YYYY-MM-DD)
            end_date (str, optional): End date filter (YYYY-MM-DD)
            
        Returns:
            pandas.DataFrame: Field notes data
        """
        endpoint = "field-notes/"
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
                print(f"Error getting field notes: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe(data)
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve field notes: {str(e)}")
            return None

    def get_field_note(self, note_id):
        """
        Retrieve specific field note by ID.
        
        Args:
            note_id (int): ID of the field note to retrieve
            
        Returns:
            pandas.DataFrame: Single field note data
        """
        endpoint = f"field-notes/{note_id}/"
        url = get_api_url(endpoint)
        
        try:
            response = requests.get(
                url,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting field note {note_id}: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe([data])  # Wrap in list for DataFrame
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve field note {note_id}: {str(e)}")
            return None

def main():
    """
    Example usage of the Field Notes client.
    """
    # Initialize authentication
    auth = TerraCLIMAuth()
    if not auth.login():
        print("Failed to authenticate")
        return

    # Create client
    client = FieldNotes(auth)
    
    # Example: Get all field notes for a date range
    df = client.get_field_notes(
        start_date="2025-01-01",
        end_date="2025-12-31"
    )
    
    if df is not None:
        print("Field Notes Data:")
        print(df.head())
        
        # Optionally save to CSV for Power BI
        output_file = "field_notes.csv"
        df.to_csv(output_file, index=False)
        print(f"Data saved to {output_file}")
        
        # Example: Get specific note if we have data
        if not df.empty and 'id' in df.columns:
            first_note_id = df.iloc[0]['id']
            single_note = client.get_field_note(first_note_id)
            if single_note is not None:
                print(f"\nSingle Field Note (ID: {first_note_id}):")
                print(single_note)
                
        # Example: Get notes for a specific field if we have field_id
        if not df.empty and 'field_id' in df.columns:
            first_field_id = df.iloc[0]['field_id']
            field_notes = client.get_field_notes(field_id=first_field_id)
            if field_notes is not None:
                print(f"\nField Notes for Field {first_field_id}:")
                print(field_notes)

if __name__ == "__main__":
    main()