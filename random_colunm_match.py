import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

st.title("Dynamic Column Matcher with Full Preprocessing")

# Upload files
file1 = st.file_uploader("Upload first Excel/CSV file", type=["xlsx", "csv"])
file2 = st.file_uploader("Upload second Excel/CSV file", type=["xlsx", "csv"])

if file1 and file2:

    # ---------- Read file ----------
    def read_file(file, label):
        if file.name.endswith(".csv"):
            return pd.read_csv(file)
        else:
            xls = pd.ExcelFile(file)
            sheet = st.selectbox(f"Select sheet from {label}", xls.sheet_names)
            return pd.read_excel(xls, sheet_name=sheet)

    df1 = read_file(file1, "File 1")
    df2 = read_file(file2, "File 2")

    st.subheader("File Previews")
    st.write("File 1")
    st.dataframe(df1.head())
    st.write("File 2")
    st.dataframe(df2.head())

    # ---------- Clean ALL columns ----------
    def clean_dataframe(df):
        df_clean = df.copy()
        for col in df_clean.columns:
            df_clean[col] = (
                df_clean[col]
                .astype(str)
                .str.lower()
                .str.strip()
                .str.replace(r"\s+", "", regex=True)
            )
        return df_clean

    df1_clean = clean_dataframe(df1)
    df2_clean = clean_dataframe(df2)

    # ---------- Select match columns ----------
    col1 = st.selectbox("Select column from File 1 to match", df1.columns)
    col2 = st.selectbox("Select column from File 2 to match", df2.columns)

    # ---------- Fuzzy matching ----------
    threshold = st.slider("Fuzzy match threshold (%)", 50, 100, 80)

    matches = df1_clean[col1].apply(
        lambda x: process.extractOne(x, df2_clean[col2], scorer=fuzz.ratio)
    )

    matched_mask = matches.apply(lambda x: x is not None and x[1] >= threshold)
    match_count = matched_mask.sum()

    st.success(f"✅ Total matched rows: {match_count}")

    # ---------- Highlight File 1 ----------
    def highlight_file1(row):
        return ["background-color: yellow" if matched_mask[row.name] else "" for _ in row]

    st.subheader("Highlighted Matches – File 1")
    st.dataframe(df1.style.apply(highlight_file1, axis=1))

    # ---------- Highlight File 2 ----------
    matched_values_df2 = df2_clean[col2].isin(df1_clean.loc[matched_mask, col1])

    def highlight_file2(row):
        return ["background-color: yellow" if matched_values_df2[row.name] else "" for _ in row]

    st.subheader("Highlighted Matches – File 2")
    st.dataframe(df2.style.apply(highlight_file2, axis=1))

    # ---------- Save files ----------
    if st.button("Save Highlighted Files"):
        df1.to_excel("highlighted_file1.xlsx", index=False)
        df2.to_excel("highlighted_file2.xlsx", index=False)
        st.success("✅ Files saved successfully!")
