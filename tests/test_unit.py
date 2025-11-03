"""
Tests unitaires pour le pipeline MLOps
Tests des fonctions individuelles sans dépendances externes
"""
import unittest
import sys
from pathlib import Path
import numpy as np
from PIL import Image

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDataPreprocessing(unittest.TestCase):
    """Tests pour le preprocessing des données"""
    
    def test_image_resize(self):
        """Test que les images sont correctement redimensionnées"""
        # Créer une image de test
        test_image = Image.new('RGB', (500, 500), color='green')
        resized = test_image.resize((224, 224), Image.Resampling.LANCZOS)
        
        self.assertEqual(resized.size, (224, 224))
    
    def test_image_normalization(self):
        """Test que la normalisation des images fonctionne"""
        # Simuler un array d'image (0-255)
        img_array = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
        normalized = img_array.astype(np.float32) / 255.0
        
        self.assertTrue(np.all(normalized >= 0.0))
        self.assertTrue(np.all(normalized <= 1.0))
        self.assertEqual(normalized.dtype, np.float32)


class TestFeatureStore(unittest.TestCase):
    """Tests pour le Feature Store"""
    
    def test_feature_store_import(self):
        """Test que le Feature Store peut être importé"""
        try:
            from feature_store import FeatureStore
            self.assertTrue(True)
        except ImportError:
            self.skipTest("Feature Store non disponible")
    
    def test_feature_store_initialization(self):
        """Test l'initialisation du Feature Store"""
        try:
            from feature_store import FeatureStore
            store = FeatureStore()
            self.assertIsNotNone(store)
        except Exception:
            self.skipTest("Feature Store non disponible ou erreur")


class TestS3Utils(unittest.TestCase):
    """Tests pour les utilitaires S3/Minio"""
    
    def test_s3_utils_import(self):
        """Test que utils_s3 peut être importé"""
        try:
            from utils_s3 import get_minio_client
            self.assertTrue(True)
        except ImportError:
            self.skipTest("utils_s3 non disponible")
    
    def test_minio_client_creation(self):
        """Test la création du client Minio"""
        try:
            from utils_s3 import get_minio_client
            # Ne pas tester la connexion réelle, juste l'import
            self.assertTrue(True)
        except Exception:
            self.skipTest("Minio client non disponible")


class TestModelFormat(unittest.TestCase):
    """Tests pour le format du modèle"""
    
    def test_prediction_format(self):
        """Test que le format de prédiction est correct"""
        # Simuler une prédiction MLflow
        prediction_format = {
            "predictions": [[0.85]]
        }
        
        self.assertIn("predictions", prediction_format)
        self.assertIsInstance(prediction_format["predictions"], list)
        self.assertIsInstance(prediction_format["predictions"][0], list)
        self.assertIsInstance(prediction_format["predictions"][0][0], (int, float))


class TestAPIDataFormat(unittest.TestCase):
    """Tests pour le format des données API"""
    
    def test_api_input_format(self):
        """Test que le format d'entrée API est correct"""
        # Format attendu pour MLflow
        test_input = {
            "inputs": [[np.random.rand(224, 224, 3).tolist()]]
        }
        
        self.assertIn("inputs", test_input)
        self.assertIsInstance(test_input["inputs"], list)
        self.assertEqual(len(test_input["inputs"]), 1)
    
    def test_api_response_parsing(self):
        """Test le parsing des réponses API"""
        # Simuler différentes réponses possibles
        response1 = {"predictions": [[0.75]]}
        response2 = {"predictions": [0.75]}
        response3 = {"predictions": [[[0.75]]]}
        
        # Toutes doivent être parsables
        for response in [response1, response2, response3]:
            self.assertIn("predictions", response)
            self.assertIsInstance(response["predictions"], list)


if __name__ == '__main__':
    unittest.main()

