import os
import subprocess
import sys
import argparse

def run_command(cmd, cwd=None):
    """Run a command and return its output"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            text=True,
            capture_output=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(cmd)}")
        print(f"Error output: {e.stderr}")
        return False

def install_terraclim(python_path=None):
    """Install terraclim package in the specified Python environment"""
    # Use provided Python path or current Python interpreter
    python_exe = python_path if python_path else sys.executable
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Using Python interpreter: {python_exe}")
    print("Building package...")
    
    # Install build dependencies
    if not run_command([python_exe, "-m", "pip", "install", "setuptools", "wheel"]):
        return False
    
    # Build the package
    if not run_command([python_exe, "setup.py", "sdist", "bdist_wheel"], cwd=script_dir):
        return False
    
    # Find the latest wheel file
    dist_dir = os.path.join(script_dir, "dist")
    wheel_files = [f for f in os.listdir(dist_dir) if f.endswith(".whl")]
    if not wheel_files:
        print("No wheel file found after building")
        return False
    
    latest_wheel = max(wheel_files)  # Gets the latest version
    wheel_path = os.path.join(dist_dir, latest_wheel)
    
    print(f"Installing wheel: {latest_wheel}")
    
    # Install the package
    if not run_command([python_exe, "-m", "pip", "install", "--force-reinstall", wheel_path]):
        return False
    
    # Verify installation
    try:
        verification_cmd = [
            python_exe,
            "-c",
            "from terraclim import powerbi_wrapper; print('Package installed successfully!')"
        ]
        subprocess.run(verification_cmd, check=True, text=True, capture_output=True)
        print("Terraclim package installation verified successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print("Failed to verify package installation")
        print(f"Error: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Install or update the terraclim package in a Python environment')
    parser.add_argument('--python', help='Path to the Python executable where terraclim should be installed')
    args = parser.parse_args()
    
    success = install_terraclim(args.python)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()