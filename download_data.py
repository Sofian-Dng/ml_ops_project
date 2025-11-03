"""
Script pour télécharger les images de pissenlit et d'herbe depuis GitHub.
"""
import os
import urllib.request
from pathlib import Path
from tqdm import tqdm

# URLs de base pour les données
BASE_URL = "https://raw.githubusercontent.com/btphan95/greenr-airflow/refs/heads/master/data"
DANDELION_URL = f"{BASE_URL}/dandelion"
GRASS_URL = f"{BASE_URL}/grass"

# Nombre d'images par classe
NUM_IMAGES = 200

# Dossier de destination
DATA_DIR = Path("data")
DANDELION_DIR = DATA_DIR / "dandelion"
GRASS_DIR = DATA_DIR / "grass"


def download_image(url: str, dest_path: Path) -> bool:
    """Télécharge une image depuis une URL vers un chemin local."""
    try:
        urllib.request.urlretrieve(url, dest_path)
        return True
    except Exception as e:
        print(f"Erreur lors du téléchargement de {url}: {e}")
        return False


def download_class_images(class_name: str, base_url: str, output_dir: Path, num_images: int):
    """Télécharge toutes les images d'une classe."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nTéléchargement de {num_images} images de {class_name}...")
    
    success_count = 0
    for i in tqdm(range(num_images), desc=f"{class_name}"):
        # Format: 00000000.jpg jusqu'à 00000199.jpg
        image_name = f"{i:08d}.jpg"
        url = f"{base_url}/{image_name}"
        dest_path = output_dir / image_name
        
        if download_image(url, dest_path):
            success_count += 1
    
    print(f"OK - {success_count}/{num_images} images de {class_name} telechargees avec succes")
    return success_count


def main():
    """Fonction principale pour télécharger toutes les images."""
    print("=" * 60)
    print("Téléchargement des données pour la classification d'images")
    print("=" * 60)
    
    # Télécharger les pissenlits
    dandelion_count = download_class_images(
        "pissenlit", 
        DANDELION_URL, 
        DANDELION_DIR, 
        NUM_IMAGES
    )
    
    # Télécharger l'herbe
    grass_count = download_class_images(
        "herbe", 
        GRASS_URL, 
        GRASS_DIR, 
        NUM_IMAGES
    )
    
    print("\n" + "=" * 60)
    print(f"Résumé du téléchargement:")
    print(f"  - Pissenlit: {dandelion_count}/{NUM_IMAGES} images")
    print(f"  - Herbe: {grass_count}/{NUM_IMAGES} images")
    print(f"  - Total: {dandelion_count + grass_count}/{NUM_IMAGES * 2} images")
    print("=" * 60)


if __name__ == "__main__":
    main()

