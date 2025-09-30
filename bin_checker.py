import streamlit as st
import pandas as pd

# === Page config ===
st.set_page_config(page_title="BIN Checker", layout="wide")

st.title("🔍 BIN Checker & Filter Tool")

# === Upload files ===
st.sidebar.header("📂 Upload Your Files")

bin_db_file = st.sidebar.file_uploader("Upload BIN Database (CSV)", type="csv")
bin_list_file = st.sidebar.file_uploader("Upload BIN List to Check (CSV)", type="csv")

# === Load files ===
if bin_db_file and bin_list_file:
    bin_db = pd.read_csv(bin_db_file, dtype=str)
    bin_list = pd.read_csv(bin_list_file, dtype=str)

    # Normalize columns
    bin_db.columns = bin_db.columns.str.strip()
    bin_db['BIN'] = bin_db['BIN'].astype(str).str.strip().str[:6]
    bin_list.columns = ['BIN']
    bin_list['BIN'] = bin_list['BIN'].astype(str).str.strip().str[:6]

    # Merge data
    merged = bin_list.merge(bin_db, on='BIN', how='left')

    # Sidebar filters
    st.sidebar.subheader("🔧 Filters")

    issuer_filter = st.sidebar.multiselect("Issuer / Bank", options=sorted(merged['Issuer'].dropna().unique()))
    brand_filter = st.sidebar.multiselect("Brand", options=sorted(merged['Brand'].dropna().unique()))
    type_filter = st.sidebar.multiselect("Type", options=sorted(merged['Type'].dropna().unique()))
    country_filter = st.sidebar.multiselect("Country", options=sorted(merged['CountryName'].dropna().unique()))

    # Apply filters
    filtered = merged.copy()
    if issuer_filter:
        filtered = filtered[filtered['Issuer'].isin(issuer_filter)]
    if brand_filter:
        filtered = filtered[filtered['Brand'].isin(brand_filter)]
    if type_filter:
        filtered = filtered[filtered['Type'].isin(type_filter)]
    if country_filter:
        filtered = filtered[filtered['CountryName'].isin(country_filter)]

    # Display results
    st.subheader("✅ Filtered BIN Matches")
    st.write(f"Showing {len(filtered)} out of {len(merged)} BINs")
    st.dataframe(filtered)

    # Download option
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Results as CSV",
        data=csv,
        file_name='filtered_bins.csv',
        mime='text/csv'
    )

    # Search individual BIN
    st.subheader("🔎 Lookup a BIN")
    bin_input = st.text_input("Enter a BIN to search (first 6 digits)")
    if bin_input:
        bin_input = bin_input.strip()[:6]
        match = bin_db[bin_db['BIN'] == bin_input]
        if not match.empty:
            st.success("BIN Found:")
            st.dataframe(match)
        else:
            st.warning("BIN not found in database.")

else:
    st.info("Please upload both BIN database and BIN list to begin.")
