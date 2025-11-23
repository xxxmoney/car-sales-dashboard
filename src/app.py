from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from src.data_loader import DataLoader

# --- Initialization ---
external_stylesheets = [dbc.themes.FLATLY]
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

loader = DataLoader()
data = loader.load_data()
brands = loader.get_brands()
min_year, max_year = loader.get_year_range()

# --- Layout (The View) ---
app.layout = dbc.Container([

    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Used Car Market Analysis", className="text-center mt-4"),
            html.P("Interactive dashboard for AutoScout24 data", className="text-center text-muted mb-5")
        ], width=12)
    ]),

    # Main Grid
    dbc.Row([

        # --- Left Sidebar (Filters) ---
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Filters", className="card-title mb-4"),

                    # Brand Filter
                    html.Div([
                        html.Label("Car Brand:", className="fw-bold mb-1"),
                        dcc.Dropdown(
                            id='filter-brand',
                            options=[{'label': b, 'value': b} for b in brands],
                            multi=True,
                            placeholder="Select brands..."
                        )
                    ], className="mb-3"),

                    # Year Filter
                    html.Div([
                        html.Label("Production Year:", className="fw-bold mb-1"),
                        dcc.RangeSlider(
                            id='filter-year',
                            min=min_year, max=max_year, step=1,
                            marks={i: str(i) for i in range(min_year, max_year + 1, 2)},
                            value=[min_year, max_year]
                        )
                    ], className="mb-3"),

                    # Fuel Filter (Added mb-4 for extra space before Transmission)
                    html.Div([
                        html.Label("Fuel Type:", className="fw-bold mb-1"),
                        dcc.Dropdown(
                            id='filter-fuel',
                            options=[{'label': f, 'value': f} for f in data['fuel'].unique()],
                            multi=True,
                            placeholder="All fuels"
                        )
                    ], className="mb-4"),

                    # Transmission Filter
                    html.Div([
                        html.Label("Transmission:", className="fw-bold mb-2"),
                        dcc.Checklist(
                            id='filter-gear',
                            options=[{'label': g, 'value': g} for g in data['gear'].unique()],
                            value=[g for g in data['gear'].unique()],
                            inline=True,
                            inputClassName="me-2",
                            labelClassName="me-3"
                        )
                    ])
                ])
            ], className="bg-light border-0 shadow-sm h-100")
        ], xs=12, lg=3, className="mb-4 mb-lg-0"),

        # --- Right Content (Graphs) ---
        dbc.Col([
            dcc.Loading(
                id="loading-data",
                type="default",
                children=[

                    # KPI Cards
                    dbc.Row([
                        dbc.Col(dbc.Card(dbc.CardBody([
                            html.H6("Total Cars", className="card-title text-muted"),
                            html.H3(id='kpi-count', className="card-text")
                        ]), className="text-center shadow-sm border-0 h-100"), xs=12, md=4, className="mb-4"),

                        dbc.Col(dbc.Card(dbc.CardBody([
                            html.H6("Avg Price", className="card-title text-muted"),
                            html.H3(id='kpi-price', className="card-text text-primary")
                        ]), className="text-center shadow-sm border-0 h-100"), xs=12, md=4, className="mb-4"),

                        dbc.Col(dbc.Card(dbc.CardBody([
                            html.H6("Avg Mileage", className="card-title text-muted"),
                            html.H3(id='kpi-mileage', className="card-text text-info")
                        ]), className="text-center shadow-sm border-0 h-100"), xs=12, md=4, className="mb-4"),
                    ]),

                    # Scatter: Price vs Mileage
                    dbc.Card(dbc.CardBody([
                        dcc.Graph(id='graph-scatter')
                    ]), className="mb-4 shadow-sm border-0"),

                    # Row: Box Plot & Pie Chart
                    dbc.Row([
                        dbc.Col(dbc.Card(dbc.CardBody([
                            dcc.Graph(id='graph-box')
                        ]), className="shadow-sm border-0 h-100"), xs=12, lg=8, className="mb-4"),

                        dbc.Col(dbc.Card(dbc.CardBody([
                            dcc.Graph(id='graph-pie')
                        ]), className="shadow-sm border-0 h-100"), xs=12, lg=4, className="mb-4"),
                    ]),

                    # Row: Histogram & Heatmap
                    dbc.Row([
                        dbc.Col(dbc.Card(dbc.CardBody([
                            dcc.Graph(id='graph-histogram')
                        ]), className="shadow-sm border-0 h-100"), xs=12, lg=6, className="mb-4"),

                        dbc.Col(dbc.Card(dbc.CardBody([
                            dcc.Graph(id='graph-heatmap')
                        ]), className="shadow-sm border-0 h-100"), xs=12, lg=6, className="mb-4"),
                    ]),
                ]
            )
        ], xs=12, lg=9)

    ], className="mb-5")
], fluid=True)


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

    # Common template for consistent look
    common_template = 'plotly_white'

    # Graphs
    scatter_price_mileage = px.scatter(
        data_copy, x='mileage', y='price', color='fuel',
        title='Price vs. Mileage Correlation',
        hover_data=['make', 'model', 'year', 'hp'],
        opacity=0.6, template=common_template
    )
    scatter_price_mileage.update_layout(autosize=True, margin=dict(l=20, r=20, t=40, b=20))

    box_price_brand = px.box(
        data_copy, x='make', y='price',
        title='Price Distribution by Brand (Box Plot)',
        points="outliers", template=common_template
    )

    pie_transmission = px.pie(
        data_copy, names='gear',
        title='Transmission Share',
        hole=0.4, template=common_template
    )

    histogram_price = px.histogram(
        data_copy, x="price", nbins=50,
        title="Price Frequency Distribution",
        color_discrete_sequence=['#636EFA'], template=common_template
    )

    numeric_columns = ['price', 'mileage', 'hp', 'year']
    correlation_matrix = data_copy[numeric_columns].corr()
    heatmap_numeric_columns = px.imshow(
        correlation_matrix,
        text_auto=True, aspect="auto",
        title='Correlation Matrix',
        color_continuous_scale='RdBu_r', template=common_template
    )

    return kpi_count, kpi_price, kpi_mileage, scatter_price_mileage, box_price_brand, pie_transmission, histogram_price, heatmap_numeric_columns