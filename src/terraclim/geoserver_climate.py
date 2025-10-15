"""
Module for retrieving GeoServer climate WMS data from TerraCLIM API.
"""

import requests
from .auth import TerraCLIMAuth
from .utils import get_api_url, response_to_dataframe, handle_error_response, format_date

class GeoServerClimate:
    def __init__(self, auth_client=None):
        """
        Initialize the GeoServer Climate WMS client.
        
        Args:
            auth_client (TerraCLIMAuth, optional): Authentication client. If not provided, creates new one.
        """
        self.auth = auth_client if auth_client else TerraCLIMAuth()
        if not self.auth.is_authenticated():
            raise ValueError("Authentication required. Please login first.")

    def get_climate_wms(self, date=None, variable=None, bbox=None, width=None, height=None):
        """
        Retrieve GeoServer climate WMS data.
        
        Args:
            date (str, optional): Date for climate data (YYYY-MM-DD)
            variable (str, optional): Climate variable to retrieve
            bbox (str, optional): Bounding box coordinates (minx,miny,maxx,maxy)
            width (int, optional): Width of the output image in pixels
            height (int, optional): Height of the output image in pixels
            
        Returns:
            pandas.DataFrame: Climate WMS data
        """
        endpoint = "geoserver/climate/wms"
        url = get_api_url(endpoint)
        
        params = {
            'service': 'WMS',
            'version': '1.3.0',
            'request': 'GetMap',
            'format': 'image/png'
        }
        
        if date:
            params['time'] = format_date(date)
        if variable:
            params['layers'] = variable
        if bbox:
            params['bbox'] = bbox
        if width:
            params['width'] = width
        if height:
            params['height'] = height
            
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting climate WMS data: {error_msg}")
                return None
            
            # For WMS GetMap requests, the response is typically an image
            # We'll return the response content and metadata as a DataFrame
            metadata = {
                'content_type': response.headers.get('content-type'),
                'content_length': response.headers.get('content-length'),
                'date': date,
                'variable': variable,
                'bbox': bbox,
                'width': width,
                'height': height
            }
            
            return response_to_dataframe([metadata])
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve climate WMS data: {str(e)}")
            return None

    def get_capabilities(self):
        """
        Retrieve WMS GetCapabilities document.
        
        Returns:
            pandas.DataFrame: WMS capabilities data
        """
        endpoint = "geoserver/climate/wms"
        url = get_api_url(endpoint)
        
        params = {
            'service': 'WMS',
            'version': '1.3.0',
            'request': 'GetCapabilities'
        }
        
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting WMS capabilities: {error_msg}")
                return None
                
            # GetCapabilities returns XML, but we'll convert relevant info to DataFrame
            capabilities = {
                'content_type': response.headers.get('content-type'),
                'content_length': response.headers.get('content-length'),
                'raw_content': response.text
            }
            
            return response_to_dataframe([capabilities])
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve WMS capabilities: {str(e)}")
            return None

def show_help():
    """
    Display help message for command-line usage.
    """
    print("""
TerraCLIM GeoServer Climate WMS Script Usage:
-----------------------------------------
Basic Usage:
    python geoserver_climate.py [command] [options]

Commands:
    capabilities          Get WMS capabilities information
    map                  Get climate map data
    help                 Show this help message

Options for 'map' command:
    --date DATE         Date for climate data (YYYY-MM-DD)
    --variable VAR      Climate variable to retrieve
    --bbox COORDS       Bounding box coordinates (minx,miny,maxx,maxy)
    --width PIXELS      Width of output image in pixels
    --height PIXELS     Height of output image in pixels
    --output FILE       Output CSV filename for metadata (default: climate_wms.csv)

Examples:
    python geoserver_climate.py capabilities
    python geoserver_climate.py map --variable temperature --date 2025-01-01
    python geoserver_climate.py map --bbox "-180,-90,180,90" --width 800 --height 600
    """)

def main():
    """
    Command-line interface for GeoServer Climate WMS client.
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
    client = GeoServerClimate(auth)
    
    command = sys.argv[1]

    try:
        if command == 'capabilities':
            print("\nFetching WMS capabilities...")
            df = client.get_capabilities()
            
            if df is not None:
                print("\nWMS Capabilities:")
                print(df)
                
                # Save capabilities to CSV
                output_file = "wms_capabilities.csv"
                df.to_csv(output_file, index=False)
                print(f"\nCapabilities saved to {output_file}")

        elif command == 'map':
            # Parse command options
            date = None
            variable = None
            bbox = None
            width = None
            height = None
            output_file = "climate_wms.csv"
            
            args = sys.argv[2:]
            for i in range(0, len(args), 2):
                if i + 1 >= len(args):
                    break
                    
                if args[i] == '--date':
                    date = args[i + 1]
                elif args[i] == '--variable':
                    variable = args[i + 1]
                elif args[i] == '--bbox':
                    bbox = args[i + 1]
                elif args[i] == '--width':
                    width = int(args[i + 1])
                elif args[i] == '--height':
                    height = int(args[i + 1])
                elif args[i] == '--output':
                    output_file = args[i + 1]
            
            # Build description of what we're fetching
            print("\nFetching climate WMS data with options:")
            if date:
                print(f"Date: {date}")
            if variable:
                print(f"Variable: {variable}")
            if bbox:
                print(f"Bounding box: {bbox}")
            if width:
                print(f"Width: {width} pixels")
            if height:
                print(f"Height: {height} pixels")
            
            df = client.get_climate_wms(
                date=date,
                variable=variable,
                bbox=bbox,
                width=width,
                height=height
            )
            
            if df is not None:
                print("\nClimate WMS Data:")
                print(df)
                
                df.to_csv(output_file, index=False)
                print(f"\nMetadata saved to {output_file}")

        else:
            print(f"Unknown command: {command}")
            show_help()

    except ValueError as e:
        print(f"Error: Invalid number format - {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()