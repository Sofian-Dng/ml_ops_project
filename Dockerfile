# Dockerfile pour servir le modèle MLflow
# Utiliser Python 3.11 pour correspondre à la version d'entraînement
FROM python:3.11-slim

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le modèle MLflow depuis mlruns (sera fourni au build)
# Le modèle sera dans mlruns/0/<run-id>/artifacts/model
COPY mlruns/ ./mlruns/

# Exposer le port 5000
EXPOSE 5000

# Copier et rendre exécutable le script d'entrée
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Utiliser le script d'entrée
CMD ["/entrypoint.sh"]

