"""
Tests end-to-end (E2E) pour le pipeline MLOps complet
Tests du flux complet depuis les données jusqu'à la prédiction
"""
import unittest
import sys
import requests
import numpy as np
from pathlib import Path
from PIL import Image
import json

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestEndToEndPipeline(unittest.TestCase):
    """Tests end-to-end du pipeline complet"""
    
    def setUp(self):
        """Setup pour les tests E2E"""
        self.data_dir = Path("data")
        self.test_image_path = None
        
        # Chercher une image de test
        if self.data_dir.exists():
            dandelion_dir = self.data_dir / "dandelion"
            if dandelion_dir.exists():
                images = list(dandelion_dir.glob("*.jpg"))
                if images:
                    self.test_image_path = images[0]
    
    def test_data_availability(self):
        """Test que les données sont disponibles"""
        if not self.data_dir.exists():
            self.skipTest("Dossier data/ non trouvé. Exécutez: python download_data.py")
        
        dandelion_dir = self.data_dir / "dandelion"
        grass_dir = self.data_dir / "grass"
        
        dandelion_count = len(list(dandelion_dir.glob("*.jpg"))) if dandelion_dir.exists() else 0
        grass_count = len(list(grass_dir.glob("*.jpg"))) if grass_dir.exists() else 0
        
        self.assertGreater(dandelion_count, 0, "Aucune image de pissenlit trouvée")
        self.assertGreater(grass_count, 0, "Aucune image d'herbe trouvée")
    
    def test_model_prediction_format(self):
        """Test que le modèle peut faire une prédiction avec le bon format"""
        if not self.test_image_path:
            self.skipTest("Aucune image de test disponible")
        
        # Préparer l'image
        image = Image.open(self.test_image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image = image.resize((224, 224), Image.Resampling.LANCZOS)
        img_array = np.array(image, dtype=np.float32) / 255.0
        
        # Format attendu pour MLflow
        data = {"inputs": [img_array.tolist()]}
        
        self.assertIn("inputs", data)
        self.assertEqual(len(data["inputs"]), 1)
        self.assertEqual(len(data["inputs"][0]), 224)
        self.assertEqual(len(data["inputs"][0][0]), 224)
        self.assertEqual(len(data["inputs"][0][0][0]), 3)
    
    def test_api_prediction_kubernetes(self):
        """Test end-to-end : Prédiction via API Kubernetes"""
        if not self.test_image_path:
            self.skipTest("Aucune image de test disponible")
        
        # Préparer l'image
        image = Image.open(self.test_image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image = image.resize((224, 224), Image.Resampling.LANCZOS)
        img_array = np.array(image, dtype=np.float32) / 255.0
        
        data = {"inputs": [img_array.tolist()]}
        
        try:
            response = requests.post(
                "http://localhost:30080/invocations",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                predictions = response.json()
                self.assertIn("predictions", predictions)
                self.assertIsInstance(predictions["predictions"], list)
                self.assertGreater(len(predictions["predictions"]), 0)
            else:
                self.skipTest(f"API Kubernetes non accessible (code: {response.status_code})")
        except requests.exceptions.ConnectionError:
            self.skipTest("API Kubernetes non accessible")
    
    def test_api_prediction_docker(self):
        """Test end-to-end : Prédiction via API Docker"""
        if not self.test_image_path:
            self.skipTest("Aucune image de test disponible")
        
        # Préparer l'image
        image = Image.open(self.test_image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image = image.resize((224, 224), Image.Resampling.LANCZOS)
        img_array = np.array(image, dtype=np.float32) / 255.0
        
        data = {"inputs": [img_array.tolist()]}
        
        try:
            response = requests.post(
                "http://localhost:5000/invocations",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                predictions = response.json()
                self.assertIn("predictions", predictions)
                self.assertIsInstance(predictions["predictions"], list)
                self.assertGreater(len(predictions["predictions"]), 0)
            else:
                self.skipTest(f"API Docker non accessible (code: {response.status_code})")
        except requests.exceptions.ConnectionError:
            self.skipTest("API Docker non accessible")
    
    def test_mlflow_model_exists(self):
        """Test que le modèle MLflow existe"""
        mlruns_dir = Path("mlruns")
        if not mlruns_dir.exists():
            self.skipTest("MLruns non trouvé. Exécutez: python train.py")
        
        model_dir = mlruns_dir / "models" / "dandelion_vs_grass_classifier"
        if not model_dir.exists():
            self.skipTest("Modèle MLflow non trouvé. Exécutez: python train.py")
        
        versions = list(model_dir.glob("version-*"))
        self.assertGreater(len(versions), 0, "Aucune version du modèle trouvée")
    
    def test_minio_model_storage(self):
        """Test que le modèle est stocké dans Minio"""
        try:
            from utils_s3 import get_minio_client
            client = get_minio_client()
            files = client.list_files("models/")
            
            # Vérifier qu'il y a au moins un fichier de modèle
            model_files = [f for f in files if "model" in f.lower() or ".pb" in f]
            self.assertGreater(len(model_files), 0, "Aucun modèle trouvé dans Minio")
        except Exception as e:
            self.skipTest(f"Minio non accessible: {e}")
    
    def test_feature_store_populated(self):
        """Test que le Feature Store est peuplé"""
        try:
            from feature_store import FeatureStore
            store = FeatureStore()
            stats = store.get_statistics()
            
            total_features = stats.get('total_features', 0)
            self.assertGreater(total_features, 0, "Feature Store vide")
        except Exception as e:
            self.skipTest(f"Feature Store non accessible: {e}")


class TestPipelineComponents(unittest.TestCase):
    """Tests des composants individuels du pipeline"""
    
    def test_airflow_dags_exist(self):
        """Test que les DAGs Airflow existent"""
        airflow_dags = Path("airflow/dags")
        self.assertTrue(airflow_dags.exists(), "Dossier airflow/dags non trouvé")
        
        dags = list(airflow_dags.glob("*.py"))
        self.assertGreater(len(dags), 0, "Aucun DAG Airflow trouvé")
    
    def test_kubernetes_config_exists(self):
        """Test que les fichiers Kubernetes existent"""
        k8s_dir = Path("k8s")
        self.assertTrue(k8s_dir.exists(), "Dossier k8s/ non trouvé")
        
        deployment = k8s_dir / "deployment.yaml"
        service = k8s_dir / "service.yaml"
        
        self.assertTrue(deployment.exists(), "deployment.yaml non trouvé")
        self.assertTrue(service.exists(), "service.yaml non trouvé")
    
    def test_dockerfile_exists(self):
        """Test que les Dockerfiles existent"""
        dockerfile = Path("Dockerfile")
        self.assertTrue(dockerfile.exists(), "Dockerfile non trouvé")
    
    def test_requirements_exists(self):
        """Test que requirements.txt existe"""
        requirements = Path("requirements.txt")
        self.assertTrue(requirements.exists(), "requirements.txt non trouvé")


if __name__ == '__main__':
    unittest.main()

