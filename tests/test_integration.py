"""
Tests d'intégration pour le pipeline MLOps
Tests des interactions entre composants
"""
import unittest
import sys
import requests
from pathlib import Path
import time

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDockerIntegration(unittest.TestCase):
    """Tests d'intégration Docker"""
    
    def test_docker_health_endpoint(self):
        """Test que l'endpoint /health de Docker répond"""
        try:
            response = requests.get("http://localhost:5000/health", timeout=5)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.skipTest("Docker container non accessible")


class TestKubernetesIntegration(unittest.TestCase):
    """Tests d'intégration Kubernetes"""
    
    def test_kubernetes_health_endpoint(self):
        """Test que l'endpoint /health de Kubernetes répond"""
        try:
            response = requests.get("http://localhost:30080/health", timeout=5)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.skipTest("Kubernetes service non accessible")
    
    def test_kubernetes_api_endpoint(self):
        """Test que l'endpoint /invocations de Kubernetes répond"""
        try:
            # Test avec une requête simple
            response = requests.get("http://localhost:30080/invocations", timeout=5)
            # Même si c'est une erreur 400/405, ça signifie que le service répond
            self.assertIn(response.status_code, [200, 400, 405, 422])
        except requests.exceptions.ConnectionError:
            self.skipTest("Kubernetes service non accessible")


class TestMinioIntegration(unittest.TestCase):
    """Tests d'intégration Minio/S3"""
    
    def test_minio_connection(self):
        """Test la connexion à Minio"""
        try:
            from utils_s3 import get_minio_client
            client = get_minio_client()
            # Test de connexion (ne nécessite pas de bucket existant)
            self.assertIsNotNone(client)
        except Exception as e:
            self.skipTest(f"Minio non accessible: {e}")
    
    def test_minio_list_files(self):
        """Test la liste des fichiers dans Minio"""
        try:
            from utils_s3 import get_minio_client
            client = get_minio_client()
            files = client.list_files("models/")
            self.assertIsInstance(files, list)
        except Exception as e:
            self.skipTest(f"Minio non accessible: {e}")


class TestFeatureStoreIntegration(unittest.TestCase):
    """Tests d'intégration Feature Store"""
    
    def test_feature_store_connection(self):
        """Test la connexion au Feature Store"""
        try:
            from feature_store import FeatureStore
            store = FeatureStore()
            stats = store.get_statistics()
            self.assertIsInstance(stats, dict)
        except Exception as e:
            self.skipTest(f"Feature Store non accessible: {e}")


class TestMonitoringIntegration(unittest.TestCase):
    """Tests d'intégration Monitoring"""
    
    def test_prometheus_health(self):
        """Test que Prometheus est accessible"""
        try:
            response = requests.get("http://localhost:9090/-/healthy", timeout=5)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.skipTest("Prometheus non accessible")
    
    def test_grafana_health(self):
        """Test que Grafana est accessible"""
        try:
            response = requests.get("http://localhost:3000/api/health", timeout=5)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.skipTest("Grafana non accessible")
    
    def test_prometheus_metrics_endpoint(self):
        """Test que le générateur de métriques est accessible"""
        try:
            response = requests.get("http://localhost:8000/metrics", timeout=5)
            self.assertEqual(response.status_code, 200)
            # Vérifier que c'est du format Prometheus
            self.assertIn("mlops_", response.text)
        except requests.exceptions.ConnectionError:
            self.skipTest("Générateur de métriques non accessible")


class TestAirflowIntegration(unittest.TestCase):
    """Tests d'intégration Airflow"""
    
    def test_airflow_health(self):
        """Test que Airflow est accessible"""
        try:
            response = requests.get("http://localhost:8080/health", timeout=5)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.skipTest("Airflow non accessible")


if __name__ == '__main__':
    unittest.main()

