# 📸 Screenshots du Projet

Ce dossier contient les captures d'écran du pipeline MLOps en production.

## Screenshots à ajouter

Pour compléter le README principal, ajoutez les screenshots suivants :

### 1. Interface Gradio
- **Fichier** : `gradio_interface.png`
- **Description** : Interface web Gradio avec une prédiction réussie (pissenlit ou herbe)
- **Comment capturer** : Ouvrir http://localhost:7860, uploader une image, prendre screenshot

### 2. Dashboard Grafana
- **Fichier** : `grafana_dashboard.png`
- **Description** : Dashboard Grafana avec les 4 panels de monitoring (API requests, Predictions, Confidence, Pods)
- **Comment capturer** : Ouvrir http://localhost:3000, aller sur le dashboard MLOps, prendre screenshot

### 3. Airflow DAGs
- **Fichier** : `airflow_dags.png`
- **Description** : Interface Airflow avec les DAGs `mlops_retraining_pipeline` et `continuous_training_dag` visibles
- **Comment capturer** : Ouvrir http://localhost:8080, aller sur la page DAGs, prendre screenshot

### 4. MLflow UI
- **Fichier** : `mlflow_ui.png`
- **Description** : Interface MLflow avec les runs d'entraînement, métriques et modèles versionnés
- **Comment capturer** : Exécuter `mlflow ui`, ouvrir http://localhost:5000, prendre screenshot

### 5. Minio Console
- **Fichier** : `minio_console.png`
- **Description** : Console Minio avec le bucket `mlops-models` et les fichiers du modèle stockés
- **Comment capturer** : Ouvrir http://localhost:9001, naviguer vers le bucket, prendre screenshot

### 6. Kubernetes Pods
- **Fichier** : `kubernetes_pods.png`
- **Description** : Interface Kubernetes (ou `kubectl get pods`) montrant les 2 pods en cours d'exécution
- **Comment capturer** : Exécuter `kubectl get pods -l app=dandelion-grass-classifier`, prendre screenshot du terminal

### 7. Prometheus Metrics
- **Fichier** : `prometheus_metrics.png`
- **Description** : Interface Prometheus avec les métriques MLOps (mlops_api_requests_total, etc.)
- **Comment capturer** : Ouvrir http://localhost:9090, rechercher une métrique, prendre screenshot

## Structure attendue

```
screenshots/
├── README.md
├── gradio_interface.png
├── grafana_dashboard.png
├── airflow_dags.png
├── mlflow_ui.png
├── minio_console.png
├── kubernetes_pods.png
└── prometheus_metrics.png
```

## Notes

- Utilisez des formats PNG ou JPG
- Recommandation : Résolution minimale 1280x720 pour la lisibilité
- Les screenshots doivent être clairs et montrer les éléments importants

