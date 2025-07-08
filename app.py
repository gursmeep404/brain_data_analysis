import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re
import requests
from io import BytesIO

# Load data
url = st.secrets["DATA_URL"]
response = requests.get(url)
df = pd.read_excel(BytesIO(response.content), engine="openpyxl")


st.set_page_config(layout="wide")
st.title("Brain CT Scan Dashboard")



# Clean Data
# df = pd.read_excel("data/brain_dataset_final.xlsx", engine='openpyxl')
df.columns = df.columns.str.strip()  
# Clean age column
def clean_age(val):
    if pd.isnull(val):
        return None
    if isinstance(val, (int, float)):
        return float(val)

    val = str(val).strip().lower()

    if 'w' in val:
        try:
            return float(val.replace('w', '').replace('weeks', '')) / 52
        except:
            return None
    if 'm' in val and 'mo' not in val:
        try:
            return float(val.replace('m', '').replace('months', '')) / 12
        except:
            return None
    if 'y' in val:
        try:
            return float(val.replace('yrs', '').replace('years', '').replace('y', '').strip())
        except:
            return None
    try:
        return float(val)
    except:
        return None

df["Age_clean"] = df["Age"].apply(clean_age)


# 1. Demographics
st.header("1. Demographics")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Age Distribution")
    fig1, ax1 = plt.subplots()
    sns.histplot(df["Age_clean"].dropna(), bins=15, kde=True, ax=ax1, color="#BE4B4B")
    st.pyplot(fig1)

with col2:
    st.subheader("Gender Distribution")

    gender_counts = df["Gender"].value_counts()

    fig2, ax2 = plt.subplots(figsize=(3.5, 2.5))  
    colors = ["#F0B55D","#FA99D5", "#99B3FA"] 
    bars = ax2.bar(gender_counts.index, gender_counts.values, color=colors)

    ax2.set_ylabel("Count", fontsize=9)
    ax2.set_xlabel("")
    ax2.set_title("Gender Distribution", fontsize=10, color="#2F4F4F")
    ax2.tick_params(axis='both', labelsize=8)

    fig2.tight_layout()
    st.pyplot(fig2)



# 2. Scan Acquisition
st.markdown("---")
st.header("2. Scan Acquisition")

col3, col4 = st.columns(2)

with col3:
    st.subheader("Slice Thickness Count")

    slice_cols = {
        '1mm': 'Slice Thickness (in mm) - 1mm',
        '5mm': 'Slice Thickness (in mm) - 5mm',
        'others': 'Slice Thickness (in mm) - others'
    }

    if all(col in df.columns for col in slice_cols.values()):
        count_1mm = (df[slice_cols['1mm']] == 1).sum()
        count_5mm = (df[slice_cols['5mm']] == 1).sum()
        count_others = df[slice_cols['others']].apply(lambda x: pd.notnull(x) and x != 0).sum()

        slice_counts = pd.Series({
            '1mm': count_1mm,
            '5mm': count_5mm,
            'others': count_others
        })

        colors = sns.color_palette("coolwarm", len(slice_counts)).as_hex()
        fig, ax = plt.subplots()
        slice_counts.plot(kind="bar", color=colors, ax=ax)

        ax.set_title("Slice Thickness Count")
        ax.set_ylabel("Count")
        ax.tick_params(axis='x', labelrotation=0, labelsize=8)

        st.pyplot(fig)
    else:
        st.warning("Some slice thickness columns are missing.")


with col4:
    st.subheader("Data Source Distribution")
    source_columns = [
        "Data Obtained from - Oviyam",
        "Data Obtained from - Centricity"
    ]

    source_counts = {}
    for col in source_columns:
        if col in df.columns:
            numeric_col = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            source_counts[col.split(" - ")[-1]] = numeric_col.sum()

    if source_counts:
        # Create bar chart with custom colors
        source_series = pd.Series(source_counts)
        fig, ax = plt.subplots(figsize=(3.5, 2.5))
        bar_colors = [ "#AF4571", "#6A5ACD"]
        ax.bar(source_series.index, source_series.values, color=bar_colors)

        ax.set_title("Data Source Distribution", fontsize=10, color="#2F4F4F")
        ax.set_ylabel("Count", fontsize=9)
        ax.set_xlabel("")
        ax.tick_params(axis='x', labelrotation=10, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
        fig.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("Data source columns not found.")



# 3. Pathology Summary
st.markdown("---")
col_path = st.columns([0.2, 0.6, 0.2])[1]  

with col_path:
    st.markdown("<h2 style='color:#4B8BBE;'>3. Pathology Summary</h2>", unsafe_allow_html=True)

    pathology_cols = [
        "Pathology- Trauma/ Head Injury",
        "Pathology- stroke",
        "Pathology - Hydrocephalus",
        "Pathology - CVJ Spine",
        "Pathology - Others"
    ]

    valid_pathologies = [col for col in pathology_cols if col in df.columns]

    if valid_pathologies:
        counts = df[valid_pathologies].sum()
        fig, ax = plt.subplots(figsize=(3.5, 2.5))  

        bars = ax.bar(counts.index, counts.values, 
                      color=sns.color_palette("Set2", len(counts)).as_hex(), width=0.6)

        ax.set_title("Pathology Summary", fontsize=10, color="#2F4F4F")
        ax.set_ylabel("Count", fontsize=8)
        ax.set_xlabel("")
        ax.tick_params(axis='x', labelrotation=0, labelsize=3)
        ax.tick_params(axis='y', labelsize=4)

        fig.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("Pathology columns not found.")


# GCS + Injury Details side by side
st.markdown("---")
st.header("4 & 5. GCS vs Injury Details")

col5, col6 = st.columns(2)

with col5:
    st.subheader("GCS Score Comparison")

    def extract_score(value):
        if isinstance(value, str):
            match = re.search(r'=(\d+)', value)
            if match:
                return int(match.group(1))
        try:
            return float(value)  
        except:
            return None

    admission_col = "Admission GCS  - Score"
    discharge_col = "Discharge GCS - Score"

    if all(col in df.columns for col in [admission_col, discharge_col]):
        df["Admission GCS"] = df[admission_col].apply(extract_score)
        df["Discharge GCS"] = df[discharge_col].apply(extract_score)

        gcs_df = df[["Admission GCS", "Discharge GCS"]].dropna()
        gcs_melted = gcs_df.melt(var_name="Stage", value_name="GCS Score")

        fig, ax = plt.subplots(figsize=(4, 3))
        sns.stripplot(x="Stage", y="GCS Score", data=gcs_melted, jitter=True, size=6, ax=ax, palette="Set2")
        ax.set_title("GCS: Admission vs Discharge")
        st.pyplot(fig)
    else:
        st.warning("Required GCS score columns are missing.")

with col6:
    st.subheader("Side of Injury")

    column_name = "Side Present in (L/R)"
    if column_name in df.columns:
        side_counts = df[column_name].value_counts()
        threshold = 5  

        # Group low-frequency categories
        side_counts_grouped = side_counts.copy()
        side_counts_grouped["Others"] = side_counts[side_counts < threshold].sum()
        side_counts_grouped = side_counts_grouped[side_counts_grouped >= threshold]

        fig, ax = plt.subplots(figsize=(4, 3))
        side_counts_grouped.plot(kind="bar", color="#64E4ED", ax=ax)

        ax.set_title("Side of Injury (Grouped)", fontsize=10, color="#2F4F4F")
        ax.set_ylabel("Count", fontsize=8)
        ax.tick_params(axis='x', labelrotation=30, labelsize=7)
        ax.tick_params(axis='y', labelsize=7)

        fig.tight_layout()
        st.pyplot(fig)
    else:
        st.warning(f"Column '{column_name}' not found.")



# 6. Additional Brain CT Insights
st.markdown("---")
st.header("6. Brain CT Insights from Radiologist's notes")

col_a1, col_a2 = st.columns(2)

# 6.1 Abnormal/Normal Classification
with col_a1:
    st.subheader("Abnormal vs Normal")
    if "Abnormal/Normal" in df.columns:
        status_counts = df["Abnormal/Normal"].value_counts()
        fig, ax = plt.subplots(figsize=(3.5, 2.5))
        colors = ["#FF9999", "#99FF99", "#99D6FF"]
        ax.pie(status_counts, labels=status_counts.index, autopct="%1.1f%%", colors=colors, startangle=140)
        ax.axis("equal")
        st.pyplot(fig)
    else:
        st.warning("Column 'Abnormal/Normal' not found.")

# 6.2 Midline Shift
with col_a2:
    st.subheader("Midline Shift Status")
    if "Midline Shift" in df.columns:
        shift_counts = df["Midline Shift"].astype(str).str.strip().str.lower().value_counts()
        fig, ax = plt.subplots(figsize=(3.5, 2.5))
        shift_counts.plot(kind="bar", color=[ "#A78CF1","#F785C3","#E3E566" ], ax=ax)
        ax.set_ylabel("Count")
        ax.set_title("Midline Shift Presence")
        ax.tick_params(axis='x', labelrotation=0, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
        st.pyplot(fig)
    else:
        st.warning("Column 'Midline Shift' not found.")


st.markdown("---")
st.header("7. Pathologies & Anatomical Location")

col_b1, col_b2 = st.columns(2)

# 7.1 Pathologies Extracted
with col_b1:
    st.subheader("Pathologies Extracted")
    if "Pathologies Extracted" in df.columns:
        extracted = df["Pathologies Extracted"].dropna()
        extracted_counts = extracted.value_counts().head(10)
        fig, ax = plt.subplots(figsize=(4, 3))
        sns.barplot(y=extracted_counts.index, x=extracted_counts.values, palette="magma", ax=ax)
        ax.set_title("Top Pathologies Extracted")
        ax.set_xlabel("Count")
        ax.set_ylabel("")
        st.pyplot(fig)
    else:
        st.warning("Column 'Pathologies Extracted' not found.")

# Location & Brain Organ Plot
with col_b2:
    st.subheader("Location & Brain Organ (Filtered)")
    if "Location & Brain Organ" in df.columns:
        location_cleaned = df["Location & Brain Organ"].astype(str).str.strip().str.lower()
        location_counts = location_cleaned[location_cleaned != "none"].value_counts().head(10)

        fig, ax = plt.subplots(figsize=(4, 3))
        sns.barplot(y=location_counts.index, x=location_counts.values, palette="viridis", ax=ax)
        ax.set_title("Top Brain Locations")
        ax.set_xlabel("Count")
        ax.set_ylabel("")
        st.pyplot(fig)
    else:
        st.warning("Column 'Location & Brain Organ' not found.")


st.markdown("---")
st.header("8. Bleed Subcategory")

if "Bleed Subcategory" in df.columns:
    bleed_counts = df["Bleed Subcategory"].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(5, 3))
    sns.barplot(x=bleed_counts.values, y=bleed_counts.index, palette="coolwarm", ax=ax)
    ax.set_title("Common Bleed Subcategories")
    ax.set_xlabel("Count")
    ax.set_ylabel("")
    st.pyplot(fig)
else:
    st.warning("Column 'Bleed Subcategory' not found.")


# 6. Raw Data Table
# st.markdown("---")
# st.subheader("Raw Data (filtered)")
# st.dataframe(df)


# 7. Debug: Show Problematic Ages
st.markdown("---")
st.caption("Non-numeric Age entries (skipped in plot):")
bad_ages = df[df["Age_clean"].isnull() & df["Age"].notnull()]
st.write(bad_ages["Age"].unique())
