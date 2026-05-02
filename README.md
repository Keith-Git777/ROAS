An interactive Streamlit dashboard built to analyze a real-world advertising dataset and identify which demographic groups deliver the best return on ad spend.
Using age, gender, interest category, and campaign performance metrics, this app reveals which audiences are worth targeting and which consistently underperform.



-Data Loading & Cleaning
Reads the KAG_conversion_data.csv dataset using pandas

Removes invalid rows and handles missing values

Computes key marketing metrics including:

CTR (Click‑Through Rate)

CR (Conversion Rate)

CPA (Cost per Approved Conversion)

-Dynamic KPIs
Displayed at the top of the dashboard using st.metric():

Cost per Conversion (CPA)

Conversion Rate (CR)

Share of Total Conversions

-Each KPI includes:

A clear, plain‑English label

Formatted values (e.g., $12.45, 3.2%)

A delta comparison vs overall dataset performance

-Interactive Filters
Users can refine the analysis using:

1. Age group selector

2. Gender selector

3. Minimum impressions slider

(All KPIs and charts update instantly when filters change)

Three Visualizations
Each visualization directly supports the main analytical question:

1. Heatmap: CPA by Age × Gender  
Reveals which demographic combinations are most cost‑efficient.

2. Bar Chart: CPA by Interest Category  
Ranks interest groups from most to least valuable.

3. Scatter Plot: Spend vs Conversions by Demographic  
Shows which demographics convert efficiently relative to spend.

-Downloadable Filtered Dataset
A built‑in download button allows users to export the filtered data as a CSV.

-Key Findings Section
Summarizes the most important insights in plain English for non‑technical stakeholders.
