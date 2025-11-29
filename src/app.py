from dash import Dash, html, dcc, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc
from src.data_loader import DataLoader
import src.charts as charts
from src import constants

# --- App Initialization ---
external_stylesheets = [
    dbc.themes.FLATLY,
    "https://use.fontawesome.com/releases/v6.4.0/css/all.css"
]
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# --- Data Loading ---
loader = DataLoader()
data = loader.load_data()
brands = loader.get_brands()
min_year, max_year = loader.get_year_range()
# Calculate global average price for comparison logic
GLOBAL_AVG_PRICE = data["price"].mean()


# --- Components ---

def create_kpi_card(title, icon_class, id_value, color):
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.I(className=f"{icon_class} fa-2x text-{color} mb-3"),
            ], className="text-center"),
            html.H6(title, className="text-muted text-center text-uppercase", style={"fontSize": "0.8rem"}),
            html.H3(id=id_value, className="card-text text-center fw-bold"),
        ]),
        className="shadow-sm border-0 h-100 mb-4 hover-shadow"
    )


# --- Main Layout ---
app.layout = html.Div([

    # 1. Navigation Bar
    dbc.NavbarSimple(
        brand="AutoScout24 Analytics",
        brand_href="#",
        color="primary",
        dark=True,
        className="mb-4 shadow-sm"
    ),

    dbc.Container([

        # 2. Header Section
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

        # 3. Main Grid
        dbc.Row([

            # --- LEFT PANEL: FILTERS ---
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Filter Data", className="bg-white fw-bold"),
                    dbc.CardBody([
                        # Smart Insight (Updated Logic)
                        dbc.Alert(
                            id="smart-insight",
                            color="info",
                            className="mb-4 small",
                            style={"borderLeft": "4px solid #3498DB", "backgroundColor": "#eef9fd"}
                        ),

                        # Brand
                        html.Label([html.I(className="fa-solid fa-car me-2"), "Brand"], className="fw-bold mt-2"),
                        dcc.Dropdown(
                            id="filter-brand",
                            options=[{"label": b, "value": b} for b in brands],
                            multi=True,
                            placeholder="Select brand...",
                            className="mb-3"
                        ),

                        # Year
                        html.Label([html.I(className="fa-regular fa-calendar me-2"), "Year Range"],
                                   className="fw-bold"),
                        dcc.RangeSlider(
                            id="filter-year",
                            min=min_year, max=max_year, step=1,
                            marks={i: str(i) for i in range(min_year, max_year + 1, 3)},
                            value=[min_year, max_year],
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

            # --- RIGHT PANEL: VISUALIZATIONS ---
            dbc.Col([
                dcc.Loading(id="loading", type="dot", children=[

                    # KPIs
                    dbc.Row([
                        dbc.Col(create_kpi_card("Total Vehicles", "fa-solid fa-list", "kpi-count", "primary"), width=4),
                        dbc.Col(create_kpi_card("Avg. Price", "fa-solid fa-euro-sign", "kpi-price", "success"),
                                width=4),
                        dbc.Col(create_kpi_card("Avg. Mileage", "fa-solid fa-road", "kpi-mileage", "info"), width=4),
                    ]),

                    # Sunburst Chart
                    dbc.Row([
                        dbc.Col(dbc.Card(dcc.Graph(id="graph-sunburst"), className="shadow-sm border-0 mb-4 p-2"),
                                width=12),
                    ]),

                    # Charts Row 1
                    dbc.Row([
                        dbc.Col(
                            dbc.Card(dcc.Graph(id="graph-line-price-year"), className="shadow-sm border-0 mb-4 p-2"),
                            lg=8),
                        dbc.Col(
                            dbc.Card(dcc.Graph(id="graph-pie-transmission"), className="shadow-sm border-0 mb-4 p-2"),
                            lg=4),
                    ]),

                    # Charts Row 2
                    dbc.Row([
                        dbc.Col(dbc.Card(dcc.Graph(id="graph-scatter-price-mileage"),
                                         className="shadow-sm border-0 mb-4 p-2"), lg=12),
                    ]),

                    # Charts Row 3
                    dbc.Row([
                        dbc.Col(
                            dbc.Card(dcc.Graph(id="graph-box-price-brand"), className="shadow-sm border-0 mb-4 p-2"),
                            lg=6),
                        dbc.Col(dbc.Card(dcc.Graph(id="graph-heatmap-price-mileage-hp-year"),
                                         className="shadow-sm border-0 mb-4 p-2"), lg=6),
                    ])
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


# --- Callbacks ---

@app.callback(
    [
        Output("kpi-count", "children"),
        Output("kpi-price", "children"),
        Output("kpi-mileage", "children"),
        Output("smart-insight", "children"),
        Output("graph-sunburst", "figure"),
        Output("graph-line-price-year", "figure"),
        Output("graph-scatter-price-mileage", "figure"),
        Output("graph-box-price-brand", "figure"),
        Output("graph-pie-transmission", "figure"),
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
    data_filtered = data.copy()

    # Apply Filters
    data_filtered = data_filtered[(data_filtered["year"] >= year_range[0]) & (data_filtered["year"] <= year_range[1])]
    if selected_brands:
        data_filtered = data_filtered[data_filtered["make"].isin(selected_brands)]
    if selected_fuels:
        data_filtered = data_filtered[data_filtered["fuel"].isin(selected_fuels)]
    if selected_gears:
        data_filtered = data_filtered[data_filtered["gear"].isin(selected_gears)]

    if data_filtered.empty:
        return "0", "0", "0", "No data available", {}, {}, {}, {}, {}, {}

    # KPIs
    kpi_count = f"{len(data_filtered)}"
    kpi_price = f"{data_filtered['price'].mean():,.0f} €"
    kpi_mileage = f"{data_filtered['mileage'].mean():,.0f} km"

    # --- Smart Insight Logic (Refined) ---
    if not data_filtered.empty:
        # Case 1: Brands are selected -> Show Model info & Price comparison
        if selected_brands:
            # Most popular model in selection
            top_model = data_filtered["model"].value_counts().idxmax()
            top_model_count = data_filtered["model"].value_counts().max()
            model_share = (top_model_count / len(data_filtered)) * 100

            # Price comparison vs Global Market
            avg_price_selection = data_filtered["price"].mean()
            price_diff_pct = ((avg_price_selection - GLOBAL_AVG_PRICE) / GLOBAL_AVG_PRICE) * 100
            price_status = "higher" if price_diff_pct > 0 else "lower"

            # Wrap content in a Div to fix React error
            insight_content = html.Div([
                html.Strong(f"Top Model: {top_model}"),
                f" represents {model_share:.1f}% of selection.",
                html.Br(),
                html.Span(f"Price is {abs(price_diff_pct):.1f}% {price_status} than market avg.",
                          className="text-muted small")
            ])

        # Case 2: No brand selected (Market View) -> Show Brand Leader & Fuel Trend
        else:
            top_brand = data_filtered["make"].value_counts().idxmax()
            top_brand_share = (data_filtered["make"].value_counts().max() / len(data_filtered)) * 100

            top_fuel = data_filtered["fuel"].value_counts().idxmax()

            # Wrap content in a Div to fix React error
            insight_content = html.Div([
                html.Strong(f"Market Leader: {top_brand}"),
                f" ({top_brand_share:.1f}% share).",
                html.Br(),
                f"Dominant fuel type is {top_fuel}."
            ])

        # Final structure wrapped properly
        insight = html.Div([
            html.I(className="fa-solid fa-lightbulb me-2 text-info"),
            insight_content
        ], className="d-flex align-items-start")
    else:
        insight = "No data"

    return (
        kpi_count,
        kpi_price,
        kpi_mileage,
        insight,
        charts.create_sunburst_chart(data_filtered),
        charts.create_line_chart_price_year(data_filtered),
        charts.create_scatter_chart_price_mileage(data_filtered),
        charts.create_box_plot_price_brand(data_filtered),
        charts.create_pie_chart_transmission(data_filtered),
        charts.create_heatmap_price_mileage_hp_year(data_filtered)
    )


@app.callback(
    [Output("car-modal", "is_open"), Output("modal-body", "children")],
    [Input("graph-scatter-price-mileage", "clickData"), Input("close-modal", "n_clicks")],
    [State("car-modal", "is_open")]
)
def toggle_modal(click_data, n_clicks, is_open):
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "graph-scatter-price-mileage" and click_data:
        try:
            car_id = click_data["points"][0]["customdata"][0]
            car_row = data.loc[car_id]
            details = dbc.Table([html.Tbody([
                html.Tr([html.Td(k, className="text-muted"), html.Td(v, className="fw-bold")])
                for k, v in row_data(car_row).items()
            ])], borderless=True, size="sm")
            return True, details
        except:
            return True, "Error loading details"
    elif trigger_id == "close-modal":
        return False, no_update
    return is_open, no_update


def row_data(row):
    return {
        "Make": row["make"], "Model": row["model"],
        "Price": f"{row['price']:,.0f} €",
        "Mileage": f"{row['mileage']:,.0f} km",
        "Year": row["year"], "Power": f"{row['hp']} HP",
        "Fuel": row["fuel"], "Transmission": row["gear"]
    }