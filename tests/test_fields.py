"""
Test script for fields module.
"""

from terraclim.auth import TerraCLIMAuth
from terraclim.fields import Fields

def test_fields():
    print("\nTesting Fields Module")
    print("-------------------")
    
    # Initialize authentication
    auth = TerraCLIMAuth()
    if not auth.login():
        print("Failed to authenticate")
        return
        
    # Create client
    client = Fields(auth)
    
    print("\nTest 1: Get all fields")
    df = client.get_fields()
    if df is not None and not df.empty:
        print("Success: Retrieved all fields")
        print(f"Number of fields: {len(df)}")
        print("\nColumns available:")
        print(df.columns.tolist())
        print("\nSample data:")
        print(df.head())
    else:
        print("Error: Failed to retrieve fields")
        
    # Test 2: Filter by specific farm ID
    print("\nTest 2: Filter by farm ID 525")
    farm_fields = client.get_fields(farm_id=525)
    if farm_fields is not None and not farm_fields.empty:
        print("Success: Retrieved fields for farm 525")
        print(f"Number of fields in farm: {len(farm_fields)}")
        print("\nSample data:")
        print(farm_fields.head())
    else:
        print("Error: Failed to retrieve fields for farm 525")
    
    # Test 3: Test error handling with non-existent farm ID
    print("\nTest 3: Filter by non-existent farm ID")
    non_existent_fields = client.get_fields(farm_id=99999)
    if non_existent_fields is None:
        print("Success: Properly returned None for non-existent farm ID")
    else:
        print("Error: Should have returned None for non-existent farm ID")

if __name__ == "__main__":
    test_fields()