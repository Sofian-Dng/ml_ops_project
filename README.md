# 🚀 Pipeline MLOps - Classification Binaire d'Images

**Classification pissenlit vs herbe avec pipeline MLOps **

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

##  Notes 

- **Modèle** : CNN simple (3 couches convolutionnelles) pour classification binaire
- **Format API** : JSON avec `{"inputs": [[image_normalisée_224x224x3]]}`
- **MLflow** : Tracking automatique des métriques et versioning du modèle
- **Docker** : Utilise `mlflow models serve` (pas besoin de FastAPI)
- **Kubernetes** : 2 pods pour haute disponibilité, NodePort 30080
- **CI/CD** : Workflow GitHub Actions déclenché sur push vers `main`


