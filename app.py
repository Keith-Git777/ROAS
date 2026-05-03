import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ================================
# Title (same text, cursive style)
# ================================
st.markdown(
    "<h1 style='text-align:center; font-family:cursive; font-weight:700;'>Ad Demographic Value Dashboard</h1>",
    unsafe_allow_html=True
)

st.write("Identify which demographics are most valuable to advertise to based on cost and conversion performance.")

# ================================
# Load and prepare data
# ================================
df = pd.read_csv("KAG_conversion_data.csv")

df = df.dropna()

df["CTR"] = df["Clicks"] / df["Impressions"]
df["CR"] = df["Approved_Conversion"] / df["Clicks"].replace(0, np.nan)
df["CPA"] = df["Spent"] / df["Approved_Conversion"].replace(0, np.nan)

# ================================
# Sidebar filters
# ================================
st.sidebar.header("Filters")

age_filter = st.sidebar.multiselect(
    "Age group",
    sorted(df["age"].unique()),
    default=sorted(df["age"].unique())
)

gender_filter = st.sidebar.multiselect(
    "Gender",
    sorted(df["gender"].unique()),
    default=sorted(df["gender"].unique())
)

# Interactive impressions slider:
# min = 0, max = same as before, default (start) = 150,000
min_impressions = st.sidebar.slider(
    "Minimum impressions per row",
    min_value=0,
    max_value=int(df["Impressions"].max()),
    value=150000,
    step=10000
)

df_filtered = df[
    (df["age"].isin(age_filter)) &
    (df["gender"].isin(gender_filter)) &
    (df["Impressions"] >= min_impressions)
]

# Guard against empty filter result
if df_filtered.empty:
    st.warning("No data matches the current filters. Try lowering the minimum impressions or widening age/gender selections.")
    st.stop()

# ================================
# KPIs
# ================================
st.markdown("## 📊 Key Performance Indicators")

col1, col2, col3 = st.columns(3)

overall_cpa = df["CPA"].mean()
overall_cr = df["CR"].mean()

filtered_cpa = df_filtered["CPA"].mean()
filtered_cr = df_filtered["CR"].mean()
share_conversions = df_filtered["Approved_Conversion"].sum() / df["Approved_Conversion"].sum()

col1.metric(
    "Cost per Acquisition (CPA)",
    f"${filtered_cpa:.2f}",
    delta=f"{filtered_cpa - overall_cpa:.2f}"
)

col2.metric(
    "Conversion Rate (CR)",
    f"{filtered_cr*100:.2f}%",
    delta=f"{(filtered_cr - overall_cr)*100:.2f}%"
)

col3.metric(
    "Share of Total Conversions",
    f"{share_conversions*100:.2f}%"
)

# ================================
# Chart 1 — CPA by Age × Gender (Heatmap)
# ================================
st.markdown("## 1️⃣ CPA by Age × Gender")

heatmap_data = df_filtered.groupby(["gender", "age"])["CPA"].mean().reset_index()
heatmap_pivot = heatmap_data.pivot(index="gender", columns="age", values="CPA")

heatmap_fig = px.imshow(
    heatmap_pivot,
    color_continuous_scale="RdYlGn_r",
    labels=dict(color="CPA ($)"),
)

heatmap_fig.update_layout(
    xaxis_title="Age group",
    yaxis_title="Gender",
    coloraxis_colorbar_title="CPA ($)"
)

st.plotly_chart(heatmap_fig, use_container_width=True)

# ================================
# Chart 2 — Original style: CPA by Interest Level (Line)
# ================================
st.markdown("## 2️⃣ Cost per Conversion by Interest Category")

interest_data = df_filtered.groupby("interest_level")["CPA"].mean().reset_index()
interest_data = interest_data.sort_values("interest_level")

interest_fig = px.line(
    interest_data,
    x="interest_level",
    y="CPA",
    markers=True,
    title="CPA by Interest Level"
)

interest_fig.update_layout(
    xaxis_title="Interest Level",
    yaxis_title="CPA ($)"
)

st.plotly_chart(interest_fig, use_container_width=True)

# ================================
# Chart 3 — Spend vs Conversions (Scatter)
# ================================
st.markdown("## 3️⃣ Spend vs Conversions by Demographic")

scatter_fig = px.scatter(
    df_filtered,
    x="Spent",
    y="Approved_Conversion",
    color="CPA",
    color_continuous_scale="RdYlGn_r",
    hover_data=["age", "gender", "Impressions", "interest_level"],
    title="Spend vs Approved Conversions (Color = CPA)"
)

scatter_fig.update_layout(
    xaxis_title="Spend ($)",
    yaxis_title="Approved Conversions"
)

st.plotly_chart(scatter_fig, use_container_width=True)

# ================================
# Download filtered data
# ================================
st.markdown("### 📥 Download Filtered Data")

csv_data = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download filtered dataset as CSV",
    data=csv_data,
    file_name="filtered_demographic_data.csv",
    mime="text/csv"
)

# ================================
# Detailed, prescriptive insights
# ================================
st.markdown("---")
st.header("🔍 Key Insights and Recommendations")

st.markdown("""
### 1. Demographics that consistently deliver lower CPA
From the heatmap, the segments that appear in **darker green** (for example, female groups in the mid-age ranges such as 30–39, or male groups that stay green even as you raise the minimum impressions) tend to have **lower CPA at scale**.  
These are **high-value demographics**:  
- Prioritize these segments when allocating budget  
- Test higher bids or more frequent exposure for them  
- Use tailored creatives that speak directly to these age–gender combinations

### 2. Interest levels that drive expensive conversions
In the interest-level chart, you’ll notice some interest levels sit **well above the average CPA line**, especially when the impressions filter is set high.  
These categories are **consistently more expensive per conversion**:  
- Reduce spend on the highest-CPA interest levels  
- Reallocate that budget toward mid-CPA or low-CPA interest levels  
- Consider refining targeting or creative for the worst-performing interest levels before cutting them entirely

### 3. Where spend is being wasted
In the scatter plot, look for points that are:  
- Far to the **right** (high spend)  
- But relatively **low on the y-axis** (few conversions)  
- And often colored **yellow to red** (high CPA)  

These represent demographics where you are **spending a lot but not getting proportional conversions**:  
- Lower bids or frequency for these segments  
- Move budget away from them toward the green, high-conversion clusters  
- Use them as “test only” audiences rather than core targets

### 4. How the impressions filter changes the story
As you increase the minimum impressions slider (e.g., from 0 up to 150,000 and beyond), some “star” segments disappear while others remain stable and green.  
Segments that **stay green even at high impression thresholds** are your **most reliable, scalable audiences**:  
- Treat these as your primary target demographics  
- Build campaigns specifically around them  
- Use them as a benchmark when testing new audiences
""")

st.caption(
    "These recommendations are based on patterns visible in the filtered data and should guide, not replace, ongoing testing."
)
