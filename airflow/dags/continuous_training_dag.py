"""
DAG Airflow pour Continuous Training (CT)
Déclenchement automatique basé sur différents triggers
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
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


def check_model_performance():
    """Vérifie les performances du modèle et déclenche retraining si nécessaire."""
    import mlflow
    import requests
    
    mlflow.set_tracking_uri("http://mlflow:5000")  # Si MLflow est déployé
    
    # Récupérer les dernières métriques
    try:
        # Simuler une vérification de performance
        # En production, on récupérerait les vraies métriques depuis MLflow
        api_url = "http://localhost:30080/health"
        response = requests.get(api_url, timeout=5)
        
        if response.status_code != 200:
            print("⚠️  Modèle en dégradation détectée")
            return True  # Déclencher retraining
        
        print("✅ Performance du modèle OK")
        return False
        
    except Exception as e:
        print(f"⚠️  Erreur vérification performance: {str(e)}")
        return True  # En cas d'erreur, déclencher retraining


def trigger_retraining(**context):
    """Déclenche le retraining si nécessaire."""
    should_retrain = check_model_performance()
    
    if should_retrain:
        print("🚀 Déclenchement du retraining...")
        # Importer et exécuter le pipeline de retraining
        from mlops_retraining_pipeline import (
            download_data_task,
            train_model_task,
            build_docker_task,
            deploy_k8s_task
        )
        
        download_data_task()
        train_model_task()
        build_docker_task()
        deploy_k8s_task()
        
        print("✅ Retraining terminé")
    else:
        print("⏭️  Retraining non nécessaire")


# DAG pour Continuous Training avec triggers
dag = DAG(
    'continuous_training',
    default_args=default_args,
    description='Continuous Training avec triggers automatiques',
    schedule_interval=timedelta(hours=6),  # Vérification toutes les 6h
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['mlops', 'continuous_training', 'automated'],
)

# Sensor pour détecter nouvelles données (exemple)
# new_data_sensor = FileSensor(
#     task_id='wait_for_new_data',
#     filepath='/opt/airflow/data/new_images',
#     fs_conn_id='fs_default',
#     poke_interval=300,  # Vérifie toutes les 5 minutes
#     timeout=3600,  # Timeout après 1h
#     dag=dag,
# )

# Sensor pour détecter nouveau modèle dans S3
# s3_model_sensor = S3KeySensor(
#     task_id='wait_for_new_model',
#     bucket_name='mlops-models',
#     bucket_key='models/dandelion_vs_grass_classifier/',
#     aws_conn_id='aws_default',
#     poke_interval=60,
#     timeout=600,
#     dag=dag,
# )

# Tâche de vérification de performance
check_performance = PythonOperator(
    task_id='check_model_performance',
    python_callable=check_model_performance,
    dag=dag,
)

# Tâche de retraining conditionnel
trigger_retraining_task = PythonOperator(
    task_id='trigger_retraining',
    python_callable=trigger_retraining,
    dag=dag,
)

# Définir les dépendances
check_performance >> trigger_retraining_task

