import dash
from dash import html, Input, Output
import dash_bootstrap_components as dbc
from layout.navbar import navbar
from layout.pages.map import map_layout
from layout.pages.contact import contact_layout
from layout.pages.homepage import homepage_layout

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([navbar, homepage_layout])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return homepage_layout
    elif pathname == "/map":
        return map_layout
    elif pathname == "/contact":
        return contact_layout

    return dbc.Container(children=[
        dbc.Jumbotron(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognised..."),
            ], className="mt-5")
        ],
    )


if __name__ == "__main__":
    app.run_server(debug=True)
