"""
Test script for farms module.
"""

from terraclim.auth import TerraCLIMAuth
from terraclim.farms import Farms

def test_farms():
    print("\nTesting Farms Module")
    print("-------------------")
    
    # Initialize authentication
    auth = TerraCLIMAuth()
    if not auth.login():
        print("Failed to authenticate")
        return
        
    # Create client
    client = Farms(auth)
    
    print("\nTest 1: Get all farms")
    df = client.get_farms()
    if df is not None:
        print("Success: Retrieved all farms")
        farm_dict = df.iloc[0].to_dict()
        all_farm_ids = list(farm_dict.keys())
        farm_count = len(all_farm_ids)
        print(f"Number of farms: {farm_count}")
        
        # Get details of first farm for sample
        first_farm_id = all_farm_ids[0]
        first_farm = farm_dict[first_farm_id]
        print("\nAvailable farm properties:")
        print(list(first_farm.keys()))
        print("\nSample farm data (Farm ID: {}):" .format(first_farm_id))
        for key, value in first_farm.items():
            if key not in ['farm_boundary']:  # Skip the large geometry object
                print(f"{key}: {value}")
    else:
        print("Error: Failed to retrieve farms")
        
    # Test 2: Extract specific farm from all farms response
    farm_id_to_find = "525"  # Farm IDs are returned as strings
    print(f"\nTest 2: Get specific farm (ID: {farm_id_to_find})")
    if df is not None and farm_id_to_find in farm_dict:
        farm_data = farm_dict[farm_id_to_find]
        print("Success: Found farm 525 in farms list")
        print("\nFarm details:")
        for key, value in farm_data.items():
            if key not in ['farm_boundary']:  # Skip the large geometry object
                print(f"{key}: {value}")
    else:
        print(f"Error: Failed to find farm {farm_id_to_find} in farms list")
            
    # Test 3: Test error handling with non-existent farm ID
    non_existent_id = "99999"
    print(f"\nTest 3: Look for non-existent farm ID ({non_existent_id})")
    if df is not None and non_existent_id not in farm_dict:
        print("Success: Non-existent farm ID was not found in farms list")
    else:
        print("Error: Unexpectedly found non-existent farm ID in farms list")

if __name__ == "__main__":
    test_farms()