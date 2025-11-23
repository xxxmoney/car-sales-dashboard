from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from src.data_loader import DataLoader

# --- Initialization ---
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

loader = DataLoader()
data = loader.load_data()
brands = loader.get_brands()
min_year, max_year = loader.get_year_range()

# --- Layout (The View) ---
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
                options=[{'label': f, 'value': f} for f in data['fuel'].unique()],
                multi=True,
                placeholder="All fuels"
            ),

            html.Br(),

            html.Label("Transmission:"),
            dcc.Checklist(
                id='filter-gear',
                options=[{'label': g, 'value': g} for g in data['gear'].unique()],
                value=[g for g in data['gear'].unique()],
                inline=True
            )
        ], className="four columns", style={'padding': '20px', 'backgroundColor': '#f9f9f9', 'borderRadius': '5px'}),

        # --- Right Content (Graphs) ---
        html.Div([
            dcc.Loading(
                id="loading-data",
                type="default",
                children=[
                    # KPI Cards
                    html.Div([
                        html.Div([html.H6("Total Cars"), html.H3(id='kpi-count')], className="four columns box"),
                        html.Div([html.H6("Avg Price"), html.H3(id='kpi-price')], className="four columns box"),
                        html.Div([html.H6("Avg Mileage"), html.H3(id='kpi-mileage')], className="four columns box"),
                    ], className="row", style={'textAlign': 'center', 'marginBottom': '20px'}),

                    # Scatter: Price vs Mileage
                    dcc.Graph(id='graph-scatter'),

                    #
                    html.Div([
                        # Box Plot: Price Analysis by Brand
                        html.Div([dcc.Graph(id='graph-box')], className="eight columns"),
                        # Pie: Transmission
                        html.Div([dcc.Graph(id='graph-pie')], className="four columns"),
                    ], className="row"),

                    html.Div([
                        # Histogram: Price Distribution
                        html.Div([dcc.Graph(id='graph-histogram')], className="six columns"),
                        # Heatmap: Correlation (price, mileage, hp, year)
                        html.Div([dcc.Graph(id='graph-heatmap')], className="six columns"),
                    ], className="row"),
                ]
            )

        ], className="eight columns")

    ], className="row")
])


# --- App callback for data update ---
@app.callback(
    [Output('kpi-count', 'children'),
     Output('kpi-price', 'children'),
     Output('kpi-mileage', 'children'),
     Output('graph-scatter', 'figure'),
     Output('graph-box', 'figure'),
     Output('graph-pie', 'figure'),
     Output('graph-histogram', 'figure'),
     Output('graph-heatmap', 'figure')],
    [Input('filter-brand', 'value'),
     Input('filter-year', 'value'),
     Input('filter-fuel', 'value'),
     Input('filter-gear', 'value')]
)
def update_dashboard(selected_brands, year_range, selected_fuels, selected_gears):
    # Filter Data
    data_copy = data.copy()
    data_copy = data_copy[(data_copy['year'] >= year_range[0]) & (data_copy['year'] <= year_range[1])]
    if selected_brands:
        data_copy = data_copy[data_copy['make'].isin(selected_brands)]
    if selected_fuels:
        data_copy = data_copy[data_copy['fuel'].isin(selected_fuels)]
    if selected_gears:
        data_copy = data_copy[data_copy['gear'].isin(selected_gears)]

    # Handle Empty Data
    if data_copy.empty:
        return "0", "0 €", "0 km", {}, {}, {}, {}, {}

    # KPIs
    kpi_count = f"{len(data_copy)}"
    kpi_price = f"{data_copy['price'].mean():,.0f} €"
    kpi_mileage = f"{data_copy['mileage'].mean():,.0f} km"

    # Graphs
    scatter_price_mileage = px.scatter(
        data_copy, x='mileage', y='price', color='fuel',
        title='Price vs. Mileage Correlation',
        hover_data=['make', 'model', 'year', 'hp'],
        opacity=0.6
    )
    box_price_brand = px.box(
        data_copy, x='make', y='price',
        title='Price Distribution by Brand (Box Plot)',
        points="outliers"  # Only show outliers as points to avoid clutter
    )
    pie_transmission = px.pie(
        data_copy, names='gear',
        title='Transmission Share',
        hole=0.4
    )
    histogram_price = px.histogram(
        data_copy, x="price", nbins=50,
        title="Price Frequency Distribution",
        color_discrete_sequence=['#636EFA']
    )
    numeric_columns = ['price', 'mileage', 'hp', 'year']
    correlation_matrix = data_copy[numeric_columns].corr()
    heatmap_numeric_columns = px.imshow(
        correlation_matrix,
        text_auto=True, aspect="auto",
        title='Correlation Matrix',
        color_continuous_scale='RdBu_r'
    )

    return kpi_count, kpi_price, kpi_mileage, scatter_price_mileage, box_price_brand, pie_transmission, histogram_price, heatmap_numeric_columns