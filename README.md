# Brain CT Scan Dashboard

This Streamlit-based web app provides an interactive and insightful dashboard for analyzing and visualizing brain CT scan data. It supports machine learning engineers and  researchers by offering quick visual summaries of demographics, scan acquisition parameters, pathology insights, and injury details. It simplifies the data exploration process before modeling

---

## Features

### 1. **Demographics Overview**
- **Age Distribution**: Histogram with KDE for cleaned age data (supports conversion from weeks, months, years).
- **Gender Distribution**: Bar chart of gender counts.

### 2. **Scan Acquisition**
- **Slice Thickness Count**: Categorized into 1mm, 5mm, and others with accurate filtering logic.
- **Data Source Distribution**: Comparison between data obtained from different PACS systems (Oviyam, Centricity).

### 3. **Pathology Summary**
- Visual breakdown of pathology categories such as trauma, stroke, hydrocephalus, CVJ spine, and others.

### 4. **GCS Score Comparison**
- Side-by-side comparison of **Admission GCS vs Discharge GCS** using a strip plot.

### 5. **Side of Injury**
- Distribution of injury sides (Left, Right, Bilateral) with grouped low-frequency categories.

### 6. **Additional Insights**

#### Abnormal vs Normal Findings
- Visual breakdown of cases labeled as **Abnormal** or **Normal**
- Helps identify the proportion of radiologically significant findings
- Useful for filtering out healthy scans or targeting abnormal cases for modeling

#### Pathologies Extracted
- Count of specific pathologies extracted or annotated from reports
- Useful for understanding dataset diversity and selecting labels for ML models

#### Midline Shift (Present vs None)
- Binary classification of **midline shift presence**
- Important indicator for injury severity and outcome prediction

#### Location & Brain Organ Involvement
- Horizontal bar chart of frequently involved brain regions (e.g., temporal lobe, cerebellum)
- Helps identify anatomical patterns and spatial clustering

#### Bleed Subcategory Distribution
- Visualization of hemorrhage types (e.g., **epidural**, **subdural**, **intraventricular**, etc.)
- Assists in subtype modeling and clinical stratification


---

## Deployment

This app is deployed on [Streamlit Cloud](https://braindatadashboard-gursmeep.streamlit.app/).  
The dataset is securely stored and loaded via a private `DATA_URL` using Streamlit's secret manager to prevent public access to sensitive medical data.

---

## Security Note

- **No patient-identifiable information is exposed**.
- Dataset is stored privately (not on GitHub).
- Uses Streamlit **`secrets.toml`** to manage dataset access securely.
