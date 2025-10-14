"""
Module for retrieving GeoServer information from TerraCLIM API.
"""

import requests
from auth import TerraCLIMAuth
from utils import get_api_url, response_to_dataframe, handle_error_response

class GeoServerInfo:
    def __init__(self, auth_client=None):
        """
        Initialize the GeoServer Info client.
        
        Args:
            auth_client (TerraCLIMAuth, optional): Authentication client. If not provided, creates new one.
        """
        self.auth = auth_client if auth_client else TerraCLIMAuth()
        if not self.auth.is_authenticated():
            raise ValueError("Authentication required. Please login first.")

    def get_info(self, workspace):
        """
        Retrieve GeoServer information.
        
        Args:
            workspace (str): GeoServer workspace name
        
        Returns:
            pandas.DataFrame: GeoServer information data
        """
        endpoint = "geoserver-info/get_info/"
        url = get_api_url(endpoint)
        
        try:
            response = requests.get(
                url,
                params={'workspace': workspace},
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting GeoServer info: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe([data])  # Wrap in list for DataFrame
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve GeoServer info: {str(e)}")
            return None

    def get_layer_info(self, layer_name, workspace):
        """
        Retrieve information about a specific GeoServer layer.
        
        Args:
            layer_name (str): Name of the layer to get information about
            workspace (str): GeoServer workspace name
            
        Returns:
            pandas.DataFrame: Layer information data
        """
        endpoint = f"geoserver-info/get_info/{layer_name}/"
        url = get_api_url(endpoint)
        
        try:
            response = requests.get(
                url,
                params={'workspace': workspace},
                headers=self.auth.get_headers()
            )
            
            success, error_msg = handle_error_response(response)
            if not success:
                print(f"Error getting layer info for {layer_name}: {error_msg}")
                return None
                
            data = response.json()
            return response_to_dataframe([data])  # Wrap in list for DataFrame
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve layer info for {layer_name}: {str(e)}")
            return None

def show_help():
    """
    Display help message for command-line usage.
    """
    print("""
TerraCLIM GeoServer Info Script Usage:
-----------------------------------
Basic Usage:
    python geoserver_info.py [command] [options]

Commands:
    info                   Get general GeoServer information
    layer [layer_name]     Get information about a specific layer
    help                   Show this help message

Required options for all commands:
    --workspace NAME      GeoServer workspace name

Optional options:
    --output FILE        Output CSV filename (default: geoserver_info.csv or layer_[name]_info.csv)

Examples:
    python geoserver_info.py info --workspace terraclim
    python geoserver_info.py layer climate_layer --workspace terraclim
    python geoserver_info.py info --workspace terraclim --output custom_info.csv
    """)

def main():
    """
    Command-line interface for GeoServer Info client.
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
    client = GeoServerInfo(auth)
    
    command = sys.argv[1]

    try:
        if command == 'info':
            # Parse command options
            workspace = None
            output_file = "geoserver_info.csv"
            
            args = sys.argv[2:]
            for i in range(0, len(args), 2):
                if i + 1 >= len(args):
                    break
                if args[i] == '--workspace':
                    workspace = args[i + 1]
                elif args[i] == '--output':
                    output_file = args[i + 1]
            
            if not workspace:
                print("Error: --workspace parameter is required")
                show_help()
                return
            
            print(f"\nFetching GeoServer information for workspace '{workspace}'...")
            df = client.get_info(workspace)
            
            if df is not None:
                print("\nGeoServer Information:")
                print(df)
                
                df.to_csv(output_file, index=False)
                print(f"\nInformation saved to {output_file}")
                
                # If we have layers, print them out for reference
                if not df.empty and 'layers' in df.columns:
                    layers = df.iloc[0]['layers']
                    if isinstance(layers, list):
                        print("\nAvailable layers:")
                        for layer in layers:
                            print(f"  - {layer}")

        elif command == 'layer':
            if len(sys.argv) < 3:
                print("Error: Layer name required")
                show_help()
                return
                
            layer_name = sys.argv[2]
            
            # Parse command options
            workspace = None
            output_file = f"layer_{layer_name}_info.csv"
            
            args = sys.argv[3:]
            for i in range(0, len(args), 2):
                if i + 1 >= len(args):
                    break
                if args[i] == '--workspace':
                    workspace = args[i + 1]
                elif args[i] == '--output':
                    output_file = args[i + 1]
            
            if not workspace:
                print("Error: --workspace parameter is required")
                show_help()
                return
            
            print(f"\nFetching information for layer '{layer_name}' in workspace '{workspace}'...")
            df = client.get_layer_info(layer_name, workspace)
            
            if df is not None:
                print(f"\nLayer Information for '{layer_name}':")
                print(df)
                
                df.to_csv(output_file, index=False)
                print(f"\nInformation saved to {output_file}")

        else:
            print(f"Unknown command: {command}")
            show_help()

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()