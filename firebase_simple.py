import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import os
from datetime import datetime

# Initialize Firebase Admin SDK
db = None

def initialize_firebase():
    """Initialize Firebase connection"""
    global db
    try:
        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            # Your Firebase project configuration
            # You can either use a service account key file or initialize with project ID
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'projectId': 'she-speaks-2025'
            })
        
        db = firestore.client()
        return True
    except Exception as e:
        st.error(f"Firebase initialization error: {str(e)}")
        return False

# Initialize Firebase when module is imported
if initialize_firebase():
    st.success("✅ Firebase initialized successfully!")
else:
    st.error("❌ Failed to initialize Firebase")

def test_connection():
    """Test Firebase connection"""
    try:
        if db:
            # Try to read from a test document
            test_doc = db.collection('test').document('connection_test').get()
            st.success("✅ Firebase connection successful!")
            return True
        else:
            st.error("❌ Firebase not initialized")
            return False
    except Exception as e:
        st.error(f"❌ Firebase connection failed: {str(e)}")
        return False

def add_survey_response(data):
    """Add a new survey response to Firebase"""
    try:
        if not db:
            return False, "Firebase not initialized"
        
        # Add timestamp
        data['submittedAt'] = datetime.now()
        
        # Add to Firestore
        doc_ref = db.collection('responses').add(data)
        
        return True, f"Response added successfully! ID: {doc_ref[1].id}"
    except Exception as e:
        return False, f"Error adding response: {str(e)}"

def get_all_responses():
    """Get all survey responses from Firebase"""
    try:
        if not db:
            return None
        
        responses = []
        docs = db.collection('responses').order_by('submittedAt', direction=firestore.Query.DESCENDING).stream()
        
        for doc in docs:
            response_data = doc.to_dict()
            response_data['id'] = doc.id
            responses.append(response_data)
        
        return responses
    except Exception as e:
        st.error(f"Error fetching responses: {str(e)}")
        return None

def get_response_count():
    """Get total number of responses"""
    try:
        if not db:
            return 0
        
        # Get count of documents in responses collection
        docs = db.collection('responses').stream()
        count = sum(1 for _ in docs)
        return count
    except Exception as e:
        st.error(f"Error counting responses: {str(e)}")
        return 0

def get_responses_by_field(field_name, field_value):
    """Get responses filtered by a specific field"""
    try:
        if not db:
            return None
        
        responses = []
        docs = db.collection('responses').where(field_name, '==', field_value).stream()
        
        for doc in docs:
            response_data = doc.to_dict()
            response_data['id'] = doc.id
            responses.append(response_data)
        
        return responses
    except Exception as e:
        st.error(f"Error fetching filtered responses: {str(e)}")
        return None

def get_recent_responses(limit=10):
    """Get recent responses with limit"""
    try:
        if not db:
            return None
        
        responses = []
        docs = db.collection('responses').order_by('submittedAt', direction=firestore.Query.DESCENDING).limit(limit).stream()
        
        for doc in docs:
            response_data = doc.to_dict()
            response_data['id'] = doc.id
            responses.append(response_data)
        
        return responses
    except Exception as e:
        st.error(f"Error fetching recent responses: {str(e)}")
        return None
