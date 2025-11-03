"""
Client Gradio pour tester l'API de classification d'images déployée sur Kubernetes.
"""
import gradio as gr
import requests
import numpy as np
from PIL import Image
import io
import json

# URL de l'API (ajuster selon votre déploiement K8s)
# Pour NodePort avec port 30080 sur localhost (Kubernetes):
API_URL = "http://localhost:30080/invocations"
# Alternative si vous utilisez Docker directement:
# API_URL = "http://localhost:5000/invocations"


def classify_image(image):
    """
    Envoie une image à l'API MLflow et retourne la prédiction.
    
    Args:
        image: Image PIL ou numpy array
        
    Returns:
        dict: Prédiction avec classe et probabilité
    """
    try:
        # Convertir l'image en format compatible avec MLflow
        if isinstance(image, Image.Image):
            # Convertir en RGB si nécessaire (gère RGBA, grayscale, etc.)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Redimensionner à 224x224 (le modèle attend cette taille)
            image = image.resize((224, 224), Image.Resampling.LANCZOS)
            
            # Convertir en numpy array et normaliser [0, 1]
            img_array = np.array(image, dtype=np.float32) / 255.0
            
            # Vérifier la shape: doit être (224, 224, 3)
            if len(img_array.shape) != 3 or img_array.shape[2] != 3:
                return {
                    "Erreur": f"Format d'image invalide. Shape: {img_array.shape}. Attendu: (224, 224, 3)",
                    "Mode original": image.mode if isinstance(image, Image.Image) else "N/A"
                }
        elif isinstance(image, np.ndarray):
            # Si c'est déjà un numpy array, vérifier et convertir si nécessaire
            if len(image.shape) == 2:  # Grayscale
                image = np.stack([image, image, image], axis=-1)
            elif len(image.shape) == 3 and image.shape[2] == 4:  # RGBA
                image = image[:, :, :3]  # Garder seulement RGB
            
            # Redimensionner si nécessaire
            if image.shape[:2] != (224, 224):
                from PIL import Image as PILImage
                img_pil = PILImage.fromarray((image * 255).astype(np.uint8))
                img_pil = img_pil.resize((224, 224), PILImage.Resampling.LANCZOS)
                img_array = np.array(img_pil, dtype=np.float32) / 255.0
            else:
                img_array = image.astype(np.float32)
                if img_array.max() > 1.0:
                    img_array = img_array / 255.0
        else:
            return {
                "Erreur": f"Type d'image non supporté: {type(image)}",
                "Attendu": "PIL.Image ou numpy.ndarray"
            }
        
        # Préparer les données pour MLflow
        # Format attendu par mlflow models serve: {"inputs": [...]}
        data = {
            "inputs": [img_array.tolist()]
        }
        
        # Envoyer la requête avec timeout augmenté pour la première charge du modèle
        response = requests.post(
            API_URL,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30  # Augmenté pour permettre le chargement du modèle
        )
        
        if response.status_code == 200:
            predictions = response.json()
            
            # MLflow retourne {'predictions': [[prob]]} ou {'predictions': [prob]}
            # Gérer les deux formats
            prob = None
            
            try:
                if isinstance(predictions, dict) and "predictions" in predictions:
                    # Format: {'predictions': [[0.85]]} ou {'predictions': [0.85]}
                    prob_list = predictions["predictions"]
                    if len(prob_list) > 0:
                        prob = prob_list[0]
                        # Si c'est une liste imbriquée, extraire la valeur
                        while isinstance(prob, list) and len(prob) > 0:
                            prob = prob[0]
                        # Convertir en float si ce n'est pas déjà le cas
                        prob = float(prob)
                    else:
                        return {"Erreur": "Liste 'predictions' vide", "Réponse": str(predictions)}
                elif isinstance(predictions, list) and len(predictions) > 0:
                    # Format: [[0.85]] ou [0.85]
                    prob = predictions[0]
                    while isinstance(prob, list) and len(prob) > 0:
                        prob = prob[0]
                    prob = float(prob)
                else:
                    return {"Erreur": f"Format de réponse non reconnu: {type(predictions)}", "Contenu": str(predictions)}
                
                # Vérifier que prob est un nombre valide (déjà converti en float ci-dessus)
                if prob is not None:
                    # prob est déjà un float à ce stade
                    if np.isnan(prob) or np.isinf(prob):
                        return {"Erreur": f"Probabilité invalide (NaN ou Inf): {prob}"}
                    
                    # Interprétation: < 0.5 = herbe, >= 0.5 = pissenlit
                    predicted_class = "Pissenlit" if prob >= 0.5 else "Herbe"
                    confidence = prob if prob >= 0.5 else (1 - prob)
                    
                    return {
                        "Classe prédite": predicted_class,
                        "Confiance": f"{confidence * 100:.2f}%",
                        "Probabilité brute": f"{prob:.6f}"
                    }
                else:
                    return {"Erreur": f"Format de réponse inattendu: {predictions}", "Structure": "prob est None après parsing"}
            except Exception as e:
                # Capturer TOUTES les exceptions pour debug
                import traceback
                return {
                    "Erreur": f"Exception lors du parsing: {type(e).__name__}: {str(e)}",
                    "Réponse brute": str(predictions),
                    "Traceback": traceback.format_exc()
                }
        else:
            return {
                "Erreur": f"Erreur API (code {response.status_code})",
                "Détails": response.text
            }
    
    except requests.exceptions.ConnectionError:
        return {
            "Erreur": "Impossible de se connecter à l'API",
            "Vérifiez": f"Que l'API est accessible à {API_URL}"
        }
    except Exception as e:
        return {
            "Erreur": "Erreur lors de la prédiction",
            "Détails": str(e)
        }


def create_interface():
    """Crée l'interface Gradio."""
    
    # Description
    description = """
    # Classificateur Pissenlit vs Herbe
    
    Téléchargez une image pour classer si c'est un pissenlit ou de l'herbe.
    
    **Note**: L'API doit être déployée sur Kubernetes et accessible à l'URL configurée.
    """
    
    # Interface Gradio
    iface = gr.Interface(
        fn=classify_image,
        inputs=gr.Image(type="pil", label="Image à classifier"),
        outputs=gr.JSON(label="Résultats de la prédiction"),
        title="Classification Pissenlit vs Herbe",
        description=description,
        examples=None,  # Vous pouvez ajouter des exemples ici
        theme="default",
    )
    
    return iface


if __name__ == "__main__":
    print("=" * 60)
    print("Lancement du client Gradio")
    print(f"API URL configurée: {API_URL}")
    print("=" * 60)
    print("\nPour utiliser l'interface:")
    print("1. Assurez-vous que l'API est déployée et accessible")
    print("2. Ouvrez votre navigateur à l'URL affichée ci-dessous")
    print("3. Téléchargez une image et obtenez la prédiction")
    print("\n" + "=" * 60 + "\n")
    
    # Lancer l'interface
    iface = create_interface()
    
    # Essayer le port 7860, sinon utiliser un port disponible automatiquement
    try:
        iface.launch(server_name="0.0.0.0", server_port=7860, share=False)
    except OSError:
        # Si le port est occupé, utiliser un port automatique
        print("⚠️  Port 7860 occupé, utilisation d'un port automatique...")
        iface.launch(server_name="0.0.0.0", server_port=0, share=False)  # 0 = port automatique

