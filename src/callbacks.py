from dash import Dash, html, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc
import src.charts as charts
from src import constants
from src.data_loader import DataLoader
from src.helpers import format_number, create_insight_icon


def setup(app: Dash, loader: DataLoader):
    data = loader.data

    # Cascading model dropdown callback
    @app.callback(
        [
            Output("filter-model", "options"),
            Output("filter-model", "disabled"),
            Output("filter-model", "value")  # Added output to clear value
        ],
        [
            Input("filter-brand", "value")
        ]
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

    # Main dashboard callback
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
        metadata = loader.get_metadata()
        data_filtered = data.copy()

        # Year filter
        data_filtered = data_filtered[
            (data_filtered["year"] >= year_range[0]) &
            (data_filtered["year"] <= year_range[1])
            ]

        # Price robust filtering
        if price_range[1] >= metadata.max_price:
            data_filtered = data_filtered[data_filtered["price"] >= price_range[0]]
        else:
            data_filtered = data_filtered[
                (data_filtered["price"] >= price_range[0]) &
                (data_filtered["price"] <= price_range[1])
                ]

        # Mileage robust filtering
        if mileage_range[1] >= metadata.max_mileage:
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

        # Insights
        if not data_filtered.empty:
            avg_price_selection = data_filtered["price"].mean()
            if metadata.average_price > 0:
                price_diff_pct = ((avg_price_selection - metadata.average_price) / metadata.average_price) * 100
            else:
                price_diff_pct = 0

            price_status = "Premium" if price_diff_pct > 0 else "Budget-Friendly"
            price_desc = "above market avg" if price_diff_pct > 0 else "below market avg"
            price_color = constants.COLOR_DANGER if price_diff_pct > 0 else constants.COLOR_ACCENT

            # Single Brand Selected
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

            # Or multiple brands or global
            else:
                if not data_filtered["make"].dropna().empty:
                    top_brand = data_filtered["make"].value_counts().idxmax()
                    top_count = data_filtered["make"].value_counts().max()
                    share = (top_count / len(data_filtered)) * 100
                else:
                    top_brand, top_count, share = "N/A", 0, 0

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
        [
            Output("car-modal", "is_open"),
            Output("modal-body", "children")
        ],
        [
            Input("graph-scatter-price-mileage", "clickData"),
        ],
        [
            State("car-modal", "is_open")
        ]
    )
    def toggle_modal(click_data, is_open):
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
                    for k, v in _row_data(car_row).items()
                ])], borderless=True, size="sm")
                return True, details
            except:
                return True, "Error loading details"
        elif trigger_id == "close-modal":
            return False, no_update
        return is_open, no_update

    def _row_data(row):
        return {
            "Make": row["make"], "Model": row["model"],
            "Price": f"{row['price']:,.0f} €",
            "Mileage": f"{row['mileage']:,.0f} km",
            "Year": row["year"], "Power": f"{row['hp']} HP",
            "Fuel": row["fuel"], "Transmission": row["gear"]
        }
