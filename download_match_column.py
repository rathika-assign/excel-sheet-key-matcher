import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz
from io import BytesIO

st.title("Dynamic Column Matcher with Highlighted Download")

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

    st.subheader("File Preview")
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

    # ---------- Select columns ----------
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

    # ---------- UI Highlight ----------
    def highlight_ui(row):
        return ["background-color: yellow" if matched_mask[row.name] else "" for _ in row]

    st.subheader("Matched Rows (Highlighted)")
    st.dataframe(df1.style.apply(highlight_ui, axis=1))

    # ---------- Create matched + highlighted Excel ----------
    matched_df = df1.loc[matched_mask].copy()

    def highlight_excel(row):
        return ["background-color: yellow" for _ in row]

    styled_df = matched_df.style.apply(highlight_excel, axis=1)

    output = BytesIO()
    styled_df.to_excel(
        output,
        index=False,
        engine="openpyxl"
    )
    output.seek(0)

    # ---------- Download ----------
    st.subheader("Download Result")

    st.download_button(
        label="⬇️ Download Matched Highlighted File",
        data=output,
        file_name="matched_highlighted.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
