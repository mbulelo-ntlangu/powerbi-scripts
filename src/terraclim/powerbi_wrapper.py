"""
Power BI wrapper functions for TerraCLIM API scripts.
These functions are designed to be called directly from Power BI's Python script connector.
"""

import os
import sys
import logging
import pandas as pd
import requests
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.getenv('TEMP', ''), 'terraclim_powerbi.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('terraclim_powerbi')

# Add package directory to Python path if needed
package_dir = Path(__file__).parent.parent
if str(package_dir) not in sys.path:
    sys.path.insert(0, str(package_dir))

from .auth import TerraCLIMAuth
from .geoserver_info import GeoServerInfo
from .fields import Fields
from .farms import Farms
from .field_notes import FieldNotes
from .farm_portions import FarmPortions

class TerraCLIMError(Exception):
    """Base exception for TerraCLIM errors"""
    pass

class AuthenticationError(TerraCLIMError):
    """Raised when authentication fails"""
    pass

class APIError(TerraCLIMError):
    """Raised when API calls fail"""
    pass

class DataValidationError(TerraCLIMError):
    """Raised when data validation fails"""
    pass

def handle_api_error(func):
    """Decorator to handle API errors and return appropriate DataFrames"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AuthenticationError as e:
            logger.error(f"Authentication failed: {str(e)}")
            return pd.DataFrame({'error': ['Authentication failed. Please check your credentials.']})
        except APIError as e:
            logger.error(f"API error: {str(e)}")
            return pd.DataFrame({'error': [f'API Error: {str(e)}']})
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error: {str(e)}")
            return pd.DataFrame({'error': ['Network error. Please check your internet connection.']})
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            return pd.DataFrame({'error': [f'Unexpected error: {str(e)}']})
    return wrapper

def validate_dataframe(df: pd.DataFrame, required_columns: list) -> None:
    """Validate DataFrame has required columns and is not empty"""
    if df.empty:
        raise DataValidationError("No data returned from API")
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise DataValidationError(f"Missing required columns: {', '.join(missing_cols)}")

def get_version_info() -> Dict[str, str]:
    """Get version information for troubleshooting"""
    return {
        'terraclim_version': getattr(sys.modules[__package__], '__version__', 'unknown'),
        'python_version': sys.version,
        'pandas_version': pd.__version__,
        'timestamp': datetime.now().isoformat()
    }

@handle_api_error
def get_workspaces(username: Optional[str] = None, password: Optional[str] = None) -> pd.DataFrame:
    """
    Get all available GeoServer workspaces.
    
    Args:
        username (str, optional): TerraCLIM username
        password (str, optional): TerraCLIM password
        
    Returns:
        pandas.DataFrame: Workspaces information with columns ['name', 'description']
        
    Raises:
        AuthenticationError: If login fails
        APIError: If API request fails
    """
    logger.info("Retrieving GeoServer workspaces")
    auth_client = TerraCLIMAuth()
    
    if not auth_client.login(username, password):
        raise AuthenticationError("Failed to authenticate with provided credentials")
        
    client = GeoServerInfo(auth_client)
    df = client.get_workspaces()
    
    try:
        validate_dataframe(df, ['name'])
        logger.info(f"Successfully retrieved {len(df)} workspaces")
        return df
    except DataValidationError as e:
        logger.error(f"Data validation error: {str(e)}")
        raise APIError(f"Invalid workspace data returned: {str(e)}")

def get_fields(username=None, password=None):
    """
    Get all fields information.
    
    Args:
        username (str, optional): TerraCLIM username
        password (str, optional): TerraCLIM password
        
    Returns:
        pandas.DataFrame: Fields information
    """
    auth_client = TerraCLIMAuth()
    if not auth_client.login(username, password):
        return pd.DataFrame()
        
    client = Fields(auth_client)
    return client.get_fields()

def get_farms(username=None, password=None):
    """
    Get all farms information.
    
    Args:
        username (str, optional): TerraCLIM username
        password (str, optional): TerraCLIM password
        
    Returns:
        pandas.DataFrame: Farms information
    """
    auth_client = TerraCLIMAuth()
    if not auth_client.login(username, password):
        return pd.DataFrame()
        
    client = Farms(auth_client)
    return client.get_farms()

def get_field_notes(username=None, password=None, field_id=None):
    """
    Get field notes for a specific field or all fields.
    
    Args:
        username (str, optional): TerraCLIM username
        password (str, optional): TerraCLIM password
        field_id (int, optional): Specific field ID to get notes for
        
    Returns:
        pandas.DataFrame: Field notes
    """
    auth_client = TerraCLIMAuth()
    if not auth_client.login(username, password):
        return pd.DataFrame()
        
    client = FieldNotes(auth_client)
    if field_id:
        return client.get_field_notes(field_id)
    return client.get_all_notes()

@handle_api_error
def get_farm_portions(username=None, password=None, farm_id=None, extent=None):
    """
    Get farm portions data, optionally filtered by farm ID and/or geographic extent.
    
    Args:
        username (str, optional): TerraCLIM username
        password (str, optional): TerraCLIM password
        farm_id (int, optional): Filter portions by farm ID
        extent (list, optional): Bounding box coordinates [minx, miny, maxx, maxy].
                               Example: [2086038.1755925221, -4033790.723493586, 
                                       2112561.824407478, -4007477.276506414]
        
    Returns:
        pandas.DataFrame: Farm portions data
    
    Examples:
        >>> # In Power BI, create these parameters:
        >>> # EXTENT_MINX (number)
        >>> # EXTENT_MINY (number)
        >>> # EXTENT_MAXX (number)
        >>> # EXTENT_MAXY (number)
        
        >>> # Then use in your script:
        >>> extent = [EXTENT_MINX, EXTENT_MINY, EXTENT_MAXX, EXTENT_MAXY]
        >>> df = tc.get_farm_portions(
        ...     username=TERRACLIM_USERNAME,
        ...     password=TERRACLIM_PASSWORD,
        ...     extent=extent
        ... )
    """
    auth_client = TerraCLIMAuth()
    if not auth_client.login(username, password):
        raise AuthenticationError("Failed to authenticate with provided credentials")
        
    client = FarmPortions(auth_client)
    df = client.get_farm_portions(farm_id=farm_id, extent=extent)
    
    try:
        required_columns = ['portion_id', 'farm_id']  # Add other required columns
        validate_dataframe(df, required_columns)
        logger.info(f"Successfully retrieved {len(df)} farm portions")
        return df
    except DataValidationError as e:
        logger.error(f"Data validation error: {str(e)}")
        raise APIError(f"Invalid farm portions data returned: {str(e)}")

def get_geoserver_info(username=None, password=None, workspace=None):
    """
    Get GeoServer information for a specific workspace.
    
    Args:
        username (str, optional): TerraCLIM username
        password (str, optional): TerraCLIM password
        workspace (str): GeoServer workspace name
        
    Returns:
        pandas.DataFrame: GeoServer information
    """
    auth_client = TerraCLIMAuth()
    if not auth_client.login(username, password):
        return pd.DataFrame()
        
    client = GeoServerInfo(auth_client)
    return client.get_info(workspace)