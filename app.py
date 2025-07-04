import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🧠 Hospital CT Scan Patient Dashboard")

# Load the sample data
df = pd.read_csv("sample_ct_data.csv")

# Gender filter
gender = st.sidebar.selectbox("Filter by Gender", options=["All", "Male", "Female"])
if gender != "All":
    df = df[df["Gender"] == gender]

st.header("1. Demographics")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Age Distribution")
    fig1, ax1 = plt.subplots()
    sns.histplot(df["Age"], bins=15, kde=True, ax=ax1)
    st.pyplot(fig1)

with col2:
    st.subheader("Gender Distribution")
    st.bar_chart(df["Gender"].value_counts())

st.markdown("---")
st.header("2. Scan Acquisition")

col3, col4 = st.columns(2)

with col3:
    st.subheader("Slice Thickness Count")
    slice_counts = df[[
        'Slice Thickness (in mm) - 1mm',
        'Slice Thickness (in mm) - 5mm',
        'Slice Thickness (in mm) - others'
    ]].notnull().sum()
    st.bar_chart(slice_counts)

with col4:
    st.subheader("Data Source Distribution")
    source_counts = {
        "Oviyam": df["Data Obtained from - Oviyam"].sum(),
        "Centricity": df["Data Obtained from - Centricity"].sum()
    }
    st.bar_chart(pd.Series(source_counts))

st.markdown("---")
st.header("3. Pathology Summary")

pathology_cols = [
    "Pathology- Trauma/ Head Injury",
    "Pathology- stroke"
]
st.bar_chart(df[pathology_cols].sum())

st.markdown("---")
st.header("4. GCS Score Comparison")

fig2, ax2 = plt.subplots()
sns.boxplot(data=df[["Admission GCS - Score", "Discharge GCS - Score"]], ax=ax2)
st.pyplot(fig2)

st.markdown("---")
st.header("5. Injury Details")

col5, col6 = st.columns(2)

with col5:
    st.subheader("Side of Injury")
    st.bar_chart(df["Side Present in (L/R)"].value_counts())

with col6:
    st.subheader("Injury Volume Distribution")
    fig3, ax3 = plt.subplots()
    sns.histplot(df["Volume in mm"], bins=20, ax=ax3)
    st.pyplot(fig3)

st.markdown("---")
st.subheader("📋 Raw Data (filtered)")
st.dataframe(df)
