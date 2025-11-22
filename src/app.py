from dash import Dash, html, dcc
import plotly.express as px
from src.data_loader import DataLoader

# --- Initialization ---
# Load CSS from a CDN (simple grid system similar to Bootstrap)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Expose server variable for WSGI deployments (e.g. Gunicorn)
server = app.server

# Load Data
loader = DataLoader()
df = loader.load_data()
brands = loader.get_brands()
min_year, max_year = loader.get_year_range()

# --- Layout Definition (The "Template") ---
app.layout = html.Div([

    # 1. Header Section
    html.Div([
        html.H1("Used Car Market Analysis (AutoScout24)", style={'textAlign': 'center'}),
        html.P("Interactive dashboard for price and trend analysis", style={'textAlign': 'center', 'color': '#7f7f7f'})
    ], style={'padding': '20px'}),

    # 2. Main Container (Grid)
    html.Div([

        # --- Left Sidebar (Filters) ---
        html.Div([
            html.H4("Filters"),

            html.Label("Car Brand:"),
            dcc.Dropdown(
                id='filter-brand',
                options=[{'label': b, 'value': b} for b in brands],
                multi=True,  # Allow selecting multiple brands
                placeholder="Select brand..."
            ),

            html.Br(),

            html.Label("Production Year:"),
            dcc.RangeSlider(
                id='filter-year',
                min=min_year,
                max=max_year,
                step=1,
                marks={i: str(i) for i in range(min_year, max_year + 1, 2)},
                value=[min_year, max_year]
            ),

            html.Br(),

            html.Label("Fuel Type:"),
            dcc.Dropdown(
                id='filter-fuel',
                options=[{'label': f, 'value': f} for f in df['fuel'].unique()],
                multi=True,
                placeholder="All fuel types"
            ),

            html.Br(),

            html.Label("Transmission:"),
            dcc.Checklist(
                id='filter-gear',
                options=[{'label': g, 'value': g} for g in df['gear'].unique()],
                value=[g for g in df['gear'].unique()],  # All selected by default
                inline=True
            )

        ], className="four columns", style={'padding': '20px', 'backgroundColor': '#f9f9f9', 'borderRadius': '5px'}),

        # --- Right Content Area (Graphs) ---
        html.Div([

            # KPI Cards Row
            html.Div([
                html.Div([
                    html.H6("Total Cars"),
                    html.H3(id='kpi-count', children="0")
                ], className="four columns",
                    style={'textAlign': 'center', 'border': '1px solid #ddd', 'padding': '10px'}),

                html.Div([
                    html.H6("Avg Price"),
                    html.H3(id='kpi-price', children="0 €")
                ], className="four columns",
                    style={'textAlign': 'center', 'border': '1px solid #ddd', 'padding': '10px'}),

                html.Div([
                    html.H6("Avg Mileage"),
                    html.H3(id='kpi-mileage', children="0 km")
                ], className="four columns",
                    style={'textAlign': 'center', 'border': '1px solid #ddd', 'padding': '10px'}),
            ], className="row"),

            html.Br(),

            # Graph Row 1: Scatter Plot
            dcc.Graph(id='graph-scatter'),

            # Graph Row 2: Bar Chart & Pie Chart
            html.Div([
                html.Div([dcc.Graph(id='graph-bar')], className="eight columns"),
                html.Div([dcc.Graph(id='graph-pie')], className="four columns"),
            ], className="row"),

            # Graph Row 3: Heatmap
            dcc.Graph(id='graph-heatmap')

        ], className="eight columns")

    ], className="row")  # End of Main Container

])