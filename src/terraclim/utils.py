"""
Utility functions and constants for TerraCLIM API integration.
"""

import os
from datetime import datetime
import pandas as pd

# API Constants
BASE_URL = "https://dashboard.staging.terraclim.co.za"
API_VERSION = "v0"

def get_api_url(endpoint):
    """
    Construct full API URL for a given endpoint.
    
    Args:
        endpoint (str): API endpoint path
        
    Returns:
        str: Full API URL
    """
    # Remove leading slash if present
    endpoint = endpoint.lstrip('/')
    return f"{BASE_URL}/api/{API_VERSION}/{endpoint}"

def response_to_dataframe(response_data, flatten=False):
    """
    Convert API response to pandas DataFrame for PowerBI consumption.
    
    Args:
        response_data (dict/list): API response data
        flatten (bool): Whether to flatten nested JSON structures
        
    Returns:
        pandas.DataFrame: DataFrame containing the response data
    """
    if not response_data:
        return pd.DataFrame()
    
    try:
        if isinstance(response_data, dict):
            if flatten:
                df = pd.json_normalize([response_data])
            else:
                df = pd.DataFrame([response_data])
        else:
            if flatten:
                df = pd.json_normalize(response_data)
            else:
                df = pd.DataFrame(response_data)
        
        return df
    except Exception as e:
        print(f"Error converting response to DataFrame: {str(e)}")
        print(f"Response data type: {type(response_data)}")
        print(f"Response data: {response_data}")
        return pd.DataFrame()

def format_date(date_str):
    """
    Format date string to ISO format.
    
    Args:
        date_str (str): Date string in any format
        
    Returns:
        str: ISO formatted date string
    """
    if not date_str:
        return None
        
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.isoformat()
    except ValueError:
        try:
            # Try parsing with datetime if date fails
            date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            return date_obj.isoformat()
        except ValueError:
            return None

def handle_error_response(response):
    """
    Handle error responses from the API.
    
    Args:
        response (requests.Response): API response object
        
    Returns:
        tuple: (bool, str) - (Success status, Error message if any)
    """
    if response.ok:
        return True, None
        
    error_msg = "Unknown error"
    try:
        error_data = response.json()
        if isinstance(error_data, dict):
            error_msg = error_data.get('detail', error_data.get('message', str(error_data)))
        else:
            error_msg = str(error_data)
    except:
        error_msg = response.text or f"HTTP {response.status_code}"
        
    return False, error_msg