import plotly.express as px
import pandas as pd

COMMON_TEMPLATE = 'plotly_white'
COLOR_SEQ = ['#636EFA']


def create_scatter_chart(df: pd.DataFrame) -> dict:
    """Creates Price vs. Mileage scatter plot."""
    if df.empty:
        return {}

    # Reset index to make sure we can pass it as a column
    df_reset = df.reset_index()

    fig = px.scatter(
        df_reset, x='mileage', y='price', color='fuel',
        title='Price vs. Mileage Correlation (Click for details)',
        # Custom data indices for hovertemplate:
        # 0=index, 1=make, 2=model, 3=year, 4=hp
        custom_data=['index', 'make', 'model', 'year', 'hp'],
        opacity=0.6,
        template=COMMON_TEMPLATE
    )

    # --- FIX: Custom Hover Tooltip ---
    fig.update_traces(
        hovertemplate=(
                "<b>%{customdata[1]} %{customdata[2]}</b><br>" +  # Bold Make + Model
                "Price: %{y:,.0f} €<br>" +  # Format Price (comma separator)
                "Mileage: %{x:,.0f} km<br>" +  # Format Mileage
                "Year: %{customdata[3]}<br>" +  # Year
                "Power: %{customdata[4]} HP"  # HP
                "<extra></extra>"  # Hides the secondary box (trace name)
        )
    )

    fig.update_layout(clickmode='event+select')

    return fig


def create_box_plot(df: pd.DataFrame) -> dict:
    """Creates Price Distribution by Brand box plot."""
    if df.empty: return {}
    fig = px.box(
        df, x='make', y='price',
        title='Price Distribution by Brand',
        points="outliers",
        template=COMMON_TEMPLATE
    )
    return fig


def create_pie_chart(df: pd.DataFrame) -> dict:
    """Creates Transmission share pie chart."""
    if df.empty: return {}
    fig = px.pie(
        df, names='gear',
        title='Transmission Share',
        hole=0.4,
        template=COMMON_TEMPLATE
    )
    fig.update_traces(textinfo='percent+label')
    return fig


def create_histogram(df: pd.DataFrame) -> dict:
    """Creates Price frequency distribution histogram."""
    if df.empty: return {}
    fig = px.histogram(
        df, x="price", nbins=50,
        title="Price Distribution",
        color_discrete_sequence=COLOR_SEQ,
        template=COMMON_TEMPLATE
    )
    return fig


def create_heatmap(df: pd.DataFrame) -> dict:
    """Creates Correlation Matrix heatmap."""
    if df.empty: return {}

    numeric_cols = ['price', 'mileage', 'hp', 'year']
    corr = df[numeric_cols].corr()

    fig = px.imshow(
        corr,
        text_auto='.2f',  # Show 2 decimal places
        aspect="auto",
        title='Correlation Matrix',
        color_continuous_scale='RdBu_r',
        template=COMMON_TEMPLATE
    )
    return fig