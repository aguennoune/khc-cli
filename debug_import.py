#!/usr/bin/env python3
import os
import sys
import importlib

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current directory: {os.getcwd()}")
print("\nPython path:")
for path in sys.path:
    print(f" - {path}")

# Tente d'importer le module
try:
    print("\nTentative d'import khc_cli:")
    khc_cli = importlib.import_module("khc_cli")
    print(f"Module trouvé: {khc_cli.__file__}")
    
    # Liste les sous-modules
    print("\nSous-modules:")
    for finder, name, ispkg in pkgutil.iter_modules(khc_cli.__path__):
        print(f" - {name} {'(package)' if ispkg else ''}")
    
except ImportError as e:
    print(f"Erreur d'import: {e}")
    
    # Vérifier les fichiers dans les chemins de recherche
    print("\nRecherche de khc_cli dans les chemins de recherche:")
    for path in sys.path:
        khc_cli_path = os.path.join(path, "khc_cli")
        if os.path.exists(khc_cli_path):
            print(f"Trouvé à {khc_cli_path}")
            if os.path.isdir(khc_cli_path):
                print(f"C'est un répertoire:")
                for item in os.listdir(khc_cli_path):
                    print(f"  - {item}")
