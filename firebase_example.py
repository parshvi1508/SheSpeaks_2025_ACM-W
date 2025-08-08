#!/usr/bin/env python3
"""
Simple example of using Firebase connection with environment variables
"""

import os
from dotenv import load_dotenv
from firebase_connection import initialize_firebase, get_all_responses, add_survey_response

# Load environment variables from .env file
load_dotenv()

def main():
    """Main example function"""
    print("Firebase Connection Example")
    print("=" * 40)
    
    # Initialize Firebase using environment variables
    print("Initializing Firebase...")
    if initialize_firebase("env"):
        print("✅ Firebase initialized successfully!")
        
        # Example: Get all responses
        print("\nFetching all responses...")
        responses = get_all_responses()
        
        if responses:
            print(f"Found {len(responses)} responses:")
            for i, response in enumerate(responses[:3], 1):  # Show first 3
                print(f"  {i}. {response}")
        else:
            print("No responses found")
        
        # Example: Add a new response
        print("\nAdding a new test response...")
        test_data = {
            'name': 'Example User',
            'email': 'example@test.com',
            'feedback': 'This is a test response from the example script'
        }
        
        doc_id = add_survey_response(test_data)
        if doc_id:
            print(f"✅ Response added with ID: {doc_id}")
        else:
            print("❌ Failed to add response")
            
    else:
        print("❌ Failed to initialize Firebase")
        print("\nMake sure you have:")
        print("1. Created a .env file with your Firebase credentials")
        print("2. Set the required environment variables (see env_example.txt)")
        print("3. Have the correct Firebase project ID")

if __name__ == "__main__":
    main()
