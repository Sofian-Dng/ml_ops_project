#!/usr/bin/env python
"""
Script pour exécuter tous les tests du pipeline MLOps
"""
import sys
import subprocess
from pathlib import Path

def run_tests():
    """Exécute tous les tests"""
    print("=" * 60)
    print("🧪 EXÉCUTION DES TESTS")
    print("=" * 60)
    
    # Vérifier que pytest est installé
    try:
        import pytest
    except ImportError:
        print("❌ pytest non installé")
        print("💡 Installez avec: pip install pytest pytest-cov")
        return 1
    
    # Options de pytest (utiliser python -m pytest pour Windows)
    args = [
        sys.executable,  # Utiliser le même Python que le script
        "-m", "pytest",
        "tests/",
        "-v",  # Verbose
        "--tb=short",  # Traceback court
        "--color=yes",  # Couleurs
    ]
    
    # Exécuter les tests
    print("\n📋 Exécution des tests...")
    print(f"Command: {' '.join(args)}\n")
    
    result = subprocess.run(args)
    
    if result.returncode == 0:
        print("\n✅ Tous les tests sont passés!")
    else:
        print("\n⚠️  Certains tests ont échoué")
        print("💡 Note: Certains tests peuvent être ignorés si les services ne sont pas démarrés")
    
    return result.returncode


def run_tests_by_category():
    """Exécute les tests par catégorie"""
    print("=" * 60)
    print("🧪 TESTS PAR CATÉGORIE")
    print("=" * 60)
    
    categories = [
        ("Tests Unitaires", "tests/test_unit.py"),
        ("Tests d'Intégration", "tests/test_integration.py"),
        ("Tests End-to-End", "tests/test_e2e.py"),
    ]
    
    results = []
    
    for name, test_file in categories:
        print(f"\n📊 {name}")
        print("-" * 60)
        
        if not Path(test_file).exists():
            print(f"⚠️  {test_file} non trouvé")
            continue
        
        args = [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"]
        result = subprocess.run(args)
        results.append((name, result.returncode))
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    
    for name, code in results:
        status = "✅" if code == 0 else "❌"
        print(f"{status} {name}")
    
    return 0 if all(code == 0 for _, code in results) else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--category":
        sys.exit(run_tests_by_category())
    else:
        sys.exit(run_tests())

