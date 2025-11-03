# 🚀 Pipeline MLOps - Classification Binaire d'Images

**Classification pissenlit vs herbe avec pipeline MLOps **

## 👥 Équipe

**Membres du projet :**
- Sofian Duong
- Joseph Dejean
- Maxandre Michel
- Paul Montier
- Mathieu Chabirand

## 📊 Stack Technique

- **Modèle**: TensorFlow/Keras (CNN)
- **Tracking & API**: MLflow
- **Storage S3**: Minio (S3 compatible)
- **Feature Store**: Parquet + MySQL
- **Orchestration**: Apache Airflow
- **Conteneurisation**: Docker
- **Déploiement**: Kubernetes (2 pods)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Interface**: Gradio


## 📁 Structure du Projet

```
mlops-project-git/
├── NOTEBOOK_PRESENTATION_FINAL.ipynb  # Notebook présentation
├── download_data.py                   # Téléchargement images
├── train.py                           # Entraînement modèle
├── gradio_app.py                      # Interface web
├── utils_s3.py                        # Client Minio/S3
├── feature_store.py                   # Feature Store
├── requirements.txt                   # Dépendances Python
├── Dockerfile                         # Image Docker (local)
├── Dockerfile.s3                      # Image Docker (depuis S3)
├── entrypoint.sh                      # Script démarrage Docker
├── entrypoint_s3.sh                   # Script démarrage Docker S3
├── docker-compose.yml                 # Services (Minio, Airflow, Monitoring)
├── init_db.sql                        # Initialisation MySQL
├── k8s/
│   ├── deployment.yaml                # Deployment Kubernetes
│   └── service.yaml                   # Service Kubernetes
├── airflow/
│   └── dags/
│       ├── mlops_retraining_pipeline.py
│       └── continuous_training_dag.py
├── monitoring/
│   ├── prometheus.yml
│   └── grafana/
│       ├── datasources/prometheus.yml
│       └── dashboards/
│           ├── dashboard.json
│           └── mlops_dashboard.json
└── .github/
    └── workflows/
        └── mlops-pipeline.yml         # CI/CD GitHub Actions
```



### 1. Dépendances Python

```bash
pip install -r requirements.txt
```

### 2. Services Docker Compose

```bash
# Démarrer tous les services
docker-compose up -d

# Services disponibles:
# - Minio: http://localhost:9001 (minioadmin/minioadmin)
# - Airflow: http://localhost:8080 (admin/admin)
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin)
# - MySQL: localhost:3306
```

## 📋 Utilisation

### Phase 1 : Données et Modèle

```bash
# 1. Télécharger les données (400 images)
python download_data.py

# 2. Entraîner le modèle (5-10 minutes)
python train.py
```

**Résultat** :
- Modèle enregistré dans `mlruns/` (MLflow)
- Modèle uploadé vers Minio/S3
- Features extraites et stockées

### Phase 2 : Docker

```bash
# Build l'image Docker
docker build -t dandelion-grass-classifier:latest .

# Tester localement
docker run -p 5000:5000 dandelion-grass-classifier:latest
```

**API accessible** : http://localhost:5000/invocations

### Phase 3 : Kubernetes

```bash
# Déployer
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Vérifier
kubectl get pods
kubectl get services
```

**API accessible** : http://localhost:30080/invocations

### Phase 4 : Airflow

1. Ouvrir http://localhost:8080 (admin/admin)
2. Activer le DAG `mlops_retraining_pipeline`
3. Déclencher manuellement ou attendre le schedule

### Phase 5 : Interface Gradio

```bash
python gradio_app.py
```

**Interface accessible** : http://localhost:7860

## 📊 Notebook de Présentation

Ouvrir `NOTEBOOK_PRESENTATION_FINAL.ipynb` pour :
- Vue d'ensemble du projet
- Tests exécutables pour chaque phase
- Démonstration complète

## 🔗 URLs d'Accès

| Service | URL | Credentials |
|---------|-----|------------|
| Gradio | http://localhost:7860 | - |
| API K8s | http://localhost:30080/invocations | - |
| API Docker | http://localhost:5000/invocations | - |
| MLflow UI | `mlflow ui` → http://localhost:5000 | - |
| Airflow | http://localhost:8080 | admin/admin |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin/admin |
| Minio Console | http://localhost:9001 | minioadmin/minioadmin |

## 🛠️ Commandes Essentielles

```bash
# Démarrer tous les services
docker-compose up -d

# Entraîner le modèle (avec upload S3 et Feature Store)
python train.py

# Lancer l'interface Gradio
python gradio_app.py

# Vérifier les pods Kubernetes
kubectl get pods -l app=dandelion-grass-classifier

# Voir les logs d'un pod
kubectl logs <pod-name>
```

<<<<<<< HEAD
## 🎓 Choix Techniques et Justifications

### Pourquoi ces outils ?

#### **TensorFlow/Keras**
- **Choix** : Framework de deep learning standard et bien documenté
- **Avantage** : Intégration native avec MLflow, support complet de SavedModel

#### **MLflow**
- **Choix** : Solution open-source pour le tracking et versioning de modèles
- **Avantage** : Tracking automatique des métriques, versioning, API REST intégrée (`mlflow models serve`)

#### **Minio (S3 compatible)**
- **Choix** : Stockage objet compatible S3 pour stocker les modèles
- **Avantage** : Facile à déployer localement, compatible avec boto3, migration vers AWS S3 transparente

#### **Apache Airflow**
- **Choix** : Orchestrateur de workflows open-source standard
- **Avantage** : DAGs visuels, scheduling flexible, gestion d'erreurs robuste

#### **Docker**
- **Choix** : Conteneurisation standard pour isoler les dépendances
- **Avantage** : Reproducibilité, portabilité, isolation des dépendances

#### **Kubernetes**
- **Choix** : Orchestration de conteneurs pour haute disponibilité
- **Alternative** : Docker Swarm (mais K8s est le standard industriel)
- **Avantage** : Scalabilité automatique, 2 pods pour haute disponibilité, load balancing

#### **Prometheus + Grafana**
- **Choix** : Stack de monitoring standard dans l'industrie
- **Avantage** : Métriques temps réel, dashboards personnalisables, alerting

#### **Gradio**
- **Choix** : Interface web interactive rapide à développer
- **Avantage** : Interface prête en quelques lignes, upload d'images facile

#### **Feature Store (Parquet + MySQL)**
- **Choix** : Stockage de features avec métadonnées
- **Avantage** : Parquet pour performances, MySQL pour métadonnées et requêtes

## 🧪 Tests

Le projet inclut une suite de tests complète :

### Structure des tests

- **Tests unitaires** (`tests/test_unit.py`) : 10 tests pour les fonctions individuelles
- **Tests d'intégration** (`tests/test_integration.py`) : 8 tests pour les interactions entre composants
- **Tests end-to-end** (`tests/test_e2e.py`) : 11 tests pour le flux complet du pipeline

### Exécution des tests

```bash
# Tous les tests
python run_tests.py

# Ou avec pytest directement
python -m pytest tests/ -v

# Par catégorie
python -m pytest tests/test_unit.py -v
python -m pytest tests/test_integration.py -v
python -m pytest tests/test_e2e.py -v
```

> 📖 Voir `tests/README.md` pour plus de détails

## 📊 Résultats Obtenus

### Métriques du Modèle

- **Accuracy d'entraînement** : ~85-90% (selon les runs)
- **Accuracy de validation** : ~80-85%
- **Format** : Classification binaire (Pissenlit vs Herbe)
- **Taille du modèle** : ~10-15 MB (SavedModel)

### Performance du Pipeline

- **Temps d'entraînement** : 5-10 minutes (400 images, 10 epochs)
- **Temps de déploiement Docker** : ~2 minutes (build + run)
- **Temps de déploiement Kubernetes** : ~1 minute (2 pods)
- **Latence API** : < 500ms par prédiction


## 🐳 Docker Hub

### Image Docker disponible

L'image Docker du modèle est disponible sur Docker Hub :

**URL de l'image :** https://hub.docker.com/r/khal160/dandelion-grass-classifier

✅ Image publiée et accessible publiquement sur Docker Hub.

### Pull et utilisation

```bash
# Pull l'image depuis Docker Hub
docker pull khal160/dandelion-grass-classifier:latest

# Lancer le container
docker run -p 5000:5000 khal160/dandelion-grass-classifier:latest
```

### Push vers Docker Hub

```bash
# 1. Se connecter à Docker Hub
docker login

# 2. Tag l'image
docker tag dandelion-grass-classifier:latest khal160/dandelion-grass-classifier:latest

# 3. Push l'image
docker push khal160/dandelion-grass-classifier:latest
```

## 📝 Notes Techniques

- **Modèle** : CNN simple (3 couches convolutionnelles) pour classification binaire
- **Format API** : JSON avec `{"inputs": [[image_normalisée_224x224x3]]}`
- **MLflow** : Tracking automatique des métriques et versioning du modèle
- **Docker** : Utilise `mlflow models serve` (pas besoin de FastAPI)
- **Kubernetes** : 2 pods pour haute disponibilité, NodePort 30080
- **CI/CD** : Workflow GitHub Actions déclenché sur push vers `main`
- **Tests** : Suite complète de tests unitaires, intégration et E2E

## 🔄 CI/CD Pipeline

Le pipeline CI/CD GitHub Actions :

1. **Checkout** du code
2. **Installation** des dépendances Python
3. **Téléchargement** des données d'entraînement
4. **Entraînement** du modèle avec MLflow
5. **Build** de l'image Docker
6. **Déploiement** (optionnel, selon configuration)

> 📖 Voir `.github/workflows/mlops-pipeline.yml` pour les détails


