import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Website Traffic Sources Dashboard",
    layout="wide",
    page_icon="📊"
)

@st.cache_data
def load_data():
    df = pd.read_csv("amazon-web-traffic-dataset.csv")
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    numeric_cols = [
        "Avg Session Duration",
        "Bounce Rate",
        "Conversions",
        "New Users",
        "Page Views",
        "Returning Users",
        "Unique Page Views",
        "Average time on home page (min)"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Month"] = df["Timestamp"].dt.to_period("M").astype(str)
    df["Hour"] = df["Timestamp"].dt.hour
    df["Conversion Rate"] = (df["Conversions"] / df["Page Views"]) * 100
    df["Engagement Score"] = (
        df["Avg Session Duration"] * 0.4
        + (100 - df["Bounce Rate"]) * 0.3
        + (df["Average time on home page (min)"] * 10) * 0.3
    )

    return df

df = load_data()

st.markdown(
    """
    <h1 style='text-align: center; color: #1f4e79;'>
        Website Traffic Sources Analysis Dashboard
    </h1>
    <p style='text-align: center; font-size:18px; color: gray;'>
        Explore traffic sources, conversions, user behavior, engagement, and performance trends
    </p>
    """,
    unsafe_allow_html=True
)

st.sidebar.header("Dashboard Filters")

selected_sources = st.sidebar.multiselect(
    "Select Traffic Source",
    options=sorted(df["Source"].dropna().unique()),
    default=sorted(df["Source"].dropna().unique())
)

selected_countries = st.sidebar.multiselect(
    "Select Country",
    options=sorted(df["Country"].dropna().unique()),
    default=sorted(df["Country"].dropna().unique())
)

selected_devices = st.sidebar.multiselect(
    "Select Device Category",
    options=sorted(df["Device Category"].dropna().unique()),
    default=sorted(df["Device Category"].dropna().unique())
)

selected_websites = st.sidebar.multiselect(
    "Select Website",
    options=sorted(df["Website"].dropna().unique()),
    default=sorted(df["Website"].dropna().unique())
)

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

selected_date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

filtered_df = df[
    df["Source"].isin(selected_sources) &
    df["Country"].isin(selected_countries) &
    df["Device Category"].isin(selected_devices) &
    df["Website"].isin(selected_websites)
].copy()

if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
    start_date = pd.to_datetime(selected_date_range[0])
    end_date = pd.to_datetime(selected_date_range[1])
    filtered_df = filtered_df[
        (filtered_df["Date"] >= start_date) &
        (filtered_df["Date"] <= end_date)
    ]

if filtered_df.empty:
    st.warning("No data found for the selected filters.")
    st.stop()

total_page_views = int(filtered_df["Page Views"].sum())
total_conversions = int(filtered_df["Conversions"].sum())
avg_bounce_rate = round(filtered_df["Bounce Rate"].mean(), 2)
avg_session_duration = round(filtered_df["Avg Session Duration"].mean(), 2)
conversion_rate = round((filtered_df["Conversions"].sum() / filtered_df["Page Views"].sum()) * 100, 2)

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Total Page Views", f"{total_page_views:,}")
k2.metric("Total Conversions", f"{total_conversions:,}")
k3.metric("Avg Bounce Rate", f"{avg_bounce_rate}%")
k4.metric("Avg Session Duration", f"{avg_session_duration} sec")
k5.metric("Conversion Rate", f"{conversion_rate}%")

st.markdown("---")

trend_df = filtered_df.groupby("Date", as_index=False)[["Page Views", "Conversions", "New Users"]].sum()
trend_df = trend_df.sort_values("Date")

fig_trend = px.line(
    trend_df,
    x="Date",
    y=["Page Views", "Conversions", "New Users"],
    markers=True,
    title="Traffic and Conversion Trend Over Time"
)
st.plotly_chart(fig_trend, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    source_summary = filtered_df.groupby("Source", as_index=False)[["Page Views", "Conversions", "New Users"]].sum()
    source_summary = source_summary.sort_values("Page Views", ascending=False)

    fig_source = px.bar(
        source_summary,
        x="Source",
        y="Page Views",
        color="Conversions",
        text_auto=True,
        title="Traffic Source Performance"
    )
    st.plotly_chart(fig_source, use_container_width=True)

with col2:
    source_quality = filtered_df.groupby("Source", as_index=False)[["Bounce Rate", "Avg Session Duration"]].mean()

    fig_quality = px.scatter(
        source_quality,
        x="Bounce Rate",
        y="Avg Session Duration",
        color="Source",
        size_max=40,
        hover_name="Source",
        title="Traffic Source Quality Analysis"
    )
    st.plotly_chart(fig_quality, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    device_summary = filtered_df.groupby("Device Category", as_index=False)[["Page Views", "Conversions"]].sum()

    fig_device = px.pie(
        device_summary,
        names="Device Category",
        values="Page Views",
        hole=0.45,
        title="Device Contribution to Page Views"
    )
    st.plotly_chart(fig_device, use_container_width=True)

with col4:
    country_summary = filtered_df.groupby("Country", as_index=False)[["Page Views", "Conversions"]].sum()
    country_summary = country_summary.sort_values("Page Views", ascending=False).head(10)

    fig_country = px.bar(
        country_summary,
        x="Country",
        y="Page Views",
        color="Conversions",
        text_auto=True,
        title="Top Countries by Page Views"
    )
    st.plotly_chart(fig_country, use_container_width=True)

col5, col6 = st.columns(2)

with col5:
    page_summary = filtered_df.groupby("Page Path", as_index=False)[["Page Views", "Conversions"]].sum()
    page_summary = page_summary.sort_values("Page Views", ascending=False)

    fig_page = px.bar(
        page_summary,
        x="Page Path",
        y="Page Views",
        color="Conversions",
        text_auto=True,
        title="Page Path Performance"
    )
    st.plotly_chart(fig_page, use_container_width=True)

with col6:
    hour_summary = filtered_df.groupby("Hour", as_index=False)[["Page Views", "Conversions"]].sum()
    hour_summary = hour_summary.sort_values("Hour")

    fig_hour = go.Figure()
    fig_hour.add_trace(go.Scatter(
        x=hour_summary["Hour"],
        y=hour_summary["Page Views"],
        mode="lines+markers",
        name="Page Views"
    ))
    fig_hour.add_trace(go.Bar(
        x=hour_summary["Hour"],
        y=hour_summary["Conversions"],
        name="Conversions",
        opacity=0.5
    ))
    fig_hour.update_layout(title="Hourly Traffic and Conversion Pattern")
    st.plotly_chart(fig_hour, use_container_width=True)

heat_df = filtered_df.pivot_table(
    index="Day",
    columns="Source",
    values="Page Views",
    aggfunc="sum",
    fill_value=0
)

day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
heat_df = heat_df.reindex([d for d in day_order if d in heat_df.index])

fig_heat = px.imshow(
    heat_df,
    text_auto=True,
    aspect="auto",
    color_continuous_scale="Blues",
    title="Heatmap of Traffic by Day and Source"
)
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("## Website Summary Table")

website_summary = filtered_df.groupby("Website", as_index=False)[
    ["Page Views", "Conversions", "Bounce Rate", "Avg Session Duration", "Engagement Score"]
].mean()

website_summary = website_summary.sort_values("Page Views", ascending=False)
st.dataframe(website_summary, use_container_width=True)

st.markdown("## Filtered Raw Dataset")
st.dataframe(filtered_df, use_container_width=True)