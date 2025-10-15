# Setting up TerraCLIM Scripts in Power BI

## Prerequisites

### Required Software
1. Python 3.7 or higher installed on your system
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   
2. pip (Python package installer)
   - Usually comes with Python
   - Verify with: `pip --version`
   
3. Power BI Desktop
   - Download from [Microsoft Store](https://www.microsoft.com/store/productId/9NTXR16HNW1T)
   - Or [Direct Download](https://powerbi.microsoft.com/desktop/)

### System Requirements
- Windows 10 or higher
- 4GB RAM minimum (8GB recommended)
- Internet connection for API access

## Installation Steps

1. Open PowerShell or Command Prompt as Administrator
   ```powershell
   # Verify Python installation
   python --version  # Should show 3.7 or higher
   pip --version    # Verify pip is installed
   ```

2. Set up a virtual environment (recommended):
   ```powershell
   # Navigate to a suitable directory
   cd C:\Users\YourUsername\Documents
   
   # Create a new directory for TerraCLIM
   mkdir TerraCLIM
   cd TerraCLIM
   
   # Create virtual environment
   python -m venv .venv
   
   # Activate virtual environment
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the TerraCLIM package:
   ```powershell
   # Clone the repository (if you haven't already)
   git clone https://github.com/mbulelo-ntlangu/powerbi-scripts.git
   cd powerbi-scripts
   
   # Install in editable mode
   pip install -e .
   ```

4. Verify the installation:
   ```python
   python -c "import terraclim; print(terraclim.__version__)"
   ```

5. Configure Power BI Python Environment:
   - Open Power BI Desktop
   - Go to File → Options and settings → Options
   - Under Global → Python scripting:
     - Verify Python is detected
     - If not, set Python home directory to your virtual environment
     - Example: `C:\Users\YourUsername\Documents\TerraCLIM\.venv`

## Using in Power BI

### Basic Usage

1. In Power BI Desktop:
   - Click "Get Data"
   - Select "Python script"
   - Enter the following script:

   ```python
   import terraclim as tc

   # Get data (replace with your credentials)
   username = "your_username"
   password = "your_password"

   # Get fields data
   df = tc.get_fields(username, password)
   ```

### Advanced Usage Examples

1. Getting Farm Information with Error Handling:
   ```python
   import terraclim as tc
   import pandas as pd

   try:
       df = tc.get_farms(username, password)
       if df.empty:
           df = pd.DataFrame({'Error': ['No farms found or authentication failed']})
   except Exception as e:
       df = pd.DataFrame({'Error': [str(e)]})
   ```

2. Combining Multiple Data Sources:
   ```python
   import terraclim as tc

   # Get both farms and fields
   farms_df = tc.get_farms(username, password)
   fields_df = tc.get_fields(username, password)

   # Merge the data
   df = fields_df.merge(farms_df, on='farm_id', how='left')
   ```

3. Working with GeoServer Data:
   ```python
   import terraclim as tc

   # Get available workspaces
   workspaces_df = tc.get_workspaces(username, password)

   # Get info for a specific workspace
   workspace_name = workspaces_df.iloc[0]['name']  # First workspace
   info_df = tc.get_geoserver_info(username, password, workspace_name)
   ```

2. Using Power BI Parameters for Credentials:
   a. Create parameters:
      - File → Options and settings → Parameters
      - Add parameters for username and password
   
   b. Use in script:
   ```python
   import terraclim as tc

   # Parameters will be available as variables
   df = tc.get_fields(username, password)
   ```

## Available Functions

- `get_fields()`: Retrieve field information
- `get_farms()`: Retrieve farm information
- `get_workspaces()`: List GeoServer workspaces
- `get_field_notes()`: Get field notes
- `get_geoserver_info()`: Get GeoServer workspace information

## Troubleshooting

### Common Issues and Solutions

1. Import Errors
   ```
   Error: No module named 'terraclim'
   ```
   Solutions:
   - Verify installation: `pip list | findstr terraclim`
   - Check Python path: `python -c "import sys; print(sys.path)"`
   - Reinstall package: `pip install -e .`

2. Authentication Errors
   ```
   Error: Authentication required. Please login first.
   ```
   Solutions:
   - Verify credentials
   - Check internet connection
   - Ensure API endpoint is accessible

3. Power BI Python Environment Issues
   - Open Python Script window in Power BI
   - Run test import:
     ```python
     import sys
     print(sys.executable)  # Should point to your virtual environment
     ```
   - If wrong Python version:
     1. Update Power BI Python settings
     2. Restart Power BI Desktop
     3. Clear Python cache

4. Data Loading Issues
   - Check dataframe shape: `print(df.shape)`
   - Verify data types: `print(df.dtypes)`
   - Look for null values: `print(df.isnull().sum())`

### Getting Help

1. Contact Support:
   - Email: support@terraclim.co.za
   - Documentation: [TerraCLIM Docs](https://docs.terraclim.co.za)

2. Check Logs:
   - Python logs: `%TEMP%\Python-Errors.txt`
   - Power BI logs: Event Viewer → Applications

3. Version Information:
   ```python
   import terraclim
   import pandas as pd
   import sys

   print(f"TerraCLIM Version: {terraclim.__version__}")
   print(f"Python Version: {sys.version}")
   print(f"Pandas Version: {pd.__version__}")
   ```