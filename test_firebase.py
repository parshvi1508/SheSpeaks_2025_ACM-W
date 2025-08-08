#!/usr/bin/env python3
"""
Test script for Firebase connection
This script demonstrates how to use the Firebase connection with different initialization methods
"""

import os
from firebase_connection import FirebaseConnection, initialize_firebase

def test_environment_variables():
    """Test Firebase initialization with environment variables"""
    print("Testing Firebase initialization with environment variables...")
    
    # Check if environment variables are set
    required_vars = ['FIREBASE_PROJECT_ID', 'FIREBASE_PRIVATE_KEY', 'FIREBASE_CLIENT_EMAIL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please set the required environment variables or use a different initialization method")
        return False
    
    # Initialize Firebase
    success = initialize_firebase("env")
    if success:
        print("✅ Environment variables initialization successful!")
        return True
    else:
        print("❌ Environment variables initialization failed!")
        return False

def test_service_account_file():
    """Test Firebase initialization with service account file"""
    print("\nTesting Firebase initialization with service account file...")
    
    # You can specify the path to your service account JSON file
    service_account_path = "path/to/your/serviceAccountKey.json"
    
    # Check if file exists
    if not os.path.exists(service_account_path):
        print(f"❌ Service account file not found: {service_account_path}")
        print("Please update the path to your service account JSON file")
        return False
    
    # Initialize Firebase
    success = initialize_firebase("service_account", service_account_path=service_account_path)
    if success:
        print("✅ Service account file initialization successful!")
        return True
    else:
        print("❌ Service account file initialization failed!")
        return False

def test_default_credentials():
    """Test Firebase initialization with default credentials"""
    print("\nTesting Firebase initialization with default credentials...")
    
    # Initialize Firebase with default credentials
    success = initialize_firebase("default", project_id="she-speaks-2025")
    if success:
        print("✅ Default credentials initialization successful!")
        return True
    else:
        print("❌ Default credentials initialization failed!")
        return False

def test_database_operations():
    """Test various database operations"""
    print("\nTesting database operations...")
    
    # Create a new Firebase connection instance
    firebase_conn = FirebaseConnection()
    
    # Try to initialize with default credentials first
    if not firebase_conn.initialize_default("she-speaks-2025"):
        print("❌ Could not initialize Firebase for testing")
        return False
    
    # Test connection
    if not firebase_conn.test_connection():
        print("❌ Firebase connection test failed")
        return False
    
    # Test getting data from responses collection
    print("Fetching responses from database...")
    responses = firebase_conn.get_collection_data('responses', limit=5)
    
    if responses:
        print(f"✅ Found {len(responses)} responses:")
        for i, response in enumerate(responses, 1):
            print(f"  {i}. ID: {response.get('id', 'No ID')}")
            # Print some key fields (adjust based on your data structure)
            for key, value in response.items():
                if key not in ['id', 'createdAt', 'updatedAt']:
                    print(f"     {key}: {value}")
            print()
    else:
        print("ℹ️  No responses found in database")
    
    # Test adding a sample document
    print("Adding a test document...")
    test_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'message': 'This is a test message from the Firebase connection test'
    }
    
    doc_id = firebase_conn.add_document('test_collection', test_data)
    if doc_id:
        print(f"✅ Test document added with ID: {doc_id}")
        
        # Test updating the document
        update_data = {'status': 'updated'}
        if firebase_conn.update_document('test_collection', doc_id, update_data):
            print("✅ Test document updated successfully")
        
        # Test deleting the document
        if firebase_conn.delete_document('test_collection', doc_id):
            print("✅ Test document deleted successfully")
    else:
        print("❌ Failed to add test document")
    
    return True

def main():
    """Main test function"""
    print("Firebase Connection Test Suite")
    print("=" * 50)
    
    # Test different initialization methods
    methods = [
        ("Environment Variables", test_environment_variables),
        ("Service Account File", test_service_account_file),
        ("Default Credentials", test_default_credentials)
    ]
    
    successful_method = None
    
    for method_name, test_func in methods:
        try:
            if test_func():
                successful_method = method_name
                print(f"✅ {method_name} method works!")
                break
            else:
                print(f"❌ {method_name} method failed")
        except Exception as e:
            print(f"❌ {method_name} method failed with error: {str(e)}")
    
    if successful_method:
        print(f"\n🎉 Successfully connected using: {successful_method}")
        
        # Test database operations
        test_database_operations()
    else:
        print("\n❌ All initialization methods failed!")
        print("\nTroubleshooting tips:")
        print("1. Make sure you have the correct Firebase project ID")
        print("2. For environment variables: Set up a .env file with your Firebase credentials")
        print("3. For service account: Download the JSON file from Firebase Console")
        print("4. For default credentials: Set up Google Cloud SDK authentication")

if __name__ == "__main__":
    main()
