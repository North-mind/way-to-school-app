from fcntl import F_SETSIG
import os
from turtle import right
import dash
import dash_bootstrap_components as dbc
from numpy import NaN
import pandas as pd
import plotly.express as px
import numpy as np
from dash import Input, Output, dcc, html, no_update

from geodata.adm_units import AdmUnits
from layout.navbar import navbar
from layout.pages.contact import contact_layout
from layout.pages.homepage import homepage_layout
from layout.pages.map import map_layout

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([navbar, homepage_layout])

df = pd.read_csv("data/school.csv")
#df['dl_centroid_pow'] = (np.sqrt(np.power((df.gps_sz_pow-df.lon),2)+np.power((df.gps_dl_pow-df.lat),2)))
#   df['dl_centroid_gmi'] = (np.sqrt(np.power((df.gps_sz_gmi-df.lon),2)+np.power((df.gps_dl_gmi-df.lat),2)))
        
fig = px.scatter_mapbox(
    df,
    lat="lon",
    lon="lat",
    mapbox_style="carto-positron",
    zoom=6,
    height=900,
    color="Kategoria_szkoły",
    hover_data = {'lat':False, 'lon':False, 'Kategoria_szkoły':False},
    hover_name = None
)
fig.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    mapbox_center={"lat": 52.1089496, "lon": 19.443120},
    hovermode="closest",
    
)

def prep_map(data_level:str):
    adm_data = AdmUnits(data_path=os.path.join("data/admin_units_pl.geojson"))
    geo_df = adm_data.get_data(data_level=data_level)
    geo_df.teryt = geo_df.teryt.astype(int)

   # school_pow = df[['kod_terytorialny_powiat', 'dl_centroid_pow']].groupby('dl_centroid_pow').agg('mean').reset_index()
   # school_gmi = df[['kod_terytorialny_gmina', 'dl_centroid_gmi']].groupby('dl_centroid_gmi').agg('mean').reset_index()


    if data_level == 'pow':
        col_cent = 'dl_centroid_pow'
        school_pow = df[['kod_terytorialny_powiat', 'dl_centroid_pow']].groupby('kod_terytorialny_powiat').agg('mean').reset_index()
        geo_pow = pd.merge(geo_df, school_pow, how='left', left_on="teryt", right_on="kod_terytorialny_powiat") 
    elif data_level == 'gmi':
        col_cent = 'dl_centroid_gmi'
        school_gmi = df[['kod_terytorialny_gmina_prep2', 'dl_centroid_gmi']].groupby('kod_terytorialny_gmina_prep2').agg('mean').reset_index()
        geo_pow = pd.merge(geo_df, school_gmi, how='left', left_on="teryt", right_on="kod_terytorialny_gmina_prep2")
        
    #school_df = df[[teryt_df, centroid_df]].groupby(centroid_df).agg('mean').reset_index()
    #geo_pow = pd.merge(geo_df, school_pow, how='left', left_on="teryt", right_on=teryt_df)
    
    fig_pow = px.choropleth_mapbox(
    geo_pow, geojson=geo_pow.geometry, locations=geo_pow.index, mapbox_style="carto-positron", zoom=6,color=col_cent ,
    color_continuous_scale="Magma", opacity = 0.7
    )

    return fig_pow.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, mapbox_center={"lat": 52.1089496, "lon": 19.443120})



@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return homepage_layout
    elif pathname == "/map":
        return map_layout
    elif pathname == "/contact":
        return contact_layout

    return dbc.Container(
        children=[
            dbc.Jumbotron(
                [
                    html.H1("404: Not found", className="text-danger"),
                    html.Hr(),
                    html.P(f"The pathname {pathname} was not recognised..."),
                ],
                className="mt-5",
            )
        ]
    )


# @app.callback(
#     Output("county-choropleth", "figure"),
#     [
#         # Input("school_types-indicator", "value"),
#         Input("wojewodztwo-indicator", "value")
#     ],
# )
# def display_selected_data(wojewodztwo):

#     # dff = df[df["Kategoria_szkoły"]=='Szkoła podstawowa']
#     dff = df[(df["Województwo"].isin(wojewodztwo))]
#     fig = px.scatter_mapbox(
#         dff,
#         lat="lon",
#         lon="lat",
#         hover_name="Nazwa",
#         mapbox_style="carto-darkmatter",
#         zoom=6,
#         height=900,
#         color="Kategoria_szkoły",
#         color_discrete_map=px.colors.cyclical.IceFire,
#         size_max=15
#     )
#     fig.update_layout(
#         margin={"r": 0, "t": 0, "l": 0, "b": 0},
#         mapbox_center={"lat": 52.1089496, "lon": 19.443120},
#         hovermode="closest",
#         # annotations=annotations,
#     )

#     return fig


@app.callback(Output("tabs-example-content-1", "children"), Input("tabs-example-1", "value"))
def render_content(tab):
    if tab == "tab-1":
        return html.Div(
            [
                html.Div(
                    id="tabs-content'",
                    children=[
                        dcc.Graph(id="county-choropleth", figure=fig
                            ),
                        dcc.Tooltip(
                            id="graph-tooltip-1",
                            background_color="darkblue",
                            border_color="white",
                            style={"color": "white", "width": "450px", "white-space": "normal"},
                            loading_text="Wczytywanie danych ...",
                            
                        ),
                    ],
                    className="mt-3",
                )
            ]
        )
    elif tab == "tab-2":
        return html.Div(
            [
                html.Div(
                    id="tabs-content'",
                    children=[
                        dcc.Graph(id="county-choropleth", figure=prep_map('pow')
                            ),
                        dcc.Tooltip(
                            id="graph-tooltip-1",
                            background_color="darkblue",
                            border_color="white",
                            style={"color": "white", "width": "450px", "white-space": "normal"},
                            loading_text="Wczytywanie danych ...",
                            
                        ),
                    ],
                    className="mt-3",
                )
            ]
        )
    elif tab == "tab-3":
        return html.Div(
            [
                html.Div(
                    id="tabs-content'",
                    children=[
                        dcc.Graph(id="county-choropleth", figure=prep_map('gmi')
                            ),
                        dcc.Tooltip(
                            id="graph-tooltip-1",
                            background_color="darkblue",
                            border_color="white",
                            style={"color": "white", "width": "450px", "white-space": "normal"},
                            loading_text="Wczytywanie danych ...",
                            
                        ),
                    ],
                    className="mt-3",
                )
            ]
        )

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
    lat = pt["lat"]
    lon = pt["lon"]

    school = df[(df["lon"] == lat) & (df["lat"] == lon)].head(1)

    def my_repl(value):
        return str(value).replace("['", "").replace("']", "")

    name = my_repl(school["Nazwa"].values)
    kat = my_repl(school["Kategoria_szkoły"].values)
    status = my_repl(school["Status"].values)

    woj = my_repl(school["Województwo"].values)
    pow = my_repl(school["Powiat"].values)
    miejscowosc = my_repl(school["Miejscowość"].values)
    ul = my_repl(school["Ulica"].values)
    nr_bud = my_repl(school["Nr_budynku"].values)
    nr_loc = my_repl(school["Nr_lokalu"].values)

    def adres(ul):
        if ul != "[nan]":
            ulica = my_repl(ul) + " " + my_repl(nr_bud)
        else:
            ulica = my_repl(miejscowosc) + " " + my_repl(nr_bud)

        return ulica

    ulica = adres(ul)

    children = [
        html.P(name, style={"font-weight": "bold", "font-size": "15px"}),
        html.P(f"Typ: {kat} ({status}) \n Miejscowość: {miejscowosc}")
        #"Adres: {}".format(ulica),
        #"Woj: {}".format(woj)',)
    ]

    return True, bbox, children


if __name__ == "__main__":
    app.run_server(debug=True)
