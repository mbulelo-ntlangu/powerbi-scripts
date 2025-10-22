git merge main# Setting up TerraCLIM Scripts in Power BI

## Quick Start Guide

### Required Software
1. Python 3.11 (standard installation, NOT Windows Store version)
   - Download from [python.org](https://www.python.org/downloads/release/python-3118/)
   - Install to `C:\PowerBI_Python`
   - Do NOT check "Add Python to PATH"
   
2. Power BI Desktop
   - Download from [Microsoft Store](https://www.microsoft.com/store/productId/9NTXR16HNW1T)
   - Or [Direct Download](https://powerbi.microsoft.com/desktop/)

### System Requirements
- Windows 10 or higher
- 4GB RAM minimum (8GB recommended)
- Internet connection for API access
- Administrative access (for Python installation)

## Installation Steps

1. Install Python 3.11:
   - Download Python 3.11 from [python.org](https://www.python.org/downloads/release/python-3118/)
   - Run installer as Administrator
   - Choose "Customize installation"
   - Set installation directory to: `C:\PowerBI_Python`
   - Do NOT add Python to PATH

2. Install Required Packages:
   ```powershell
   # Open PowerShell as Administrator and run:
   cd C:\PowerBI_Python
   .\python.exe -m pip install --upgrade pip
   .\python.exe -m pip install pandas matplotlib requests python-dotenv
   
   # Install TerraCLIM package (adjust path as needed)
   .\python.exe -m pip install -e "C:\path\to\terraclim\powerbi-scripts"
   ```

3. Configure PowerBI:
   - Open PowerBI Desktop
   - Go to File → Options and settings → Options
   - Under Global, select "Python scripting"
   - Set "Python home directory" to: `C:\PowerBI_Python`
   - Click OK and restart PowerBI Desktop

4. Create PowerBI Parameters:
   - In PowerBI Desktop, go to Transform data → Manage Parameters
   - Create these parameters:
     - `TERRACLIM_USERNAME` (Type: Text)
     - `TERRACLIM_PASSWORD` (Type: Text)
     - `TERRACLIM_BASE_URL` (Type: Text, optional)

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

1. Test the Setup:
   - In Power BI Desktop, click "Get Data" → "Python script"
   - Copy and paste this minimal test:
   ```python
   import pandas as pd
   
   # Create a simple test DataFrame
   df = pd.DataFrame({
       'test': ['Simple Test'],
       'result': ['Success']
   })
   ```

2. Import TerraCLIM Data:
   - Click "Get Data" → "Python script"
   - Copy the contents of `powerbi_farm_fields.py`
   - Click OK

The script will automatically use your PowerBI parameters for authentication.

### Advanced Usage Examples

1. Getting Farm Information with Error Handling:
   ```python
   from terraclim import TerraCLIMAuth, Farms
   import pandas as pd

   try:
       # Initialize authentication
       auth = TerraCLIMAuth()
       login_result = auth.login(
           username=TERRACLIM_USERNAME,  # Power BI parameter
           password=TERRACLIM_PASSWORD   # Power BI parameter
       )

       if not login_result:
           df = pd.DataFrame({'Error': ['Authentication failed']})
       else:
           # Get farms data
           farms_client = Farms(auth)
           df = farms_client.get_farms()
           if df.empty:
               df = pd.DataFrame({'Error': ['No farms found']})
   except Exception as e:
       df = pd.DataFrame({'Error': [str(e)]})
   ```

2. Combining Multiple Data Sources:
   ```python
   from terraclim import TerraCLIMAuth, Farms, Fields
   
   # Initialize authentication
   auth = TerraCLIMAuth()
   auth.login(
       username=TERRACLIM_USERNAME,  # Power BI parameter
       password=TERRACLIM_PASSWORD   # Power BI parameter
   )
   
   # Get both farms and fields data
   farms_client = Farms(auth)
   fields_client = Fields(auth)
   
   farms_df = farms_client.get_farms()
   fields_df = fields_client.get_fields()
   
   # Merge the data
   df = fields_df.merge(farms_df, on='farm_id', how='left')
   ```

3. Working with GeoServer Data:
   ```python
   from terraclim import TerraCLIMAuth
   from terraclim import get_workspaces, get_geoserver_info

   # Initialize authentication
   auth = TerraCLIMAuth()
   auth.login(
       username=TERRACLIM_USERNAME,  # Power BI parameter
       password=TERRACLIM_PASSWORD   # Power BI parameter
   )

   # Get available workspaces
   workspaces_df = get_workspaces(auth)

   # Get info for a specific workspace
   workspace_name = workspaces_df.iloc[0]['name']  # First workspace
   info_df = get_geoserver_info(auth, workspace_name)
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

1. "Access Denied" Error:
   ```
   ADO.NET: A problem occurred while processing your Python script.
   Here are the technical details: Access is denied
   ```
   Solutions:
   - Make sure you're using standard Python (not Windows Store version)
   - Verify Python is installed in `C:\PowerBI_Python`
   - Run all pip commands as administrator
   - Try the test scripts in this order:
     1. `test_minimal.py` (basic pandas test)
     2. `test_matplotlib.py` (matplotlib test)
     3. `test_powerbi_import.py` (TerraCLIM test)

2. Import Errors
   ```
   Error: No module named 'terraclim'
   ```
   Solutions:
   - Open PowerShell as admin and run:
     ```powershell
     cd C:\PowerBI_Python
     .\python.exe -m pip list  # Check installed packages
     .\python.exe -m pip install -e "path/to/terraclim/powerbi-scripts"  # Reinstall
     ```

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