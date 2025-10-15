# TerraCLIM PowerBI Scripts

A collection of Python scripts for retrieving and processing data from the TerraCLIM API for use with PowerBI.

## Table of Contents

- [Power BI Integration Guide](#power-bi-integration-guide)
  - [Prerequisites](#prerequisites)
  - [Installation Steps](#installation-steps)
  - [Setting up Power BI](#setting-up-power-bi)
  - [Creating Your First Report](#creating-your-first-report)
  - [Troubleshooting](#troubleshooting)
- [Installation](#installation)
- [Configuration](#configuration)
- [Available Scripts](#available-scripts)
  - [Authentication](#authentication)
  - [Fields Management](#fields-management)
  - [Farms Management](#farms-management)
  - [Analysis and Statistics](#analysis-and-statistics)
  - [Climate Data](#climate-data)
  - [GeoServer Integration](#geoserver-integration)
- [Usage Examples](#usage-examples)

## Power BI Integration Guide

### Prerequisites

Before you begin, ensure you have:
- Power BI Desktop installed (latest version)
- Python 3.7 or higher
- TerraCLIM account credentials
- Internet connection
- Administrator access to your machine

### Installation Steps

1. **Set up Python Environment**:
   ```powershell
   # Create a dedicated directory
   mkdir C:\TerraCLIM
   cd C:\TerraCLIM

   # Create virtual environment
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Clone and install package
   git clone https://github.com/mbulelo-ntlangu/powerbi-scripts.git
   cd powerbi-scripts
   pip install -e .
   ```

2. **Verify Installation**:
   ```python
   python -c "import terraclim; print(terraclim.__version__)"
   ```

### Setting up Power BI

1. **Configure Python in Power BI**:
   - Open Power BI Desktop
   - Go to File → Options and settings → Options
   - Navigate to Global → Python scripting
   - Set Python home directory to your virtual environment:
     ```
     C:\TerraCLIM\.venv
     ```

2. **Create Parameters**:
   - File → Options and settings → Parameters
   - Add two parameters:
     1. TERRACLIM_USERNAME (Type: Text)
     2. TERRACLIM_PASSWORD (Type: Text)
   - Set appropriate values
   - Mark as Required

### Creating Your First Report

1. **Get TerraCLIM Data**:
   - Click "Get Data"
   - Choose "Python script"
   - Copy this basic script:
     ```python
     import terraclim as tc
     
     # Get fields data
     df = tc.get_fields(
         username=TERRACLIM_USERNAME,  # Power BI parameter
         password=TERRACLIM_PASSWORD   # Power BI parameter
     )
     ```

2. **Create Basic Visualizations**:
   - Table of Fields:
     - Drag field names to create columns
     - Add sorting and filtering
   
   - Map View (if coordinates available):
     - Use Map visual
     - Set latitude and longitude
   
   - Summary Cards:
     - Total fields
     - Total area
     - Active fields

3. **Add Refresh Schedule**:
   - Set up credentials in Power BI service
   - Configure automatic refresh
   - Test refresh functionality

### Advanced Features

1. **Combining Multiple Data Sources**:
   ```python
   import terraclim as tc
   
   # Get both farms and fields
   farms_df = tc.get_farms(TERRACLIM_USERNAME, TERRACLIM_PASSWORD)
   fields_df = tc.get_fields(TERRACLIM_USERNAME, TERRACLIM_PASSWORD)
   
   # Merge data
   df = fields_df.merge(
       farms_df[['farm_id', 'farm_name']], 
       on='farm_id', 
       how='left'
   )
   ```

2. **Adding GeoServer Layers**:
   ```python
   import terraclim as tc
   
   # Get available layers
   workspaces = tc.get_workspaces(TERRACLIM_USERNAME, TERRACLIM_PASSWORD)
   
   # Get specific workspace info
   workspace_info = tc.get_geoserver_info(
       TERRACLIM_USERNAME,
       TERRACLIM_PASSWORD,
       workspace='TerraClim_Terrain'
   )
   ```

### Troubleshooting

1. **Common Issues**:
   - "Module not found" error:
     - Verify Python path in Power BI settings
     - Check package installation
   
   - Authentication errors:
     - Verify credentials
     - Check network connectivity
   
   - Empty data:
     - Check parameter values
     - Verify API access

2. **Getting Help**:
   - Check logs at: `%TEMP%\terraclim_powerbi.log`
   - Contact support: support@terraclim.co.za
   - Review error messages in Power BI

3. **Version Verification**:
   ```python
   import terraclim as tc
   version_info = tc.get_version_info()
   print(version_info)  # Shows versions of all components
   ```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd PowerBI-scripts
```

2. Create a virtual environment and activate it:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root with your TerraCLIM credentials:
```env
TERRACLIM_USERNAME=your_username
TERRACLIM_PASSWORD=your_password
```

## Available Scripts

### Authentication (`auth.py`)

Manage TerraCLIM API authentication.

```bash
# Login to TerraCLIM API
python auth.py login

# Check authentication status
python auth.py status

# Refresh access token
python auth.py refresh
```

### Fields Management (`fields.py`)

Manage and retrieve field data.

```bash
# List all fields
python fields.py list

# Get specific field details
python fields.py get <field_id>

# Get field statistics
python fields.py stats <field_id> --start-date 2025-01-01 --end-date 2025-12-31
```

### Farms Management

#### Farms (`farms.py`)

Manage farm data.

```bash
# List all farms
python farms.py list

# Get specific farm details
python farms.py get <farm_id>

# Get farm statistics
python farms.py stats <farm_id> --start-date 2025-01-01 --end-date 2025-12-31

# Extract farm IDs to CSV
python farms.py extract-ids
```

#### Farm Portions (`farm_portions.py`)

Manage farm portions.

```bash
# List all farm portions
python farm_portions.py list

# List portions for specific farm
python farm_portions.py list-farm <farm_id>

# Get portion details
python farm_portions.py get <portion_id>

# Get portion statistics
python farm_portions.py stats <portion_id> --start-date 2025-01-01 --end-date 2025-12-31
```

### Analysis and Statistics (`analysis_stats.py`)

Retrieve analysis statistics.

```bash
# Get statistics for last 60 days
python analysis_stats.py get

# Get statistics for specific date range
python analysis_stats.py get --start-date 2025-01-01 --end-date 2025-12-31

# Get statistics for specific fields
python analysis_stats.py get --fields 1,2,3
```

### Climate Data

#### Climate Filter (`climate_filter.py`)

Access climate data and variables.

```bash
# List available climate variables
python climate_filter.py variables

# Get climate data
python climate_filter.py data --variable temperature
python climate_filter.py data --field 123 --start-date 2025-01-01 --end-date 2025-12-31
```

#### GeoServer Climate (`geoserver_climate.py`)

Access climate WMS data.

```bash
# Get WMS capabilities
python geoserver_climate.py capabilities

# Get climate map data
python geoserver_climate.py map --variable temperature --date 2025-01-01
python geoserver_climate.py map --bbox "-180,-90,180,90" --width 800 --height 600
```

### GeoServer Integration

#### GeoServer Feature Info (`geoserver_feature.py`)

Retrieve feature information.

```bash
# Get feature information
python geoserver_feature.py info --x 100 --y 100 --bbox "-180,-90,180,90" --width 800 --height 600 --layers climate_layer
```

#### GeoServer Info (`geoserver_info.py`)

Access GeoServer metadata.

```bash
# Get GeoServer information
python geoserver_info.py info --workspace <workspace_name>

# Get layer information
python geoserver_info.py layer <layer_name> --workspace <workspace_name>
```

## Usage Examples

### Example 1: Basic Field Analysis

```bash
# Login to the API
python auth.py login

# Get list of fields
python fields.py list

# Get statistics for specific fields
python analysis_stats.py get --fields 1,2,3 --start-date 2025-01-01 --end-date 2025-12-31
```

### Example 2: Climate Data Analysis

```bash
# Get available climate variables
python climate_filter.py variables

# Get climate data for a specific field
python climate_filter.py data --field 123 --variable temperature --start-date 2025-01-01 --end-date 2025-12-31
```

### Example 3: Farm Management

```bash
# List all farms
python farms.py list

# Get farm portions for a specific farm
python farm_portions.py list-farm 123

# Get statistics for a farm portion
python farm_portions.py stats 456 --start-date 2025-01-01 --end-date 2025-12-31
```

## Data Output

All scripts output data in CSV format suitable for PowerBI consumption. By default, files are saved with descriptive names (e.g., `fields.csv`, `farm_123_stats.csv`), but you can specify custom output filenames using the `--output` parameter with most commands.

## Error Handling

The scripts include comprehensive error handling:
- Authentication errors will prompt you to login
- API errors are displayed with descriptive messages
- Invalid parameters are caught and help messages are displayed
- Network errors are handled gracefully

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a new Pull Request