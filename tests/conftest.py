"""
PyTest configuration and fixtures
"""
import pytest
import os

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables before each test"""
    # Store original environment variables
    old_env = {}
    for key in ['TERRACLIM_USERNAME', 'TERRACLIM_PASSWORD', 'TERRACLIM_BASE_URL']:
        old_env[key] = os.environ.get(key)
    
    # Set test environment variables
    os.environ['TERRACLIM_USERNAME'] = 'test_user'
    os.environ['TERRACLIM_PASSWORD'] = 'test_pass'
    os.environ['TERRACLIM_BASE_URL'] = 'https://dashboard.staging.terraclim.co.za/api/v0/'
    
    yield
    
    # Restore original environment variables
    for key, value in old_env.items():
        if value is None:
            del os.environ[key]
        else:
            os.environ[key] = value