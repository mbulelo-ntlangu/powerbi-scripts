"""
TerraCLIM PowerBI Integration Package

This package provides integration between TerraCLIM and PowerBI,
offering access to farm data, field information, and various statistics.

Classes:
    TerraCLIMAuth: Authentication handler for TerraCLIM API
    Farms: Access and manage farm data
    Fields: Access and manage field data
    OverviewStats: Retrieve farm and field overview statistics
    AnalysisStats: Access detailed analysis statistics
"""

from .auth import TerraCLIMAuth
from .farms import Farms
from .fields import Fields
from .overview_stats import OverviewStats
from .analysis_stats import AnalysisStats
from .powerbi_wrapper import (
    get_workspaces,
    get_fields,
    get_farms,
    get_field_notes,
    get_geoserver_info
)

__version__ = "0.1.1"
__all__ = [
    # Main classes
    'TerraCLIMAuth',
    'Farms',
    'Fields',
    'OverviewStats',
    'AnalysisStats',
    # PowerBI wrapper functions
    'get_workspaces',
    'get_fields',
    'get_farms',
    'get_field_notes',
    'get_geoserver_info'
]