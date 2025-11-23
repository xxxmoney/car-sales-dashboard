import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

COMMON_TEMPLATE = 'plotly_white'
COLOR_SEQ = ['#636EFA']


def create_line_chart_price_year(data: pd.DataFrame) -> go.Figure:
    """Creates Average Price Evolution over Time line chart"""
    if data.empty:
        return go.Figure()

    data_trend = data.groupby('year')['price'].mean().reset_index()

    line_chart = px.line(
        data_trend, x='year', y='price',
        title='Average Price Evolution (Depreciation)',
        markers=True,  # Add dots on the line
        template=COMMON_TEMPLATE
    )

    # Tooltip
    line_chart.update_traces(hovertemplate="Year: %{x}<br>Avg Price: %{y:,.0f} €<extra></extra>")

    return line_chart


def create_scatter_chart_price_mileage(data: pd.DataFrame) -> go.Figure:
    """Creates Price vs. Mileage scatter plot"""
    if data.empty:
        return go.Figure()

    data_reset = data.reset_index()

    scatter = px.scatter(
        data_reset, x='mileage', y='price', color='fuel',
        title='Price vs. Mileage (Click for details)',
        custom_data=['index', 'make', 'model', 'year', 'hp'],
        opacity=0.6,
        template=COMMON_TEMPLATE
    )

    # Tooltip
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

    scatter.update_layout(clickmode='event+select')
    return scatter


def create_box_plot_price_brand(data: pd.DataFrame) -> go.Figure:
    """Creates Price Distribution by Brand box plot"""
    if data.empty:
        return go.Figure()

    box_plot = px.box(
        data, x='make', y='price',
        title='Price Distribution by Brand',
        points="outliers",
        template=COMMON_TEMPLATE
    )
    return box_plot


def create_pie_chart_transmission(data: pd.DataFrame) -> go.Figure:
    """Creates Transmission share pie chart"""
    if data.empty:
        return go.Figure()

    pie_chart = px.pie(
        data, names='gear',
        title='Transmission Share',
        hole=0.4,
        template=COMMON_TEMPLATE
    )

    pie_chart.update_traces(textinfo='percent+label')

    return pie_chart


def create_histogram_price(data: pd.DataFrame) -> go.Figure:
    """Creates Price frequency distribution histogram"""
    if data.empty:
        return go.Figure()

    histogram = px.histogram(
        data, x="price", nbins=50,
        title="Price Distribution",
        color_discrete_sequence=COLOR_SEQ,
        template=COMMON_TEMPLATE
    )
    return histogram


def create_heatmap_price_mileage_hp_year(data: pd.DataFrame) -> go.Figure:
    """Creates Correlation Matrix heatmap"""
    if data.empty:
        return go.Figure()

    numeric_columns = ['price', 'mileage', 'hp', 'year']
    data_correlation = data[numeric_columns].corr()

    heatmap = px.imshow(
        data_correlation,
        text_auto='.2f',
        aspect="auto",
        title='Correlation Matrix',
        color_continuous_scale='RdBu_r',
        template=COMMON_TEMPLATE
    )
    return heatmap