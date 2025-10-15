"""
Sample Power BI data retrieval script.
This script demonstrates how to use the TerraCLIM package in Power BI.
"""

import terraclim as tc
import pandas as pd

def get_error_df(error_message):
    """Create a DataFrame for error display"""
    return pd.DataFrame({
        'status': ['error'],
        'message': [error_message],
        'timestamp': [pd.Timestamp.now()]
    })

try:
    # Get version info (useful for troubleshooting)
    version_info = tc.get_version_info()
    
    # Get credentials (replace with Power BI parameters)
    username = 'TERRACLIM_USERNAME'  # Replace with Power BI parameter
    password = 'TERRACLIM_PASSWORD'  # Replace with Power BI parameter
    
    # Get workspaces
    workspaces_df = tc.get_workspaces(username, password)
    if 'error' in workspaces_df.columns:
        df = workspaces_df  # Return error DataFrame
    else:
        # Get farms data with extent filter
        # These would be Power BI parameters
        extent = [
            2086038.1755925221,  # EXTENT_MINX
            -4033790.723493586,  # EXTENT_MINY
            2112561.824407478,   # EXTENT_MAXX
            -4007477.276506414   # EXTENT_MAXY
        ]
        
        # Get farm portions in the specified extent
        portions_df = tc.get_farm_portions(username, password, extent=extent)
        if 'error' in portions_df.columns:
            df = portions_df
        else:
            # Get farms data for these portions
            farm_ids = portions_df['farm_id'].unique().tolist()
            farms_df = tc.get_farms(username, password)
            if 'error' in farms_df.columns:
                df = farms_df
            else:
                # Filter farms to those in our extent
                farms_df = farms_df[farms_df['farm_id'].isin(farm_ids)]
                
                # Get fields data
                fields_df = tc.get_fields(username, password)
                if 'error' in fields_df.columns:
                    df = fields_df
                else:
                    # Filter fields to farms in our extent
                    fields_df = fields_df[fields_df['farm_id'].isin(farm_ids)]
                    
                    # Combine all the data
                    df = fields_df.merge(
                        farms_df[['farm_id', 'farm_name', 'farm_area']], 
                        on='farm_id', 
                        how='left'
                    ).merge(
                        portions_df[['farm_id', 'portion_id', 'area']], 
                        on='farm_id',
                        how='left'
                    )
                
                # Add workspace information if applicable
                if not workspaces_df.empty:
                    df['available_workspaces'] = ', '.join(workspaces_df['name'].tolist())

except Exception as e:
    df = get_error_df(str(e))