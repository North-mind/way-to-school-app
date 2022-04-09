import dash_bootstrap_components as dbc
from dash import html

homepage_layout = html.Content(
    children=[
            dbc.Container(
                children=[
                    html.H1("HomePage"),
                ],
            )
        ],
    id="page-content"
)