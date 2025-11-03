"""
Utils pour interagir avec Minio (S3 compatible)
"""
import boto3
from botocore.client import Config
import os
from pathlib import Path
from typing import Optional


class MinioClient:
    """Client pour interagir avec Minio (S3 compatible)."""
    
    def __init__(
        self,
        endpoint_url: str = "http://localhost:9000",
        access_key: str = "minioadmin",
        secret_key: str = "minioadmin",
        bucket_name: str = "mlops-models"
    ):
        """
        Initialise le client Minio.
        
        Args:
            endpoint_url: URL du serveur Minio
            access_key: Clé d'accès
            secret_key: Clé secrète
            bucket_name: Nom du bucket S3
        """
        self.endpoint_url = endpoint_url
        self.bucket_name = bucket_name
        self.client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'
        )
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Crée le bucket s'il n'existe pas."""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except:
            self.client.create_bucket(Bucket=self.bucket_name)
            print(f"✅ Bucket '{self.bucket_name}' créé")
    
    def upload_file(self, local_path: str, s3_path: str) -> bool:
        """
        Upload un fichier vers Minio.
        
        Args:
            local_path: Chemin local du fichier
            s3_path: Chemin S3 de destination
            
        Returns:
            True si succès, False sinon
        """
        try:
            self.client.upload_file(local_path, self.bucket_name, s3_path)
            print(f"✅ Fichier uploadé: {s3_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur upload: {str(e)}")
            return False
    
    def upload_directory(self, local_dir: str, s3_prefix: str = "") -> int:
        """
        Upload un dossier entier vers Minio.
        
        Args:
            local_dir: Dossier local
            s3_prefix: Préfixe S3 (ex: "models/v1/")
            
        Returns:
            Nombre de fichiers uploadés
        """
        local_path = Path(local_dir)
        if not local_path.exists():
            print(f"❌ Dossier non trouvé: {local_dir}")
            return 0
        
        count = 0
        for file_path in local_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(local_path)
                s3_key = f"{s3_prefix}/{relative_path}".replace("\\", "/")
                if self.upload_file(str(file_path), s3_key):
                    count += 1
        
        print(f"✅ {count} fichiers uploadés vers {s3_prefix}")
        return count
    
    def download_file(self, s3_path: str, local_path: str) -> bool:
        """
        Télécharge un fichier depuis Minio.
        
        Args:
            s3_path: Chemin S3 du fichier
            local_path: Chemin local de destination
            
        Returns:
            True si succès, False sinon
        """
        try:
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            self.client.download_file(self.bucket_name, s3_path, local_path)
            print(f"✅ Fichier téléchargé: {local_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur download: {str(e)}")
            return False
    
    def list_files(self, prefix: str = "") -> list:
        """
        Liste les fichiers dans le bucket.
        
        Args:
            prefix: Préfixe pour filtrer les fichiers
            
        Returns:
            Liste des clés S3
        """
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except Exception as e:
            print(f"❌ Erreur list: {str(e)}")
            return []
    
    def get_file_url(self, s3_path: str, expires_in: int = 3600) -> Optional[str]:
        """
        Génère une URL signée pour accéder au fichier.
        
        Args:
            s3_path: Chemin S3 du fichier
            expires_in: Durée de validité en secondes
            
        Returns:
            URL signée ou None
        """
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_path},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            print(f"❌ Erreur génération URL: {str(e)}")
            return None


def get_minio_client() -> MinioClient:
    """
    Factory pour créer un client Minio avec les variables d'environnement.
    
    Returns:
        Instance de MinioClient
    """
    endpoint = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    bucket = os.getenv("MINIO_BUCKET", "mlops-models")
    
    return MinioClient(endpoint, access_key, secret_key, bucket)

