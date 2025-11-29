import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.constants import THEME_TEMPLATE, PRIMARY_COLOR, COLOR_SEQUENCE


def create_line_chart_price_year(data: pd.DataFrame) -> go.Figure:
    """ Line chart: Price evolution over time """
    if data.empty:
        return go.Figure()

    # Group data by year and calculate average price
    data_trend = data.groupby("year")["price"].mean().reset_index()

    line_chart = px.line(
        data_trend, x="year", y="price",
        title="Average Price Evolution (Depreciation)",
        markers=True,
        template=THEME_TEMPLATE,
        color_discrete_sequence=[PRIMARY_COLOR]
    )

    # Tooltip formatting
    line_chart.update_traces(hovertemplate="Year: %{x}<br>Price: %{y:,.0f} €<extra></extra>")

    # X-axis ticks (integers only)
    line_chart.update_xaxes(dtick=1)

    return line_chart


def create_scatter_chart_price_mileage(data: pd.DataFrame) -> go.Figure:
    """ Scatter plot: Price vs. Mileage """
    if data.empty:
        return go.Figure()

    data_reset = data.reset_index()

    scatter = px.scatter(
        data_reset, x="mileage", y="price", color="fuel",
        title="Price vs. Mileage (Click for details)",
        custom_data=["index", "make", "model", "year", "hp"],
        opacity=0.7,
        template=THEME_TEMPLATE,
        color_discrete_sequence=COLOR_SEQUENCE
    )

    # Tooltip formatting
    scatter.update_traces(
        hovertemplate=(
                "<b>%{customdata[1]} %{customdata[2]}</b><br>" +
                "Price: %{y:,.0f} €<br>" +
                "Mileage: %{x:,.0f} km<br>" +
                "Year: %{customdata[3]}<br>" +
                "Power: %{customdata[4]} HP"
                "<extra></extra>"
        )
    )

    # Enable click events
    scatter.update_layout(clickmode="event+select")
    return scatter


def create_box_plot_price_brand(data: pd.DataFrame) -> go.Figure:
    """ Box plot: Price distribution by brand """
    if data.empty:
        return go.Figure()

    box_plot = px.box(
        data, x="make", y="price",
        title="Price Distribution by Brand",
        points="outliers",
        template=THEME_TEMPLATE,
        color_discrete_sequence=[PRIMARY_COLOR]
    )
    return box_plot


def create_pie_chart_transmission(data: pd.DataFrame) -> go.Figure:
    """ Pie chart: Transmission types share """
    if data.empty:
        return go.Figure()

    pie_chart = px.pie(
        data, names="gear",
        title="Transmission Types",
        hole=0.5,  # Donut chart style
        template=THEME_TEMPLATE,
        color_discrete_sequence=COLOR_SEQUENCE
    )

    pie_chart.update_traces(textinfo="percent+label")
    return pie_chart


def create_histogram_price(data: pd.DataFrame) -> go.Figure:
    """ Histogram: Price frequency distribution """
    if data.empty:
        return go.Figure()

    histogram = px.histogram(
        data, x="price", nbins=50,
        title="Market Price Distribution",
        template=THEME_TEMPLATE,
        color_discrete_sequence=[PRIMARY_COLOR]
    )
    return histogram


def create_heatmap_price_mileage_hp_year(data: pd.DataFrame) -> go.Figure:
    """ Heatmap: Correlation matrix """
    if data.empty:
        return go.Figure()

    # Select numeric columns only
    numeric_columns = ["price", "mileage", "hp", "year"]
    data_correlation = data[numeric_columns].corr()

    heatmap = px.imshow(
        data_correlation,
        text_auto=".2f",
        aspect="auto",
        title="Correlation Matrix (Variable Relationships)",
        color_continuous_scale="RdBu_r",  # Red-Blue scale
        template=THEME_TEMPLATE
    )
    return heatmap