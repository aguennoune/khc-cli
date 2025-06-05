#!/usr/bin/env python3
# Test script to import and run khc_cli

import sys
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")

try:
    import khc_cli
    print(f"Successfully imported khc_cli from: {khc_cli.__file__}")
    print(f"khc_cli version: {khc_cli.__version__ if hasattr(khc_cli, '__version__') else 'unknown'}")
    
    from khc_cli.main import run
    print(f"Successfully imported run function")
    
    # Optional: Try to run the CLI
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        print("Running khc-cli...")
        run()
except ImportError as e:
    print(f"Error importing khc_cli: {e}")
    sys.exit(1)
