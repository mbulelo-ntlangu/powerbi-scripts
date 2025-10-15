"""
Test script for analysis statistics module.
"""

from terraclim.analysis_stats import AnalysisStats
from terraclim.auth import TerraCLIMAuth
from datetime import datetime, timedelta

def test_analysis_stats():
    # Initialize auth
    auth = TerraCLIMAuth()
    if not auth.login():
        print("Failed to authenticate")
        return
        
    # Create client
    client = AnalysisStats(auth)
    
    print("\nTest 1: Get analysis stats with required field_ids")
    test_field_id = 478  # Using known valid field ID
    df = client.get_analysis_stats(field_ids=test_field_id)
    if df is not None and not df.empty:
        print("Success: Retrieved analysis stats with field ID")
        print("\nColumns available:")
        print(df.columns.tolist())
        print("\nSample data:")
        print(df.head())
    else:
        print("Error: Failed to retrieve analysis stats")
        
    print("\nTest 3: Filter by single field ID")
    test_field_id = 478  # Using known valid field ID
    df = client.get_analysis_stats(field_ids=test_field_id)
    if df is not None:
        print(f"Success: Retrieved analysis for field {test_field_id}")
        print(f"Number of records: {len(df)}")
    else:
        print(f"Error: Failed to retrieve analysis for field {test_field_id}")
        
    print("\nTest 4: Missing field_ids parameter")
    try:
        df = client.get_analysis_stats()
        print("Error: Should have raised ValueError for missing field_ids")
    except ValueError as e:
        print("Success: Properly caught missing field_ids parameter")
        print(f"Error message: {str(e)}")
        
    print("\nTest 5: Invalid field ID")
    df = client.get_analysis_stats(field_ids=-1)
    if df is None or df.empty:
        print("Success: Properly handled invalid field ID")
    else:
        print("Error: Should have failed for invalid field ID")

if __name__ == "__main__":
    test_analysis_stats()