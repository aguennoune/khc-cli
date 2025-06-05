#!/usr/bin/env python3
"""
Script de test pour confirmer que la restructuration a fonctionné.
Exécuter avec: python test_cli.py
"""

print("Début du test d'importation...")

try:
    import khc_cli
    print(f"khc_cli importé avec succès depuis: {khc_cli.__file__}")
    print(f"Version: {khc_cli.__version__}")
    
    # Test de l'import de la fonction run
    from khc_cli.main import run
    print("Fonction run importée avec succès.")
    
    print("Test réussi!")
except ImportError as e:
    print(f"Erreur d'importation: {e}")
    print("Test échoué!")
