import dash_bootstrap_components as dbc
from dash import html

contact_layout = dbc.Container(
    children=[
        dbc.Alert(
            [
                "Zapraszamy do kontaktu poprzez LinkedIn: ",
                html.A(" Łukasz Sawaniewski", href="https://www.linkedin.com/in/sawaniewski/", className="alert-link"),
                html.A(" Magdalena Lipka", href="https://www.linkedin.com/in/magdalena-lipka-11854164/", className="alert-link"),
                html.A(" Dawid Malarz", href="https://www.linkedin.com/in/dawid-malarz", className="alert-link"),
            ],
            color="info",
            className="mt-5"
        ),
    ],
)