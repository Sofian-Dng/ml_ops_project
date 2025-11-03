#!/bin/sh
# Script pour trouver et servir le modèle MLflow

# Chercher le fichier MLmodel (limité à artifacts pour être rapide)
MLMODEL_FILE=$(find ./mlruns -path "*/artifacts/MLmodel" -type f | head -1)

if [ -n "$MLMODEL_FILE" ]; then
  # Le modèle est dans le dossier parent du fichier MLmodel
  MODEL_PATH=$(dirname "$MLMODEL_FILE")
  echo "Modele trouve via MLmodel: $MODEL_PATH"
else
  # Fallback: chercher directement le dossier artifacts
  MODEL_PATH=$(find ./mlruns -type d -path "*/artifacts" -not -path "*/artifacts/data/*" | head -1)
  if [ -z "$MODEL_PATH" ] || [ ! -f "$MODEL_PATH/MLmodel" ]; then
    echo "Erreur: Aucun modele MLflow valide trouve"
    exit 1
  fi
  echo "Modele trouve via artifacts: $MODEL_PATH"
fi

echo "Serving model from: $MODEL_PATH"
# Utiliser --install-mlflow pour installer les dépendances manquantes
exec mlflow models serve -m "$MODEL_PATH" --host 0.0.0.0 --port 5000 --no-conda --install-mlflow

