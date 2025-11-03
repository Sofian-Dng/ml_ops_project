# Tests du Pipeline MLOps

## Structure des Tests

### 1. Tests Unitaires (`test_unit.py`)
Tests des fonctions individuelles sans dépendances externes :
- Preprocessing des images
- Feature Store
- Utilitaires S3/Minio
- Format des données API
- Format des prédictions

### 2. Tests d'Intégration (`test_integration.py`)
Tests des interactions entre composants :
- Docker (endpoint /health)
- Kubernetes (endpoint /health et /invocations)
- Minio/S3 (connexion et liste fichiers)
- Feature Store (connexion et statistiques)
- Monitoring (Prometheus, Grafana)
- Airflow (health check)

### 3. Tests End-to-End (`test_e2e.py`)
Tests du flux complet du pipeline :
- Disponibilité des données
- Format des prédictions
- Prédiction via API Kubernetes
- Prédiction via API Docker
- Existence du modèle MLflow
- Stockage du modèle dans Minio
- Feature Store peuplé
- Vérification des fichiers de configuration

## Exécution des Tests

### Tous les tests
```bash
python -m pytest tests/ -v
```

### Tests unitaires uniquement
```bash
python -m pytest tests/test_unit.py -v
```

### Tests d'intégration uniquement
```bash
python -m pytest tests/test_integration.py -v
```

### Tests E2E uniquement
```bash
python -m pytest tests/test_e2e.py -v
```

### Avec unittest (si pytest n'est pas installé)
```bash
python -m unittest discover tests -v
```

## Prérequis

Avant d'exécuter les tests, assurez-vous que :
1. Les services Docker Compose sont démarrés :
   ```bash
   docker-compose up -d
   ```

2. Les données sont téléchargées :
   ```bash
   python download_data.py
   ```

3. Le modèle est entraîné :
   ```bash
   python train.py
   ```

4. Docker et Kubernetes sont déployés :
   ```bash
   docker build -t dandelion-grass-classifier:latest .
   kubectl apply -f k8s/
   ```

## Installation des dépendances de test

```bash
pip install pytest pytest-cov
```

## Notes

- Les tests utilisent `skipTest` si les services ne sont pas disponibles
- Les tests d'intégration nécessitent que les services soient en cours d'exécution
- Les tests E2E nécessitent que le pipeline complet soit configuré

