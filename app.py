import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================================
# Title (Fancy Cursive Unicode Style)
# =========================================
st.markdown(
    "<h1 style='text-align:center; font-size:48px; font-family:cursive;'>𝓐𝓭 𝓓𝓮𝓶𝓸𝓰𝓻𝓪𝓹𝓱𝓲𝓬 𝓥𝓪𝓵𝓾𝓮 𝓓𝓪𝓼𝓱𝓫𝓸𝓪𝓻𝓭</h1>",
    unsafe_allow_html=True
)

st.write("### Identify which demographics deliver the strongest advertising ROI.")

# =========================================
# Load Data
# =========================================
df = pd.read_csv("KAG_conversion_data.csv")

# Clean data
df = df.dropna()
df["CTR"] = df["Clicks"] / df["Impressions"]
df["CR"] = df["Approved_Conversion"] / df["Clicks"].replace(0, np.nan)
df["CPA"] = df["Spent"] / df["Approved_Conversion"].replace(0, np.nan)

# =========================================
# Sidebar Filters
# =========================================
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

# Minimum impressions slider (STARTS AT 150,000)
min_impressions = st.sidebar.slider(
    "Minimum impressions per row",
    min_value=150000,
    max_value=int(df["Impressions"].max()),
    value=150000,
    step=50000
)

# Apply filters
df_filtered = df[
    (df["age"].isin(age_filter)) &
    (df["gender"].isin(gender_filter)) &
    (df["Impressions"] >= min_impressions)
]

# =========================================
# KPIs
# =========================================
st.markdown("## 📊 Key Performance Indicators")

col1, col2, col3 = st.columns(3)

overall_cpa = df["CPA"].mean()
overall_cr = df["CR"].mean()

col1.metric("Cost per Acquisition (CPA)", f"${df_filtered['CPA'].mean():.2f}",
            delta=f"{df_filtered['CPA'].mean() - overall_cpa:.2f}")

col2.metric("Conversion Rate (CR)", f"{df_filtered['CR'].mean()*100:.2f}%",
            delta=f"{(df_filtered['CR'].mean() - overall_cr)*100:.2f}%")

col3.metric("Share of Total Conversions",
            f"{(df_filtered['Approved_Conversion'].sum() / df['Approved_Conversion'].sum())*100:.2f}%")

# =========================================
# Chart 1 — Heatmap (CPA by Age × Gender)
# =========================================
st.markdown("## 1️⃣ CPA by Age × Gender")

heatmap_data = df_filtered.groupby(["gender", "age"])["CPA"].mean().reset_index()

heatmap_fig = px.imshow(
    heatmap_data.pivot(index="gender", columns="age", values="CPA"),
    color_continuous_scale="RdYlGn_r",
    labels=dict(color="CPA ($)"),
)

st.plotly_chart(heatmap_fig, use_container_width=True)

# =========================================
# Chart 2 — Improved Bar Chart (Interest Category Ranking)
# =========================================
st.markdown("## 2️⃣ Cost per Conversion by Interest Category")

interest_data = df_filtered.groupby("interest_level")["CPA"].mean().reset_index()
interest_data = interest_data.sort_values("CPA")

bar_fig = px.bar(
    interest_data,
    x="interest_level",
    y="CPA",
    color="CPA",
    color_continuous_scale="RdYlGn_r",
    title="Interest Categories Ranked by CPA (Lower = Better)",
)

bar_fig.update_layout(xaxis_title="Interest Category", yaxis_title="CPA ($)")
st.plotly_chart(bar_fig, use_container_width=True)

# =========================================
# Chart 3 — Scatter Plot (Spend vs Conversions)
# =========================================
st.markdown("## 3️⃣ Spend vs Conversions by Demographic")

scatter_fig = px.scatter(
    df_filtered,
    x="Spent",
    y="Approved_Conversion",
    color="CPA",
    color_continuous_scale="RdYlGn_r",
    hover_data=["age", "gender", "Impressions"],
    title="Spend vs Conversions (Color = CPA)",
)

st.plotly_chart(scatter_fig, use_container_width=True)

# =========================================
# Download Button
# =========================================
st.markdown("### 📥 Download Filtered Data")

csv_data = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download filtered dataset as CSV",
    data=csv_data,
    file_name="filtered_demographic_data.csv",
    mime="text/csv"
)

# =========================================
# Insights Section (Improved)
# =========================================
st.markdown("---")
st.header("🔍 Key Insights")

st.markdown("""
### **1. High-volume demographics reveal true profitability**
When low-impression noise is removed, **older female segments consistently show lower CPA**, indicating they convert reliably at scale. This suggests they are a strong target for budget allocation.

### **2. Interest categories vary dramatically in cost-efficiency**
The improved bar chart shows clear separation between interest groups. Several categories have **CPA 2–3× higher** than others, meaning reallocating spend away from poor performers can significantly improve ROI.

### **3. Spend vs conversion efficiency exposes wasted budget**
The scatter plot highlights demographics that consume large spend but produce few conversions. These groups represent **high-cost inefficiencies** and should be deprioritized in future campaigns.

### **4. Filters dramatically change the story**
Raising the minimum impressions threshold removes misleading outliers and reveals which demographics perform well **consistently**, not just by chance.
""")

st.caption("All insights are based on historical campaign data and should guide — not replace — ongoing experimentation.")
