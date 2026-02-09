import os
import datetime
from projects.backend.firebase_setup import get_storage_bucket

class StorageService:
    def __init__(self):
        self.bucket = get_storage_bucket()

    def upload_file(self, local_path: str, destination_path: str) -> str:
        """
        Uploads a file to Firebase Storage and returns the public URL.
        
        Args:
            local_path: Path to the local file.
            destination_path: Path where the file should be stored in the bucket.
            
        Returns:
            str: The public URL of the uploaded file.
        """
        try:
            blob = self.bucket.blob(destination_path)
            
            # Set metadata for caching (optional)
            blob.cache_control = 'public, max-age=31536000'
            
            blob.upload_from_filename(local_path)
            
            # Make public
            blob.make_public()
            
            return blob.public_url
        except Exception as e:
            print(f"Error uploading file to storage: {e}")
            raise e

    def upload_log(self, local_path: str, destination_path: str) -> str:
        """
        Uploads a log file to Firebase Storage (text/plain).
        """
        try:
            blob = self.bucket.blob(destination_path)
            blob.cache_control = 'no-cache' # Logs change, don't cache
            blob.upload_from_filename(local_path, content_type='text/plain')
            blob.make_public()
            return blob.public_url
        except Exception as e:
            print(f"Error uploading log to storage: {e}")
            # Don't raise, just return None so workflow doesn't fail
            return None

storage_service = StorageService()
