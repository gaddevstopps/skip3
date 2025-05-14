
import streamlit as st
import pandas as pd
import io
from difflib import get_close_matches

st.set_page_config(page_title="📦 Smart Skiptrace Preprocessor")

st.title("📦 Smart Skiptrace Preprocessor")
st.write("Upload your property CSV. We’ll automatically detect the address and owner fields and format it for skip tracing.")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

def fuzzy_find(possible_names, column_names):
    for name in possible_names:
        matches = get_close_matches(name, column_names, n=1, cutoff=0.6)
        if matches:
            return matches[0]
    return None

if uploaded_file:
    st.success(f"File uploaded: {uploaded_file.name}")

    try:
        df = pd.read_csv(uploaded_file)
        original_columns = df.columns.str.upper().tolist()

        # Attempt to match owner and mailing address components
        owner_field = fuzzy_find(['OWNER 1 FULL NAME', 'OWNER_NAME', 'OWNER NAME', 'OWNER1', 'PROP OWNER'], original_columns)
        house_field = fuzzy_find(['MAIL HOUSE NUMBER', 'HOUSE NUMBER', 'HOUSE NUM', 'MAILINGADDRESS1', 'ADDRESS1'], original_columns)
        street_field = fuzzy_find(['MAIL STREET NAME', 'STREET NAME', 'MAIL STREET', 'STREET'], original_columns)
        suffix_field = fuzzy_find(['MAIL STREET NAME SUFFIX', 'SUFFIX', 'ST TYPE', 'STREET TYPE'], original_columns)
        unit_field = fuzzy_find(['MAIL UNIT NUMBER', 'UNIT', 'APT', 'SUITE'], original_columns)

        if not (owner_field and house_field and street_field):
            st.error("❌ Could not detect all required fields: Owner Name, House Number, Street Name. Please check your headers.")
        else:
            # Normalize to lowercase column names for processing
            df.columns = df.columns.str.upper()
            
            # Build mailing address line 1
            df['MAILING ADDRESS LINE 1'] = (
                df[house_field].fillna('').astype(str).str.strip() + ' ' +
                df[street_field].fillna('').astype(str).str.strip() + ' ' +
                df[suffix_field].fillna('').astype(str).str.strip() if suffix_field else '' + ' ' +
                df[unit_field].fillna('').astype(str).str.strip() if unit_field else ''
            ).str.replace(r'\s+', ' ', regex=True).str.strip()

            output_df = df[[owner_field, 'MAILING ADDRESS LINE 1']]
            output_df.columns = ['OWNER 1 FULL NAME', 'MAILING ADDRESS LINE 1']

            st.write("✅ Processed preview:")
            st.dataframe(output_df.head(10))

            # Downloadable CSV
            csv = output_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download cleaned CSV",
                data=csv,
                file_name="Cleaned_For_SkipTrace.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
