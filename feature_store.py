"""
Feature Store simple pour stocker les features extraites des images.
Utilise des fichiers Parquet pour le stockage.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime
import hashlib


class FeatureStore:
    """Feature Store simple utilisant Parquet pour le stockage."""
    
    def __init__(self, store_path: str = "feature_store"):
        """
        Initialise le Feature Store.
        
        Args:
            store_path: Chemin du dossier de stockage
        """
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.features_file = self.store_path / "features.parquet"
        self.metadata_file = self.store_path / "metadata.json"
        self._load_store()
    
    def _load_store(self):
        """Charge le store depuis le fichier Parquet."""
        if self.features_file.exists():
            try:
                self.df = pd.read_parquet(self.features_file)
                print(f"✅ Feature Store chargé: {len(self.df)} features")
            except Exception as e:
                print(f"⚠️  Erreur chargement store: {str(e)}")
                self.df = pd.DataFrame()
        else:
            self.df = pd.DataFrame()
    
    def _save_store(self):
        """Sauvegarde le store dans le fichier Parquet."""
        try:
            self.df.to_parquet(self.features_file, index=False)
            # Sauvegarder métadonnées
            metadata = {
                "last_updated": datetime.now().isoformat(),
                "total_features": len(self.df),
                "features_columns": list(self.df.columns) if not self.df.empty else []
            }
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"❌ Erreur sauvegarde store: {str(e)}")
    
    def add_features(
        self,
        image_path: str,
        label: str,
        features: Dict,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Ajoute des features au store.
        
        Args:
            image_path: Chemin de l'image
            label: Label (dandelion/grass)
            features: Dictionnaire de features
            metadata: Métadonnées additionnelles
            
        Returns:
            True si succès
        """
        try:
            # Créer un hash de l'image pour ID unique
            image_hash = hashlib.md5(image_path.encode()).hexdigest()
            
            # Préparer les données
            feature_data = {
                "image_hash": image_hash,
                "image_path": image_path,
                "label": label,
                "timestamp": datetime.now().isoformat(),
                **features
            }
            
            if metadata:
                feature_data["metadata"] = json.dumps(metadata)
            
            # Ajouter au DataFrame
            new_row = pd.DataFrame([feature_data])
            
            # Supprimer l'ancienne entrée si elle existe (même hash)
            if not self.df.empty:
                self.df = self.df[self.df["image_hash"] != image_hash]
            
            self.df = pd.concat([self.df, new_row], ignore_index=True)
            self._save_store()
            
            print(f"✅ Features ajoutées: {image_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur ajout features: {str(e)}")
            return False
    
    def get_features(self, image_path: Optional[str] = None, label: Optional[str] = None) -> pd.DataFrame:
        """
        Récupère des features du store.
        
        Args:
            image_path: Filtrer par chemin d'image
            label: Filtrer par label
            
        Returns:
            DataFrame avec les features
        """
        df = self.df.copy()
        
        if image_path:
            image_hash = hashlib.md5(image_path.encode()).hexdigest()
            df = df[df["image_hash"] == image_hash]
        
        if label:
            df = df[df["label"] == label]
        
        return df
    
    def get_statistics(self) -> Dict:
        """
        Retourne des statistiques sur le store.
        
        Returns:
            Dictionnaire de statistiques
        """
        if self.df.empty:
            return {
                "total_features": 0,
                "labels": {},
                "last_updated": None
            }
        
        stats = {
            "total_features": len(self.df),
            "labels": self.df["label"].value_counts().to_dict(),
            "last_updated": self.df["timestamp"].max() if "timestamp" in self.df.columns else None
        }
        
        return stats
    
    def clear(self):
        """Vide le store."""
        self.df = pd.DataFrame()
        self._save_store()
        print("✅ Feature Store vidé")


def extract_image_features(image_path: str) -> Dict:
    """
    Extrait des features simples d'une image.
    
    Args:
        image_path: Chemin de l'image
        
    Returns:
        Dictionnaire de features
    """
    from PIL import Image
    import numpy as np
    
    try:
        image = Image.open(image_path)
        
        # Features basiques
        features = {
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
            "aspect_ratio": image.width / image.height if image.height > 0 else 0,
        }
        
        # Features de couleur (moyennes RGB)
        img_array = np.array(image.convert('RGB'))
        features["mean_r"] = float(np.mean(img_array[:, :, 0]))
        features["mean_g"] = float(np.mean(img_array[:, :, 1]))
        features["mean_b"] = float(np.mean(img_array[:, :, 2]))
        features["std_r"] = float(np.std(img_array[:, :, 0]))
        features["std_g"] = float(np.std(img_array[:, :, 1]))
        features["std_b"] = float(np.std(img_array[:, :, 2]))
        
        return features
        
    except Exception as e:
        print(f"❌ Erreur extraction features: {str(e)}")
        return {}

