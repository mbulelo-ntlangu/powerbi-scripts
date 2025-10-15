"""
Test script for TerraCLIM PowerBI integration.
Tests each component individually before running the full script.
"""

import pandas as pd
import os
import sys

# Create initial status DataFrame
df = pd.DataFrame({
    'component': ['Starting tests...'],
    'status': ['Running'],
    'details': [''],
    'timestamp': [pd.Timestamp.now()]
})

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

    print(f"\nUsername found: {'yes' if username else 'no'}")
    print(f"Password found: {'yes' if password else 'no'}")

    # Import TerraCLIM modules one by one
    from terraclim.auth import TerraCLIMAuth
    from terraclim.farms import Farms
    from terraclim.fields import Fields
    from terraclim.overview_stats import OverviewStats
    from terraclim.analysis_stats import AnalysisStats
    
    # Initialize authentication
    auth = TerraCLIMAuth()
    login_result = auth.login(username=username, password=password)
    
    if not login_result:
        df = pd.DataFrame({
            'component': ['Authentication'],
            'status': ['Failed'],
            'details': ['Check username and password'],
            'timestamp': [pd.Timestamp.now()]
        })
    else:
        # Test each component
        results = []
        
        # 1. Test Farms
        try:
            farms_client = Farms(auth)
            farms_response = farms_client.get_farms()
            farm_count = len(farms_response) if farms_response is not None else 0
            results.append({
                'component': 'Farms',
                'status': 'Success' if farms_response is not None else 'Failed',
                'details': f'Retrieved {farm_count} farms' if farms_response is not None else 'No data returned',
                'timestamp': pd.Timestamp.now()
            })
        except Exception as e:
            results.append({
                'component': 'Farms',
                'status': 'Error',
                'details': str(e),
                'timestamp': pd.Timestamp.now()
            })
        
        # 2. Test Fields
        try:
            fields_client = Fields(auth)
            fields_df = fields_client.get_fields()
            field_count = len(fields_df) if fields_df is not None else 0
            results.append({
                'component': 'Fields',
                'status': 'Success' if fields_df is not None else 'Failed',
                'details': f'Retrieved {field_count} fields' if fields_df is not None else 'No data returned',
                'timestamp': pd.Timestamp.now()
            })
        except Exception as e:
            results.append({
                'component': 'Fields',
                'status': 'Error',
                'details': str(e),
                'timestamp': pd.Timestamp.now()
            })
        
        # 3. Test Overview Stats
        try:
            overview_client = OverviewStats(auth)
            # Try with first farm if available
            farm_id = farms_response.iloc[0].name if farms_response is not None and len(farms_response) > 0 else None
            if farm_id:
                overview_df = overview_client.get_overview_stats(farm_id=farm_id)
                results.append({
                    'component': 'Overview Stats',
                    'status': 'Success' if overview_df is not None else 'Failed',
                    'details': f'Retrieved stats for farm {farm_id}' if overview_df is not None else 'No data returned',
                    'timestamp': pd.Timestamp.now()
                })
            else:
                results.append({
                    'component': 'Overview Stats',
                    'status': 'Skipped',
                    'details': 'No farms available to test with',
                    'timestamp': pd.Timestamp.now()
                })
        except Exception as e:
            results.append({
                'component': 'Overview Stats',
                'status': 'Error',
                'details': str(e),
                'timestamp': pd.Timestamp.now()
            })
        
        # 4. Test Analysis Stats
        try:
            analysis_client = AnalysisStats(auth)
            # Try with first field if available
            field_id = fields_df.iloc[0]['field_id'] if fields_df is not None and len(fields_df) > 0 else None
            if field_id:
                analysis_df = analysis_client.get_analysis_stats(field_ids=field_id)
                results.append({
                    'component': 'Analysis Stats',
                    'status': 'Success' if analysis_df is not None else 'Failed',
                    'details': f'Retrieved stats for field {field_id}' if analysis_df is not None else 'No data returned',
                    'timestamp': pd.Timestamp.now()
                })
            else:
                results.append({
                    'component': 'Analysis Stats',
                    'status': 'Skipped',
                    'details': 'No fields available to test with',
                    'timestamp': pd.Timestamp.now()
                })
        except Exception as e:
            results.append({
                'component': 'Analysis Stats',
                'status': 'Error',
                'details': str(e),
                'timestamp': pd.Timestamp.now()
            })
        
        # Create final results DataFrame
        df = pd.DataFrame(results)

except Exception as e:
    df = pd.DataFrame({
        'component': ['Overall'],
        'status': ['Error'],
        'details': [str(e)],
        'timestamp': [pd.Timestamp.now()]
    })

# PowerBI will automatically detect this DataFrame