"""
Test script for farm portions module with GeoJSON response handling.
"""

import pandas as pd
from terraclim.farm_portions import FarmPortions
from terraclim.auth import TerraCLIMAuth

def test_farm_portions():
    # Initialize auth
    auth = TerraCLIMAuth()
    if not auth.login():
        print("Failed to authenticate")
        return
        
    # Create client
    client = FarmPortions(auth)
    
    # Test extent parameter
    test_extent = [2086038.1755925221, -4033790.723493586, 
                   2112561.824407478, -4007477.276506414]
    
    print("\nTest 1: Verify extent parameter formatting")
    url = client._build_url(extent=test_extent)
    expected_format = "[2086038.1755925221, -4033790.723493586, 2112561.824407478, -4007477.276506414]"
    if "extent=" + expected_format in url:
        print("Success: Extent parameter formatted correctly")
    else:
        print(f"Error: Incorrect extent parameter format")
        print(f"Expected: {expected_format}")
        print(f"Found in URL: {url}")
    
    print("\nTest 2: Get farm portions with extent")
    df = client.get_farm_portions(extent=test_extent)
    print(f"Farm portions in extent: {len(df) if df is not None else 'Error'}")
    
    if df is not None and not df.empty:
        print("\nColumns available:")
        print(df.columns.tolist())
        print("\nFirst row summary:")
        first_row = df.iloc[0]
        print(f"Feature ID: {first_row.get('id')}")
        print(f"Type: {first_row.get('type')}")
        print(f"Farm Portion ID: {first_row.get('farm_portion_id')}")
        geometry = first_row.get('geometry', {})
        print(f"Geometry Type: {geometry.get('type')}")
        print(f"CRS: {geometry.get('crs', {}).get('properties', {}).get('name')}")
    
    print("\nTest 3: Verify GeoJSON structure")
    if df is not None and not df.empty:
        # Check required columns
        required_columns = ['id', 'type', 'geometry', 'farm_portion_id']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Error: Missing required columns: {missing_columns}")
        else:
            print("Success: All required columns present")
        
        # Check geometry structure
        first_geom = df.iloc[0]['geometry']
        if isinstance(first_geom, dict):
            print("Success: Geometry is properly preserved as dictionary")
            if first_geom.get('type') == 'MultiPolygon':
                print("Success: Geometry type is MultiPolygon")
            else:
                print(f"Error: Unexpected geometry type: {first_geom.get('type')}")
        else:
            print(f"Error: Geometry is not a dictionary: {type(first_geom)}")
    
    print("\nTest 4: Get farm portions for specific farm with extent")
    # Use a test farm_id since we can't get it from the response
    test_farm_id = 123  # Example farm ID
    df = client.get_farm_portions(farm_id=test_farm_id, extent=test_extent)
    print(f"Farm portions for farm {test_farm_id} in extent: {len(df) if df is not None else 'Error'}")
    
    # Test error handling
    print("\nTest 5: Missing extent parameter")
    try:
        df = client.get_farm_portions()  # No extent parameter
        print("Error: Test should have failed")
    except TypeError as e:
        print(f"Successfully caught error: Missing required argument 'extent'")
    
    print("\nTest 6: Invalid extent format")
    try:
        df = client.get_farm_portions(extent=[1, 2, 3])  # Missing one coordinate
        print("Error: Test should have failed")
    except ValueError as e:
        print(f"Successfully caught error: {str(e)}")
        
    print("\nTest 7: Invalid extent values")
    try:
        df = client.get_farm_portions(extent=['a', 'b', 'c', 'd'])  # Invalid coordinates
        print("Error: Test should have failed")
    except ValueError as e:
        print(f"Successfully caught error: {str(e)}")
        


if __name__ == "__main__":
    test_farm_portions()