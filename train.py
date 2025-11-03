"""
Script d'entraînement pour classification binaire d'images (pissenlit vs herbe).
Utilise TensorFlow/Keras avec MLflow pour le tracking et Minio pour le stockage S3.
"""
import os
import mlflow
import mlflow.tensorflow
import numpy as np
from pathlib import Path
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split

# Import pour S3/Minio et Feature Store
try:
    from utils_s3 import get_minio_client
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False
    print("⚠️  utils_s3 non disponible, S3/Minio désactivé")

try:
    from feature_store import FeatureStore, extract_image_features
    FEATURE_STORE_AVAILABLE = True
except ImportError:
    FEATURE_STORE_AVAILABLE = False
    print("⚠️  feature_store non disponible, Feature Store désactivé")

# Configuration
DATA_DIR = Path("data")
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10
VALIDATION_SPLIT = 0.2
RANDOM_STATE = 42

# Classes
CLASSES = ["dandelion", "grass"]


def load_and_prepare_data(data_dir: Path, img_size: tuple, validation_split: float):
    """
    Charge et prépare les données d'images pour l'entraînement.
    
    Returns:
        train_generator, validation_generator: Générateurs Keras pour train/val
    """
    # Créer le générateur d'images avec augmentation de données
    datagen = ImageDataGenerator(
        rescale=1.0 / 255.0,  # Normalisation [0, 1]
        validation_split=validation_split,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
    )
    
    # Générateur d'entraînement
    train_generator = datagen.flow_from_directory(
        data_dir,
        target_size=img_size,
        batch_size=BATCH_SIZE,
        class_mode='binary',
        subset='training',
        shuffle=True,
        seed=RANDOM_STATE,
    )
    
    # Générateur de validation
    validation_generator = datagen.flow_from_directory(
        data_dir,
        target_size=img_size,
        batch_size=BATCH_SIZE,
        class_mode='binary',
        subset='validation',
        shuffle=False,
        seed=RANDOM_STATE,
    )
    
    return train_generator, validation_generator


def create_model(input_shape: tuple, num_classes: int = 1):
    """
    Crée un modèle CNN simple pour la classification binaire.
    
    Returns:
        model: Modèle Keras compilé
    """
    model = keras.Sequential([
        # Bloc convolutionnel 1
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        layers.MaxPooling2D(2, 2),
        
        # Bloc convolutionnel 2
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D(2, 2),
        
        # Bloc convolutionnel 3
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.MaxPooling2D(2, 2),
        
        # Flatten et couches denses
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')  # Binary classification
    ])
    
    # Compiler le modèle
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    return model


def main():
    """Fonction principale d'entraînement."""
    print("=" * 60)
    print("Entraînement du modèle de classification d'images")
    print("=" * 60)
    
    # Vérifier que les données existent
    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"Le dossier {DATA_DIR} n'existe pas. "
            "Veuillez d'abord exécuter download_data.py"
        )
    
    # Charger les données
    print("\n1. Chargement et préparation des données...")
    train_gen, val_gen = load_and_prepare_data(
        DATA_DIR, 
        IMG_SIZE, 
        VALIDATION_SPLIT
    )
    
    print(f"   - Classes: {train_gen.class_indices}")
    print(f"   - Images d'entraînement: {train_gen.samples}")
    print(f"   - Images de validation: {val_gen.samples}")
    
    # Créer le modèle
    print("\n2. Création du modèle...")
    input_shape = (*IMG_SIZE, 3)  # (224, 224, 3) pour RGB
    model = create_model(input_shape)
    model.summary()
    
    # Configurer MLflow
    print("\n3. Configuration MLflow...")
    mlflow.set_experiment("dandelion_vs_grass")
    
    # Callback pour early stopping
    early_stopping = keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=3,
        restore_best_weights=True
    )
    
    # Entraînement avec MLflow
    with mlflow.start_run():
        print("\n4. Début de l'entraînement...")
        
        # Log des paramètres
        mlflow.log_params({
            "batch_size": BATCH_SIZE,
            "epochs": EPOCHS,
            "img_size": f"{IMG_SIZE[0]}x{IMG_SIZE[1]}",
            "validation_split": VALIDATION_SPLIT,
            "optimizer": "adam",
            "loss": "binary_crossentropy",
        })
        
        # Entraîner le modèle
        history = model.fit(
            train_gen,
            epochs=EPOCHS,
            validation_data=val_gen,
            callbacks=[early_stopping],
            verbose=1
        )
        
        # Évaluer le modèle
        print("\n5. Évaluation du modèle...")
        val_loss, val_accuracy = model.evaluate(val_gen, verbose=0)
        
        print(f"   - Validation Loss: {val_loss:.4f}")
        print(f"   - Validation Accuracy: {val_accuracy:.4f}")
        
        # Log des métriques finales
        mlflow.log_metrics({
            "val_loss": val_loss,
            "val_accuracy": val_accuracy,
        })
        
        # Log de l'historique d'entraînement
        for epoch in range(len(history.history['loss'])):
            mlflow.log_metric("train_loss", history.history['loss'][epoch], step=epoch)
            mlflow.log_metric("train_accuracy", history.history['accuracy'][epoch], step=epoch)
            mlflow.log_metric("val_loss", history.history['val_loss'][epoch], step=epoch)
            mlflow.log_metric("val_accuracy", history.history['val_accuracy'][epoch], step=epoch)
        
        # Enregistrer le modèle dans MLflow
        print("\n6. Enregistrement du modèle dans MLflow...")
        mlflow.tensorflow.log_model(
            model,
            artifact_path="model",
            registered_model_name="dandelion_vs_grass_classifier"
        )
        
        run_id = mlflow.active_run().info.run_id
        print("\nOK - Modele enregistre avec succes dans MLflow!")
        print(f"OK - Run ID: {run_id}")
        
        # Upload vers Minio/S3 si disponible
        if S3_AVAILABLE:
            print("\n7. Upload du modèle vers Minio/S3...")
            try:
                minio_client = get_minio_client()
                mlruns_dir = Path("mlruns")
                # Chercher le modèle dans la structure MLflow réelle
                # Structure: mlruns/experiment_id/models/m-*/artifacts/data/model/
                model_path = None
                
                # D'abord chercher dans la structure directe du run
                for exp_dir in mlruns_dir.glob("[0-9]*"):
                    if exp_dir.is_dir():
                        models_dir = exp_dir / "models"
                        if models_dir.exists():
                            # Chercher le modèle avec le run_id dans le chemin
                            for model_dir in models_dir.glob(f"m-*"):
                                potential_path = model_dir / "artifacts" / "data" / "model"
                                if potential_path.exists() and (potential_path / "saved_model.pb").exists():
                                    # Vérifier si c'est le bon run en comparant les timestamps
                                    model_path = potential_path
                                    break
                
                # Fallback: chercher le modèle le plus récent dans models/
                if not model_path:
                    models_dir = mlruns_dir / "models" / "dandelion_vs_grass_classifier"
                    if models_dir.exists():
                        versions = sorted(models_dir.glob("version-*"), key=lambda x: int(x.name.split("-")[1]), reverse=True)
                        if versions:
                            latest_version = versions[0]
                            # Chercher dans la structure exp_id/models/m-*/artifacts/data/model/
                            for exp_dir in mlruns_dir.glob("[0-9]*"):
                                models_exp_dir = exp_dir / "models"
                                if models_exp_dir.exists():
                                    for model_dir in models_exp_dir.glob("m-*"):
                                        potential_path = model_dir / "artifacts" / "data" / "model"
                                        if potential_path.exists() and (potential_path / "saved_model.pb").exists():
                                            model_path = potential_path
                                            break
                                if model_path:
                                    break
                
                if model_path and model_path.exists():
                    # Utiliser le model_id (m-...) comme identifiant
                    model_id = model_path.parent.parent.name if model_path.parent.parent.name.startswith("m-") else run_id
                    s3_prefix = f"models/dandelion_vs_grass_classifier/{model_id}"
                    count = minio_client.upload_directory(str(model_path), s3_prefix)
                    print(f"✅ Modèle uploadé vers S3: {s3_prefix} ({count} fichiers)")
                    
                    # Log l'URL S3 dans MLflow
                    mlflow.log_param("s3_model_path", s3_prefix)
                else:
                    print("⚠️  Chemin modèle MLflow non trouvé pour upload S3")
                    print("   Structure attendue: mlruns/experiment_id/models/m-*/artifacts/data/model/")
            except Exception as e:
                print(f"⚠️  Erreur upload S3: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Feature Store: Extraire et stocker les features
        if FEATURE_STORE_AVAILABLE:
            print("\n8. Extraction et stockage des features...")
            try:
                feature_store = FeatureStore()
                
                # Extraire les features de quelques images d'exemple
                data_dir = Path("data")
                sample_count = 0
                max_samples = 20  # Limiter pour ne pas ralentir l'entraînement
                
                for class_name in CLASSES:
                    class_dir = data_dir / class_name
                    if class_dir.exists():
                        for img_path in list(class_dir.glob("*.jpg"))[:max_samples//2]:
                            features = extract_image_features(str(img_path))
                            if features:
                                feature_store.add_features(
                                    image_path=str(img_path),
                                    label=class_name,
                                    features=features
                                )
                                sample_count += 1
                
                print(f"✅ {sample_count} features extraites et stockées")
                
                # Log statistiques feature store dans MLflow
                stats = feature_store.get_statistics()
                mlflow.log_param("feature_store_total", stats.get("total_features", 0))
                
            except Exception as e:
                print(f"⚠️  Erreur feature store: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Entraînement terminé!")
    print("=" * 60)


if __name__ == "__main__":
    main()
