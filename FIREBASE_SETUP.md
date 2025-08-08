# Firebase Setup for SheSpeaks 2025 Dashboard

## Prerequisites

1. **Google Cloud Project**: You already have a Firebase project called `she-speaks-2025`
2. **Python Environment**: Make sure you have Python 3.8+ installed

## Setup Steps

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Firebase Authentication Setup

You have two options for Firebase authentication:

#### Option A: Service Account Key (Recommended for production)

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `she-speaks-2025`
3. Go to Project Settings → Service Accounts
4. Click "Generate new private key"
5. Download the JSON file
6. Set the environment variable:
   ```bash
   # Windows
   set GOOGLE_APPLICATION_CREDENTIALS=path\to\your\service-account-key.json
   
   # Linux/Mac
   export GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
   ```

#### Option B: Application Default Credentials (Easier for development)

1. Install Google Cloud CLI: https://cloud.google.com/sdk/docs/install
2. Run authentication:
   ```bash
   gcloud auth application-default login
   ```

### 3. Run the Dashboard

```bash
cd dashboard
streamlit run simple_app.py
```

## Your Firebase Configuration

Based on your project, your Firebase config is:
- **Project ID**: `she-speaks-2025`
- **Collection**: `responses` (where survey data is stored)

## Troubleshooting

### If you get authentication errors:
1. Make sure you're logged into the correct Google account
2. Verify your project ID matches: `she-speaks-2025`
3. Check that you have the necessary permissions

### If the dashboard shows no data:
1. Make sure your HTML form is actually submitting data to Firebase
2. Check the Firebase console to see if responses are being saved
3. Verify the collection name is `responses`

## Data Structure

Your survey responses are stored with this structure:
```json
{
  "year": "3rd",
  "course": "CSE", 
  "judged": "sometimes",
  "voice": "heard",
  "stepped-back": "no",
  "curfews": "sometimes",
  "boys-club": 3,
  "equal-chances": 4,
  "safe-supported": 4,
  "held-back": 2,
  "women-mentors": 5,
  "help": ["women-mentors", "late-night-access"],
  "advice": "Don't be afraid to speak up!",
  "submittedAt": "2025-01-XX..."
}
```
