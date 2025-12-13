from dash import Dash, html, dcc, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc
from src.data_loader import DataLoader
import src.charts as charts
from src import constants
import math
from src.helpers import create_kpi_card, format_number, create_insight_icon

# --- App Initialization ---
external_stylesheets = [
    dbc.themes.FLATLY,
    constants.FONT_AWESOME_CDN,
]
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# --- Data Loading ---
loader = DataLoader()
data = loader.load_data()
brands = loader.get_brands()
min_year, max_year = loader.get_year_range()
global_average_price = data["price"].mean()

# Calculate robust ranges for sliders
min_price = math.floor(data["price"].min())
max_price = math.ceil(data["price"].quantile(0.98))
min_mileage = math.floor(data["mileage"].min())
max_mileage = math.ceil(data["mileage"].quantile(0.98))


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

        # 2. Header
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
                            min=min_price, max=max_price, step=1000,
                            value=[min_price, max_price],
                            marks={
                                min_price: f"{min_price / 1000:.0f}k",
                                max_price: f"{max_price / 1000:.0f}k+"
                            },
                            tooltip={"placement": "bottom", "always_visible": False},
                            className="mb-3"
                        ),

                        # Mileage Range (Fixed: Only Min/Max Marks)
                        html.Label([html.I(className="fa-solid fa-road me-2"), "Mileage Range"], className="fw-bold"),
                        dcc.RangeSlider(
                            id="filter-mileage",
                            min=min_mileage, max=max_mileage, step=5000,
                            value=[min_mileage, max_mileage],
                            marks={
                                min_mileage: f"{min_mileage / 1000:.0f}k",
                                max_mileage: f"{max_mileage / 1000:.0f}k+"
                            },
                            tooltip={"placement": "bottom", "always_visible": False},
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

                    # TABS Section
                    dbc.Tabs([

                        # TAB 1: General Overview
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

                        # TAB 2: Detailed Analysis
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

                        # TAB 3: Correlations
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


# --- Callbacks ---

# 1. Callback for Cascading Model Dropdown
@app.callback(
    [
        Output("filter-model", "options"),
        Output("filter-model", "disabled"),
        Output("filter-model", "value")  # Added output to clear value
    ],
    Input("filter-brand", "value")
)
def update_model_options(selected_brands):
    """ Updates model dropdown based on selected brands and resets selection """
    if not selected_brands:
        return [], True, []  # Reset options, disable, clear value

    # Filter data for selected brands and get unique models
    relevant_models = data[data["make"].isin(selected_brands)]["model"].dropna().unique()
    sorted_models = sorted(relevant_models)

    options = [{"label": m, "value": m} for m in sorted_models]
    # Return new options, enable dropdown, and CLEAR previous value (return [])
    return options, False, []


# 2. Main Dashboard Callback
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
        Input("filter-model", "value"),
        Input("filter-year", "value"),
        Input("filter-price", "value"),
        Input("filter-mileage", "value"),
        Input("filter-fuel", "value"),
        Input("filter-transmission", "value")
    ]
)
def update_dashboard(selected_brands, selected_models, year_range, price_range, mileage_range, selected_fuels,
                     selected_gears):
    data_filtered = data.copy()

    # Apply Filters
    # Year
    data_filtered = data_filtered[
        (data_filtered["year"] >= year_range[0]) &
        (data_filtered["year"] <= year_range[1])
        ]
    # Price (Robust filtering: allow values slightly above slider max to capture edge cases)
    # If the user selects the absolute max on slider, include everything above it too (the 2% outliers)
    if price_range[1] >= max_price:
        data_filtered = data_filtered[data_filtered["price"] >= price_range[0]]
    else:
        data_filtered = data_filtered[
            (data_filtered["price"] >= price_range[0]) &
            (data_filtered["price"] <= price_range[1])
            ]

    # Mileage (Same logic for outliers)
    if mileage_range[1] >= max_mileage:
        data_filtered = data_filtered[data_filtered["mileage"] >= mileage_range[0]]
    else:
        data_filtered = data_filtered[
            (data_filtered["mileage"] >= mileage_range[0]) &
            (data_filtered["mileage"] <= mileage_range[1])
            ]

    if selected_brands:
        data_filtered = data_filtered[data_filtered["make"].isin(selected_brands)]

    if selected_models:
        data_filtered = data_filtered[data_filtered["model"].isin(selected_models)]

    if selected_fuels:
        data_filtered = data_filtered[data_filtered["fuel"].isin(selected_fuels)]
    if selected_gears:
        data_filtered = data_filtered[data_filtered["gear"].isin(selected_gears)]

    if data_filtered.empty:
        return "0", "0", "0", "No data available", {}, {}, {}, {}, {}, {}

    # KPIs
    kpi_count = f"{format_number(len(data_filtered))}"
    kpi_price = f"{format_number(data_filtered['price'].mean())} €"
    kpi_mileage = f"{format_number(data_filtered['mileage'].mean())} km"

    # --- Smart Insight Logic ---
    # NO try-except here - errors will be exposed in console/debug if any
    if not data_filtered.empty:
        avg_price_selection = data_filtered["price"].mean()
        if global_average_price > 0:
            price_diff_pct = ((avg_price_selection - global_average_price) / global_average_price) * 100
        else:
            price_diff_pct = 0

        price_status = "Premium" if price_diff_pct > 0 else "Budget-Friendly"
        price_desc = "above market avg" if price_diff_pct > 0 else "below market avg"
        price_color = constants.COLOR_DANGER if price_diff_pct > 0 else constants.COLOR_ACCENT

        # Case 1: Single Brand Selected
        if selected_brands and len(selected_brands) == 1:
            # If models are selected, show specific model info
            if selected_models and len(selected_models) == 1:
                target_name = selected_models[0]
                target_type = "Specific Model"
                count = len(data_filtered)
                share = 100
            elif not data_filtered["model"].dropna().empty:
                target_name = data_filtered["model"].value_counts().idxmax()
                count = data_filtered["model"].value_counts().max()
                share = (count / len(data_filtered)) * 100
                target_type = "Most Listed Model"
            else:
                target_name = "N/A"
                count, share = 0, 0
                target_type = "Model"

            insight_content = [
                html.P([
                    f"{target_type}: ",
                    html.Span(target_name, className="fw-bold", style={"color": constants.COLOR_PRIMARY}),
                    html.Br(),
                    html.Small(f"({count} listings, {share:.1f}% share)", className="text-muted")
                ], className="mb-2"),
                html.P([
                    "Price Positioning: ",
                    html.Span(f"{price_status}", className="fw-bold", style={"color": price_color}),
                    html.Br(),
                    html.Small(f"Avg. price is {abs(price_diff_pct):.1f}% {price_desc}.", className="text-muted")
                ], className="mb-0 small border-top pt-2")
            ]
            icon = "fa-solid fa-car-side"
            icon_color = constants.COLOR_PRIMARY

        # Case 2: Multiple Brands or Global
        else:
            if not data_filtered["make"].dropna().empty:
                top_brand = data_filtered["make"].value_counts().idxmax()
                top_count = data_filtered["make"].value_counts().max()
                share = (top_count / len(data_filtered)) * 100
            else:
                top_brand, top_count, share = "N/A", 0, 0

            title_text = "Multi-Brand Analysis" if selected_brands else "Global Market Trends"

            insight_content = [
                html.P([
                    "Dominant Brand: ",
                    html.Span(top_brand, className="fw-bold", style={"color": constants.COLOR_ACCENT}),
                    html.Br(),
                    html.Small(f"({top_count} listings, {share:.1f}% of selection)", className="text-muted")
                ], className="mb-2"),
                html.P([
                    "Price Trend: ",
                    html.Span(f"{price_status}", className="fw-bold", style={"color": price_color}),
                    html.Br(),
                    html.Small(f"Selection is {abs(price_diff_pct):.1f}% {price_desc}.", className="text-muted")
                ], className="mb-0 small border-top pt-2")
            ]
            icon = "fa-solid fa-chart-pie"
            icon_color = constants.COLOR_ACCENT

        insight = dbc.Card([
            dbc.CardBody([
                html.Div([
                    create_insight_icon(icon, icon_color),
                    html.Div([
                        html.H5("Analytic Insight", className="card-title mb-0"),
                        html.Small("Key Findings", className="text-muted")
                    ])
                ], className="d-flex align-items-center mb-3"),
                html.Div(insight_content)
            ])
        ], className="border-0 shadow-sm mb-3", style={"backgroundColor": "#f8f9fa"})

    else:
        insight = dbc.Alert("No data available", color="warning")

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