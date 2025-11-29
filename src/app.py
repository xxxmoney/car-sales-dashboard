from dash import Dash, html, dcc, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc
from src.data_loader import DataLoader
import src.charts as charts

# App Initialization
# FLATLY theme is clean and modern, suitable for analytical dashboards
external_stylesheets = [dbc.themes.FLATLY]
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Load data on startup
loader = DataLoader()
data = loader.load_data()
brands = loader.get_brands()
min_year, max_year = loader.get_year_range()

# Main Layout
app.layout = dbc.Container([

    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Used Car Market Analysis", className="text-center mt-4"),
            html.P("Interactive dashboard for AutoScout24 data", className="text-center text-muted mb-5")
        ], width=12)
    ]),

    # Modal (Car Detail Popup)
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Car Details")),
        dbc.ModalBody(id="modal-body"),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-modal", className="ms-auto", n_clicks=0)
        ),
    ], id="car-modal", is_open=False, size="lg"),

    # Main Grid
    dbc.Row([
        # Left Panel: Filters
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Filters", className="card-title mb-4"),

                    # Filter: Brand
                    html.Div([
                        html.Label("Brand:", className="fw-bold mb-1"),
                        dcc.Dropdown(
                            id="filter-brand",
                            options=[{"label": b, "value": b} for b in brands],
                            multi=True,
                            placeholder="Select brands..."
                        )
                    ], className="mb-3"),

                    # Filter: Year
                    html.Div([
                        html.Label("Production Year:", className="fw-bold mb-1"),
                        dcc.RangeSlider(
                            id="filter-year",
                            min=min_year, max=max_year, step=1,
                            marks={i: str(i) for i in range(min_year, max_year + 1, 2)},
                            value=[min_year, max_year]
                        )
                    ], className="mb-3"),

                    # Filter: Fuel
                    html.Div([
                        html.Label("Fuel Type:", className="fw-bold mb-1"),
                        dcc.Dropdown(
                            id="filter-fuel",
                            options=[{"label": f, "value": f} for f in data["fuel"].unique()],
                            multi=True,
                            placeholder="All fuels"
                        )
                    ], className="mb-4"),

                    # Filter: Transmission
                    html.Div([
                        html.Label("Transmission:", className="fw-bold mb-2"),
                        dcc.Checklist(
                            id="filter-transmission",
                            options=[{"label": g, "value": g} for g in data["gear"].unique()],
                            value=[g for g in data["gear"].unique()],
                            inline=True,
                            inputClassName="me-2",
                            labelClassName="me-3"
                        )
                    ])
                ])
            ], className="bg-light border-0 shadow-sm h-100")
        ], xs=12, lg=3, className="mb-4 mb-lg-0"),

        # Right Panel: Charts and KPIs
        dbc.Col([
            dcc.Loading(
                id="loading-data",
                type="default",
                children=[
                    # KPI Cards
                    dbc.Row([
                        dbc.Col(dbc.Card(dbc.CardBody([
                            html.H6("Total Cars", className="card-title text-muted"),
                            html.H3(id="kpi-count", className="card-text text-primary")
                        ]), className="text-center shadow-sm border-0 h-100"), xs=12, md=4, className="mb-4"),

                        dbc.Col(dbc.Card(dbc.CardBody([
                            html.H6("Avg Price", className="card-title text-muted"),
                            html.H3(id="kpi-price", className="card-text text-success")
                        ]), className="text-center shadow-sm border-0 h-100"), xs=12, md=4, className="mb-4"),

                        dbc.Col(dbc.Card(dbc.CardBody([
                            html.H6("Avg Mileage", className="card-title text-muted"),
                            html.H3(id="kpi-mileage", className="card-text text-info")
                        ]), className="text-center shadow-sm border-0 h-100"), xs=12, md=4, className="mb-4"),
                    ]),

                    # 1st Row of Charts
                    dbc.Row([
                        dbc.Col(dbc.Card(dbc.CardBody([
                            dcc.Graph(id="graph-line-price-year")
                        ]), className="shadow-sm border-0 h-100"), xs=12, lg=6, className="mb-4"),

                        dbc.Col(dbc.Card(dbc.CardBody([
                            dcc.Graph(id="graph-scatter-price-mileage")
                        ]), className="shadow-sm border-0 h-100"), xs=12, lg=6, className="mb-4"),
                    ]),

                    # 2nd Row of Charts
                    dbc.Row([
                        dbc.Col(dbc.Card(dbc.CardBody([
                            dcc.Graph(id="graph-box-price-brand")
                        ]), className="shadow-sm border-0 h-100"), xs=12, lg=8, className="mb-4"),

                        dbc.Col(dbc.Card(dbc.CardBody([
                            dcc.Graph(id="graph-pie-transmission")
                        ]), className="shadow-sm border-0 h-100"), xs=12, lg=4, className="mb-4"),
                    ]),

                    # 3rd Row of Charts
                    dbc.Row([
                        dbc.Col(dbc.Card(dbc.CardBody([
                            dcc.Graph(id="graph-histogram-price")
                        ]), className="shadow-sm border-0 h-100"), xs=12, lg=6, className="mb-4"),

                        dbc.Col(dbc.Card(dbc.CardBody([
                            dcc.Graph(id="graph-heatmap-price-mileage-hp-year")
                        ]), className="shadow-sm border-0 h-100"), xs=12, lg=6, className="mb-4"),
                    ]),
                ]
            )
        ], xs=12, lg=9)

    ], className="mb-5")
], fluid=True)


# --- Callbacks (Interaction) ---

@app.callback(
    [
        Output("kpi-count", "children"),
        Output("kpi-price", "children"),
        Output("kpi-mileage", "children"),
        Output("graph-line-price-year", "figure"),
        Output("graph-scatter-price-mileage", "figure"),
        Output("graph-box-price-brand", "figure"),
        Output("graph-pie-transmission", "figure"),
        Output("graph-histogram-price", "figure"),
        Output("graph-heatmap-price-mileage-hp-year", "figure")
    ],
    [
        Input("filter-brand", "value"),
        Input("filter-year", "value"),
        Input("filter-fuel", "value"),
        Input("filter-transmission", "value")
    ]
)
def update_dashboard(selected_brands, year_range, selected_fuels, selected_gears):
    """ Updates dashboard based on selected filters """
    data_filtered = data.copy()

    # Apply Filters
    data_filtered = data_filtered[(data_filtered["year"] >= year_range[0]) & (data_filtered["year"] <= year_range[1])]

    if selected_brands:
        data_filtered = data_filtered[data_filtered["make"].isin(selected_brands)]
    if selected_fuels:
        data_filtered = data_filtered[data_filtered["fuel"].isin(selected_fuels)]
    if selected_gears:
        data_filtered = data_filtered[data_filtered["gear"].isin(selected_gears)]

    # Handle empty data (prevent crash)
    if data_filtered.empty:
        return "0", "0 €", "0 km", {}, {}, {}, {}, {}, {}

    # Calculate KPIs
    kpi_count = f"{len(data_filtered)}"
    kpi_price = f"{data_filtered['price'].mean():,.0f} €"
    kpi_mileage = f"{data_filtered['mileage'].mean():,.0f} km"

    return (
        kpi_count,
        kpi_price,
        kpi_mileage,
        charts.create_line_chart_price_year(data_filtered),
        charts.create_scatter_chart_price_mileage(data_filtered),
        charts.create_box_plot_price_brand(data_filtered),
        charts.create_pie_chart_transmission(data_filtered),
        charts.create_histogram_price(data_filtered),
        charts.create_heatmap_price_mileage_hp_year(data_filtered)
    )


@app.callback(
    [
        Output("car-modal", "is_open"),
        Output("modal-body", "children")
    ],
    [
        Input("graph-scatter-price-mileage", "clickData"),
        Input("close-modal", "n_clicks")
    ],
    [
        State("car-modal", "is_open")
    ]
)
def toggle_modal(click_data, n_clicks, is_open):
    """ Controls modal visibility (open/close) """
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Open on chart click
    if trigger_id == "graph-scatter-price-mileage" and click_data:
        try:
            car_id = click_data["points"][0]["customdata"][0]
            car_row = data.loc[car_id]
            # Create details table
            details = dbc.Table([html.Tbody([
                html.Tr([html.Td(k), html.Td(v, className="fw-bold")])
                for k, v in row_data(car_row).items()
            ])], striped=True, bordered=True)
            return True, details
        except:
            return True, "Error loading details"

    # Close button click
    elif trigger_id == "close-modal":
        return False, no_update

    return is_open, no_update


def row_data(row):
    """ Helper to format row data for display """
    return {
        "Make": row["make"], "Model": row["model"],
        "Price": f"{row['price']:,.0f} €",
        "Mileage": f"{row['mileage']:,.0f} km",
        "Year": row["year"], "Power": f"{row['hp']} HP",
        "Fuel": row["fuel"], "Transmission": row["gear"],
        "Offer Type": row["offerType"]
    }