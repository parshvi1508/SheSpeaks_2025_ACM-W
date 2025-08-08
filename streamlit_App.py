import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

# Initialize Firebase (only once)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")  # Make sure this file is in your project directory
    firebase_admin.initialize_app(cred)

# Firestore DB
db = firestore.client()

# Streamlit UI
st.set_page_config(page_title="She Speaks 2025 Responses", layout="wide")
st.title("📝 She Speaks 2025 - Survey Form Responses")

@st.cache_data(ttl=300)
def fetch_responses():
    docs = db.collection("responses").stream()
    data = []
    for doc in docs:
        entry = doc.to_dict()
        entry["id"] = doc.id
        data.append(entry)
    return pd.DataFrame(data)

# Load and display
df = fetch_responses()

if df.empty:
    st.info("No survey responses found yet.")
else:
    st.success(f"Fetched {len(df)} responses.")
    st.dataframe(df, use_container_width=True)
    with st.expander("📥 Download responses as CSV"):
        st.download_button("Download CSV", df.to_csv(index=False), file_name="she_speaks_responses.csv")

