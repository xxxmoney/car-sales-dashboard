import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

COMMON_TEMPLATE = 'plotly_white'
COLOR_SEQ = ['#636EFA']


def create_line_chart(df: pd.DataFrame) -> go.Figure:
    """Creates Average Price Evolution over Time line chart."""
    if df.empty:
        return go.Figure()

    # Group by year to find average price trend
    # Reset index converts the Series back to a DataFrame
    trend_data = df.groupby('year')['price'].mean().reset_index()

    fig = px.line(
        trend_data, x='year', y='price',
        title='Average Price Evolution (Depreciation)',
        markers=True,  # Add dots on the line
        template=COMMON_TEMPLATE
    )

    # Improve tooltip
    fig.update_traces(hovertemplate="Year: %{x}<br>Avg Price: %{y:,.0f} €<extra></extra>")

    return fig


def create_scatter_chart(df: pd.DataFrame) -> go.Figure:
    """Creates Price vs. Mileage scatter plot."""
    if df.empty:
        return go.Figure()

    df_reset = df.reset_index()

    fig = px.scatter(
        df_reset, x='mileage', y='price', color='fuel',
        title='Price vs. Mileage (Click for details)',
        custom_data=['index', 'make', 'model', 'year', 'hp'],
        opacity=0.6,
        template=COMMON_TEMPLATE
    )

    fig.update_traces(
        hovertemplate=(
                "<b>%{customdata[1]} %{customdata[2]}</b><br>" +
                "Price: %{y:,.0f} €<br>" +
                "Mileage: %{x:,.0f} km<br>" +
                "Year: %{customdata[3]}<br>" +
                "Power: %{customdata[4]} HP"
                "<extra></extra>"
        )
    )

    fig.update_layout(clickmode='event+select')
    return fig


def create_box_plot(df: pd.DataFrame) -> go.Figure:
    """Creates Price Distribution by Brand box plot."""
    if df.empty:
        return go.Figure()

    fig = px.box(
        df, x='make', y='price',
        title='Price Distribution by Brand',
        points="outliers",
        template=COMMON_TEMPLATE
    )
    return fig


def create_pie_chart(df: pd.DataFrame) -> go.Figure:
    """Creates Transmission share pie chart."""
    if df.empty:
        return go.Figure()

    fig = px.pie(
        df, names='gear',
        title='Transmission Share',
        hole=0.4,
        template=COMMON_TEMPLATE
    )
    fig.update_traces(textinfo='percent+label')
    return fig


def create_histogram(df: pd.DataFrame) -> go.Figure:
    """Creates Price frequency distribution histogram."""
    if df.empty:
        return go.Figure()

    fig = px.histogram(
        df, x="price", nbins=50,
        title="Price Distribution",
        color_discrete_sequence=COLOR_SEQ,
        template=COMMON_TEMPLATE
    )
    return fig


def create_heatmap(df: pd.DataFrame) -> go.Figure:
    """Creates Correlation Matrix heatmap."""
    if df.empty:
        return go.Figure()

    numeric_cols = ['price', 'mileage', 'hp', 'year']
    corr = df[numeric_cols].corr()

    fig = px.imshow(
        corr,
        text_auto='.2f',
        aspect="auto",
        title='Correlation Matrix',
        color_continuous_scale='RdBu_r',
        template=COMMON_TEMPLATE
    )
    return fig