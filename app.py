from fcntl import F_SETSIG
import dash
from dash import html, Input, Output, dcc, no_update
import dash_bootstrap_components as dbc
from layout.navbar import navbar
from layout.pages.map import map_layout
from layout.pages.contact import contact_layout
from layout.pages.homepage import homepage_layout
import pandas as pd
import plotly.express as px

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([navbar, homepage_layout])

df = pd.read_csv("data/school.csv")

fig = px.scatter_mapbox(
      df,
      lat="lon",
      lon="lat",
      hover_name="Nazwa",
      #hover_data=['rspo','Kategoria_szkoły', 'Województwo','Miejscowość','Ulica', "Status", "Data_założenia"],
      mapbox_style="carto-positron",
      zoom=6,
      height=900,
      color="Kategoria_szkoły",
    
)
fig.update_layout(
      margin={"r": 0, "t": 0, "l": 0, "b": 0},
      mapbox_center={"lat": 52.1089496, "lon": 19.443120},
      hovermode="closest",
      #annotations=annotations,
)

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
@app.callback(
    Output("county-choropleth", "figure"),
    [
        #Input("school_types-indicator", "value"),
        Input("wojewodztwo-indicator", "value")
    ],
)
def display_selected_data(wojewodztwo):
    
    #dff = df[df["Kategoria_szkoły"]=='Szkoła podstawowa']
    dff = df[(df["Województwo"].isin(wojewodztwo))]
    fig = px.scatter_mapbox(
    dff,
    lat="lon",
    lon="lat",
    hover_name="Nazwa",
    #hover_data=['Kategoria_szkoły', 'Województwo','Miejscowość','Ulica', "Status", "Data_założenia",'rspo'],
    mapbox_style="carto-positron",
    zoom=6,
    height=900,
    color="Kategoria_szkoły",
    
    )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox_center={"lat": 52.1089496, "lon": 19.443120},
        hovermode="closest",
        #annotations=annotations,
    )

    return fig

@app.callback(
     Output('tabs-example-content-1', 'children'),
     Input('tabs-example-1', 'value')
 )

def render_content(tab):
     if tab == 'tab-1':
         return html.Div([
             html.Div(
                            id="tabs-content'",
                            children=[
                                dcc.Graph(
                                    id="county-choropleth",
                                    figure=fig
                                ),
                                dcc.Tooltip(
                                    id="graph-tooltip-1",
                                    background_color="darkblue",
                                    border_color="blue",
                                    style={'color':'white', 'width': '450px', 'white-space': 'normal'},
                                    loading_text='Wczytywanie danych ...'),
                               
                                
                            ],
                            className="mt-3"
                         ),
         ])
     elif tab == 'tab-2':
         return html.Div([
             html.H3('Tab content 2'),

             dcc.Graph(
                 figure=dict(
                     data=[dict(
                         x=[1, 2, 3],
                         y=[5, 10, 6],
                         type='bar'
                     )]
                 )
             )
         ])

@app.callback(
    Output("graph-tooltip-1", "show"),
    Output("graph-tooltip-1", "bbox"),
    Output("graph-tooltip-1", "children"),
    Input("county-choropleth", "hoverData"),
)
def update_tooltip_content(hoverData):
    if hoverData is None:
        return no_update

    pt = hoverData["points"][0]
    bbox = pt["bbox"]
    lat = pt['lat']
    lon = pt['lon']

    school = df[(df['lon'] == lat) & (df['lat'] == lon)].head(1)

    def my_repl(value):
        return str(value).replace('[\'','').replace('\']','')

    name = my_repl(school['Nazwa'].values)
    kat = my_repl(school['Kategoria_szkoły'].values)
    status = my_repl(school['Status'].values)
    
    woj = my_repl(school['Województwo'].values)
    pow = my_repl(school['Powiat'].values)
    miejscowosc = my_repl(school['Miejscowość'].values)
    ul = my_repl(school['Ulica'].values)
    nr_bud = my_repl(school['Nr_budynku'].values)
    nr_loc = my_repl(school['Nr_lokalu'].values)

    def adres(ul):
        if ul != '[nan]':
            ulica = my_repl(ul) + ' ' + my_repl(nr_bud)
        else:
            ulica = my_repl(miejscowosc) + ' ' + my_repl(nr_bud) 

        return ulica

    ulica = adres(ul)

    children = [
        html.P(name, style={'font-weight': 'bold', 'font-size': '15px'}),
        html.P('Typ: {} ({})'.format(kat, status), style={'font-weight': 'bold', 'font-size': '15px'}),
        html.P('Miejscowość: {}'.format(miejscowosc), style={'font-size': '15px'}),
        html.P('Adres: {}'.format(ulica), style={'font-size': '15px'}),
        html.P('Woj: {}'.format(woj), style={'font-size': '15px'}),

    ]


    return True, bbox, children

if __name__ == "__main__":
    app.run_server(debug=True)
