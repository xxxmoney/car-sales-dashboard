from dash import Dash, html, dcc, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc
import pandas as pd
from src.data_loader import DataLoader
import src.charts as charts

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

    # --- NEW: Detail Modal (Popup) ---
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Car Details")),
        dbc.ModalBody(id="modal-body"),  # Content will be filled by callback
        dbc.ModalFooter(
            dbc.Button("Close", id="close-modal", className="ms-auto", n_clicks=0)
        ),
    ], id="car-modal", is_open=False, size="lg"),  # lg = large modal

    # Main Grid
    dbc.Row([
        # --- Sidebar ---
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Filters", className="card-title mb-4"),

                    html.Div([
                        html.Label("Car Brand:", className="fw-bold mb-1"),
                        dcc.Dropdown(
                            id='filter-brand',
                            options=[{'label': b, 'value': b} for b in brands],
                            multi=True,
                            placeholder="Select brands..."
                        )
                    ], className="mb-3"),

                    html.Div([
                        html.Label("Production Year:", className="fw-bold mb-1"),
                        dcc.RangeSlider(
                            id='filter-year',
                            min=min_year, max=max_year, step=1,
                            marks={i: str(i) for i in range(min_year, max_year + 1, 2)},
                            value=[min_year, max_year]
                        )
                    ], className="mb-3"),

                    html.Div([
                        html.Label("Fuel Type:", className="fw-bold mb-1"),
                        dcc.Dropdown(
                            id='filter-fuel',
                            options=[{'label': f, 'value': f} for f in data['fuel'].unique()],
                            multi=True,
                            placeholder="All fuels"
                        )
                    ], className="mb-4"),

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

        # --- Right Content ---
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

                    # Scatter Plot
                    dbc.Card(dbc.CardBody([
                        dcc.Graph(id='graph-scatter')
                    ]), className="mb-4 shadow-sm border-0"),

                    # Box + Pie
                    dbc.Row([
                        dbc.Col(dbc.Card(dbc.CardBody([
                            dcc.Graph(id='graph-box')
                        ]), className="shadow-sm border-0 h-100"), xs=12, lg=8, className="mb-4"),

                        dbc.Col(dbc.Card(dbc.CardBody([
                            dcc.Graph(id='graph-pie')
                        ]), className="shadow-sm border-0 h-100"), xs=12, lg=4, className="mb-4"),
                    ]),

                    # Hist + Heatmap
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


# --- 1. Main Data Callback (Same as before) ---
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
    # (Data logic omitted for brevity - same as before)
    dff = data.copy()
    dff = dff[(dff['year'] >= year_range[0]) & (dff['year'] <= year_range[1])]
    if selected_brands: dff = dff[dff['make'].isin(selected_brands)]
    if selected_fuels: dff = dff[dff['fuel'].isin(selected_fuels)]
    if selected_gears: dff = dff[dff['gear'].isin(selected_gears)]

    if dff.empty: return "0", "0 €", "0 km", {}, {}, {}, {}, {}

    kpi_count = f"{len(dff)}"
    kpi_price = f"{dff['price'].mean():,.0f} €"
    kpi_mileage = f"{dff['mileage'].mean():,.0f} km"

    fig_scatter = charts.create_scatter_chart(dff)
    fig_box = charts.create_box_plot(dff)
    fig_pie = charts.create_pie_chart(dff)
    fig_hist = charts.create_histogram(dff)
    fig_heatmap = charts.create_heatmap(dff)

    return kpi_count, kpi_price, kpi_mileage, fig_scatter, fig_box, fig_pie, fig_hist, fig_heatmap


# --- 2. NEW: Modal Interaction Callback ---
@app.callback(
    [Output("car-modal", "is_open"),
     Output("modal-body", "children")],
    [Input("graph-scatter", "clickData"),  # Trigger: Click on graph
     Input("close-modal", "n_clicks")],  # Trigger: Click close
    [State("car-modal", "is_open")]  # State: Is it currently open?
)
def toggle_modal(clickData, n_clicks, is_open):
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # If graph was clicked
    if trigger_id == "graph-scatter" and clickData:
        # Get the 'custom_data' we passed in charts.py (Index 0 is the ID)
        point = clickData['points'][0]
        # Depending on Plotly version, customdata might be a list or value
        # In charts.py we passed: custom_data=['index', 'make', ...]
        try:
            car_id = point['customdata'][0]

            # Lookup car in original dataframe
            car_row = data.loc[car_id]

            # Create Detail View (Bootstrap Table)
            details = dbc.Table([
                html.Tbody([
                    html.Tr([html.Td("Make:"), html.Td(car_row['make'], className="fw-bold")]),
                    html.Tr([html.Td("Model:"), html.Td(car_row['model'])]),
                    html.Tr(
                        [html.Td("Price:"), html.Td(f"{car_row['price']:,.0f} €", className="text-primary fw-bold")]),
                    html.Tr([html.Td("Mileage:"), html.Td(f"{car_row['mileage']:,.0f} km")]),
                    html.Tr([html.Td("Year:"), html.Td(car_row['year'])]),
                    html.Tr([html.Td("Power:"), html.Td(f"{car_row['hp']} HP")]),
                    html.Tr([html.Td("Fuel:"), html.Td(car_row['fuel'])]),
                    html.Tr([html.Td("Gear:"), html.Td(car_row['gear'])]),
                    html.Tr([html.Td("Offer Type:"), html.Td(car_row['offerType'])]),
                ])
            ], striped=True, bordered=True, hover=True)

            return True, details

        except Exception as e:
            # Fallback for errors
            return True, html.P(f"Error loading details: {str(e)}")

    # If Close button was clicked
    elif trigger_id == "close-modal":
        return False, no_update

    return is_open, no_update