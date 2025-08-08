# Firebase Connection Setup and Usage

This guide explains how to set up and use the Firebase connection for your SheSpeaks 2025 project.

## Files Created

- `firebase_connection.py` - Main Firebase connection class with multiple authentication methods
- `test_firebase.py` - Comprehensive test script for all connection methods
- `firebase_example.py` - Simple example showing basic usage
- `env_example.txt` - Template for environment variables
- `requirements.txt` - Updated with python-dotenv dependency

## Authentication Methods

The Firebase connection supports three authentication methods:

### 1. Environment Variables (Recommended)

This is the most secure method for production environments.

#### Setup:
1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate new private key"
3. Download the JSON file
4. Create a `.env` file in your project root
5. Copy the values from the JSON file to environment variables

#### Example `.env` file:
```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
```

#### Usage:
```python
from firebase_connection import initialize_firebase
from dotenv import load_dotenv

load_dotenv()  # Load environment variables
initialize_firebase("env")
```

### 2. Service Account Key File

This method uses a JSON service account key file directly.

#### Setup:
1. Download the service account JSON file from Firebase Console
2. Place it in your project (keep it secure and don't commit to version control)

#### Usage:
```python
from firebase_connection import initialize_firebase

initialize_firebase("service_account", service_account_path="path/to/serviceAccountKey.json")
```

### 3. Default Credentials

This method uses Google Cloud SDK default credentials (good for local development).

#### Setup:
1. Install Google Cloud SDK
2. Run `gcloud auth application-default login`

#### Usage:
```python
from firebase_connection import initialize_firebase

initialize_firebase("default", project_id="she-speaks-2025")
```

## Basic Usage

### Initialize Connection
```python
from firebase_connection import FirebaseConnection, initialize_firebase

# Method 1: Using the global function
initialize_firebase("env")  # or "service_account" or "default"

# Method 2: Using the class directly
firebase_conn = FirebaseConnection()
firebase_conn.initialize_with_env_vars()
```

### Test Connection
```python
from firebase_connection import firebase_conn

if firebase_conn.test_connection():
    print("✅ Connected to Firebase!")
else:
    print("❌ Connection failed")
```

### Get Data
```python
# Get all documents from a collection
responses = firebase_conn.get_collection_data('responses')

# Get limited documents
recent_responses = firebase_conn.get_collection_data('responses', limit=10)

# Get specific document
doc = firebase_conn.get_document_data('responses', 'document_id')
```

### Add Data
```python
# Add a new document
data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'message': 'Hello World'
}
doc_id = firebase_conn.add_document('responses', data)
```

### Update Data
```python
# Update existing document
update_data = {'status': 'processed'}
firebase_conn.update_document('responses', 'document_id', update_data)
```

### Delete Data
```python
# Delete document
firebase_conn.delete_document('responses', 'document_id')
```

### Query Data
```python
# Query documents with conditions
results = firebase_conn.query_documents('responses', 'status', '==', 'pending')
```

## Convenience Functions

The module also provides convenience functions for common operations:

```python
from firebase_connection import (
    get_all_responses,
    get_recent_responses,
    add_survey_response,
    get_response_count
)

# Get all survey responses
responses = get_all_responses()

# Get recent responses (default: 10)
recent = get_recent_responses(limit=5)

# Add a new survey response
doc_id = add_survey_response({
    'name': 'Jane Doe',
    'email': 'jane@example.com',
    'feedback': 'Great event!'
})

# Get total response count
count = get_response_count()
```

## Running Tests

### Test All Connection Methods
```bash
python test_firebase.py
```

### Test Basic Functionality
```bash
python firebase_example.py
```

### Test Direct Connection
```bash
python firebase_connection.py
```

## Troubleshooting

### Common Issues

1. **"Missing environment variables"**
   - Make sure you have a `.env` file with the required variables
   - Check that the variable names match exactly

2. **"Service account file not found"**
   - Verify the path to your service account JSON file
   - Make sure the file exists and is readable

3. **"Firebase initialization error"**
   - Check your Firebase project ID
   - Verify your service account has the necessary permissions
   - Ensure your Firebase project has Firestore enabled

4. **"Connection failed"**
   - Check your internet connection
   - Verify Firebase project settings
   - Make sure Firestore is enabled in your Firebase project

### Security Best Practices

1. **Never commit sensitive files to version control**
   - Add `.env` to your `.gitignore`
   - Add `*serviceAccountKey*.json` to your `.gitignore`

2. **Use environment variables in production**
   - Set environment variables on your deployment platform
   - Don't use service account files in production

3. **Limit service account permissions**
   - Only grant necessary permissions to your service account
   - Use the principle of least privilege

## Dependencies

Make sure you have the required packages installed:

```bash
pip install -r requirements.txt
```

Required packages:
- `firebase-admin>=6.2.0`
- `python-dotenv>=1.0.0`
- `streamlit>=1.28.0` (if using Streamlit)
- `pandas>=2.0.0` (for data manipulation)
- `plotly>=5.15.0` (for visualizations)
- `numpy>=1.24.0` (for numerical operations)
