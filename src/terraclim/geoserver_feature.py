"""
Module for retrieving GeoServer feature information from TerraCLIM API.
"""

import requests
from .auth import TerraCLIMAuth
from .utils import get_api_url, response_to_dataframe, handle_error_response, format_date

class GeoServerFeature:
    def __init__(self, auth_client=None):
        """
        Initialize the GeoServer Feature Info client.
        
        Args:
            auth_client (TerraCLIMAuth, optional): Authentication client. If not provided, creates new one.
        """
        self.auth = auth_client if auth_client else TerraCLIMAuth()
        if not self.auth.is_authenticated():
            raise ValueError("Authentication required. Please login first.")

    def get_feature_info(self, x, y, bbox, width, height, layers, query_layers=None, date=None):
        """
        Retrieve feature information from GeoServer.
        
        Args:
            x (int): X coordinate in pixels
            y (int): Y coordinate in pixels
            bbox (str): Bounding box coordinates (minx,miny,maxx,maxy)
            width (int): Width of the map in pixels
            height (int): Height of the map in pixels
            layers (str): Comma-separated list of layer names
            query_layers (str, optional): Comma-separated list of layers to query (defaults to layers)
            date (str, optional): Date for temporal data (YYYY-MM-DD)
            
        Returns:
            pandas.DataFrame: Feature information data
        """
        endpoint = "geoserver/featureinfo/"
        url = get_api_url(endpoint)
        
        params = {
            'x': x,
            'y': y,
            'bbox': bbox,
            'width': width,
            'height': height,
            'layers': layers,
            'query_layers': query_layers or layers
        }
        
        if date:
            params['time'] = format_date(date)
            
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting feature info: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe(data)
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve feature info: {str(e)}")
            return None

def show_help():
    """
    Display help message for command-line usage.
    """
    print("""
TerraCLIM GeoServer Feature Info Script Usage:
------------------------------------------
Basic Usage:
    python geoserver_feature.py [command] [options]

Commands:
    info                   Get feature information for a location
    help                   Show this help message

Required options for 'info' command:
    --x PIXELS            X coordinate in pixels
    --y PIXELS            Y coordinate in pixels
    --bbox COORDS         Bounding box coordinates (minx,miny,maxx,maxy)
    --width PIXELS        Width of the map in pixels
    --height PIXELS       Height of the map in pixels
    --layers NAMES        Comma-separated list of layer names

Optional options:
    --query-layers NAMES  Comma-separated list of layers to query (defaults to --layers value)
    --date DATE          Date for temporal data (YYYY-MM-DD)
    --output FILE        Output CSV filename (default: feature_info.csv)

Examples:
    python geoserver_feature.py info --x 100 --y 100 --bbox "-180,-90,180,90" --width 800 --height 600 --layers climate_layer
    python geoserver_feature.py info --x 200 --y 300 --bbox "10,20,30,40" --width 1024 --height 768 --layers "temp,rainfall" --date 2025-01-01
    """)

def main():
    """
    Command-line interface for GeoServer Feature Info client.
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
    client = GeoServerFeature(auth)
    
    command = sys.argv[1]

    try:
        if command == 'info':
            # Initialize required parameters
            x = None
            y = None
            bbox = None
            width = None
            height = None
            layers = None
            
            # Initialize optional parameters
            query_layers = None
            date = None
            output_file = "feature_info.csv"
            
            # Parse command options
            args = sys.argv[2:]
            for i in range(0, len(args), 2):
                if i + 1 >= len(args):
                    break
                    
                if args[i] == '--x':
                    x = int(args[i + 1])
                elif args[i] == '--y':
                    y = int(args[i + 1])
                elif args[i] == '--bbox':
                    bbox = args[i + 1]
                elif args[i] == '--width':
                    width = int(args[i + 1])
                elif args[i] == '--height':
                    height = int(args[i + 1])
                elif args[i] == '--layers':
                    layers = args[i + 1]
                elif args[i] == '--query-layers':
                    query_layers = args[i + 1]
                elif args[i] == '--date':
                    date = args[i + 1]
                elif args[i] == '--output':
                    output_file = args[i + 1]
            
            # Validate required parameters
            missing = []
            if x is None: missing.append('--x')
            if y is None: missing.append('--y')
            if bbox is None: missing.append('--bbox')
            if width is None: missing.append('--width')
            if height is None: missing.append('--height')
            if layers is None: missing.append('--layers')
            
            if missing:
                print(f"Error: Missing required parameters: {', '.join(missing)}")
                show_help()
                return
            
            # Build description of what we're fetching
            print("\nFetching feature information:")
            print(f"Location: ({x}, {y})")
            print(f"Bounding box: {bbox}")
            print(f"Map size: {width}x{height} pixels")
            print(f"Layers: {layers}")
            if query_layers:
                print(f"Query layers: {query_layers}")
            if date:
                print(f"Date: {date}")
            
            df = client.get_feature_info(
                x=x,
                y=y,
                bbox=bbox,
                width=width,
                height=height,
                layers=layers,
                query_layers=query_layers,
                date=date
            )
            
            if df is not None:
                print("\nFeature Information:")
                print(df)
                
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