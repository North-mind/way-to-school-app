import dash_bootstrap_components as dbc
from dash import html


def create_custom_card(title: str, desc: str):
    return dbc.Card(
        dbc.CardBody(
            [
                html.H4(title, className="card-title"),
                html.H6("O mnie", className="card-subtitle"),
                html.P(desc,
                    className="card-text",
                ),
                dbc.CardLink("Github", href="#"),
                dbc.CardLink("LinkedIN", href="https://google.com"),
            ]
        ),
        style={"width": "18rem"},
    )
