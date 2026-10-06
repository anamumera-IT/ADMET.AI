import streamlit as st
import pandas as pd
from admet_ai import ADMETModel

st.set_page_config(page_title="ADMET-AI Predictor", layout="centered")

st.title("🔬 ADMET-AI Property Predictor")
st.write("SMILES string enter karein taakay ADMET properties predict ki jaa sakein.")

# Model ko cache karna taakay har click par reload na ho
@st.cache_resource
def load_admet_model():
    return ADMETModel()

try:
    with st.spinner("ADMET-AI Model load ho raha hai... isme thoda waqt lag sakta hai."):
        model = load_admet_model()
    st.success("Model kamyabi se load ho gaya!")
    
    # User Input
    smiles_input = st.text_input("Enter SMILES:", "CCO")
    
    if st.button("Predict Properties"):
        with st.spinner("Calculating..."):
            # Model prediction (Accepts a list of SMILES)
            preds_df = model.predict([smiles_input])
            
            st.subheader("📊 Prediction Results")
            st.dataframe(preds_df.T) # Transpose for easier reading
            
except Exception as e:
    st.error(f"Error loading or running the model: {e}")
