"""
DAG Airflow pour le pipeline de retraining automatique
Objectif 9 du devoir : Retraining pipeline avec Apache Airflow
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os


default_args = {
    'owner': 'mlops_team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def download_data_task():
    """Télécharge les données depuis GitHub."""
    import subprocess
    
    print("Téléchargement des données...")
    # Note: Airflow exécute depuis /opt/airflow/dags mais les scripts sont à la racine
    # On doit ajuster le chemin
    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "download_data.py")
    script_path = os.path.abspath(script_path)
    
    result = subprocess.run(
        ["python", script_path],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise Exception(f"Erreur téléchargement données: {result.stderr}")
    
    print("✅ Données téléchargées avec succès")


def train_model_task():
    """Entraîne le modèle avec MLflow et upload vers S3."""
    import subprocess
    
    print("Entraînement du modèle...")
    
    # Variables d'environnement pour Minio
    env = os.environ.copy()
    env['MINIO_ENDPOINT'] = 'http://minio:9000'
    env['MINIO_ACCESS_KEY'] = 'minioadmin'
    env['MINIO_SECRET_KEY'] = 'minioadmin'
    env['MINIO_BUCKET'] = 'mlops-models'
    
    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "train.py")
    script_path = os.path.abspath(script_path)
    
    result = subprocess.run(
        ["python", script_path],
        env=env,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise Exception(f"Erreur entraînement: {result.stderr}")
    
    print("✅ Modèle entraîné avec succès")


def build_docker_task():
    """Build l'image Docker avec le nouveau modèle."""
    import subprocess
    
    print("Build de l'image Docker...")
    
    project_root = os.path.dirname(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(project_root, ".."))
    
    result = subprocess.run(
        ["docker", "build", "-t", "dandelion-grass-classifier:latest", "."],
        cwd=project_root,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise Exception(f"Erreur build Docker: {result.stderr}")
    
    print("✅ Image Docker buildée avec succès")


def deploy_k8s_task():
    """Déploie le modèle sur Kubernetes."""
    import subprocess
    
    print("Déploiement sur Kubernetes...")
    
    project_root = os.path.dirname(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(project_root, ".."))
    k8s_dir = os.path.join(project_root, "k8s")
    
    # Appliquer les configurations K8s
    for yaml_file in ["deployment.yaml", "service.yaml"]:
        yaml_path = os.path.join(k8s_dir, yaml_file)
        result = subprocess.run(
            ["kubectl", "apply", "-f", yaml_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Erreur déploiement K8s {yaml_file}: {result.stderr}")
    
    print("✅ Déploiement Kubernetes réussi")


# DAG principal de retraining
dag = DAG(
    'mlops_retraining_pipeline',
    default_args=default_args,
    description='Pipeline complet de retraining MLOps',
    schedule_interval=timedelta(days=7),  # Exécution hebdomadaire
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['mlops', 'retraining', 'classification'],
)

# Tâches
download_data = PythonOperator(
    task_id='download_data',
    python_callable=download_data_task,
    dag=dag,
)

train_model = PythonOperator(
    task_id='train_model',
    python_callable=train_model_task,
    dag=dag,
)

build_docker = PythonOperator(
    task_id='build_docker',
    python_callable=build_docker_task,
    dag=dag,
)

deploy_k8s = PythonOperator(
    task_id='deploy_kubernetes',
    python_callable=deploy_k8s_task,
    dag=dag,
)

# Définir les dépendances
download_data >> train_model >> build_docker >> deploy_k8s

