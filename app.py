import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, no_update

from layout.navbar import navbar
from layout.pages.homepage import homepage_layout
from layout.callbacks import get_callbacks

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions = True)

app.layout = html.Div([navbar, homepage_layout])

#loading_style = {'align-self': 'center'}

get_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)
