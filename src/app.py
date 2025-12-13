from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from src.data_loader import DataLoader
from src import constants
from src.helpers import create_kpi_card
import src.callbacks as callbacks

# Initialize app
app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.FLATLY,
        constants.FONT_AWESOME_CDN,
    ]
)
server = app.server

# Load data
loader = DataLoader()
data = loader.load_data()
brands = loader.get_brands()
metadata = loader.get_metadata()

# Setup callback for app
callbacks.setup(app, loader)

# Main layout
app.layout = html.Div([
    # Navigation Bar
    dbc.NavbarSimple(
        brand="Car Sales Dashboard",
        brand_href="#",
        color="primary",
        dark=True,
        className="mb-4 shadow-sm"
    ),

    dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2("Market Overview", className="fw-light"),
                html.P("Real-time analysis of used car sales data.", className="text-muted")
            ], width=8),
            dbc.Col([
                html.Div(className="text-end text-muted", children=[
                    html.I(className="fa-regular fa-clock me-2"),
                    "Data Status: Up to date"
                ])
            ], width=4, className="d-flex align-items-center justify-content-end")
        ], className="mb-4 align-items-center"),

        # Main Grid
        dbc.Row([
            # Filters
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Filter Data", className="bg-white fw-bold"),
                    dbc.CardBody([
                        # Smart Insight Container
                        html.Div(id="smart-insight", className="mb-4"),

                        # Brand
                        html.Label([html.I(className="fa-solid fa-car me-2"), "Brand"], className="fw-bold mt-2"),
                        dcc.Dropdown(
                            id="filter-brand",
                            options=[{"label": b, "value": b} for b in brands],
                            multi=True,
                            placeholder="Select brand...",
                            className="mb-2"
                        ),

                        # Model (Cascading Filter)
                        html.Label([html.I(className="fa-solid fa-car-side me-2"), "Model"], className="fw-bold mt-2"),
                        dcc.Dropdown(
                            id="filter-model",
                            options=[],  # Populated by callback
                            multi=True,
                            placeholder="Select model...",
                            disabled=True,  # Enabled only after brand selection
                            className="mb-3"
                        ),

                        # Price Range (Fixed: Only Min/Max Marks)
                        html.Label([html.I(className="fa-solid fa-euro-sign me-2"), "Price Range"],
                                   className="fw-bold"),
                        dcc.RangeSlider(
                            id="filter-price",
                            min=metadata.min_price, max=metadata.max_price, step=1000,
                            value=[metadata.min_price, metadata.max_price],
                            marks={
                                metadata.min_price: f"{metadata.min_price / 1000:.0f}k",
                                metadata.max_price: f"{metadata.max_price / 1000:.0f}k+"
                            },
                            tooltip={"placement": "bottom", "always_visible": False},
                            className="mb-3"
                        ),

                        # Mileage Range
                        html.Label([html.I(className="fa-solid fa-road me-2"), "Mileage Range"], className="fw-bold"),
                        dcc.RangeSlider(
                            id="filter-mileage",
                            min=metadata.min_mileage, max=metadata.max_mileage, step=5000,
                            value=[metadata.min_mileage, metadata.max_mileage],
                            marks={
                                metadata.min_mileage: f"{metadata.min_mileage / 1000:.0f}k",
                                metadata.max_mileage: f"{metadata.max_mileage / 1000:.0f}k+"
                            },
                            tooltip={"placement": "bottom", "always_visible": False},
                            className="mb-3"
                        ),

                        # Year
                        html.Label([html.I(className="fa-regular fa-calendar me-2"), "Year Range"],
                                   className="fw-bold"),
                        dcc.RangeSlider(
                            id="filter-year",
                            min=metadata.min_year, max=metadata.max_year, step=1,
                            marks={i: str(i) for i in range(metadata.min_year, metadata.max_year + 1, 3)},
                            value=[metadata.min_year, metadata.max_year],
                            className="mb-4"
                        ),

                        # Fuel
                        html.Label([html.I(className="fa-solid fa-gas-pump me-2"), "Fuel Type"], className="fw-bold"),
                        dcc.Dropdown(
                            id="filter-fuel",
                            options=[{"label": f, "value": f} for f in data["fuel"].unique()],
                            multi=True,
                            placeholder="All fuels",
                            className="mb-3"
                        ),

                        # Transmission
                        html.Label([html.I(className="fa-solid fa-gears me-2"), "Transmission"], className="fw-bold"),
                        dcc.Checklist(
                            id="filter-transmission",
                            options=[{"label": g, "value": g} for g in data["gear"].unique()],
                            value=[g for g in data["gear"].unique()],
                            inline=True,
                            inputClassName="me-2",
                            labelClassName="me-3"
                        )
                    ])
                ], className="border-0 shadow-sm")
            ], xs=12, lg=3, className="mb-4"),

            # Graphs (in tabs), etc
            dbc.Col([
                dcc.Loading(id="loading", type="cube", color=constants.COLOR_PRIMARY, children=[

                    # KPIs
                    dbc.Row([
                        dbc.Col(
                            create_kpi_card("Total Vehicles", "fa-solid fa-list", "kpi-count", constants.COLOR_PRIMARY,
                                            "Total number of cars matching current filters."), width=4),
                        dbc.Col(
                            create_kpi_card("Avg. Price", "fa-solid fa-euro-sign", "kpi-price", constants.COLOR_ACCENT,
                                            "Average listing price for the selected cars."), width=4),
                        dbc.Col(create_kpi_card("Avg. Mileage", "fa-solid fa-road", "kpi-mileage", constants.COLOR_INFO,
                                                "Average mileage (km) for the selected cars."), width=4),
                    ]),

                    # Tabs for graphs
                    dbc.Tabs([

                        # General Overview
                        dbc.Tab(label="Market Overview", tab_id="tab-overview", children=[
                            html.Br(),
                            dbc.Row([
                                dbc.Col(
                                    dbc.Card(dcc.Graph(id="graph-sunburst"), className="shadow-sm border-0 mb-4 p-2"),
                                    width=12),
                            ]),
                            dbc.Row([
                                dbc.Col(dbc.Card(dcc.Graph(id="graph-line-price-year"),
                                                 className="shadow-sm border-0 mb-4 p-2"), lg=8),
                                dbc.Col(dbc.Card(dcc.Graph(id="graph-pie-transmission"),
                                                 className="shadow-sm border-0 mb-4 p-2"), lg=4),
                            ])
                        ]),

                        # Detailed Analysis
                        dbc.Tab(label="Price & Performance Analysis", tab_id="tab-analysis", children=[
                            html.Br(),
                            dbc.Row([
                                dbc.Col(dbc.Card(dcc.Graph(id="graph-scatter-price-mileage"),
                                                 className="shadow-sm border-0 mb-4 p-2"), width=12),
                            ]),
                            dbc.Row([
                                dbc.Col(dbc.Card(dcc.Graph(id="graph-box-price-brand"),
                                                 className="shadow-sm border-0 mb-4 p-2"), width=12),
                            ])
                        ]),

                        # Correlations
                        dbc.Tab(label="Correlations", tab_id="tab-stats", children=[
                            html.Br(),
                            dbc.Row([
                                dbc.Col(dbc.Card(dcc.Graph(id="graph-heatmap-price-mileage-hp-year"),
                                                 className="shadow-sm border-0 mb-4 p-2"), width=12),
                            ])
                        ]),

                    ], id="tabs", active_tab="tab-overview", className="mb-3")

                ])
            ], xs=12, lg=9)
        ]),

        # Footer
        dbc.Row([
            dbc.Col(html.P("© 2025 Car Sales Analytics Project", className="text-center text-muted small mt-4"),
                    width=12)
        ])

    ], fluid=True),

    # Modal
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Vehicle Detail"), close_button=True),
        dbc.ModalBody(id="modal-body"),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-modal", className="ms-auto", n_clicks=0)
        ),
    ], id="car-modal", is_open=False, size="lg", centered=True),

], style={"backgroundColor": "#f8f9fa", "minHeight": "100vh"})
