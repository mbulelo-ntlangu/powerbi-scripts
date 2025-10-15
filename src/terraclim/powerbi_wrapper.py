"""
Power BI wrapper functions for TerraCLIM API scripts.
These functions are designed to be called directly from Power BI's Python script connector.
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add package directory to Python path if needed
package_dir = Path(__file__).parent.parent
if str(package_dir) not in sys.path:
    sys.path.insert(0, str(package_dir))

from auth import TerraCLIMAuth
from geoserver_info import GeoServerInfo
from fields import FieldInfo
from farms import FarmInfo
from field_notes import FieldNotes

def get_workspaces(username=None, password=None):
    """
    Get all available GeoServer workspaces.
    
    Args:
        username (str, optional): TerraCLIM username
        password (str, optional): TerraCLIM password
        
    Returns:
        pandas.DataFrame: Workspaces information
    """
    auth_client = TerraCLIMAuth()
    if not auth_client.login(username, password):
        return pd.DataFrame()
        
    client = GeoServerInfo(auth_client)
    return client.get_workspaces()

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
        
    client = FieldInfo(auth_client)
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
        
    client = FarmInfo(auth_client)
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