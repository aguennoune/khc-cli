#!/usr/bin/env python
"""
Script de débogage simple pour localiser l'erreur d'importation khc_cli
"""
import sys
import os
import importlib.util

# 1. Informations système
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")
print(f"Current directory: {os.getcwd()}")

# 2. Essayer d'importer khc_cli directement
try:
    import khc_cli
    print(f"Successfully imported khc_cli: {khc_cli.__file__}")
except ImportError as e:
    print(f"Failed to import khc_cli: {e}")
    
    # 3. Recherche manuelle du module
    print("\nFinding khc_cli module manually:")
    for path in sys.path:
        module_path = os.path.join(path, "khc_cli")
        if os.path.exists(module_path):
            print(f"Found at: {module_path}")
            init_file = os.path.join(module_path, "__init__.py")
            if os.path.exists(init_file):
                print(f"__init__.py exists")
                with open(init_file, "r") as f:
                    print(f"Content: {f.read()[:100]}...")
            else:
                print("__init__.py missing")
    
    # 4. Alternative: essayer de charger avec importlib
    path = os.path.join(os.getcwd(), "khc_cli")
    init_file = os.path.join(path, "__init__.py")
    if os.path.exists(init_file):
        print(f"\nTrying to load from: {init_file}")
        try:
            spec = importlib.util.spec_from_file_location("khc_cli", init_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print("Successfully loaded with importlib")
        except Exception as e:
            print(f"Failed to load with importlib: {e}")
