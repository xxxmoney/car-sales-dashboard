from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from src.data_loader import DataLoader

# --- 1. Initialization ---
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

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
                value=[g for g in df['gear'].unique()],
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

            # Loading Wrapper for better UX
            dcc.Loading(
                id="loading-graphs",
                type="default",
                children=[
                    # Row 1: Scatter Plot
                    dcc.Graph(id='graph-scatter'),

                    # Row 2: Box Plot (Price Analytics) & Pie Chart
                    html.Div([
                        # Box Plot is great for analytics - shows median, range and outliers
                        html.Div([dcc.Graph(id='graph-box')], className="eight columns"),
                        html.Div([dcc.Graph(id='graph-pie')], className="four columns"),
                    ], className="row"),

                    # Row 3: Histogram (Distribution) & Heatmap
                    html.Div([
                        html.Div([dcc.Graph(id='graph-histogram')], className="six columns"),
                        html.Div([dcc.Graph(id='graph-heatmap')], className="six columns"),
                    ], className="row"),
                ]
            )

        ], className="eight columns")

    ], className="row")
])


# --- 3. Interaction Logic (Controller) ---
@app.callback(
    [Output('kpi-count', 'children'),
     Output('kpi-price', 'children'),
     Output('kpi-mileage', 'children'),
     Output('graph-scatter', 'figure'),
     Output('graph-box', 'figure'),  # Changed from graph-bar
     Output('graph-pie', 'figure'),
     Output('graph-histogram', 'figure'),  # New Histogram
     Output('graph-heatmap', 'figure')],
    [Input('filter-brand', 'value'),
     Input('filter-year', 'value'),
     Input('filter-fuel', 'value'),
     Input('filter-gear', 'value')]
)
def update_dashboard(selected_brands, year_range, selected_fuels, selected_gears):
    # A. Filter Data
    dff = df.copy()
    dff = dff[(dff['year'] >= year_range[0]) & (dff['year'] <= year_range[1])]
    if selected_brands:
        dff = dff[dff['make'].isin(selected_brands)]
    if selected_fuels:
        dff = dff[dff['fuel'].isin(selected_fuels)]
    if selected_gears:
        dff = dff[dff['gear'].isin(selected_gears)]

    # B. Handle Empty Data
    if dff.empty:
        return "0", "0 €", "0 km", {}, {}, {}, {}, {}

    # C. KPIs
    kpi_count = f"{len(dff)}"
    kpi_price = f"{dff['price'].mean():,.0f} €"
    kpi_mileage = f"{dff['mileage'].mean():,.0f} km"

    # D. Graphs

    # 1. Scatter: Price vs Mileage
    fig_scatter = px.scatter(
        dff, x='mileage', y='price', color='fuel',
        title='Price vs. Mileage Correlation',
        hover_data=['make', 'model', 'year', 'hp'],
        opacity=0.6
    )

    # 2. Box Plot: Price Analysis by Brand (Analytics)
    # Instead of just average, we see the full spread of prices
    fig_box = px.box(
        dff, x='make', y='price',
        title='Price Distribution by Brand (Box Plot)',
        points="outliers"  # Only show outliers as points to avoid clutter
    )

    # 3. Pie: Transmission
    fig_pie = px.pie(
        dff, names='gear',
        title='Transmission Share',
        hole=0.4
    )

    # 4. Histogram: Price Distribution (Analytics)
    # Shows if prices are skewed (e.g. mostly cheap cars)
    fig_hist = px.histogram(
        dff, x="price", nbins=50,
        title="Price Frequency Distribution",
        color_discrete_sequence=['#636EFA']
    )

    # 5. Heatmap: Correlation
    numeric_cols = ['price', 'mileage', 'hp', 'year']
    corr_matrix = dff[numeric_cols].corr()
    fig_heatmap = px.imshow(
        corr_matrix,
        text_auto=True, aspect="auto",
        title='Correlation Matrix',
        color_continuous_scale='RdBu_r'
    )

    return kpi_count, kpi_price, kpi_mileage, fig_scatter, fig_box, fig_pie, fig_hist, fig_heatmap