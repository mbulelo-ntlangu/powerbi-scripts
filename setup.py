from setuptools import setup, find_packages

setup(
    name="terraclim-powerbi",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'pandas',
        'requests',
        'python-dotenv'
    ],
    author="TerraCLIM",
    description="TerraCLIM PowerBI Integration Package",
    python_requires=">=3.7",
)