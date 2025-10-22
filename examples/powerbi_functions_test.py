"""
Test script for TerraCLIM PowerBI functions.
Tests that all PowerBI-specific functions are accessible and working.

Prerequisites:
1. PowerBI parameters:
   - TERRACLIM_USERNAME (Text)
   - TERRACLIM_PASSWORD (Text)
   - TERRACLIM_BASE_URL (Text, optional)
"""

import pandas as pd
import os

# Import all PowerBI wrapper functions
try:
    from terraclim import (
        get_workspaces,
        get_fields,
        get_farms,
        get_field_notes,
        get_geoserver_info
    )
    print("Successfully imported all PowerBI functions")
except ImportError as e:
    print(f"Error importing functions: {e}")
    # Create error DataFrame that PowerBI can display
    df = pd.DataFrame({
        'error': [f'Failed to import TerraCLIM functions: {str(e)}']
    })
    # Exit early
    raise SystemExit(1)

# Create initial status DataFrame
df = pd.DataFrame({
    'function_name': [],
    'import_status': [],
    'execution_status': [],
    'details': []
})

try:
    # These variables should be defined by PowerBI parameters
    username = str(TERRACLIM_USERNAME)  # PowerBI parameter
    password = str(TERRACLIM_PASSWORD)  # PowerBI parameter
    
    # Optional base URL parameter
    if 'TERRACLIM_BASE_URL' in locals():
        os.environ['TERRACLIM_BASE_URL'] = str(TERRACLIM_BASE_URL)

    # Test each function
    results = []

    # Test get_workspaces
    try:
        workspaces_df = get_workspaces(username=username, password=password)
        status = 'Success' if workspaces_df is not None else 'Failed'
        details = f'Retrieved {len(workspaces_df)} workspaces' if workspaces_df is not None else 'No data returned'
    except Exception as e:
        status = 'Error'
        details = str(e)
    results.append({
        'function_name': 'get_workspaces',
        'import_status': 'Success',
        'execution_status': status,
        'details': details
    })

    # Test get_farms
    try:
        farms_df = get_farms(username=username, password=password)
        status = 'Success' if farms_df is not None else 'Failed'
        details = f'Retrieved {len(farms_df)} farms' if farms_df is not None else 'No data returned'
    except Exception as e:
        status = 'Error'
        details = str(e)
    results.append({
        'function_name': 'get_farms',
        'import_status': 'Success',
        'execution_status': status,
        'details': details
    })

    # Test get_fields
    try:
        fields_df = get_fields(username=username, password=password)
        status = 'Success' if fields_df is not None else 'Failed'
        details = f'Retrieved {len(fields_df)} fields' if fields_df is not None else 'No data returned'
    except Exception as e:
        status = 'Error'
        details = str(e)
    results.append({
        'function_name': 'get_fields',
        'import_status': 'Success',
        'execution_status': status,
        'details': details
    })

    # Test get_field_notes (requires a field_id)
    try:
        if fields_df is not None and len(fields_df) > 0:
            field_id = fields_df.iloc[0]['field_id']
            notes_df = get_field_notes(username=username, password=password, field_id=field_id)
            status = 'Success' if notes_df is not None else 'Failed'
            details = f'Retrieved notes for field {field_id}' if notes_df is not None else 'No data returned'
        else:
            status = 'Skipped'
            details = 'No fields available to test with'
    except Exception as e:
        status = 'Error'
        details = str(e)
    results.append({
        'function_name': 'get_field_notes',
        'import_status': 'Success',
        'execution_status': status,
        'details': details
    })

    # Test get_geoserver_info
    try:
        if workspaces_df is not None and len(workspaces_df) > 0:
            workspace = workspaces_df.iloc[0]['name']
            info_df = get_geoserver_info(username=username, password=password, workspace=workspace)
            status = 'Success' if info_df is not None else 'Failed'
            details = f'Retrieved info for workspace {workspace}' if info_df is not None else 'No data returned'
        else:
            status = 'Skipped'
            details = 'No workspaces available to test with'
    except Exception as e:
        status = 'Error'
        details = str(e)
    results.append({
        'function_name': 'get_geoserver_info',
        'import_status': 'Success',
        'execution_status': status,
        'details': details
    })

    # Create final results DataFrame
    df = pd.DataFrame(results)

except Exception as e:
    # If we encounter an error before creating results, create an error DataFrame
    df = pd.DataFrame({
        'function_name': ['Overall'],
        'import_status': ['Error'],
        'execution_status': ['Error'],
        'details': [str(e)]
    })

# PowerBI will automatically detect this DataFrame