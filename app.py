import streamlit as st
import pandas as pd
import io
from admet_ai import ADMETModel

# Configure page layout
st.set_page_config(page_title="ADMET-AI Predictor", layout="wide", page_icon="🔬")

st.title("🔬 ADMET-AI Molecular Property Predictor")
st.write("Enter a SMILES string or upload a CSV file to predict ADMET properties.")

# Cache the model to prevent reloading on every interaction
@st.cache_resource
def load_admet_model():
    return ADMETModel()

try:
    with st.spinner("Loading ADMET-AI Model... Please wait."):
        model = load_admet_model()
    st.success("Model loaded successfully!")
    
    # ------------------ INPUT SECTION ------------------
    st.header("📥 Input Molecules")
    
    # Provide two options: Single SMILES or File Upload
    input_type = st.radio("Select input method:", ["Single SMILES", "Upload CSV/Text File"])
    
    smiles_list = []
    
    if input_type == "Single SMILES":
        smiles_input = st.text_input("Enter SMILES:", "CCO")
        if smiles_input:
            smiles_list = [smiles_input.strip()]
            
    else:
        uploaded_file = st.file_uploader("Upload CSV or TXT file (Must contain a SMILES column)", type=["csv", "txt"])
        if uploaded_file is not None:
            # Read the uploaded file
            if uploaded_file.name.endswith('.csv'):
                df_input = pd.read_csv(uploaded_file)
            else:
                df_input = pd.read_csv(uploaded_file, sep="\t")
                
            st.write("Uploaded File Preview:")
            st.dataframe(df_input.head(3))
            
            # Dropdown to select the specific SMILES column
            col_options = df_input.columns.tolist()
            smiles_col = st.selectbox("Select the SMILES column:", col_options)
            smiles_list = df_input[smiles_col].dropna().astype(str).tolist()

    # ------------------ PREDICTION SECTION ------------------
    if len(smiles_list) > 0 and st.button("Predict ADMET Properties", type="primary"):
        with st.spinner(f"Processing {len(smiles_list)} molecule(s)..."):
            
            # Generate predictions (returns a pandas DataFrame)
            preds_df = model.predict(smiles_list)
            
            st.header("📊 Prediction Results")
            
            # 1. DOWNLOAD BUTTONS (Excel & CSV)
            col1, col2 = st.columns(2)
            
            # CSV Download
            csv_data = preds_df.to_csv(index=True).encode('utf-8')
            col1.download_button(
                label="📥 Download Results as CSV",
                data=csv_data,
                file_name="admet_predictions.csv",
                mime="text/csv"
            )
            
            # Excel Download
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                preds_df.to_excel(writer, sheet_name='ADMET Predictions')
            excel_data = buffer.getvalue()
            col2.download_button(
                label="📥 Download Results as Excel",
                data=excel_data,
                file_name="admet_predictions.xlsx",
                mime="application/vnd.ms-excel"
            )
            
            # 2. DETAILED TABS (Categorized Metrics)
            st.write("---")
            st.subheader("📝 Detailed Categorized Results")
            
            display_df = preds_df.copy()
            
            # Group definitions matching ADMET-AI categories
            groups = {
                "Physicochemical": ["molecular_weight", "logP", "hydrogen_bond_acceptors", "hydrogen_bond_donors", "Lipinski"],
                "Absorption & Distribution": ["HIA", "Caco2", "BBB", "Pgp_substrate", "Pgp_inhibitor", "PPB"],
                "Metabolism": ["CYP1A2_inhibitor", "CYP2C9_inhibitor", "CYP2C19_inhibitor", "CYP2D6_inhibitor", "CYP3A4_inhibitor", "CYP2C9_substrate", "CYP2D6_substrate", "CYP3A4_substrate"],
                "Excretion": ["half_life", "clearance"],
                "Toxicity": ["hERG", "AMED", "LD50", "hepatotoxicity", "skin_sensitization"]
            }
            
            # Create organized tabs
            tabs = st.tabs(list(groups.keys()) + ["All Properties"])
            
            for i, (group_name, metrics) in enumerate(groups.items()):
                with tabs[i]:
                    st.write(f"### {group_name}")
                    # Filter and show columns that belong to the current group
                    available_metrics = [m for m in metrics if m in display_df.columns]
                    if available_metrics:
                        st.dataframe(display_df[available_metrics])
                    else:
                        st.info("Metrics for this category are available under the 'All Properties' tab.")
            
            # Show all properties in the final tab
            with tabs[-1]:
                st.write("### Complete ADMET Profile")
                st.dataframe(display_df)
                
except Exception as e:
    st.error(f"Error loading or running the model: {e}")
