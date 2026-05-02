# app.py

# =========================
# Imports
# =========================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================
# Page config
# =========================
st.set_page_config(
    page_title="Ad Demographic Value Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================
# Data loading & cleaning
# =========================
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """Load and clean the conversion dataset."""
    df = pd.read_csv(path)

    # Basic cleaning: drop rows with missing key fields
    df = df.dropna(subset=["Impressions", "Clicks", "Spent", "Approved_Conversion"])

    # Remove rows with zero impressions to avoid divide-by-zero in CTR
    df = df[df["Impressions"] > 0]

    # Derive core metrics
    df["CTR"] = df["Clicks"] / df["Impressions"]  # Click-through rate
    df["CR"] = np.where(df["Clicks"] > 0,
                        df["Approved_Conversion"] / df["Clicks"],
                        0.0)  # Conversion rate
    df["CPA"] = np.where(df["Approved_Conversion"] > 0,
                         df["Spent"] / df["Approved_Conversion"],
                         np.nan)  # Cost per approved conversion

    # Create a combined demographic label for readability
    df["demographic"] = df["age"] + " | " + df["gender"]

    return df


df = load_data("KAG_conversion_data.csv")

# Overall metrics (for KPI deltas)
overall_spend = df["Spent"].sum()
overall_conv = df["Approved_Conversion"].sum()
overall_clicks = df["Clicks"].sum()
overall_cpa = overall_spend / overall_conv if overall_conv > 0 else np.nan
overall_cr = overall_conv / overall_clicks if overall_clicks > 0 else np.nan

# =========================
# Sidebar filters
# =========================
st.sidebar.header("Filters")

# Filter 1: Age group
age_options = sorted(df["age"].unique().tolist())
selected_ages = st.sidebar.multiselect(
    "Age group",
    options=age_options,
    default=age_options  # default: all
)

# Filter 2: Gender
gender_options = sorted(df["gender"].unique().tolist())
selected_genders = st.sidebar.multiselect(
    "Gender",
    options=gender_options,
    default=gender_options  # default: all
)

# Optional: minimum impressions slider (acts as a quality filter)
min_impressions = st.sidebar.slider(
    "Minimum impressions per row",
    min_value=int(df["Impressions"].min()),
    max_value=int(df["Impressions"].max()),
    value=int(df["Impressions"].quantile(0.25)),  # default to 25th percentile
    step=100
)

# Apply filters
df_filtered = df[
    (df["age"].isin(selected_ages)) &
    (df["gender"].isin(selected_genders)) &
    (df["Impressions"] >= min_impressions)
].copy()

# Guard against empty filter result
if df_filtered.empty:
    st.error("No data matches the current filter selection. Please adjust your filters.")
    st.stop()

# =========================
# KPIs
# =========================
st.title("📊 Which Demographic Is Most Valuable to Advertise To?")

st.caption(
    "Interactive dashboard built from real ad performance data. "
    "Use the filters on the left to explore which demographics are most and least valuable."
)

# Filtered metrics
f_spend = df_filtered["Spent"].sum()
f_conv = df_filtered["Approved_Conversion"].sum()
f_clicks = df_filtered["Clicks"].sum()

f_cpa = f_spend / f_conv if f_conv > 0 else np.nan
f_cr = f_conv / f_clicks if f_clicks > 0 else np.nan
f_ctr = df_filtered["CTR"].mean()  # average CTR across filtered rows

# Deltas vs overall (percentage difference)
def pct_delta(filtered_value, overall_value):
    if overall_value is None or np.isnan(overall_value) or overall_value == 0:
        return "N/A"
    if filtered_value is None or np.isnan(filtered_value):
        return "N/A"
    delta = (filtered_value - overall_value) / overall_value * 100
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta:.1f}% vs overall"

cpa_delta = pct_delta(f_cpa, overall_cpa)
cr_delta = pct_delta(f_cr, overall_cr)
conv_share = f_conv / overall_conv * 100 if overall_conv > 0 else np.nan
conv_share_delta = f"{conv_share:.1f}% of all conversions" if not np.isnan(conv_share) else "N/A"

# KPI layout
kpi1, kpi2, kpi3 = st.columns(3)

# KPI 1: Cost per conversion (green = good when lower)
kpi1.metric(
    label="Cost per Conversion (CPA)",
    value=f"${f_cpa:,.2f}" if not np.isnan(f_cpa) else "N/A",
    delta=cpa_delta
)

# KPI 2: Conversion Rate
kpi2.metric(
    label="Conversion Rate (CR)",
    value=f"{f_cr:.2%}" if not np.isnan(f_cr) else "N/A",
    delta=cr_delta
)

# KPI 3: Share of Total Conversions
kpi3.metric(
    label="Share of Total Conversions",
    value=conv_share_delta.split(" ")[0] if conv_share_delta != "N/A" else "N/A",
    delta=" ".join(conv_share_delta.split(" ")[1:]) if conv_share_delta != "N/A" else "N/A"
)

st.markdown("---")

# =========================
# Visualization 1: CPA by age & gender (heatmap)
# =========================
st.subheader("1️⃣ Cost per Conversion by Age & Gender")

age_gender_group = (
    df_filtered
    .groupby(["age", "gender"], as_index=False)
    .agg(
        spend=("Spent", "sum"),
        conv=("Approved_Conversion", "sum")
    )
)
age_gender_group["CPA"] = np.where(
    age_gender_group["conv"] > 0,
    age_gender_group["spend"] / age_gender_group["conv"],
    np.nan
)

heatmap_fig = px.density_heatmap(
    age_gender_group,
    x="age",
    y="gender",
    z="CPA",
    color_continuous_scale=["green", "yellow", "red"],  # green = cheaper, red = expensive
    labels={"CPA": "Cost per Conversion"},
    title="Lower CPA (green) indicates more valuable demographics"
)
heatmap_fig.update_layout(coloraxis_colorbar_title="CPA ($)")
st.plotly_chart(heatmap_fig, use_container_width=True)

# =========================
# Visualization 2: CPA by interest category
# =========================
st.subheader("2️⃣ Cost per Conversion by Interest Category")

interest_group = (
    df_filtered
    .groupby("interest", as_index=False)
    .agg(
        spend=("Spent", "sum"),
        conv=("Approved_Conversion", "sum"),
        impressions=("Impressions", "sum")
    )
)

interest_group["CPA"] = np.where(
    interest_group["conv"] > 0,
    interest_group["spend"] / interest_group["conv"],
    np.nan
)

# Sort by CPA (ascending: most valuable first)
interest_group_sorted = interest_group.sort_values("CPA", ascending=True)

bar_fig = px.bar(
    interest_group_sorted,
    x="interest",
    y="CPA",
    labels={"interest": "Interest Category", "CPA": "Cost per Conversion ($)"},
    title="Interest Categories Ranked by Cost per Conversion",
    color="CPA",
    color_continuous_scale=["green", "yellow", "red"]
)
st.plotly_chart(bar_fig, use_container_width=True)

# =========================
# Visualization 3: Spend vs Conversions by demographic
# =========================
st.subheader("3️⃣ Spend vs Conversions by Demographic")

demo_group = (
    df_filtered
    .groupby("demographic", as_index=False)
    .agg(
        spend=("Spent", "sum"),
        conv=("Approved_Conversion", "sum"),
        clicks=("Clicks", "sum")
    )
)

demo_group["CPA"] = np.where(
    demo_group["conv"] > 0,
    demo_group["spend"] / demo_group["conv"],
    np.nan
)

scatter_fig = px.scatter(
    demo_group,
    x="spend",
    y="conv",
    size="conv",
    color="CPA",
    hover_data=["demographic", "CPA"],
    labels={"spend": "Total Spend ($)", "conv": "Total Conversions"},
    title="Which Demographics Turn Spend into Conversions?",
    color_continuous_scale=["green", "yellow", "red"]
)
st.plotly_chart(scatter_fig, use_container_width=True)

# =========================
# Download filtered data
# =========================
st.markdown("### 📥 Download Filtered Data")

csv_data = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download filtered dataset as CSV",
    data=csv_data,
    file_name="filtered_demographic_data.csv",
    mime="text/csv"
)

# =========================
# Key findings (for non-technical audience)
# =========================
st.markdown("---")
st.header("Key Findings")

st.markdown(
    """
- **Some age–gender combinations deliver conversions at a much lower cost than others**, meaning ad spend is far more efficient when focused on those demographics (green cells in the heatmap).
- **Certain interest categories are consistently expensive with few conversions**, suggesting they are poor targets and should be deprioritized or tested with different creatives.
- **A small number of demographics generate a disproportionate share of total conversions**, indicating that concentrating budget on these high-value groups would likely improve overall campaign performance.
"""
)

# =========================
# Footer
# =========================
st.caption(
    "All metrics are based on historical campaign data and are intended to guide, not replace, "
    "ongoing experimentation and A/B testing."
)
