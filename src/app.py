from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from src.data_loader import DataLoader

# --- 1. Initialization ---
# Load CSS (Simple Grid System)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server  # Expose server for deployment

# Load Data once at startup
loader = DataLoader()
df = loader.load_data()
brands = loader.get_brands()
min_year, max_year = loader.get_year_range()

# --- 2. Layout (The View) ---
app.layout = html.Div([

    # Header
    html.Div([
        html.H1("Used Car Market Analysis", style={'textAlign': 'center'}),
        html.P("Interactive dashboard for AutoScout24 data", style={'textAlign': 'center', 'color': '#7f7f7f'})
    ], style={'padding': '20px'}),

    # Main Grid
    html.Div([

        # --- Left Sidebar (Filters) ---
        html.Div([
            html.H4("Filters"),

            html.Label("Car Brand:"),
            dcc.Dropdown(
                id='filter-brand',
                options=[{'label': b, 'value': b} for b in brands],
                multi=True,
                placeholder="Select brands..."
            ),

            html.Br(),

            html.Label("Production Year:"),
            dcc.RangeSlider(
                id='filter-year',
                min=min_year, max=max_year, step=1,
                marks={i: str(i) for i in range(min_year, max_year + 1, 2)},
                value=[min_year, max_year]
            ),

            html.Br(),

            html.Label("Fuel Type:"),
            dcc.Dropdown(
                id='filter-fuel',
                options=[{'label': f, 'value': f} for f in df['fuel'].unique()],
                multi=True,
                placeholder="All fuels"
            ),

            html.Br(),

            html.Label("Transmission:"),
            dcc.Checklist(
                id='filter-gear',
                options=[{'label': g, 'value': g} for g in df['gear'].unique()],
                value=[g for g in df['gear'].unique()],  # Default: All selected
                inline=True
            )

        ], className="four columns", style={'padding': '20px', 'backgroundColor': '#f9f9f9', 'borderRadius': '5px'}),

        # --- Right Content (Graphs) ---
        html.Div([

            # KPI Cards
            html.Div([
                html.Div([html.H6("Total Cars"), html.H3(id='kpi-count')], className="four columns box"),
                html.Div([html.H6("Avg Price"), html.H3(id='kpi-price')], className="four columns box"),
                html.Div([html.H6("Avg Mileage"), html.H3(id='kpi-mileage')], className="four columns box"),
            ], className="row", style={'textAlign': 'center', 'marginBottom': '20px'}),

            # Row 1: Scatter Plot
            dcc.Graph(id='graph-scatter'),

            # Row 2: Bar & Pie
            html.Div([
                html.Div([dcc.Graph(id='graph-bar')], className="eight columns"),
                html.Div([dcc.Graph(id='graph-pie')], className="four columns"),
            ], className="row"),

            # Row 3: Heatmap
            dcc.Graph(id='graph-heatmap')

        ], className="eight columns")

    ], className="row")
])


# --- 3. Interaction Logic (Controller) ---
@app.callback(
    # Outputs (What we update)
    [Output('kpi-count', 'children'),
     Output('kpi-price', 'children'),
     Output('kpi-mileage', 'children'),
     Output('graph-scatter', 'figure'),
     Output('graph-bar', 'figure'),
     Output('graph-pie', 'figure'),
     Output('graph-heatmap', 'figure')],
    # Inputs (Triggers from UI)
    [Input('filter-brand', 'value'),
     Input('filter-year', 'value'),
     Input('filter-fuel', 'value'),
     Input('filter-gear', 'value')]
)
def update_dashboard(selected_brands, year_range, selected_fuels, selected_gears):
    """
    Reactive function: Runs every time an input changes
    Filters data and regenerates all figures
    """
    # Filter Data
    dff = df.copy()

    # Filter by Year Slider
    dff = dff[(dff['year'] >= year_range[0]) & (dff['year'] <= year_range[1])]

    # Filter by Dropdowns (if anything is selected)
    if selected_brands:
        dff = dff[dff['make'].isin(selected_brands)]
    if selected_fuels:
        dff = dff[dff['fuel'].isin(selected_fuels)]
    if selected_gears:
        dff = dff[dff['gear'].isin(selected_gears)]

    # Handle Empty Data (Edge case)
    if dff.empty:
        # Return safe defaults to avoid errors
        return "0", "0 €", "0 km", {}, {}, {}, {}

    # Calculate KPIs
    kpi_count = f"{len(dff)}"
    kpi_price = f"{dff['price'].mean():,.0f} €"
    kpi_mileage = f"{dff['mileage'].mean():,.0f} km"

    # Generate Graphs (Plotly Express)

    # Scatter: Price vs Mileage (colored by Brand or Fuel if many brands)
    # We limit points for performance if dataset is huge, but 46k is okay for modern browsers
    fig_scatter = px.scatter(
        dff, x='mileage', y='price', color='fuel',
        title='Price vs. Mileage Correlation',
        hover_data=['make', 'model', 'year', 'hp'],
        opacity=0.6
    )

    # Bar: Most Expensive Brands
    avg_price_brands = dff.groupby('make')['price'].mean().reset_index().sort_values('price', ascending=False).head(10)
    fig_bar = px.bar(
        avg_price_brands, x='make', y='price',
        title='Most Expensive Brands (Avg)',
        labels={'price': 'Avg Price (€)', 'make': 'Brand'},
        color='price'
    )

    # Pie: Transmission Share
    fig_pie = px.pie(
        dff, names='gear',
        title='Transmission Distribution',
        hole=0.4  # Donut chart style
    )

    # Heatmap: Correlation Matrix
    # Shows relationships between numerical variables
    numeric_cols = ['price', 'mileage', 'hp', 'year']
    corr_matrix = dff[numeric_cols].corr()
    fig_heatmap = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        title='Variable Correlation Matrix',
        color_continuous_scale='RdBu_r'  # Red-Blue diverging
    )

    return kpi_count, kpi_price, kpi_mileage, fig_scatter, fig_bar, fig_pie, fig_heatmap