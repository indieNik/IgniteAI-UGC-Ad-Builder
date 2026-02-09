import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from dotenv import load_dotenv

# Load environment variables from root
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../.."))
env_path = os.path.join(root_dir, ".env")
load_dotenv(env_path)

def initialize_firebase():
    """Initializes Firebase Admin SDK."""
    try:
        # Check if already initialized
        firebase_admin.get_app()
    except ValueError:
        # Not initialized
        # Check for JSON content in Env
        json_content = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        
        cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        
        if json_content:
            import json
            cred_dict = json.loads(json_content)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
            })
            print("Firebase Admin initialized with FIREBASE_SERVICE_ACCOUNT_JSON")
        elif cred_path:
            # Handle relative paths: if relative, make it relative to root_dir
            if not os.path.isabs(cred_path):
                cred_path = os.path.join(root_dir, cred_path)
            
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
                })
                print(f"Firebase Admin initialized with credentials from {cred_path}")
            else:
                 print(f"Warning: Credential path {cred_path} does not exist.")
                 # Fallback to ADC
                 firebase_admin.initialize_app(None, {
                    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
                })
        else:
            # Use Application Default Credentials (ADC)
            print("Attempting to initialize Firebase with Application Default Credentials...")
            firebase_admin.initialize_app(None, {
                'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
            })
            print("Firebase Admin initialized (ADC)")

def get_firestore_client():
    return firestore.client()

def get_storage_bucket():
    from firebase_admin import storage
    # Fallback or explicit bucket name
    bucket_name = os.getenv('FIREBASE_STORAGE_BUCKET', 'ignite-ai-01.firebasestorage.app')
    return storage.bucket(name=bucket_name)

def verify_token(token: str):
    """
    Verify Firebase ID token.
    The token must be from the same Firebase project as the service account.
    Frontend uses project: ignite-ai-01
    Backend service account must also be from: ignite-ai-01
    """
    try:
        # Verify token - Firebase Admin SDK will check against the project_id
        # from the service account credentials used during initialization
        decoded_token = auth.verify_id_token(token, check_revoked=True)
        return decoded_token
    except Exception as e:
        # Re-raise with more context
        raise ValueError(f"Token verification failed: {str(e)}")

def send_notification(user_id: str, title: str, body: str, image_url: str = None, click_action: str = None, run_id: str = None):
    """
    Send a push notification to a user via Firebase Cloud Messaging.
    
    Args:
        user_id: The user's Firebase UID
        title: Notification title
        body: Notification body text
        image_url: Optional image URL to display in notification
        click_action: Optional URL to open when notification is clicked
        run_id: Optional run ID for notification tagging
    
    Returns:
        bool: True if notification sent successfully, False otherwise
    """
    try:
        from firebase_admin import messaging
        from projects.backend.services.db_service import db_service
        
        # Get user's FCM token
        fcm_token = db_service.get_fcm_token(user_id)
        
        if not fcm_token:
            print(f"No FCM token found for user {user_id}. Notification not sent.")
            return False
        
        # Build notification payload
        notification = messaging.Notification(
            title=title,
            body=body,
            image=image_url if image_url else None
        )
        
        # Build data payload for custom handling
        data = {}

        print(f"====== DEBUG: click_action: {click_action}")
        
        # Convert relative URLs to absolute HTTPS URLs
        absolute_click_action = click_action
        if click_action and not click_action.startswith('http'):
            # Use production domain
            absolute_click_action = f"https://igniteai.in{click_action if click_action.startswith('/') else '/' + click_action}"
        
        if absolute_click_action:
            data['clickAction'] = absolute_click_action
            data['url'] = absolute_click_action
        if run_id:
            data['runId'] = run_id
        if image_url:
            data['image'] = image_url
        
        print(f"====== DEBUG: absolute_click_action: {absolute_click_action}")
        # Create message
        message = messaging.Message(
            notification=notification,
            data=data,
            token=fcm_token,
            webpush=messaging.WebpushConfig(
                fcm_options=messaging.WebpushFCMOptions(
                    link=absolute_click_action if absolute_click_action else 'https://igniteai.in/'
                ),
                notification=messaging.WebpushNotification(
                    title=title,
                    body=body,
                    icon='/favicon.ico',
                    image=image_url if image_url else None,
                    badge='/favicon.ico',
                    tag=run_id if run_id else 'igniteai-notification',
                    require_interaction=True
                )
            )
        )
        
        # Send message
        response = messaging.send(message)
        print(f"Successfully sent notification to user {user_id}. Message ID: {response}")
        return True
        
    except Exception as e:
        print(f"Error sending notification to user {user_id}: {e}")
        return False
