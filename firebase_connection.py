import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime
import json
from typing import Optional, Dict, Any, List

class FirebaseConnection:
    """Firebase connection manager with support for environment variables and service account keys"""
    
    def __init__(self):
        self.db = None
        self.is_initialized = False
        
    def initialize_with_env_vars(self) -> bool:
        """Initialize Firebase using environment variables"""
        try:
            # Check if Firebase is already initialized
            if firebase_admin._apps:
                self.db = firestore.client()
                self.is_initialized = True
                return True
            
            # Get configuration from environment variables
            project_id = os.getenv('FIREBASE_PROJECT_ID')
            private_key_id = os.getenv('FIREBASE_PRIVATE_KEY_ID')
            private_key = os.getenv('FIREBASE_PRIVATE_KEY')
            client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
            client_id = os.getenv('FIREBASE_CLIENT_ID')
            auth_uri = os.getenv('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth')
            token_uri = os.getenv('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token')
            auth_provider_x509_cert_url = os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs')
            client_x509_cert_url = os.getenv('FIREBASE_CLIENT_X509_CERT_URL')
            
            if not all([project_id, private_key, client_email]):
                print("❌ Missing required environment variables for Firebase initialization")
                return False
            
            # Create credentials dictionary
            cred_dict = {
                "type": "service_account",
                "project_id": project_id,
                "private_key_id": private_key_id,
                "private_key": private_key.replace('\\n', '\n') if private_key else None,
                "client_email": client_email,
                "client_id": client_id,
                "auth_uri": auth_uri,
                "token_uri": token_uri,
                "auth_provider_x509_cert_url": auth_provider_x509_cert_url,
                "client_x509_cert_url": client_x509_cert_url
            }
            
            # Initialize Firebase
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            self.is_initialized = True
            print("✅ Firebase initialized successfully with environment variables!")
            return True
            
        except Exception as e:
            print(f"❌ Firebase initialization error: {str(e)}")
            return False
    
    def initialize_with_service_account(self, service_account_path: str) -> bool:
        """Initialize Firebase using service account key file"""
        try:
            # Check if Firebase is already initialized
            if firebase_admin._apps:
                self.db = firestore.client()
                self.is_initialized = True
                return True
            
            # Check if service account file exists
            if not os.path.exists(service_account_path):
                print(f"❌ Service account file not found: {service_account_path}")
                return False
            
            # Initialize Firebase with service account
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            self.is_initialized = True
            print(f"✅ Firebase initialized successfully with service account: {service_account_path}")
            return True
            
        except Exception as e:
            print(f"❌ Firebase initialization error: {str(e)}")
            return False
    
    def initialize_default(self, project_id: str = None) -> bool:
        """Initialize Firebase using default credentials (for local development)"""
        try:
            # Check if Firebase is already initialized
            if firebase_admin._apps:
                self.db = firestore.client()
                self.is_initialized = True
                return True
            
            # Initialize with default credentials
            cred = credentials.ApplicationDefault()
            config = {}
            if project_id:
                config['projectId'] = project_id
            
            firebase_admin.initialize_app(cred, config)
            
            self.db = firestore.client()
            self.is_initialized = True
            print("✅ Firebase initialized successfully with default credentials!")
            return True
            
        except Exception as e:
            print(f"❌ Firebase initialization error: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """Test Firebase connection"""
        try:
            if not self.is_initialized or not self.db:
                print("❌ Firebase not initialized")
                return False
            
            # Try to read from a test document
            test_doc = self.db.collection('test').document('connection_test').get()
            print("✅ Firebase connection successful!")
            return True
            
        except Exception as e:
            print(f"❌ Firebase connection failed: {str(e)}")
            return False
    
    def get_collection_data(self, collection_name: str, limit: int = None) -> Optional[List[Dict[str, Any]]]:
        """Get data from a specific collection"""
        try:
            if not self.is_initialized or not self.db:
                print("❌ Firebase not initialized")
                return None
            
            collection_ref = self.db.collection(collection_name)
            
            if limit:
                docs = collection_ref.limit(limit).stream()
            else:
                docs = collection_ref.stream()
            
            data = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data['id'] = doc.id
                data.append(doc_data)
            
            return data
            
        except Exception as e:
            print(f"❌ Error fetching data from {collection_name}: {str(e)}")
            return None
    
    def get_document_data(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Get data from a specific document"""
        try:
            if not self.is_initialized or not self.db:
                print("❌ Firebase not initialized")
                return None
            
            doc_ref = self.db.collection(collection_name).document(document_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            else:
                print(f"❌ Document {document_id} not found in collection {collection_name}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching document {document_id}: {str(e)}")
            return None
    
    def add_document(self, collection_name: str, data: Dict[str, Any]) -> Optional[str]:
        """Add a new document to a collection"""
        try:
            if not self.is_initialized or not self.db:
                print("❌ Firebase not initialized")
                return None
            
            # Add timestamp
            data['createdAt'] = datetime.now()
            
            # Add document
            doc_ref = self.db.collection(collection_name).add(data)
            
            print(f"✅ Document added successfully! ID: {doc_ref[1].id}")
            return doc_ref[1].id
            
        except Exception as e:
            print(f"❌ Error adding document: {str(e)}")
            return None
    
    def update_document(self, collection_name: str, document_id: str, data: Dict[str, Any]) -> bool:
        """Update an existing document"""
        try:
            if not self.is_initialized or not self.db:
                print("❌ Firebase not initialized")
                return False
            
            # Add update timestamp
            data['updatedAt'] = datetime.now()
            
            # Update document
            self.db.collection(collection_name).document(document_id).update(data)
            
            print(f"✅ Document {document_id} updated successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error updating document {document_id}: {str(e)}")
            return False
    
    def delete_document(self, collection_name: str, document_id: str) -> bool:
        """Delete a document"""
        try:
            if not self.is_initialized or not self.db:
                print("❌ Firebase not initialized")
                return False
            
            # Delete document
            self.db.collection(collection_name).document(document_id).delete()
            
            print(f"✅ Document {document_id} deleted successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting document {document_id}: {str(e)}")
            return False
    
    def query_documents(self, collection_name: str, field: str, operator: str, value: Any) -> Optional[List[Dict[str, Any]]]:
        """Query documents with a specific condition"""
        try:
            if not self.is_initialized or not self.db:
                print("❌ Firebase not initialized")
                return None
            
            docs = self.db.collection(collection_name).where(field, operator, value).stream()
            
            data = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data['id'] = doc.id
                data.append(doc_data)
            
            return data
            
        except Exception as e:
            print(f"❌ Error querying documents: {str(e)}")
            return None

# Global Firebase connection instance
firebase_conn = FirebaseConnection()

def initialize_firebase(method: str = "env", **kwargs) -> bool:
    """
    Initialize Firebase connection
    
    Args:
        method: "env" for environment variables, "service_account" for service account file, "default" for default credentials
        **kwargs: Additional arguments (service_account_path for service_account method, project_id for default method)
    """
    if method == "env":
        return firebase_conn.initialize_with_env_vars()
    elif method == "service_account":
        service_account_path = kwargs.get('service_account_path')
        if not service_account_path:
            print("❌ service_account_path is required for service_account method")
            return False
        return firebase_conn.initialize_with_service_account(service_account_path)
    elif method == "default":
        project_id = kwargs.get('project_id')
        return firebase_conn.initialize_default(project_id)
    else:
        print(f"❌ Unknown initialization method: {method}")
        return False

# Example usage functions
def get_all_responses():
    """Get all survey responses from Firebase"""
    return firebase_conn.get_collection_data('responses')

def get_recent_responses(limit: int = 10):
    """Get recent survey responses"""
    return firebase_conn.get_collection_data('responses', limit)

def add_survey_response(data: Dict[str, Any]):
    """Add a new survey response"""
    return firebase_conn.add_document('responses', data)

def get_response_count():
    """Get total number of responses"""
    responses = firebase_conn.get_collection_data('responses')
    return len(responses) if responses else 0

if __name__ == "__main__":
    # Example usage
    print("Firebase Connection Test")
    print("=" * 50)
    
    # Try to initialize with environment variables first
    if not initialize_firebase("env"):
        # Fallback to default credentials
        print("Trying default credentials...")
        initialize_firebase("default", project_id="she-speaks-2025")
    
    # Test connection
    if firebase_conn.test_connection():
        # Get some data
        responses = get_all_responses()
        if responses:
            print(f"Found {len(responses)} responses")
            for response in responses[:3]:  # Show first 3
                print(f"- {response.get('id', 'No ID')}: {response}")
        else:
            print("No responses found")
    else:
        print("Failed to connect to Firebase")
