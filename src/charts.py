import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.constants import THEME_TEMPLATE, COLOR_PRIMARY, COLOR_SEQUENCE, COLOR_SECONDARY


def _update_layout(fig: go.Figure):
    """ Helper to apply common modern styling to all charts """
    fig.update_layout(
        template=THEME_TEMPLATE,
        font=dict(family="Lato, sans-serif", size=12, color=COLOR_PRIMARY),
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
        paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
        margin=dict(l=20, r=20, t=40, b=20),
        title_font_size=16
    )
    return fig


def create_line_chart_price_year(data: pd.DataFrame) -> go.Figure:
    """ Line chart: Price evolution """
    if data.empty:
        return go.Figure()

    data_trend = data.groupby("year")["price"].mean().reset_index()

    fig = px.line(
        data_trend, x="year", y="price",
        title="Avg. Price Evolution",
        markers=True
    )

    fig.update_traces(line_color=COLOR_PRIMARY, line_width=3, marker_size=8)
    fig.update_xaxes(dtick=1, showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#eee")

    return _update_layout(fig)


def create_scatter_chart_price_mileage(data: pd.DataFrame) -> go.Figure:
    """ Scatter: Price vs Mileage """
    if data.empty:
        return go.Figure()

    data_reset = data.reset_index()

    fig = px.scatter(
        data_reset, x="mileage", y="price", color="fuel",
        title="Price vs. Mileage Analysis",
        custom_data=["index", "make", "model", "year", "hp"],
        opacity=0.6,
        color_discrete_sequence=COLOR_SEQUENCE
    )

    fig.update_layout(clickmode="event+select", legend=dict(orientation="h", y=-0.2))
    return _update_layout(fig)


def create_box_plot_price_brand(data: pd.DataFrame) -> go.Figure:
    """ Box Plot: Price Distribution """
    if data.empty:
        return go.Figure()

    fig = px.box(
        data, x="make", y="price",
        title="Price Range by Brand",
        color_discrete_sequence=[COLOR_PRIMARY]
    )
    return _update_layout(fig)


def create_pie_chart_transmission(data: pd.DataFrame) -> go.Figure:
    """ Donut Chart: Transmission """
    if data.empty:
        return go.Figure()

    fig = px.pie(
        data, names="gear",
        title="Transmission Market Share",
        hole=0.6,
        color_discrete_sequence=COLOR_SEQUENCE
    )
    fig.update_traces(textinfo="percent")
    return _update_layout(fig)


def create_sunburst_chart(data: pd.DataFrame) -> go.Figure:
    """
    Sunburst Chart: Hierarchical view of the market
    Brand -> Model -> Fuel
    """
    if data.empty:
        return go.Figure()

    # --- FIX START: Drop rows with missing values in path columns ---
    # Sunburst fails if 'model' is missing but 'fuel' is present (broken hierarchy)
    # We create a copy to avoid SettingWithCopyWarning on the original dataframe
    clean_data = data.dropna(subset=["make", "model", "fuel"]).copy()

    if clean_data.empty:
        return go.Figure()
    # --- FIX END ---

    # We limit to top 15 brands to keep the chart readable
    top_brands = clean_data["make"].value_counts().nlargest(15).index
    data_filtered = clean_data[clean_data["make"].isin(top_brands)]

    fig = px.sunburst(
        data_filtered,
        path=["make", "model", "fuel"],
        title="Market Hierarchy (Click to Explore)",
        color_discrete_sequence=COLOR_SEQUENCE,
        maxdepth=2
    )

    fig.update_traces(textinfo="label+percent entry")
    return _update_layout(fig)


def create_heatmap_price_mileage_hp_year(data: pd.DataFrame) -> go.Figure:
    """ Heatmap: Correlations """
    if data.empty:
        return go.Figure()

    numeric_columns = ["price", "mileage", "hp", "year"]
    data_correlation = data[numeric_columns].corr()

    fig = px.imshow(
        data_correlation,
        text_auto=".2f",
        aspect="auto",
        title="Variable Correlation Matrix",
        color_continuous_scale="RdBu_r"
    )
    return _update_layout(fig)