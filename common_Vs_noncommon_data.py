import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Excel Assistant - Compare Common & Non-Common Data")

# Upload files
file1 = st.file_uploader("Upload File 1 (Excel/CSV)", type=["xlsx", "csv"])
file2 = st.file_uploader("Upload File 2 (Excel/CSV)", type=["xlsx", "csv"])

if file1 and file2:

    # Read files
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

    # Columns to compare
    cols_to_compare = st.multiselect(
        "Select columns to compare",
        df1.columns.tolist(),
        default=df1.columns.tolist()
    )

    if cols_to_compare:
        # ---------- Clean columns ----------
        def clean_df(df, cols):
            df_clean = df.copy()
            for c in cols:
                df_clean[c] = (
                    df_clean[c]
                    .astype(str)
                    .str.lower()
                    .str.strip()
                    .str.replace(r"\s+", "", regex=True)
                )
            return df_clean

        df1_clean = clean_df(df1, cols_to_compare)
        df2_clean = clean_df(df2, cols_to_compare)

        # ---------- Composite key ----------
        df1_clean['key'] = df1_clean[cols_to_compare].agg('|'.join, axis=1)
        df2_clean['key'] = df2_clean[cols_to_compare].agg('|'.join, axis=1)

        # ---------- Non-Common Records ----------
        only_in_file1 = df1[~df1_clean['key'].isin(df2_clean['key'])]
        only_in_file2 = df2[~df2_clean['key'].isin(df1_clean['key'])]

        st.subheader("Records only in File 1")
        st.dataframe(only_in_file1)

        st.subheader("Records only in File 2")
        st.dataframe(only_in_file2)

        # ---------- Common Records ----------
        common_records = df1[df1_clean['key'].isin(df2_clean['key'])]
        st.subheader("Common Records")
        st.dataframe(common_records)

        # ---------- Download Non-Common Records ----------
        output_non_common = BytesIO()
        with pd.ExcelWriter(output_non_common, engine="openpyxl") as writer:
            only_in_file1.to_excel(writer, sheet_name="Only_in_File1", index=False)
            only_in_file2.to_excel(writer, sheet_name="Only_in_File2", index=False)
        output_non_common.seek(0)

        st.download_button(
            label="⬇️ Download Non-Common Records",
            data=output_non_common,
            file_name="non_common_records.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # ---------- Download Common Records ----------
        output_common = BytesIO()
        with pd.ExcelWriter(output_common, engine="openpyxl") as writer:
            common_records.to_excel(writer, sheet_name="Common_Records", index=False)
        output_common.seek(0)

        st.download_button(
            label="⬇️ Download Common Records",
            data=output_common,
            file_name="common_records.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
