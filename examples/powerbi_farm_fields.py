"""
PowerBI data import script for TerraCLIM farm and field data.
This script demonstrates how to import TerraCLIM data into PowerBI.

Prerequisites:

1. Python Environment Setup:
   - Install Python 3.11 in C:\PowerBI_Python
   - Open command prompt as administrator and run:
     cd C:\PowerBI_Python
     python -m pip install --upgrade pip pandas matplotlib requests python-dotenv
     python -m pip install -e "path/to/terraclim/powerbi-scripts"

2. Configure PowerBI:
   - Open PowerBI Desktop
   - Go to File → Options and settings → Options
   - Under Global, select "Python scripting"
   - Set "Python home directory" to: C:\PowerBI_Python

3. Create PowerBI Parameters:
   - TERRACLIM_USERNAME (Text)
   - TERRACLIM_PASSWORD (Text)
   - TERRACLIM_BASE_URL (Text, optional, defaults to production URL)

Notes:
- The Python installation must be a standard installation, not a Windows Store version
- All users who need to refresh the report must have the same Python setup
- For automated refresh in PowerBI Service, contact your PowerBI admin to set up
  the Python environment on the PowerBI Service gateway
"""

import os
import sys
import pandas as pd

# PowerBI will automatically inject parameters as variables
# Make sure these parameters exist in your PowerBI report:
# - TERRACLIM_USERNAME
# - TERRACLIM_PASSWORD
# - TERRACLIM_BASE_URL (optional)

try:
    # These variables should be defined by PowerBI parameters
    username = str(TERRACLIM_USERNAME)  # PowerBI parameter
    password = str(TERRACLIM_PASSWORD)  # PowerBI parameter
    
    # Optional base URL parameter
    if 'TERRACLIM_BASE_URL' in locals():
        os.environ['TERRACLIM_BASE_URL'] = str(TERRACLIM_BASE_URL)
except NameError:
    # For testing outside PowerBI
    username = os.getenv('TERRACLIM_USERNAME', '')
    password = os.getenv('TERRACLIM_PASSWORD', '')

# Import TerraCLIM classes
from terraclim import TerraCLIMAuth, Farms, Fields

def get_error_df(error_message):
    """Create a DataFrame for error display"""
    return pd.DataFrame({
        'status': ['error'],
        'message': [error_message],
        'timestamp': [pd.Timestamp.now()]
    })

def format_farm_data(farms_response):
    """Convert farm response dictionary to DataFrame"""
    farm_list = []
    farms_dict = farms_response.iloc[0].to_dict()
    for farm_id, farm_data in farms_dict.items():
        try:
            if isinstance(farm_data, str):
                import json
                farm_data = json.loads(farm_data)
            farm_data['farm_id'] = farm_id  # Add farm_id to the dictionary
            # Skip farm_boundary to keep the data clean for PowerBI
            farm_data_clean = {k: v for k, v in farm_data.items() if k != 'farm_boundary'}
            farm_list.append(farm_data_clean)
        except Exception as e:
            print(f"Warning: Could not process farm {farm_id}: {str(e)}")
            continue
    return pd.DataFrame(farm_list)

try:
    # Print diagnostic information
    print("Authentication attempt with:")
    print(f"Username: {'[PROVIDED]' if username else '[MISSING]'}")
    print(f"Password: {'[PROVIDED]' if password else '[MISSING]'}")
    print(f"Base URL: {os.getenv('TERRACLIM_BASE_URL', '[using default]')}")
    
    # Initialize authentication with provided credentials
    auth = TerraCLIMAuth()
    login_result = auth.login(username=username, password=password)
    
    if not login_result:
        error_msg = "Failed to authenticate with TerraCLIM. Please verify:"
        error_msg += "\n1. PowerBI parameters TERRACLIM_USERNAME and TERRACLIM_PASSWORD exist"
        error_msg += "\n2. Parameter values are correct (no extra spaces)"
        error_msg += "\n3. You have an active TerraCLIM account"
        df = get_error_df(error_msg)
    else:
        print("Successfully authenticated with TerraCLIM")
        # Get farms data
        farms_client = Farms(auth)
        farms_response = farms_client.get_farms()
        
        if farms_response is None:
            df = get_error_df("Failed to retrieve farms data")
        else:
            # Convert farms data to DataFrame
            farms_df = format_farm_data(farms_response)
            print(f"\nRetrieved {len(farms_df)} farms")
            print("Available farm columns:")
            print(farms_df.columns.tolist())
            print("\nSample farm data:")
            print(farms_df.head(1))
            
            # Get fields data
            fields_client = Fields(auth)
            fields_df = fields_client.get_fields()
            
            if fields_df is None:
                df = get_error_df("Failed to retrieve fields data")
            else:
                print(f"Retrieved {len(fields_df)} fields")
                
                # Convert farm_id to same type for merging
                fields_df['farm'] = fields_df['farm'].astype(str)
                farms_df['farm_id'] = farms_df['farm_id'].astype(str)
                
                # Select farm columns for merge
                farm_columns = ['farm_id', 'farm_name', 'farmer_name']
                merge_columns = [col for col in farm_columns if col in farms_df.columns]
                
                # Merge farms and fields data
                df = fields_df.merge(
                    farms_df[merge_columns],
                    left_on='farm',  # fields table uses 'farm' column
                    right_on='farm_id',  # farms table uses 'farm_id' column
                    how='left'
                )
                
                # Clean up the merged data
                df = df.drop('farm_id', axis=1)  # Remove duplicate farm_id column
                df = df.rename(columns={'farm': 'farm_id'})  # Rename 'farm' to 'farm_id'
                
                # Reorder columns to put key information first
                desired_first = ['farm_id', 'farm_name', 'farmer_name', 
                               'field_id', 'field_name', 'area_ha', 'user_id']
                # Only include columns that actually exist
                first_columns = [col for col in desired_first if col in df.columns]
                other_columns = [col for col in df.columns if col not in first_columns]
                df = df[first_columns + other_columns]
                
                print(f"Final dataset has {len(df)} rows and {len(df.columns)} columns")

except Exception as e:
    df = get_error_df(str(e))

# The 'df' variable will be automatically detected by PowerBI