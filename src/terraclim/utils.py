"""
Utility functions and constants for TerraCLIM API integration.
"""

import os
from datetime import datetime
import pandas as pd

# API Constants
BASE_URL = "https://dashboard.staging.terraclim.co.za"
API_VERSION = os.getenv('TERRACLIM_API_VERSION', 'v0')

def get_api_url(endpoint, versioned=True):
    """
    Construct full API URL for a given endpoint.
    
    Args:
        endpoint (str): API endpoint path
        versioned (bool): Whether to include API version in URL
        
    Returns:
        str: Full API URL
    """
    # Remove leading slash if present
    endpoint = endpoint.lstrip('/')
    
    # Handle different endpoint types
    if endpoint.startswith('token'):  # Auth endpoints
        return f"{BASE_URL}/api/{endpoint}"
    else:  # All other endpoints are versioned API endpoints
        return f"{BASE_URL}/api/{API_VERSION}/{endpoint}" if versioned else f"{BASE_URL}/api/{endpoint}"

def response_to_dataframe(response_data, flatten=False):
    """
    Convert API response to pandas DataFrame for PowerBI consumption.
    Handles both regular JSON and GeoJSON FeatureCollection formats.
    
    Args:
        response_data (dict/list): API response data
        flatten (bool): Whether to flatten nested JSON structures
        
    Returns:
        pandas.DataFrame: DataFrame containing the response data
    """
    if not response_data:
        return pd.DataFrame()
    
    try:
        # Handle GeoJSON FeatureCollection format
        if isinstance(response_data, dict) and response_data.get('type') == 'FeatureCollection':
            features = response_data.get('features', [])
            records = []
            for feature in features:
                record = {
                    'id': feature.get('id'),
                    'type': feature.get('type'),
                    'geometry': feature.get('geometry'),
                }
                # Add properties if they exist
                if 'properties' in feature:
                    record.update(feature['properties'])
                records.append(record)
            return pd.DataFrame(records)
        
        # Handle regular JSON responses
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
    print(f"Response Status: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response Text: {response.text[:500]}...")  # Show first 500 chars
    
    content_type = response.headers.get('content-type', '')
    
    # First check if response is HTML
    if 'text/html' in content_type:
        return False, "Received HTML response instead of JSON"
    
    # Try to parse response as JSON
    try:
        data = response.json()
    except ValueError:
        return False, "Invalid JSON response"

    # Check for server-side AttributeError about 'user'
    if isinstance(data, dict) and any(k.startswith("<class 'AttributeError'>") for k in data.keys()):
        print("Server error: Authentication service unavailable")
        return False, "Authentication service temporarily unavailable"
        
    if response.ok:
        # For successful responses, verify it's a JSON object or array
        if isinstance(data, (dict, list)):
            return True, None
        return False, "Invalid response format"
    
    # Handle error responses
    if isinstance(data, dict):
        error_msg = data.get('detail', str(data))
    else:
        error_msg = str(data)
    
    return False, error_msg
    try:
        error_data = response.json()
        if isinstance(error_data, dict):
            # Check for error details in various formats
            error_msg = error_data.get('detail') or error_data.get('message') or error_data.get('error')
            if not error_msg and any(isinstance(v, dict) for v in error_data.values()):
                # If we have nested error objects, combine their messages
                error_msg = ", ".join(str(v) for v in error_data.values() if v)
            error_msg = error_msg or str(error_data)
        else:
            error_msg = str(error_data)
    except:
        error_msg = response.text or f"HTTP {response.status_code}"
        
    return False, error_msg