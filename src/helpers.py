from dash import Dash, html, dcc, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc


def format_number(value):
    """ Formats large numbers to human-readable string (e.g. 1.2k, 1.5M) """
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}k"
    else:
        return f"{value:.0f}"

def create_kpi_card(title, icon_class, id_value, color_hex, tooltip_text):
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.I(className=f"{icon_class} fa-2x mb-3", style={"color": color_hex}),
            ], className="text-center position-relative"),

            html.I(
                className="fa-regular fa-circle-question text-muted position-absolute top-0 end-0 m-2",
                id=f"tooltip-{id_value}",
                style={"cursor": "pointer", "fontSize": "0.9rem"}
            ),
            dbc.Tooltip(tooltip_text, target=f"tooltip-{id_value}", placement="top"),

            html.H6(title, className="text-muted text-center text-uppercase", style={"fontSize": "0.8rem"}),
            html.H3(id=id_value, className="card-text text-center fw-bold", style={"color": color_hex}),
        ]),
        className="shadow-sm border-0 h-100 mb-4 hover-shadow position-relative"
    )

def create_insight_icon(icon_class, bg_color_hex):
    return html.Div(
        html.I(className=f"{icon_class} text-white", style={"fontSize": "1.2rem"}),
        className=f"rounded-circle d-flex align-items-center justify-content-center me-3 shadow-sm",
        style={"minWidth": "45px", "height": "45px", "backgroundColor": bg_color_hex}
    )

def row_data(row):
    return {
        "Make": row["make"], "Model": row["model"],
        "Price": f"{row['price']:,.0f} €",
        "Mileage": f"{row['mileage']:,.0f} km",
        "Year": row["year"], "Power": f"{row['hp']} HP",
        "Fuel": row["fuel"], "Transmission": row["gear"]
    }

