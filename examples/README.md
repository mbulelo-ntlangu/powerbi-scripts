# TerraCLIM Power BI Examples

This directory contains example files demonstrating how to use the TerraCLIM package in Power BI.

## Sample Files

1. `powerbi_farm_fields.py`
   - Basic script for retrieving and combining farm and field data
   - Shows proper error handling and parameter usage
   - Demonstrates data merging and cleanup

2. `test_terraclim_components.py`
   - Comprehensive test script for all TerraCLIM components
   - Tests authentication, farms, fields, and statistics
   - Provides detailed status information for each component
   - Useful for validating setup and troubleshooting

3. `powerbi_sample.py`
   - Simple example showing basic TerraCLIM integration
   - Shows proper error handling
   - Demonstrates data merging

## Setting up the Power BI Template

1. Open Power BI Desktop
2. Create two parameters:
   - TERRACLIM_USERNAME (Text)
   - TERRACLIM_PASSWORD (Text)

3. Get Python Data:
   - Click "Get Data"
   - Choose "Python script"
   - Choose one of our example scripts:
     - `powerbi_farm_fields.py` for basic farm/field data
     - `test_terraclim_components.py` to validate your setup
   - The scripts will automatically use your PowerBI parameters:
     ```python
     # Parameters are automatically injected by PowerBI
     username = TERRACLIM_USERNAME
     password = TERRACLIM_PASSWORD
     ```
   - Our example scripts include proper error handling and parameter validation

4. Create Visualizations:
   - Table of fields with farm information
   - Map of field locations
   - Summary statistics
   - Workspace availability indicator

## Refresh Settings

1. Schedule Refresh:
   - Set up credentials in Power BI service
   - Configure refresh schedule based on data needs

2. Error Handling:
   - The script includes built-in error handling
   - Errors will be displayed in a readable format
   - Check `terraclim_powerbi.log` for detailed error information

## Security Notes

1. Always use Power BI parameters for credentials
2. Never hard-code credentials in the script
3. Use encrypted connections when publishing
4. Set appropriate data refresh policies

## Need Help?

Check the main documentation or contact support:
- Email: support@terraclim.co.za
- Documentation: [TerraCLIM Docs](https://docs.terraclim.co.za)