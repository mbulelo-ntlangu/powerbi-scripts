"""
Module for retrieving farm portions data from TerraCLIM API.

The API provides access to farm portions data through extent-based queries,
allowing retrieval of portions that fall within a specified bounding box.
Individual portion queries are not supported.
"""

import requests
from .auth import TerraCLIMAuth
from .utils import get_api_url, response_to_dataframe, handle_error_response

class FarmPortions:
    def __init__(self, auth_client=None):
        """
        Initialize the Farm Portions client.
        
        Args:
            auth_client (TerraCLIMAuth, optional): Authentication client. If not provided, creates new one.
        """
        self.auth = auth_client if auth_client else TerraCLIMAuth()
        if not self.auth.is_authenticated():
            if not self.auth.login():  # Try to login if not authenticated
                raise ValueError("Authentication required. Login failed.")

    def _build_url(self, farm_id=None, extent=None):
        """
        Build the URL for farm portions request including query parameters.
        Helper method for testing and debugging.
        
        Args:
            farm_id (int, optional): Filter portions by farm ID
            extent (list, optional): Bounding box coordinates [minx, miny, maxx, maxy]
            
        Returns:
            str: Complete URL with query parameters
        """
        endpoint = "farms/portions/"
        url = get_api_url(endpoint)
        
        params = {}
        if farm_id:
            params['farm_id'] = farm_id
            
        if extent:
            if not isinstance(extent, list) or len(extent) != 4:
                raise ValueError("Extent must be a list of 4 coordinates [minx, miny, maxx, maxy]")
            if not all(isinstance(x, (int, float)) for x in extent):
                raise ValueError("All extent coordinates must be numbers")
            params['extent'] = f"[{', '.join(map(str, extent))}]"
            
        if params:
            return f"{url}{'?' if '?' not in url else '&'}{'&'.join(f'{k}={v}' for k, v in params.items())}"
        return url

    def get_farm_portions(self, extent, farm_id=None):
        """
        Retrieve farm portions data as GeoJSON FeatureCollection.
        
        Args:
            extent (list): Required bounding box coordinates [minx, miny, maxx, maxy].
                         Example: [2086038.1755925221, -4033790.723493586, 
                                 2112561.824407478, -4007477.276506414]
            farm_id (int, optional): Filter portions by farm ID
            
        Returns:
            pandas.DataFrame: Farm portions data with the following columns:
                - id (int): Feature ID
                - type (str): Feature type (always "Feature")
                - geometry (dict): GeoJSON geometry object with MultiPolygon coordinates
                - farm_portion_id (int): Farm portion identifier
                - Additional properties from the GeoJSON properties object
        
        Examples:
            >>> # Get portions within a specific extent
            >>> extent = [2086038.1755925221, -4033790.723493586,
            ...          2112561.824407478, -4007477.276506414]
            >>> client.get_farm_portions(extent=extent)
            
            >>> # Get portions within an extent for a specific farm
            >>> client.get_farm_portions(
            ...     extent=[2086038.1755925221, -4033790.723493586,
            ...            2112561.824407478, -4007477.276506414],
            ...     farm_id=123
            ... )
            
        Note:
            The response is a GeoJSON FeatureCollection containing MultiPolygon geometries
            in EPSG:3857 projection (Web Mercator).
        """
        if not extent:
            raise ValueError("The extent parameter is required")
            
        try:
            url = self._build_url(farm_id=farm_id, extent=extent)
            response = requests.get(
                url,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting farm portions: {error_msg}")
                return None
                
            try:
                data = response.json()
                # Validate GeoJSON FeatureCollection format
                if not isinstance(data, dict) or data.get('type') != 'FeatureCollection':
                    print("Invalid response format: Expected GeoJSON FeatureCollection")
                    return None
                    
                return response_to_dataframe(data)
            except ValueError as e:
                print(f"Error parsing response: {str(e)}")
                return None
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve farm portions: {str(e)}")
            return None




def show_help():
    """
    Display help message for command-line usage.
    """
    print("""
TerraCLIM Farm Portions Script Usage:
----------------------------------
Basic Usage:
    python farm_portions.py [command] [options]

Commands:
    list                   List farm portions within an extent
    list-farm [farm_id]    List portions for a specific farm within an extent
    help                   Show this help message

Required options for 'list' and 'list-farm' commands:
    --extent x1,y1,x2,y2  Bounding box coordinates [minx,miny,maxx,maxy]

Optional options:
    --output FILE         Output CSV filename (default: farm_portions.csv)

Examples:
    python farm_portions.py list --extent 2086038.17,-4033790.72,2112561.82,-4007477.27
    python farm_portions.py list-farm 123 --extent 2086038.17,-4033790.72,2112561.82,-4007477.27
    python farm_portions.py get 456
    python farm_portions.py stats 456 --start-date 2025-01-01 --end-date 2025-12-31
    """)

def main():
    """
    Command-line interface for Farm Portions client.
    """
    import sys

    # Show help if no arguments or help requested
    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        return

    # Initialize authentication
    auth = TerraCLIMAuth()
    if not auth.login():
        print("Failed to authenticate")
        return

    # Create client
    client = FarmPortions(auth)
    
    command = sys.argv[1]

    try:
        if command == 'list':
            # Parse extent and output filename
            extent = None
            output_file = "farm_portions.csv"
            args = sys.argv[2:]
            for i in range(0, len(args), 2):
                if i + 1 >= len(args):
                    break
                if args[i] == '--extent':
                    extent = [float(x) for x in args[i + 1].split(',')]
                elif args[i] == '--output':
                    output_file = args[i + 1]
            
            if not extent:
                print("Error: --extent parameter is required")
                print("Example: --extent 2086038.17,-4033790.72,2112561.82,-4007477.27")
                return
                
            # Get portions within extent
            print("\nFetching farm portions within extent...")
            df = client.get_farm_portions(extent=extent)
            
            if df is not None:
                print(f"Total portions: {len(df)}")
                print("\nSample of portions data:")
                print(df.head())
                
                df.to_csv(output_file, index=False)
                print(f"\nData saved to {output_file}")

        elif command == 'list-farm':
            if len(sys.argv) < 3:
                print("Error: Farm ID required")
                show_help()
                return
                
            farm_id = int(sys.argv[2])
            
            # Parse extent and output filename
            extent = None
            output_file = f"farm_{farm_id}_portions.csv"
            args = sys.argv[3:]
            for i in range(0, len(args), 2):
                if i + 1 >= len(args):
                    break
                if args[i] == '--extent':
                    extent = [float(x) for x in args[i + 1].split(',')]
                elif args[i] == '--output':
                    output_file = args[i + 1]
            
            if not extent:
                print("Error: --extent parameter is required")
                print("Example: --extent 2086038.17,-4033790.72,2112561.82,-4007477.27")
                return
            
            print(f"\nFetching portions for farm {farm_id} within extent...")
            df = client.get_farm_portions(extent=extent, farm_id=farm_id)
            
            if df is not None:
                print(f"Total portions for farm {farm_id}: {len(df)}")
                print("\nSample of portions data:")
                print(df.head())
                
                df.to_csv(output_file, index=False)
                print(f"\nData saved to {output_file}")



        else:
            print(f"Unknown command: {command}")
            show_help()

    except ValueError as e:
        print(f"Error: Invalid number format - {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()