import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Excel Assistant - Find New, Existing & Missing Data")

file1 = st.file_uploader("Upload File 1 (Excel/CSV)", type=["xlsx", "csv"])
file2 = st.file_uploader("Upload File 2 (Excel/CSV)", type=["xlsx", "csv"])

if file1 and file2:

    # ---------- Read files ----------
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
    st.dataframe(df1)
    st.dataframe(df2)

    # ---------- Select Primary Key ----------
    primary_key = st.selectbox("Select Primary Key Column (e.g. ID)", df1.columns)

    # ---------- Select Columns to Compare ----------
    compare_cols = st.multiselect(
        "Select columns to compare",
        [c for c in df1.columns if c != primary_key],
        default=[c for c in df1.columns if c != primary_key]
    )

    # ---------- Clean values ----------
    def clean_series(s):
        return (
            s.astype(str)
             .str.lower()
             .str.strip()
             .str.replace(r"\s+", "", regex=True)
        )

    df1_clean = df1.copy()
    df2_clean = df2.copy()

    for c in [primary_key] + compare_cols:
        df1_clean[c] = clean_series(df1_clean[c])
        df2_clean[c] = clean_series(df2_clean[c])

    # ---------- Identify ID sets ----------
    ids_file1 = set(df1_clean[primary_key])
    ids_file2 = set(df2_clean[primary_key])

    only_file1_ids = ids_file1 - ids_file2
    only_file2_ids = ids_file2 - ids_file1
    common_ids = ids_file1 & ids_file2

    # ---------- New Records ----------
    only_in_file1 = df1[df1_clean[primary_key].isin(only_file1_ids)]
    only_in_file2 = df2[df2_clean[primary_key].isin(only_file2_ids)]

    # ---------- Existing & Missing ----------
    common_rows = []
    missing_rows = []

    for pid in common_ids:
        row1 = df1_clean[df1_clean[primary_key] == pid].iloc[0]
        row2 = df2_clean[df2_clean[primary_key] == pid].iloc[0]

        mismatches = [c for c in compare_cols if row1[c] != row2[c]]

        if mismatches:
            original = df1[df1_clean[primary_key] == pid].iloc[0].copy()
            original["Mismatch_Columns"] = ", ".join(mismatches)
            missing_rows.append(original)
        else:
            common_rows.append(df1[df1_clean[primary_key] == pid].iloc[0])

    common_df = pd.DataFrame(common_rows)
    missing_df = pd.DataFrame(missing_rows)

    # ---------- Display ----------
    st.subheader("🆕 New Records (Only in File 1)")
    st.dataframe(only_in_file1)

    st.subheader("📤 Records only in File 2")
    st.dataframe(only_in_file2)

    st.subheader("✅ Existing Records (Exact Match)")
    st.dataframe(common_df)

    st.subheader("⚠️ Missing / Mismatched Data")
    st.dataframe(missing_df)

    # ---------- Download helper ----------
    def download_excel(df_dict, filename, label):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for sheet, df in df_dict.items():
                df.to_excel(writer, sheet_name=sheet, index=False)
        output.seek(0)
        st.download_button(
            label=label,
            data=output,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # ---------- Downloads ----------
    download_excel(
        {"New_Records_File1": only_in_file1, "Only_in_File2": only_in_file2},
        "new_records.xlsx",
        "⬇️ Download New Records"
    )

    download_excel(
        {"Existing_Records": common_df},
        "existing_records.xlsx",
        "⬇️ Download Existing Records"
    )

    download_excel(
        {"Missing_Data": missing_df},
        "missing_data.xlsx",
        "⬇️ Download Missing Data"
    )
