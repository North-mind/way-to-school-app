import dash_bootstrap_components as dbc
from dash import dcc, html

navbar = html.Nav([
    html.Div([
        dcc.Location(id="url"),
        dbc.NavbarSimple(
            children=[
                dbc.NavLink("Strona Główna", href="/", active="exact"),
                dbc.NavLink("Mapa", href="/map", active="exact"),
                dbc.NavLink("Kontakt", href="/contact", active="exact")
            ],
            brand="Way-To-School",
        )
    ], className="container-fluid")
], className="navbar navbar-light bg-light")