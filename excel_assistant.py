import streamlit as st
import pandas as pd
from io import BytesIO

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Excel Assistant", layout="wide")

# ================= GLOBAL CSS =================
st.markdown("""
<style>
/* Black background */
.stApp {
    background-color: #000000 !important;
    color: #ffffff;
}

/* Remove extra padding */
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 0rem !important;
    color: #ffffff !important;
}

/* File uploader text */
section[data-testid="stFileUploader"] button,
div[data-baseweb="select"] span,
div[data-baseweb="tag"] {
    color: #ffffff !important;
    background-color: #222222 !important;
    border-radius: 6px;
}

/* Uploaded file name labels */
.file-label {
    color: #ffffff !important;
    font-weight: 700;
    font-size: 16px;
}

/* Download buttons */
.stDownloadButton button {
    background-color: #444444 !important;
    color: #ffffff !important;
    font-weight: 700;
    border-radius: 8px;
}

/* Dataframe border and header */
[data-testid="stDataFrame"] {
    border: 1px solid #555555;
    border-radius: 10px;
    color: #ffffff;
    background-color: #111111;
}

/* Make dataframe header text white */
[data-testid="stDataFrame"] thead tr th {
    color: #ffffff !important;
    background-color: #222222 !important;
}

/* Table cells text */
[data-testid="stDataFrame"] tbody tr td {
    color: #ffffff !important;
    background-color: #111111 !important;
}
/* Multiselect dropdown text white for dark theme */
div[data-baseweb="select"] span,        /* selected items */
div[data-baseweb="option"] span {       /* dropdown options */
    color: #ffffff !important;
}
/* All markdown headers and paragraphs in white */
h1, h4, p, span, div {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("""
<div class="black-section">
<h1>📊 Excel Assistant</h1>
<p>
Find <b>New</b>, <b>Existing</b>, and <b>Missing / Mismatched</b> data
between two Excel or CSV files.
</p>
</div>
""", unsafe_allow_html=True)


def read_uploaded_file(file):
    if file is None:
        return None
    return pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
# ================= FILE UPLOAD =================
file1 = st.file_uploader("📁 Upload File 1 (Excel / CSV)", type=["xlsx", "csv"], key="file1")
df1 = read_uploaded_file(file1)
if df1 is not None:
    st.dataframe(df1, use_container_width=True)
    # st.markdown(f"<div class='file-label'>📄 File 1: {file1.name}</div>", unsafe_allow_html=True)

file2 = st.file_uploader("📁 Upload File 2 (Excel / CSV)", type=["xlsx", "csv"], key="file2")
df2 = read_uploaded_file(file2)
if df2 is not None:
    st.dataframe(df2, use_container_width=True)
    # st.markdown(f"<div class='file-label'>📄 File 2: {file2.name}</div>", unsafe_allow_html=True)
# ================= READ FILES =================



# ================= COMPARISON LOGIC =================
if df1 is not None and df2 is not None:

    # Sheet selector for Excel
    def read_file(file, label):
        if file.name.endswith(".csv"):
            return pd.read_csv(file)
        xls = pd.ExcelFile(file)
        sheet = st.selectbox(f"Select sheet from {label}", xls.sheet_names)
        return pd.read_excel(xls, sheet_name=sheet)

    df1 = read_file(file1, "File 1")
    df2 = read_file(file2, "File 2")

    primary_key = st.selectbox("Primary Key Column", df1.columns)

    compare_cols = st.multiselect(
        "Columns to Compare",
        [c for c in df1.columns if c != primary_key],
        default=[c for c in df1.columns if c != primary_key]
    )

    def clean_series(s):
        return s.astype(str).str.lower().str.strip().str.replace(r"\s+", "", regex=True)

    df1_clean, df2_clean = df1.copy(), df2.copy()
    for c in [primary_key] + compare_cols:
        df1_clean[c] = clean_series(df1_clean[c])
        df2_clean[c] = clean_series(df2_clean[c])

    ids1, ids2 = set(df1_clean[primary_key]), set(df2_clean[primary_key])
    only_file1_ids, only_file2_ids, common_ids = ids1 - ids2, ids2 - ids1, ids1 & ids2

    only_in_file1 = df1[df1_clean[primary_key].isin(only_file1_ids)]
    only_in_file2 = df2[df2_clean[primary_key].isin(only_file2_ids)]

    common_rows, missing_rows = [], []

    for pid in common_ids:
        r1 = df1_clean[df1_clean[primary_key] == pid].iloc[0]
        r2 = df2_clean[df2_clean[primary_key] == pid].iloc[0]
        mismatches = [c for c in compare_cols if r1[c] != r2[c]]

        if mismatches:
            row = df1[df1_clean[primary_key] == pid].iloc[0].copy()
            row["Mismatch_Columns"] = ", ".join(mismatches)
            missing_rows.append(row)
        else:
            common_rows.append(df1[df1_clean[primary_key] == pid].iloc[0])

    common_df = pd.DataFrame(common_rows)
    missing_df = pd.DataFrame(missing_rows)

    st.markdown("<h4>🆕 Only in File 1</h4>", unsafe_allow_html=True)
    st.dataframe(only_in_file1, use_container_width=True)

    st.markdown("<h4>📤 Only in File 2</h4>", unsafe_allow_html=True)
    st.dataframe(only_in_file2, use_container_width=True)

    st.markdown("<h4>✅ Existing Records</h4>", unsafe_allow_html=True)
    st.dataframe(common_df, use_container_width=True)

    st.markdown("<h4>⚠️ Mismatched Data</h4>", unsafe_allow_html=True)
    st.dataframe(missing_df, use_container_width=True)

    # ================= DOWNLOAD =================
    def download_excel(df_dict, filename, label):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for sheet, df in df_dict.items():
                df.to_excel(writer, sheet_name=sheet, index=False)
        output.seek(0)
        st.download_button(label, output, filename)

    c1, c2, c3 = st.columns(3)
    with c1:
        download_excel(
            {"New_Records_File1": only_in_file1, "Only_in_File2": only_in_file2},
            "new_records.xlsx", "⬇️ New Records"
        )
    with c2:
        download_excel(
            {"Existing_Records": common_df},
            "existing_records.xlsx", "⬇️ Existing Records"
        )
    with c3:
        download_excel(
            {"Missing_Data": missing_df},
            "missing_data.xlsx", "⬇️ Mismatched Data"
        )
