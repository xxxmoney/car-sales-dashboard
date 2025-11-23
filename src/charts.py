import plotly.express as px
import pandas as pd

# Define a common template for consistency across all charts
COMMON_TEMPLATE = 'plotly_white'
COLOR_SEQ = ['#636EFA']  # Uniform color for histograms etc.


def create_scatter_chart(df: pd.DataFrame) -> dict:
    """Creates Price vs. Mileage scatter plot."""
    if df.empty:
        return {}

    fig = px.scatter(
        df, x='mileage', y='price', color='fuel',
        title='Price vs. Mileage Correlation',
        hover_data=['make', 'model', 'year', 'hp'],
        opacity=0.6,
        template=COMMON_TEMPLATE
    )
    return fig


def create_box_plot(df: pd.DataFrame) -> dict:
    """Creates Price Distribution by Brand box plot."""
    if df.empty:
        return {}

    fig = px.box(
        df, x='make', y='price',
        title='Price Distribution by Brand',
        points="outliers",
        template=COMMON_TEMPLATE
    )
    return fig


def create_pie_chart(df: pd.DataFrame) -> dict:
    """Creates Transmission share pie chart."""
    if df.empty:
        return {}

    fig = px.pie(
        df, names='gear',
        title='Transmission Share',
        hole=0.4,
        template=COMMON_TEMPLATE
    )
    return fig


def create_histogram(df: pd.DataFrame) -> dict:
    """Creates Price frequency distribution histogram."""
    if df.empty:
        return {}

    fig = px.histogram(
        df, x="price", nbins=50,
        title="Price Distribution",
        color_discrete_sequence=COLOR_SEQ,
        template=COMMON_TEMPLATE
    )
    return fig


def create_heatmap(df: pd.DataFrame) -> dict:
    """Creates Correlation Matrix heatmap."""
    if df.empty:
        return {}

    numeric_cols = ['price', 'mileage', 'hp', 'year']
    corr = df[numeric_cols].corr()

    fig = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        title='Correlation Matrix',
        color_continuous_scale='RdBu_r',
        template=COMMON_TEMPLATE
    )
    return fig