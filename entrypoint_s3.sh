#!/bin/sh
# Script pour télécharger le modèle depuis Minio/S3 et le servir avec MLflow

echo "============================================================"
echo "Démarrage du serveur MLflow avec modèle depuis S3/Minio"
echo "============================================================"

# Configuration Minio depuis variables d'environnement
MINIO_ENDPOINT=${MINIO_ENDPOINT:-http://minio:9000}
MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}
MINIO_BUCKET=${MINIO_BUCKET:-mlops-models}

# Créer le dossier pour le modèle local
mkdir -p /app/mlruns_model

# Trouver le dernier modèle dans S3
echo "Recherche du dernier modèle dans S3..."

# Utiliser boto3 pour télécharger depuis S3
python3 << EOF
import boto3
from botocore.client import Config
import os
from pathlib import Path

# Configuration
endpoint_url = "${MINIO_ENDPOINT}"
access_key = "${MINIO_ACCESS_KEY}"
secret_key = "${MINIO_SECRET_KEY}"
bucket_name = "${MINIO_BUCKET}"

try:
    client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )
    
    # Lister les modèles disponibles
    prefix = "models/dandelion_vs_grass_classifier/"
    response = client.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter='/')
    
    # Trouver le dernier run
    runs = []
    if 'CommonPrefixes' in response:
        for prefix_obj in response['CommonPrefixes']:
            run_path = prefix_obj['Prefix']
            runs.append(run_path)
    
    if not runs:
        print("Erreur: Aucun modèle trouvé dans S3")
        exit(1)
    
    # Trier et prendre le dernier
    latest_run = sorted(runs)[-1]
    print(f"Modèle trouvé dans S3: {latest_run}")
    
    # Télécharger le modèle
    local_path = Path("/app/mlruns_model")
    
    # Télécharger tous les fichiers du run
    paginator = client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=latest_run)
    
    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                s3_key = obj['Key']
                local_file = local_path / s3_key.replace(latest_run, "")
                local_file.parent.mkdir(parents=True, exist_ok=True)
                
                print(f"Téléchargement: {s3_key} -> {local_file}")
                client.download_file(bucket_name, s3_key, str(local_file))
    
    # Trouver le dossier du modèle (qui contient MLmodel)
    model_dir = local_path
    mlmodel_file = None
    
    for root, dirs, files in os.walk(local_path):
        if 'MLmodel' in files:
            model_dir = root
            mlmodel_file = os.path.join(root, 'MLmodel')
            break
    
    if mlmodel_file:
        print(f"✅ Modèle téléchargé: {model_dir}")
        print(f"MODEL_PATH={model_dir}" >> os.environ.get('GITHUB_ENV', '/tmp/model_path'))
        with open('/tmp/model_path', 'w') as f:
            f.write(model_dir)
    else:
        print("Erreur: MLmodel non trouvé dans le modèle téléchargé")
        exit(1)

except Exception as e:
    print(f"Erreur lors du téléchargement depuis S3: {str(e)}")
    exit(1)
EOF

MODEL_PATH=$(cat /tmp/model_path 2>/dev/null || echo "")

if [ -z "$MODEL_PATH" ] || [ ! -f "$MODEL_PATH/MLmodel" ]; then
    echo "Erreur: Impossible de télécharger le modèle depuis S3"
    exit 1
fi

echo "Modèle téléchargé depuis S3: $MODEL_PATH"
echo "Serving model from: $MODEL_PATH"

# Servir le modèle avec MLflow
exec mlflow models serve -m "$MODEL_PATH" --host 0.0.0.0 --port 5000 --no-conda --install-mlflow

