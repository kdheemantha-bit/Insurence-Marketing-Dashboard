"""
5DATA004C - Data Science Project Lifecycle
Starter Streamlit dashboard for insurance_data_aggregated.csv

This is a STARTER SKELETON, not a finished submission. You are expected to:
  - extend the visualisations and interactivity,
  - restyle it to make it your own (design & usability marks reward originality),
  - add your own insights/commentary,
  - test it against the test cases in your report, and
  - deploy it yourself via Streamlit Community Cloud.

Run locally with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- Page config ----------
st.set_page_config(
    page_title="Insurance Website Marketing Dashboard",
    layout="wide",
)

# ---------- Load data ----------
@st.cache_data
def load_data():
    df = pd.read_csv("insurance_data_aggregated.csv")
    df.columns = [c.strip() for c in df.columns]
    return df

df = load_data()

st.title("Insurance Website – Marketing Channel & Device Dashboard")
st.caption(
    "Explore how users referred by different marketing channels, on different devices, "
    "behave on the insurance company's website."
)

# ---------- Sidebar filters (FR1 / FR2) ----------
st.sidebar.header("Filters")

channels = sorted(df["Marketing Channel"].unique())
devices = sorted(df["Device Category"].unique())

selected_channels = st.sidebar.multiselect(
    "Marketing Channel", options=channels, default=channels
)
selected_devices = st.sidebar.multiselect(
    "Device Category", options=devices, default=devices
)

filtered = df[
    df["Marketing Channel"].isin(selected_channels)
    & df["Device Category"].isin(selected_devices)
]

if filtered.empty:
    st.warning("No data matches the current filters. Please adjust your selection.")
    st.stop()

# ---------- KPI row (FR3) ----------
total_users = int(filtered["Users"].sum())
total_revenue = filtered["Revenue"].sum()
total_quotes = int(filtered["TotalNumberOfInsuranceQuotes"].sum())
total_policies = int(filtered["TotalNumberOfInsurancePoliciesPurchaed"].sum())
conversion_rate = (total_policies / total_users * 100) if total_users else 0
quote_rate = (total_quotes / total_users * 100) if total_users else 0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Users", f"{total_users:,}")
k2.metric("Revenue", f"£{total_revenue:,.2f}")
k3.metric("Quotes", f"{total_quotes:,}")
k4.metric("Policies Purchased", f"{total_policies:,}")
k5.metric("Conversion Rate", f"{conversion_rate:.2f}%")

st.divider()

# ---------- Channel comparison (FR5) ----------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue by Marketing Channel")
    by_channel = (
        filtered.groupby("Marketing Channel")
        .agg(Users=("Users", "sum"), Revenue=("Revenue", "sum"))
        .reset_index()
        .sort_values("Revenue", ascending=False)
    )
    fig = px.bar(by_channel, x="Marketing Channel", y="Revenue", color="Revenue")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Conversion Rate by Marketing Channel (FR4)")
    by_channel_conv = (
        filtered.groupby("Marketing Channel")
        .apply(
            lambda g: pd.Series(
                {
                    "Users": g["Users"].sum(),
                    "Policies": g["TotalNumberOfInsurancePoliciesPurchaed"].sum(),
                }
            )
        )
        .reset_index()
    )
    by_channel_conv["Conversion Rate (%)"] = (
        by_channel_conv["Policies"] / by_channel_conv["Users"] * 100
    ).round(2)
    fig2 = px.bar(
        by_channel_conv.sort_values("Conversion Rate (%)", ascending=False),
        x="Marketing Channel",
        y="Conversion Rate (%)",
        color="Conversion Rate (%)",
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------- Device comparison (FR6) ----------
st.subheader("Performance by Device Category")
by_device = (
    filtered.groupby("Device Category")
    .agg(
        Users=("Users", "sum"),
        Revenue=("Revenue", "sum"),
        Policies=("TotalNumberOfInsurancePoliciesPurchaed", "sum"),
    )
    .reset_index()
)
by_device["Conversion Rate (%)"] = (by_device["Policies"] / by_device["Users"] * 100).round(2)
st.dataframe(by_device, use_container_width=True)

# ---------- Funnel (FR8 - optional/Could have) ----------
st.subheader("User Funnel: Users → Quotes → Policies Purchased")
funnel_df = pd.DataFrame(
    {
        "Stage": ["Users", "Quotes", "Policies Purchased"],
        "Count": [total_users, total_quotes, total_policies],
    }
)
fig3 = px.funnel(funnel_df, x="Count", y="Stage")
st.plotly_chart(fig3, use_container_width=True)

# ---------- Download filtered data (FR7 - optional/Could have) ----------
st.download_button(
    "Download filtered data as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_insurance_data.csv",
    mime="text/csv",
)

st.divider()
st.caption(
    "TODO (for you): add your own key-insight callouts, restyle colours/layout, "
    "and reference this app in your test cases (TC1–TC5)."
)
