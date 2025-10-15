"""
Test script for overview statistics module.
"""

from terraclim.overview_stats import OverviewStats
from terraclim.auth import TerraCLIMAuth

def test_overview_stats():
    # Initialize auth
    auth = TerraCLIMAuth()
    if not auth.login():
        print("Failed to authenticate")
        return
        
    # Create client
    client = OverviewStats(auth)
    
    print("\nTest 1: Get overview stats with farm_id")
    test_farm_id = 38  # Known valid farm ID
    df = client.get_overview_stats(farm_id=test_farm_id)
    if df is not None and not df.empty:
        print("Success: Retrieved overview stats for farm")
        print("\nColumns available:")
        print(df.columns.tolist())
        print("\nSample data:")
        print(df.head())
    else:
        print("Error: Failed to retrieve overview stats")
        
    print("\nTest 2: Get overview stats with fieldID")
    test_field_id = 478  # Known valid field ID within farm 38
    df = client.get_overview_stats(field_id=test_field_id)
    if df is not None and not df.empty:
        print(f"Success: Retrieved statistics for field {test_field_id}")
        print(f"Number of records: {len(df)}")
    else:
        print(f"Error: Failed to retrieve statistics for field {test_field_id}")
        
    print("\nTest 3: Get overview stats with both farm_id and fieldID")
    df = client.get_overview_stats(farm_id=test_farm_id, field_id=test_field_id)
    if df is not None and not df.empty:
        print(f"Success: Retrieved statistics for field {test_field_id} in farm {test_farm_id}")
        print(f"Number of records: {len(df)}")
    else:
        print(f"Error: Failed to retrieve statistics for field in farm")
        
    print("\nTest 4: Missing both farm_id and fieldID")
    try:
        df = client.get_overview_stats()
        print("Error: Should have raised ValueError for missing parameters")
    except ValueError as e:
        print("Success: Properly caught missing parameters")
        print(f"Error message: {str(e)}")
        
    print("\nTest 5: Invalid farm_id")
    df = client.get_overview_stats(farm_id=-1)
    if df is None or df.empty:
        print("Success: Properly handled invalid farm ID")
    else:
        print("Error: Should have failed for invalid farm ID")
        
    print("\nTest 6: Invalid fieldID")
    df = client.get_overview_stats(field_id=-1)
    if df is None or df.empty:
        print("Success: Properly handled invalid field ID")
    else:
        print("Error: Should have failed for invalid field ID")

if __name__ == "__main__":
    test_overview_stats()