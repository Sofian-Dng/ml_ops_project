"""
Script pour générer des métriques Prometheus de démonstration
"""
import time
import random
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Créer les métriques
api_requests_total = Counter('mlops_api_requests_total', 'Total API requests', ['method', 'endpoint'])
api_request_duration = Histogram('mlops_api_request_duration_seconds', 'API request duration')
model_predictions = Counter('mlops_model_predictions_total', 'Total model predictions', ['predicted_class'])
model_confidence = Gauge('mlops_model_confidence', 'Model prediction confidence', ['predicted_class'])
active_pods = Gauge('mlops_kubernetes_pods', 'Number of active Kubernetes pods')

print("=" * 70)
print("📊 GÉNÉRATION DE MÉTRIQUES PROMETHEUS")
print("=" * 70)
print("\n📡 Métriques disponibles sur http://localhost:8000/metrics")
print("   (Prometheus les collectera automatiquement)")
print("\n⚠️  Pour arrêter: Ctrl+C")
print("=" * 70)

# Démarrer le serveur HTTP pour exposer les métriques
start_http_server(8000)

try:
    while True:
        # Simuler des requêtes API
        api_requests_total.labels(method='POST', endpoint='/invocations').inc(random.randint(1, 5))
        api_request_duration.observe(random.uniform(0.1, 2.0))
        
        # Simuler des prédictions
        if random.random() > 0.5:
            model_predictions.labels(predicted_class='dandelion').inc()
            model_confidence.labels(predicted_class='dandelion').set(random.uniform(0.7, 0.99))
        else:
            model_predictions.labels(predicted_class='grass').inc()
            model_confidence.labels(predicted_class='grass').set(random.uniform(0.7, 0.99))
        
        # Simuler des pods Kubernetes (entre 1 et 3)
        active_pods.set(random.randint(1, 3))
        
        time.sleep(5)  # Mettre à jour toutes les 5 secondes
        
except KeyboardInterrupt:
    print("\n\n✅ Serveur arrêté")